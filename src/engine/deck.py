"""
Card and Deck classes for Texas Hold'em poker.
"""
from enum import IntEnum
from dataclasses import dataclass
from typing import List
import random


class Suit(IntEnum):
    """Card suits."""
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    @property
    def symbol(self) -> str:
        return ['♣', '♦', '♥', '♠'][self.value]

    @property
    def name_short(self) -> str:
        return ['c', 'd', 'h', 's'][self.value]

    @property
    def color(self) -> str:
        return 'red' if self in (Suit.DIAMONDS, Suit.HEARTS) else 'black'


class Rank(IntEnum):
    """Card ranks (2-14, where 14 is Ace)."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def symbol(self) -> str:
        if self.value <= 10:
            return str(self.value)
        return {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}[self.value]


@dataclass(frozen=True)
class Card:
    """Represents a playing card."""
    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.rank.symbol}{self.suit.symbol}"

    def __repr__(self) -> str:
        return f"Card({self.rank.symbol}{self.suit.name_short})"

    @property
    def filename(self) -> str:
        """Get the image filename for this card."""
        return f"{self.rank.symbol.lower()}{self.suit.name_short}.png"

    def to_tuple(self) -> tuple:
        """Convert to tuple for serialization."""
        return (self.rank.value, self.suit.value)

    @classmethod
    def from_tuple(cls, t: tuple) -> 'Card':
        """Create card from tuple."""
        return cls(Rank(t[0]), Suit(t[1]))

    @classmethod
    def from_string(cls, s: str) -> 'Card':
        """Create card from string like 'As', 'Kh', '10c'."""
        s = s.strip()
        suit_char = s[-1].lower()
        rank_str = s[:-1].upper()
        
        suit_map = {'c': Suit.CLUBS, 'd': Suit.DIAMONDS, 'h': Suit.HEARTS, 's': Suit.SPADES}
        rank_map = {'A': Rank.ACE, 'K': Rank.KING, 'Q': Rank.QUEEN, 'J': Rank.JACK, 'T': Rank.TEN, '10': Rank.TEN}
        
        for i in range(2, 10):
            rank_map[str(i)] = Rank(i)
        
        return cls(rank_map[rank_str], suit_map[suit_char])


class Deck:
    """A standard 52-card deck."""

    def __init__(self):
        self._cards: List[Card] = []
        self._dealt_index: int = 0
        self.reset()

    def reset(self) -> None:
        """Reset and shuffle the deck."""
        self._cards = [
            Card(rank, suit)
            for suit in Suit
            for rank in Rank
        ]
        self._dealt_index = 0
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffle the remaining cards."""
        remaining = self._cards[self._dealt_index:]
        random.shuffle(remaining)
        self._cards = self._cards[:self._dealt_index] + remaining

    def deal(self, count: int = 1) -> List[Card]:
        """Deal cards from the deck."""
        if self._dealt_index + count > len(self._cards):
            raise ValueError("Not enough cards in deck")
        
        cards = self._cards[self._dealt_index:self._dealt_index + count]
        self._dealt_index += count
        return cards

    def deal_one(self) -> Card:
        """Deal a single card."""
        return self.deal(1)[0]

    def burn(self) -> None:
        """Burn one card (discard without revealing)."""
        self._dealt_index += 1

    @property
    def remaining(self) -> int:
        """Number of cards remaining in deck."""
        return len(self._cards) - self._dealt_index
