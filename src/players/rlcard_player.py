"""
AI player implementation using RLCard agents (DQN, NFSP).
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

class RLCardPlayer(BasePlayer):
    """AI player using RLCard agents for decisions."""

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
        self.player_type = os.path.basename(model_path)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.agent = self._load_agent(model_path)

    def _load_agent(self, model_path: str):
        """Load RLCard agent from checkpoint."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            
            if 'policy_network' in checkpoint or checkpoint.get('agent_type') == 'NFSPAgent':
                from rlcard.agents import NFSPAgent
                # NFSPAgent.from_checkpoint is sometimes buggy, so we load manually if needed
                try:
                    agent = NFSPAgent.from_checkpoint(checkpoint)
                except Exception:
                    agent = NFSPAgent(
                        num_actions=checkpoint.get('num_actions', 5),
                        state_shape=checkpoint['rl_agent']['q_estimator'].get('state_shape', [54]),
                        hidden_layers_sizes=[512, 512],
                        q_mlp_layers=[512, 512],
                        device=self.device
                    )
                    # Manually load the networks
                    agent.policy_network.load_state_dict(checkpoint['policy_network']['qnet'])
                    agent._rl_agent.q_estimator.qnet.load_state_dict(checkpoint['rl_agent']['q_estimator']['qnet'])
            else:
                from rlcard.agents import DQNAgent
                agent = DQNAgent(
                    num_actions=checkpoint.get('num_actions', 5),
                    state_shape=checkpoint['q_estimator'].get('state_shape', [54]),
                    mlp_layers=[512, 512],
                    device=self.device
                )
                agent.from_checkpoint(checkpoint)
            
            return agent
            
        except Exception as e:
            print(f"Failed to load RLCard agent from {model_path}: {e}")
            return None

    def _get_obs(self, game_state: GameState) -> np.ndarray:
        """Convert GameState to RLCard 54-dim observation."""
        obs = np.zeros(54, dtype=np.float32)
        
        # Find our player state
        me = next((p for p in game_state.players if p.seat == self.seat), None)
        if not me:
            return obs
            
        # 1. Encode cards (0-51)
        # RLCard Suit Order: S, H, D, C (0, 1, 2, 3)
        # Our Suit Order: C, D, H, S (0, 1, 2, 3)
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
        # RLCard is 2-player, so we use the "other" player's chips.
        # In 6-player, we'll use the sum of all other players' chips.
        others_chips = sum(p.chips for p in game_state.players if p.seat != self.seat)
        obs[53] = others_chips / total_chips if total_chips > 0 else 0
        
        return obs

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

    async def get_action(self, game_state: GameState) -> Action:
        """Get action from RLCard agent."""
        # Thinking delay
        await asyncio.sleep(self.thinking_time * (0.5 + random.random()))
        
        if not self.agent:
            return Action(ActionType.FOLD)
            
        obs = self._get_obs(game_state)
        legal_actions = self._get_legal_actions(game_state)
        
        # RLCard state format
        state = {
            'obs': obs,
            'legal_actions': legal_actions
        }
        
        # Get action ID from agent
        action_id, _ = self.agent.eval_step(state)
        
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
            # Ensure min raise
            raise_to = max(raise_to, game_state.current_bet + game_state.min_raise)
            # Ensure we have enough chips
            raise_to = min(raise_to, me.chips + me.current_bet)
            
            if game_state.current_bet == 0:
                return Action(ActionType.BET, raise_to)
            return Action(ActionType.RAISE, raise_to)
            
        elif action_id == 3: # RAISE_POT
            raise_amount = to_call + game_state.pot_total
            raise_to = game_state.current_bet + raise_amount
            # Ensure min raise
            raise_to = max(raise_to, game_state.current_bet + game_state.min_raise)
            # Ensure we have enough chips
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
