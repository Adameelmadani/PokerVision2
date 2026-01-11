"""
Pot management for Texas Hold'em poker.
Handles main pot and side pots for all-in situations.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from collections import defaultdict


@dataclass
class Pot:
    """Represents a pot (main or side)."""
    amount: int = 0
    eligible_players: Set[int] = field(default_factory=set)
    
    def add(self, amount: int) -> None:
        self.amount += amount


class PotManager:
    """Manages main pot and side pots."""

    def __init__(self, num_players: int):
        self.num_players = num_players
        self.pots: List[Pot] = [Pot()]
        self.player_bets: Dict[int, int] = defaultdict(int)  # Current round bets
        self.player_total_bets: Dict[int, int] = defaultdict(int)  # Total bets in hand
        self.all_in_players: Set[int] = set()
        self.folded_players: Set[int] = set()

    def reset(self) -> None:
        """Reset for a new hand."""
        self.pots = [Pot()]
        self.player_bets.clear()
        self.player_total_bets.clear()
        self.all_in_players.clear()
        self.folded_players.clear()

    def add_bet(self, player_idx: int, amount: int, is_all_in: bool = False) -> None:
        """Add a bet from a player."""
        self.player_bets[player_idx] += amount
        self.player_total_bets[player_idx] += amount
        
        if is_all_in:
            self.all_in_players.add(player_idx)

    def fold(self, player_idx: int) -> None:
        """Mark player as folded."""
        self.folded_players.add(player_idx)

    def collect_bets(self) -> None:
        """
        Collect all bets into pots at end of betting round.
        Creates side pots if needed for all-in situations.
        """
        if not self.player_bets:
            return

        # Get all unique bet amounts from all-in players
        all_in_amounts = sorted(set(
            self.player_bets[p] for p in self.all_in_players
            if p in self.player_bets and self.player_bets[p] > 0
        ))

        # Active players for this collection (not folded)
        active = set(
            p for p in self.player_bets.keys()
            if p not in self.folded_players and self.player_bets[p] > 0
        )

        if not active:
            self.player_bets.clear()
            return

        # Create side pots for each all-in level
        prev_level = 0
        for level in all_in_amounts:
            pot_amount = 0
            eligible = set()
            
            for player in list(active):
                bet = self.player_bets[player]
                contribution = min(bet, level) - prev_level
                if contribution > 0:
                    pot_amount += contribution
                    self.player_bets[player] -= contribution
                    eligible.add(player)
            
            if pot_amount > 0:
                # Add to existing pot or create new one
                if not self.pots[-1].eligible_players:
                    self.pots[-1].amount += pot_amount
                    self.pots[-1].eligible_players = eligible
                elif self.pots[-1].eligible_players == eligible:
                    self.pots[-1].amount += pot_amount
                else:
                    self.pots.append(Pot(pot_amount, eligible))
            
            prev_level = level

        # Remaining bets go to main pot
        remaining_amount = sum(self.player_bets.values())
        if remaining_amount > 0:
            remaining_eligible = set(
                p for p in active
                if self.player_bets[p] > 0
            )
            
            if not self.pots[-1].eligible_players:
                self.pots[-1].amount += remaining_amount
                self.pots[-1].eligible_players = remaining_eligible
            elif self.pots[-1].eligible_players >= remaining_eligible:
                self.pots[-1].amount += remaining_amount
            else:
                self.pots.append(Pot(remaining_amount, remaining_eligible))

        self.player_bets.clear()

    @property
    def total(self) -> int:
        """Total chips in all pots."""
        return sum(p.amount for p in self.pots) + sum(self.player_bets.values())

    @property
    def current_bet(self) -> int:
        """Current highest bet in this round."""
        if not self.player_bets:
            return 0
        return max(self.player_bets.values())

    def get_to_call(self, player_idx: int) -> int:
        """Amount player needs to call."""
        return self.current_bet - self.player_bets.get(player_idx, 0)

    def distribute(self, winners_by_pot: List[List[int]]) -> Dict[int, int]:
        """
        Distribute pots to winners.
        
        Args:
            winners_by_pot: List of winner lists, one per pot
            
        Returns:
            Dict of player_idx -> amount won
        """
        winnings: Dict[int, int] = defaultdict(int)
        
        for pot_idx, pot in enumerate(self.pots):
            if pot_idx < len(winners_by_pot):
                winners = winners_by_pot[pot_idx]
            else:
                winners = winners_by_pot[-1] if winners_by_pot else []
            
            if not winners:
                continue
                
            # Filter winners to those eligible for this pot
            eligible_winners = [w for w in winners if w in pot.eligible_players]
            if not eligible_winners:
                eligible_winners = winners
            
            # Split pot among winners
            share = pot.amount // len(eligible_winners)
            remainder = pot.amount % len(eligible_winners)
            
            for i, winner in enumerate(eligible_winners):
                win_amount = share + (1 if i < remainder else 0)
                winnings[winner] += win_amount

        return dict(winnings)

    def get_pot_display(self) -> List[Dict]:
        """Get pot info for display."""
        result = []
        for i, pot in enumerate(self.pots):
            name = "Main Pot" if i == 0 else f"Side Pot {i}"
            result.append({
                'name': name,
                'amount': pot.amount,
                'eligible': list(pot.eligible_players)
            })
        return result
