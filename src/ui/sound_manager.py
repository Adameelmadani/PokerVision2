"""
Sound manager for poker game audio.
"""
import os
from pathlib import Path
from typing import Optional

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("pygame not installed - sounds disabled")


class SoundManager:
    """Manages game sound effects."""

    # Sound file names
    SOUNDS = {
        'card_deal': 'card_deal.wav',
        'card_flip': 'card_flip.wav',
        'chip_bet': 'chip_bet.wav',
        'chip_win': 'chip_win.wav',
        'check': 'check.wav',
        'fold': 'fold.wav',
        'all_in': 'all_in.wav',
        'turn_notify': 'turn_notify.wav',
        'timer_warning': 'timer_warning.wav',
    }

    def __init__(self, sounds_dir: str = "assets/sounds"):
        self.sounds_dir = Path(sounds_dir)
        self.sounds = {}
        self.enabled = PYGAME_AVAILABLE
        self.volume = 0.7
        
        if self.enabled:
            self._load_sounds()

    def _load_sounds(self):
        """Load all sound files."""
        if not self.sounds_dir.exists():
            self.sounds_dir.mkdir(parents=True, exist_ok=True)
        
        for name, filename in self.SOUNDS.items():
            path = self.sounds_dir / filename
            if path.exists():
                try:
                    self.sounds[name] = pygame.mixer.Sound(str(path))
                    self.sounds[name].set_volume(self.volume)
                except Exception as e:
                    print(f"Failed to load sound {filename}: {e}")

    def play(self, sound_name: str):
        """Play a sound effect."""
        if not self.enabled:
            return
        
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()

    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def enable(self, enabled: bool = True):
        """Enable or disable sounds."""
        self.enabled = enabled and PYGAME_AVAILABLE

    def stop_all(self):
        """Stop all playing sounds."""
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()


# Global sound manager instance
_sound_manager: Optional[SoundManager] = None


def get_sound_manager() -> SoundManager:
    """Get the global sound manager instance."""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundManager()
    return _sound_manager


def play_sound(name: str):
    """Convenience function to play a sound."""
    get_sound_manager().play(name)
