"""
AI player implementation using RLCard CFR Agent.
"""
import os
import asyncio
import random
import torch
import numpy as np
from typing import Optional, List, Dict, Any

from .base_player import BasePlayer
from ..engine.game import GameState, Action, ActionType, GamePhase
from ..engine.deck import Card, Suit
from rlcard.agents import CFRAgent

class CFRPlayer(BasePlayer):
    """AI player using RLCard CFR agent for decisions."""

    # RLCard No-Limit Hold'em Action Mapping
    # 0: FOLD, 1: CHECK_CALL, 2: RAISE_HALF_POT, 3: RAISE_POT, 4: ALL_IN
    RLCARD_ACTION_MAP = {
        0: ActionType.FOLD,
        1: ActionType.CALL, # or CHECK
        2: ActionType.RAISE, # Half pot
        3: ActionType.RAISE, # Full pot
        4: ActionType.ALL_IN
    }

    def __init__(
        self,
        seat: int,
        name: str,
        model_path: str,
        thinking_time: float = 1.0
    ):
        super().__init__(seat, name)
        self.model_path = model_path
        self.thinking_time = thinking_time
        self.player_type = "CFR"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.agent = self._load_agent(model_path)

    def _load_agent(self, model_path: str):
        """Load RLCard CFR agent from checkpoint."""
        try:
            # Note: CFR in RLCard saves policy not a full checkpoint like DQN
            # We assume model_path points to the policy binary
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Recreate agent structure
            # Note: CFR usually requires the environment to be passed to init, 
            # but for inference we just need the policy and action translation.
            # Here we wrap it simply to use the policy.
            
            from rlcard.agents import CFRAgent
            # We create a dummy environment config just to satisfy Init if needed,
            # but usually we just load the policy.
            # In RLCard, loading a CFR model purely from file without the env object 
            # is tricky. We'll instantiate a fresh one and load policy.
            
            import rlcard
            env = rlcard.make('no-limit-holdem')
            agent = CFRAgent(env, model_path)
            agent.load() # This looks for 'model_path' on disk to load policy
            
            return agent
            
        except Exception as e:
            print(f"Failed to load CFR agent from {model_path}: {e}")
            return None

    def _get_legal_actions(self, game_state: GameState) -> List[int]:
        """Get legal action IDs for RLCard."""
        # 0: FOLD, 1: CHECK_CALL, 2: RAISE_HALF_POT, 3: RAISE_POT, 4: ALL_IN
        legal = [0, 1] # Fold and Call/Check are almost always legal if it's our turn
        
        me = next((p for p in game_state.players if p.seat == self.seat), None)
        if not me:
            return [0]
            
        to_call = game_state.current_bet - me.current_bet
        
        # Raise actions
        if me.chips > to_call:
            # Half pot
            if me.chips > to_call + game_state.pot_total // 2:
                legal.append(2)
            # Full pot
            if me.chips > to_call + game_state.pot_total:
                legal.append(3)
            # All in
            legal.append(4)
            
        return legal

    def _get_obs(self, game_state: GameState) -> np.ndarray:
        """Convert GameState to RLCard 54-dim observation."""
        obs = np.zeros(54, dtype=np.float32)
        
        # Find our player state
        me = next((p for p in game_state.players if p.seat == self.seat), None)
        if not me:
            return obs
            
        # 1. Encode cards (0-51)
        suit_map = {
            Suit.SPADES: 0,
            Suit.HEARTS: 1,
            Suit.DIAMONDS: 2,
            Suit.CLUBS: 3
        }
        
        all_cards = me.hole_cards + game_state.community_cards
        for card in all_cards:
            suit_idx = suit_map.get(card.suit, 0)
            rank_idx = card.rank.value - 2 # 2-14 -> 0-12
            idx = rank_idx + suit_idx * 13
            if 0 <= idx < 52:
                obs[idx] = 1.0
                
        # 2. Chips (52)
        total_chips = sum(p.chips for p in game_state.players) + game_state.pot_total
        obs[52] = me.chips / total_chips if total_chips > 0 else 0
        
        # 3. Other chips (53)
        others_chips = sum(p.chips for p in game_state.players if p.seat != self.seat)
        obs[53] = others_chips / total_chips if total_chips > 0 else 0
        
        return obs

    async def get_action(self, game_state: GameState) -> Action:
        """Get action from CFR agent."""
        await asyncio.sleep(self.thinking_time * (0.5 + random.random()))
        
        if not self.agent:
            return Action(ActionType.FOLD)
            
        obs = self._get_obs(game_state)
        legal_actions = self._get_legal_actions(game_state)
        
        # RLCard state format
        state = {
            'obs': obs,
            'legal_actions': legal_actions,
            # CFR often requires string representation of cards for abstraction
            # We'll rely on the numeric observation if possible, or build basic dict
            'raw_obs': obs, 
            'raw_legal_actions': legal_actions
        }
        
        # Evaluate step in CFR usually returns action_id directly or probs
        action_id = self.agent.step(state)
        
        return self._translate_action(action_id, game_state)

    def _translate_action(self, action_id: int, game_state: GameState) -> Action:
        """Translate RLCard action ID to engine Action."""
        me = next((p for p in game_state.players if p.seat == self.seat), None)
        if not me:
            return Action(ActionType.FOLD)
            
        to_call = game_state.current_bet - me.current_bet
        
        if action_id == 0: # FOLD
            return Action(ActionType.FOLD)
            
        elif action_id == 1: # CHECK_CALL
            if to_call == 0:
                return Action(ActionType.CHECK)
            return Action(ActionType.CALL, min(to_call, me.chips))
            
        elif action_id == 2: # RAISE_HALF_POT
            raise_amount = to_call + game_state.pot_total // 2
            raise_to = game_state.current_bet + raise_amount
            raise_to = max(raise_to, game_state.current_bet + game_state.min_raise)
            raise_to = min(raise_to, me.chips + me.current_bet)
            
            if game_state.current_bet == 0:
                return Action(ActionType.BET, raise_to)
            return Action(ActionType.RAISE, raise_to)
            
        elif action_id == 3: # RAISE_POT
            raise_amount = to_call + game_state.pot_total
            raise_to = game_state.current_bet + raise_amount
            raise_to = max(raise_to, game_state.current_bet + game_state.min_raise)
            raise_to = min(raise_to, me.chips + me.current_bet)
            
            if game_state.current_bet == 0:
                return Action(ActionType.BET, raise_to)
            return Action(ActionType.RAISE, raise_to)
            
        elif action_id == 4: # ALL_IN
            return Action(ActionType.ALL_IN, me.chips + me.current_bet)
            
        return Action(ActionType.FOLD)

    def reset(self) -> None:
        """Reset for new hand."""
        pass