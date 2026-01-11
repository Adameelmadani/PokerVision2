"""
Main game controller for Texas Hold'em poker.
"""
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
import copy

from .deck import Card, Deck
from .hand_evaluator import HandEvaluator, HandResult
from .pot import PotManager


class ActionType(Enum):
    """Types of player actions."""
    FOLD = auto()
    CHECK = auto()
    CALL = auto()
    BET = auto()
    RAISE = auto()
    ALL_IN = auto()


@dataclass
class Action:
    """A player action."""
    action_type: ActionType
    amount: int = 0

    def __str__(self) -> str:
        if self.action_type == ActionType.FOLD:
            return "Fold"
        elif self.action_type == ActionType.CHECK:
            return "Check"
        elif self.action_type == ActionType.CALL:
            return f"Call ${self.amount}"
        elif self.action_type == ActionType.BET:
            return f"Bet ${self.amount}"
        elif self.action_type == ActionType.RAISE:
            return f"Raise to ${self.amount}"
        elif self.action_type == ActionType.ALL_IN:
            return f"All-In ${self.amount}"
        return str(self.action_type)


class GamePhase(Enum):
    """Phases of a poker hand."""
    WAITING = auto()
    PREFLOP = auto()
    FLOP = auto()
    TURN = auto()
    RIVER = auto()
    SHOWDOWN = auto()
    HAND_OVER = auto()


@dataclass
class PlayerState:
    """State of a player in the game."""
    seat: int
    name: str
    chips: int
    hole_cards: List[Card] = field(default_factory=list)
    is_active: bool = True
    is_folded: bool = False
    is_all_in: bool = False
    current_bet: int = 0
    total_bet: int = 0
    is_dealer: bool = False
    is_small_blind: bool = False
    is_big_blind: bool = False
    last_action: Optional[Action] = None
    hand_result: Optional[HandResult] = None


@dataclass
class GameState:
    """Complete game state for display and AI."""
    phase: GamePhase
    community_cards: List[Card]
    pot_total: int
    current_bet: int
    min_raise: int
    players: List[PlayerState]
    current_player_idx: int
    dealer_idx: int
    small_blind: int
    big_blind: int
    hand_number: int
    
    def get_player_view(self, player_idx: int, show_all: bool = False) -> 'GameState':
        """Get state from a player's perspective (hide other hole cards)."""
        state_copy = copy.deepcopy(self)
        for i, player in enumerate(state_copy.players):
            if i != player_idx and not show_all:
                if state_copy.phase != GamePhase.SHOWDOWN:
                    player.hole_cards = []
        return state_copy


class PokerGame:
    """Main Texas Hold'em game controller."""

    def __init__(
        self,
        num_players: int = 6,
        starting_chips: int = 10000,
        small_blind: int = 50,
        big_blind: int = 100
    ):
        self.num_players = num_players
        self.starting_chips = starting_chips
        self.small_blind = small_blind
        self.big_blind = big_blind
        
        self.deck = Deck()
        self.pot_manager = PotManager(num_players)
        
        self.players: List[PlayerState] = []
        self.community_cards: List[Card] = []
        self.phase = GamePhase.WAITING
        self.current_player_idx = 0
        self.dealer_idx = 0
        self.hand_number = 0
        
        self.min_raise = big_blind
        self.last_raise_amount = big_blind
        self.last_aggressor_idx = -1
        self.players_acted: set = set()
        
        # Callbacks for UI updates
        self.on_state_change: Optional[Callable[[GameState], None]] = None
        self.on_action: Optional[Callable[[int, Action], None]] = None
        self.on_deal_card: Optional[Callable[[int, Card, bool], None]] = None
        self.on_community_card: Optional[Callable[[Card, int], None]] = None
        self.on_winner: Optional[Callable[[List[int], int, HandResult], None]] = None

    def setup_players(self, player_names: List[str]) -> None:
        """Initialize players with names."""
        self.players = []
        for i, name in enumerate(player_names):
            if name:  # Only add if name is not empty (seat is occupied)
                self.players.append(PlayerState(
                    seat=i,
                    name=name,
                    chips=self.starting_chips,
                    is_active=True
                ))
        self.num_players = len(self.players)
        self.pot_manager = PotManager(self.num_players)

    def start_hand(self) -> None:
        """Start a new hand."""
        self.hand_number += 1
        self.deck.reset()
        self.pot_manager.reset()
        self.community_cards = []
        self.phase = GamePhase.PREFLOP
        
        # Reset player states
        for player in self.players:
            player.hole_cards = []
            player.is_folded = False
            player.is_all_in = False
            player.current_bet = 0
            player.total_bet = 0
            player.last_action = None
            player.hand_result = None
            player.is_dealer = False
            player.is_small_blind = False
            player.is_big_blind = False
        
        # Move dealer button
        self._rotate_dealer()
        
        # Set positions
        active_players = [i for i, p in enumerate(self.players) if p.chips > 0]
        if len(active_players) < 2:
            return  # Not enough players
        
        dealer_pos = active_players.index(self.dealer_idx) if self.dealer_idx in active_players else 0
        self.dealer_idx = active_players[dealer_pos]
        self.players[self.dealer_idx].is_dealer = True
        
        # Small blind
        sb_pos = (dealer_pos + 1) % len(active_players)
        sb_idx = active_players[sb_pos]
        self.players[sb_idx].is_small_blind = True
        self._post_blind(sb_idx, self.small_blind)
        
        # Big blind
        bb_pos = (dealer_pos + 2) % len(active_players)
        bb_idx = active_players[bb_pos]
        self.players[bb_idx].is_big_blind = True
        self._post_blind(bb_idx, self.big_blind)
        
        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                if player.chips > 0 or player.total_bet > 0:
                    card = self.deck.deal_one()
                    player.hole_cards.append(card)
                    if self.on_deal_card:
                        self.on_deal_card(player.seat, card, False)
        
        # Set first to act (after big blind)
        first_pos = (bb_pos + 1) % len(active_players)
        self.current_player_idx = active_players[first_pos]
        self.last_aggressor_idx = bb_idx
        self.min_raise = self.big_blind
        self.last_raise_amount = self.big_blind
        self.players_acted = set()
        
        self._notify_state_change()

    def _rotate_dealer(self) -> None:
        """Move dealer button to next active player."""
        active = [i for i, p in enumerate(self.players) if p.chips > 0]
        if not active:
            return
        
        if self.hand_number == 1:
            self.dealer_idx = active[0]
        else:
            try:
                current_pos = active.index(self.dealer_idx)
                self.dealer_idx = active[(current_pos + 1) % len(active)]
            except ValueError:
                self.dealer_idx = active[0]

    def _post_blind(self, player_idx: int, amount: int) -> None:
        """Post a blind bet."""
        player = self.players[player_idx]
        actual_amount = min(amount, player.chips)
        player.chips -= actual_amount
        player.current_bet = actual_amount
        player.total_bet = actual_amount
        self.pot_manager.add_bet(player_idx, actual_amount, player.chips == 0)
        
        if player.chips == 0:
            player.is_all_in = True

    def get_valid_actions(self, player_idx: int) -> List[ActionType]:
        """Get valid actions for a player."""
        player = self.players[player_idx]
        actions = [ActionType.FOLD]
        
        to_call = self.pot_manager.get_to_call(player_idx)
        
        if to_call == 0:
            actions.append(ActionType.CHECK)
        else:
            actions.append(ActionType.CALL)
        
        if player.chips > to_call:
            if self.pot_manager.current_bet == 0:
                actions.append(ActionType.BET)
            else:
                actions.append(ActionType.RAISE)
        
        if player.chips > 0:
            actions.append(ActionType.ALL_IN)
        
        return actions

    def get_call_amount(self, player_idx: int) -> int:
        """Get amount needed to call."""
        return min(
            self.pot_manager.get_to_call(player_idx),
            self.players[player_idx].chips
        )

    def get_min_raise_to(self, player_idx: int) -> int:
        """Get minimum raise-to amount."""
        current_bet = self.pot_manager.current_bet
        return current_bet + self.min_raise

    def apply_action(self, player_idx: int, action: Action) -> bool:
        """
        Apply a player action.
        
        Returns True if the action was valid and applied.
        """
        player = self.players[player_idx]
        
        if player_idx != self.current_player_idx:
            return False
        
        if player.is_folded or player.is_all_in:
            return False

        valid = False
        
        if action.action_type == ActionType.FOLD:
            player.is_folded = True
            self.pot_manager.fold(player_idx)
            valid = True
            
        elif action.action_type == ActionType.CHECK:
            if self.pot_manager.get_to_call(player_idx) == 0:
                valid = True
                
        elif action.action_type == ActionType.CALL:
            call_amount = self.get_call_amount(player_idx)
            if call_amount > 0:
                player.chips -= call_amount
                player.current_bet += call_amount
                player.total_bet += call_amount
                action.amount = call_amount
                self.pot_manager.add_bet(player_idx, call_amount, player.chips == 0)
                if player.chips == 0:
                    player.is_all_in = True
                valid = True
                
        elif action.action_type in (ActionType.BET, ActionType.RAISE):
            raise_to = action.amount
            to_call = self.pot_manager.get_to_call(player_idx)
            raise_amount = raise_to - self.pot_manager.current_bet
            
            if raise_to >= self.get_min_raise_to(player_idx) or raise_to == player.chips + player.current_bet:
                total_to_put = raise_to - player.current_bet
                if total_to_put <= player.chips:
                    player.chips -= total_to_put
                    player.current_bet = raise_to
                    player.total_bet += total_to_put
                    self.pot_manager.add_bet(player_idx, total_to_put, player.chips == 0)
                    
                    if raise_amount > self.last_raise_amount:
                        self.min_raise = raise_amount
                        self.last_raise_amount = raise_amount
                    
                    self.last_aggressor_idx = player_idx
                    self.players_acted = {player_idx}  # Reset - everyone needs to act again
                    
                    if player.chips == 0:
                        player.is_all_in = True
                    valid = True
                    
        elif action.action_type == ActionType.ALL_IN:
            all_in_amount = player.chips
            new_total_bet = player.current_bet + all_in_amount
            
            player.chips = 0
            player.current_bet = new_total_bet
            player.total_bet += all_in_amount
            player.is_all_in = True
            action.amount = new_total_bet
            self.pot_manager.add_bet(player_idx, all_in_amount, True)
            
            # Check if this is a raise
            if new_total_bet > self.pot_manager.current_bet:
                raise_amount = new_total_bet - self.pot_manager.current_bet
                if raise_amount >= self.min_raise:
                    self.min_raise = raise_amount
                    self.last_raise_amount = raise_amount
                    self.last_aggressor_idx = player_idx
                    self.players_acted = {player_idx}
            
            valid = True

        if valid:
            player.last_action = action
            self.players_acted.add(player_idx)
            
            if self.on_action:
                self.on_action(player_idx, action)
            
            self._advance_game()
            
        return valid

    def _get_active_players(self) -> List[int]:
        """Get indices of players still in the hand."""
        return [
            i for i, p in enumerate(self.players)
            if not p.is_folded and (p.chips > 0 or p.is_all_in or p.total_bet > 0)
        ]

    def _get_players_to_act(self) -> List[int]:
        """Get players who still need to act this round."""
        return [
            i for i, p in enumerate(self.players)
            if not p.is_folded and not p.is_all_in and p.chips > 0
        ]

    def _advance_game(self) -> None:
        """Advance game state after an action."""
        active = self._get_active_players()
        to_act = self._get_players_to_act()
        
        # Check for immediate win
        non_folded = [i for i, p in enumerate(self.players) if not p.is_folded]
        if len(non_folded) == 1:
            self._end_hand([non_folded[0]])
            return
        
        # Check if betting round is complete
        betting_complete = True
        current_bet = self.pot_manager.current_bet
        
        for i in to_act:
            player = self.players[i]
            if i not in self.players_acted:
                betting_complete = False
                break
            if player.current_bet < current_bet and not player.is_all_in:
                betting_complete = False
                break
        
        if betting_complete or len(to_act) == 0:
            self._advance_phase()
        else:
            self._next_player()
        
        self._notify_state_change()

    def _next_player(self) -> None:
        """Move to next player to act."""
        to_act = self._get_players_to_act()
        if not to_act:
            return
        
        current = self.current_player_idx
        for _ in range(len(self.players)):
            current = (current + 1) % len(self.players)
            if current in to_act:
                self.current_player_idx = current
                return
        
        self.current_player_idx = to_act[0]

    def _advance_phase(self) -> None:
        """Advance to next phase of the hand."""
        # Collect bets into pot
        self.pot_manager.collect_bets()
        
        # Reset for new round
        for player in self.players:
            player.current_bet = 0
        self.players_acted = set()
        self.min_raise = self.big_blind
        self.last_raise_amount = self.big_blind
        
        active = self._get_active_players()
        to_act = self._get_players_to_act()
        
        # If only one player can act, skip to showdown
        if len(to_act) <= 1 and self.phase != GamePhase.RIVER:
            # Deal remaining community cards
            while len(self.community_cards) < 5:
                if len(self.community_cards) == 0:
                    self.phase = GamePhase.FLOP
                    self.deck.burn()
                    for _ in range(3):
                        card = self.deck.deal_one()
                        self.community_cards.append(card)
                        if self.on_community_card:
                            self.on_community_card(card, len(self.community_cards) - 1)
                else:
                    if len(self.community_cards) == 3:
                        self.phase = GamePhase.TURN
                    else:
                        self.phase = GamePhase.RIVER
                    self.deck.burn()
                    card = self.deck.deal_one()
                    self.community_cards.append(card)
                    if self.on_community_card:
                        self.on_community_card(card, len(self.community_cards) - 1)
            
            self._showdown()
            return
        
        # Normal phase progression
        if self.phase == GamePhase.PREFLOP:
            self.phase = GamePhase.FLOP
            self.deck.burn()
            for _ in range(3):
                card = self.deck.deal_one()
                self.community_cards.append(card)
                if self.on_community_card:
                    self.on_community_card(card, len(self.community_cards) - 1)
                    
        elif self.phase == GamePhase.FLOP:
            self.phase = GamePhase.TURN
            self.deck.burn()
            card = self.deck.deal_one()
            self.community_cards.append(card)
            if self.on_community_card:
                self.on_community_card(card, len(self.community_cards) - 1)
                
        elif self.phase == GamePhase.TURN:
            self.phase = GamePhase.RIVER
            self.deck.burn()
            card = self.deck.deal_one()
            self.community_cards.append(card)
            if self.on_community_card:
                self.on_community_card(card, len(self.community_cards) - 1)
                
        elif self.phase == GamePhase.RIVER:
            self._showdown()
            return
        
        # Set first to act (first active player after dealer)
        dealer_pos = 0
        for i, p in enumerate(self.players):
            if p.is_dealer:
                dealer_pos = i
                break
        
        for offset in range(1, len(self.players) + 1):
            idx = (dealer_pos + offset) % len(self.players)
            if idx in to_act:
                self.current_player_idx = idx
                break

    def _showdown(self) -> None:
        """Handle showdown and determine winners."""
        self.phase = GamePhase.SHOWDOWN
        self.pot_manager.collect_bets()
        
        active = [i for i, p in enumerate(self.players) if not p.is_folded]
        
        # Evaluate all hands
        for idx in active:
            player = self.players[idx]
            all_cards = player.hole_cards + self.community_cards
            if len(all_cards) >= 5:
                player.hand_result = HandEvaluator.evaluate(all_cards)
        
        # Determine winners for each pot
        winners_by_pot = []
        for pot in self.pot_manager.pots:
            eligible = [i for i in active if i in pot.eligible_players]
            if not eligible:
                eligible = active
            
            if len(eligible) == 1:
                winners_by_pot.append(eligible)
            else:
                hands = [(i, self.players[i].hole_cards + self.community_cards) for i in eligible]
                winners = HandEvaluator.compare_hands(hands)
                winners_by_pot.append(winners)
        
        # Distribute pots
        winnings = self.pot_manager.distribute(winners_by_pot)
        
        for player_idx, amount in winnings.items():
            self.players[player_idx].chips += amount
            if self.on_winner:
                self.on_winner(
                    [player_idx],
                    amount,
                    self.players[player_idx].hand_result
                )
        
        self.phase = GamePhase.HAND_OVER
        self._notify_state_change()

    def _end_hand(self, winners: List[int]) -> None:
        """End hand when all but one player folds."""
        self.pot_manager.collect_bets()
        total_pot = self.pot_manager.total
        
        for winner_idx in winners:
            share = total_pot // len(winners)
            self.players[winner_idx].chips += share
            
            if self.on_winner:
                self.on_winner(winners, share, None)
        
        self.phase = GamePhase.HAND_OVER
        self._notify_state_change()

    def get_state(self) -> GameState:
        """Get current game state."""
        return GameState(
            phase=self.phase,
            community_cards=list(self.community_cards),
            pot_total=self.pot_manager.total,
            current_bet=self.pot_manager.current_bet,
            min_raise=self.min_raise,
            players=[copy.deepcopy(p) for p in self.players],
            current_player_idx=self.current_player_idx,
            dealer_idx=self.dealer_idx,
            small_blind=self.small_blind,
            big_blind=self.big_blind,
            hand_number=self.hand_number
        )

    def _notify_state_change(self) -> None:
        """Notify callbacks of state change."""
        if self.on_state_change:
            self.on_state_change(self.get_state())

    def is_hand_over(self) -> bool:
        """Check if current hand is complete."""
        return self.phase == GamePhase.HAND_OVER

    def get_remaining_players(self) -> int:
        """Get number of players with chips."""
        return sum(1 for p in self.players if p.chips > 0)
