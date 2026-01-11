"""
Hand evaluation for Texas Hold'em poker.
Uses 7 cards (2 hole + 5 community) to find best 5-card hand.
"""
from enum import IntEnum
from typing import List, Tuple, Optional
from itertools import combinations
from collections import Counter
from dataclasses import dataclass

from .deck import Card, Rank, Suit


class HandRank(IntEnum):
    """Poker hand rankings (higher is better)."""
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

    @property
    def display_name(self) -> str:
        names = {
            1: "High Card",
            2: "One Pair",
            3: "Two Pair",
            4: "Three of a Kind",
            5: "Straight",
            6: "Flush",
            7: "Full House",
            8: "Four of a Kind",
            9: "Straight Flush",
            10: "Royal Flush"
        }
        return names[self.value]


@dataclass
class HandResult:
    """Result of hand evaluation."""
    rank: HandRank
    cards: List[Card]  # Best 5 cards
    kickers: Tuple[int, ...]  # Tiebreaker values
    description: str

    def __lt__(self, other: 'HandResult') -> bool:
        if self.rank != other.rank:
            return self.rank < other.rank
        return self.kickers < other.kickers

    def __eq__(self, other: 'HandResult') -> bool:
        return self.rank == other.rank and self.kickers == other.kickers

    def __le__(self, other: 'HandResult') -> bool:
        return self < other or self == other

    def __gt__(self, other: 'HandResult') -> bool:
        return not self <= other

    def __ge__(self, other: 'HandResult') -> bool:
        return not self < other


class HandEvaluator:
    """Evaluates poker hands."""

    @staticmethod
    def evaluate(cards: List[Card]) -> HandResult:
        """
        Evaluate the best 5-card hand from given cards.
        
        Args:
            cards: List of 5-7 cards
            
        Returns:
            HandResult with rank, best cards, and tiebreakers
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")

        best_result: Optional[HandResult] = None

        # Try all 5-card combinations
        for combo in combinations(cards, 5):
            result = HandEvaluator._evaluate_five(list(combo))
            if best_result is None or result > best_result:
                best_result = result

        return best_result

    @staticmethod
    def _evaluate_five(cards: List[Card]) -> HandResult:
        """Evaluate exactly 5 cards."""
        ranks = sorted([c.rank.value for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        rank_counts = Counter(ranks)
        
        is_flush = len(set(suits)) == 1
        is_straight, straight_high = HandEvaluator._check_straight(ranks)

        # Royal Flush
        if is_flush and is_straight and straight_high == 14:
            return HandResult(
                HandRank.ROYAL_FLUSH,
                cards,
                (14,),
                "Royal Flush"
            )

        # Straight Flush
        if is_flush and is_straight:
            return HandResult(
                HandRank.STRAIGHT_FLUSH,
                cards,
                (straight_high,),
                f"Straight Flush, {Rank(straight_high).symbol} high"
            )

        # Four of a Kind
        quads = [r for r, c in rank_counts.items() if c == 4]
        if quads:
            kicker = [r for r in ranks if r != quads[0]][0]
            return HandResult(
                HandRank.FOUR_OF_A_KIND,
                cards,
                (quads[0], kicker),
                f"Four of a Kind, {Rank(quads[0]).symbol}s"
            )

        # Full House
        trips = [r for r, c in rank_counts.items() if c == 3]
        pairs = [r for r, c in rank_counts.items() if c == 2]
        if trips and pairs:
            return HandResult(
                HandRank.FULL_HOUSE,
                cards,
                (trips[0], pairs[0]),
                f"Full House, {Rank(trips[0]).symbol}s full of {Rank(pairs[0]).symbol}s"
            )

        # Flush
        if is_flush:
            return HandResult(
                HandRank.FLUSH,
                cards,
                tuple(ranks),
                f"Flush, {Rank(ranks[0]).symbol} high"
            )

        # Straight
        if is_straight:
            return HandResult(
                HandRank.STRAIGHT,
                cards,
                (straight_high,),
                f"Straight, {Rank(straight_high).symbol} high"
            )

        # Three of a Kind
        if trips:
            kickers = sorted([r for r in ranks if r != trips[0]], reverse=True)
            return HandResult(
                HandRank.THREE_OF_A_KIND,
                cards,
                (trips[0],) + tuple(kickers),
                f"Three of a Kind, {Rank(trips[0]).symbol}s"
            )

        # Two Pair
        if len(pairs) >= 2:
            pairs_sorted = sorted(pairs, reverse=True)
            kicker = [r for r in ranks if r not in pairs_sorted[:2]][0]
            return HandResult(
                HandRank.TWO_PAIR,
                cards,
                (pairs_sorted[0], pairs_sorted[1], kicker),
                f"Two Pair, {Rank(pairs_sorted[0]).symbol}s and {Rank(pairs_sorted[1]).symbol}s"
            )

        # One Pair
        if pairs:
            kickers = sorted([r for r in ranks if r != pairs[0]], reverse=True)
            return HandResult(
                HandRank.ONE_PAIR,
                cards,
                (pairs[0],) + tuple(kickers),
                f"Pair of {Rank(pairs[0]).symbol}s"
            )

        # High Card
        return HandResult(
            HandRank.HIGH_CARD,
            cards,
            tuple(ranks),
            f"High Card, {Rank(ranks[0]).symbol}"
        )

    @staticmethod
    def _check_straight(ranks: List[int]) -> Tuple[bool, int]:
        """Check if ranks form a straight. Returns (is_straight, high_card)."""
        unique_ranks = sorted(set(ranks), reverse=True)
        
        if len(unique_ranks) < 5:
            return False, 0

        # Check regular straight
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i + 4] == 4:
                return True, unique_ranks[i]

        # Check wheel (A-2-3-4-5)
        if set([14, 5, 4, 3, 2]).issubset(set(unique_ranks)):
            return True, 5  # 5-high straight

        return False, 0

    @staticmethod
    def compare_hands(hands: List[Tuple[int, List[Card]]]) -> List[int]:
        """
        Compare multiple hands and return winner indices.
        
        Args:
            hands: List of (player_idx, cards) tuples
            
        Returns:
            List of winning player indices (multiple if tie)
        """
        results = [(idx, HandEvaluator.evaluate(cards)) for idx, cards in hands]
        
        # Find best result
        best = max(results, key=lambda x: x[1])
        
        # Find all players with the best hand
        winners = [idx for idx, result in results if result == best[1]]
        
        return winners
