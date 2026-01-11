"""
Human player implementation - waits for GUI input.
"""
import asyncio
from typing import Optional

from .base_player import BasePlayer
from ..engine.game import GameState, Action


class HumanPlayer(BasePlayer):
    """Human player controlled via GUI."""

    def __init__(self, seat: int, name: str = "Player"):
        super().__init__(seat, name)
        self.player_type = "human"
        self._pending_action: Optional[Action] = None
        self._action_event = asyncio.Event()

    async def get_action(self, game_state: GameState) -> Action:
        """Wait for human input from GUI."""
        self._action_event.clear()
        self._pending_action = None
        
        # Wait for action to be set via set_action
        await self._action_event.wait()
        
        action = self._pending_action
        self._pending_action = None
        return action

    def set_action(self, action: Action) -> None:
        """Set action from GUI (called by UI thread)."""
        self._pending_action = action
        self._action_event.set()

    def cancel_action(self) -> None:
        """Cancel waiting for action."""
        self._action_event.set()

    def reset(self) -> None:
        """Reset for new hand."""
        self._pending_action = None
        self._action_event.clear()

    def is_waiting(self) -> bool:
        """Check if waiting for input."""
        return not self._action_event.is_set()
