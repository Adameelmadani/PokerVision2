"""
Base player interface for Texas Hold'em.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..engine.game import GameState, Action


@dataclass
class PlayerInfo:
    """Static player information."""
    seat: int
    name: str
    player_type: str  # 'human' or model name


class BasePlayer(ABC):
    """Abstract base class for all player types."""

    def __init__(self, seat: int, name: str):
        self.seat = seat
        self.name = name
        self.player_type = "base"

    @abstractmethod
    async def get_action(self, game_state: 'GameState') -> 'Action':
        """
        Get player's action for the current game state.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            Action to take
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset player state for new hand."""
        pass

    def get_info(self) -> PlayerInfo:
        """Get player info for display."""
        return PlayerInfo(
            seat=self.seat,
            name=self.name,
            player_type=self.player_type
        )
