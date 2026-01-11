"""
AI player implementation - uses PyTorch models for decisions.
"""
import asyncio
import os
import random
from pathlib import Path
from typing import Optional, List, Dict, Any

import torch
import numpy as np

from .base_player import BasePlayer
from ..engine.game import GameState, Action, ActionType, GamePhase
from ..engine.deck import Card


class AIPlayer(BasePlayer):
    """AI player using PyTorch model for decisions."""

    # Action mapping for RL models
    ACTION_MAP = {
        0: ActionType.FOLD,
        1: ActionType.CHECK,  # or CALL
        2: ActionType.RAISE,  # or BET
        3: ActionType.ALL_IN
    }

    def __init__(
        self,
        seat: int,
        name: str,
        model_path: Optional[str] = None,
        thinking_time: float = 1.0
    ):
        super().__init__(seat, name)
        self.player_type = os.path.basename(model_path) if model_path else "AI"
        self.model_path = model_path
        self.model: Optional[torch.nn.Module] = None
        self.thinking_time = thinking_time
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)

    def _load_model(self, model_path: str) -> None:
        """Load PyTorch model from .pth file."""
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'model_state_dict' in checkpoint:
                    # Standard checkpoint format
                    self.model = self._create_default_network()
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                elif 'state_dict' in checkpoint:
                    self.model = self._create_default_network()
                    self.model.load_state_dict(checkpoint['state_dict'])
                elif 'q_network' in checkpoint:
                    # DQN format
                    self.model = checkpoint['q_network']
                elif 'actor' in checkpoint:
                    # PPO/Actor-Critic format
                    self.model = checkpoint['actor']
                elif 'average_policy' in checkpoint:
                    # NFSP format
                    self.model = checkpoint['average_policy']
                else:
                    # Try loading as state dict directly
                    self.model = self._create_default_network()
                    self.model.load_state_dict(checkpoint)
            else:
                # Assume it's a full model
                self.model = checkpoint
            
            if self.model:
                self.model.to(self.device)
                self.model.eval()
                print(f"Loaded model from {model_path}")
                
        except Exception as e:
            print(f"Failed to load model {model_path}: {e}")
            self.model = None

    def _create_default_network(self) -> torch.nn.Module:
        """Create a default network architecture."""
        # Default architecture for poker (54 input features -> 4 actions)
        return torch.nn.Sequential(
            torch.nn.Linear(54, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 256),
            torch.nn.ReLU(),
            torch.nn.Linear(256, 4)
        )

    def _state_to_tensor(self, game_state: GameState) -> torch.Tensor:
        """
        Convert game state to model input tensor.
        
        Feature vector (54 dimensions):
        - 52: One-hot encoding of hole cards and community cards
        - 1: Normalized pot size
        - 1: Normalized stack size
        """
        features = np.zeros(54, dtype=np.float32)
        
        # Find our player state
        our_player = None
        for p in game_state.players:
            if p.seat == self.seat:
                our_player = p
                break
        
        if not our_player:
            return torch.tensor(features).unsqueeze(0).to(self.device)
        
        # Encode hole cards (indices 0-51)
        for card in our_player.hole_cards:
            idx = (card.rank.value - 2) + (card.suit.value * 13)
            if 0 <= idx < 52:
                features[idx] = 1.0
        
        # Encode community cards
        for card in game_state.community_cards:
            idx = (card.rank.value - 2) + (card.suit.value * 13)
            if 0 <= idx < 52:
                features[idx] = 0.5  # Different weight for community cards
        
        # Pot size (normalized)
        total_chips = sum(p.chips for p in game_state.players) + game_state.pot_total
        features[52] = game_state.pot_total / max(total_chips, 1)
        
        # Our stack (normalized)
        features[53] = our_player.chips / max(total_chips, 1)
        
        return torch.tensor(features).unsqueeze(0).to(self.device)

    def _get_valid_action(
        self,
        model_action: int,
        game_state: GameState
    ) -> Action:
        """Convert model action to valid game action."""
        # Find our player
        our_player = None
        for p in game_state.players:
            if p.seat == self.seat:
                our_player = p
                break
        
        if not our_player:
            return Action(ActionType.FOLD)
        
        to_call = game_state.current_bet - our_player.current_bet
        
        action_type = self.ACTION_MAP.get(model_action, ActionType.FOLD)
        
        if action_type == ActionType.FOLD:
            return Action(ActionType.FOLD)
        
        elif action_type == ActionType.CHECK:
            if to_call == 0:
                return Action(ActionType.CHECK)
            else:
                # Call instead
                return Action(ActionType.CALL, min(to_call, our_player.chips))
        
        elif action_type == ActionType.RAISE:
            if our_player.chips <= to_call:
                # Not enough to raise, just call
                return Action(ActionType.CALL, our_player.chips)
            
            # Raise amount: between min raise and 3x pot
            min_raise = game_state.min_raise + game_state.current_bet
            max_raise = min(
                game_state.current_bet + game_state.pot_total * 3,
                our_player.chips + our_player.current_bet
            )
            
            # Use a random raise size between min and max
            raise_to = random.randint(min_raise, max(min_raise, int(max_raise)))
            
            if game_state.current_bet == 0:
                return Action(ActionType.BET, raise_to)
            else:
                return Action(ActionType.RAISE, raise_to)
        
        elif action_type == ActionType.ALL_IN:
            return Action(ActionType.ALL_IN, our_player.chips + our_player.current_bet)
        
        return Action(ActionType.FOLD)

    async def get_action(self, game_state: GameState) -> Action:
        """Get AI decision with thinking delay."""
        # Add thinking time for natural feel
        await asyncio.sleep(self.thinking_time * (0.5 + random.random()))
        
        if self.model is None:
            # Fallback to simple heuristic if no model
            return self._heuristic_action(game_state)
        
        try:
            with torch.no_grad():
                state_tensor = self._state_to_tensor(game_state)
                action_probs = self.model(state_tensor)
                
                if isinstance(action_probs, tuple):
                    action_probs = action_probs[0]
                
                # Get action with highest probability
                action_idx = action_probs.argmax(dim=1).item()
                
                return self._get_valid_action(action_idx, game_state)
                
        except Exception as e:
            print(f"Model inference error: {e}")
            return self._heuristic_action(game_state)

    def _heuristic_action(self, game_state: GameState) -> Action:
        """Simple heuristic-based play when no model available."""
        our_player = None
        for p in game_state.players:
            if p.seat == self.seat:
                our_player = p
                break
        
        if not our_player:
            return Action(ActionType.FOLD)
        
        to_call = game_state.current_bet - our_player.current_bet
        pot_odds = to_call / max(game_state.pot_total + to_call, 1)
        
        # Simple hand strength estimation
        hand_strength = self._estimate_hand_strength(
            our_player.hole_cards,
            game_state.community_cards
        )
        
        # Decision logic
        if hand_strength > 0.8:
            # Strong hand - raise
            raise_amount = game_state.current_bet + game_state.pot_total // 2
            raise_amount = min(raise_amount, our_player.chips + our_player.current_bet)
            if game_state.current_bet == 0:
                return Action(ActionType.BET, max(game_state.big_blind, raise_amount))
            return Action(ActionType.RAISE, raise_amount)
        
        elif hand_strength > 0.5:
            # Medium hand - call/check
            if to_call == 0:
                return Action(ActionType.CHECK)
            if pot_odds < 0.3:
                return Action(ActionType.CALL, min(to_call, our_player.chips))
            return Action(ActionType.FOLD)
        
        elif hand_strength > 0.3:
            # Weak hand - check or fold
            if to_call == 0:
                return Action(ActionType.CHECK)
            if pot_odds < 0.15:
                return Action(ActionType.CALL, min(to_call, our_player.chips))
            return Action(ActionType.FOLD)
        
        else:
            # Very weak - fold unless free
            if to_call == 0:
                return Action(ActionType.CHECK)
            return Action(ActionType.FOLD)

    def _estimate_hand_strength(
        self,
        hole_cards: List[Card],
        community_cards: List[Card]
    ) -> float:
        """Estimate hand strength (0-1)."""
        if not hole_cards:
            return 0.0
        
        # Simple pre-flop hand strength
        if not community_cards:
            return self._preflop_strength(hole_cards)
        
        # Post-flop: use hand evaluator
        from ..engine.hand_evaluator import HandEvaluator, HandRank
        
        try:
            all_cards = hole_cards + community_cards
            if len(all_cards) >= 5:
                result = HandEvaluator.evaluate(all_cards)
                # Normalize hand rank to 0-1
                return result.rank.value / 10.0
        except:
            pass
        
        return 0.3

    def _preflop_strength(self, hole_cards: List[Card]) -> float:
        """Estimate pre-flop hand strength."""
        if len(hole_cards) != 2:
            return 0.3
        
        c1, c2 = hole_cards
        high = max(c1.rank.value, c2.rank.value)
        low = min(c1.rank.value, c2.rank.value)
        is_pair = c1.rank == c2.rank
        is_suited = c1.suit == c2.suit
        gap = high - low
        
        strength = 0.3
        
        # Pairs
        if is_pair:
            strength = 0.5 + (high - 2) / 24  # 0.5 - 1.0
        else:
            # High cards
            strength = (high + low - 4) / 48  # 0 - 0.5
            
            # Suited bonus
            if is_suited:
                strength += 0.08
            
            # Connector bonus
            if gap == 1:
                strength += 0.05
            elif gap == 2:
                strength += 0.03
        
        # Premium hands
        if is_pair and high >= 12:  # QQ+
            strength = min(1.0, strength + 0.2)
        if high == 14 and low >= 12:  # AK, AQ
            strength = min(1.0, strength + 0.15)
        
        return min(1.0, max(0.0, strength))

    def reset(self) -> None:
        """Reset for new hand."""
        pass


def get_available_models(models_dir: str = "models") -> List[str]:
    """Get list of available .pth model files."""
    models_path = Path(models_dir)
    if not models_path.exists():
        return []
    
    return [
        str(f) for f in models_path.glob("*.pth")
    ]


def get_model_name(model_path: str) -> str:
    """Get display name for a model file."""
    return Path(model_path).stem
