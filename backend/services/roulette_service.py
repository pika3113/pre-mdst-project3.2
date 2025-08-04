"""
Roulette game service
"""
import random
from typing import List, Dict, Any

# Import the multiplier and wheel from models
multiplier = {
    "single" : 35,
    "double" : 17,
    "three" : 11,
    "four" : 8,
    "five" : 6,
    "six" : 5,
    "dozens" : 2,
    "column" : 2,
    "eighteens" : 1,
    "color" : 1,
    "evenodd" : 1
}

wheel = {
    0 : "green",
    1 : "red", 2 : "black", 3 : "red", 4 : "black", 5 : "red", 6 : "black",
    7 : "red", 8 : "black", 9 : "red", 10 : "black", 11 : "black", 12 : "red",
    13 : "black", 14 : "red", 15 : "black", 16 : "red", 17 : "black", 18 : "red",
    19 : "red", 20 : "black", 21 : "red", 22 : "black", 23 : "red", 24 : "black",
    25 : "red", 26 : "black", 27 : "red", 28 : "black", 29 : "black", 30 : "red",
    31 : "black", 32 : "red", 33 : "black", 34 : "red", 35 : "black", 36 : "red"
}


class RouletteService:
    """Service to handle Roulette game logic"""
    
    def __init__(self):
        self.multiplier = multiplier
        self.wheel = wheel
    
    def play_roulette(self, bets: List[List]) -> Dict[str, Any]:
        """
        Play a round of roulette with given bets
        
        Args:
            bets: List of bets in format [bet_type, amount, ...numbers/color/evenodd]
            
        Returns:
            Dictionary with result information
        """
        winnings = 0
        pocket = random.randint(0, 36)
        winning_bets = []
        losing_bets = []

        for bet in bets:
            bet_type = bet[0]
            bet_amount = bet[1]
            is_winning_bet = False
            
            # Follow the exact logic from roulette_models.py
            if bet_type not in ["color", "evenodd"]:
                # Number-based bets (single, double, three, four, five, six, dozens, column, eighteens)
                if pocket in bet[2:]:
                    payout = bet_amount + (self.multiplier[bet_type] * bet_amount)
                    winnings += payout
                    winning_bets.append({
                        "type": bet_type,
                        "amount": bet_amount,
                        "payout": payout,
                        "numbers": bet[2:]
                    })
                    is_winning_bet = True
            elif pocket != 0 and bet_type == "color":
                # Color bet - only wins if pocket is not 0 (green) and matches color
                if bet[2] == self.wheel[pocket]:
                    payout = bet_amount + (self.multiplier[bet_type] * bet_amount)
                    winnings += payout
                    winning_bets.append({
                        "type": bet_type,
                        "amount": bet_amount,
                        "payout": payout,
                        "color": bet[2]
                    })
                    is_winning_bet = True
            elif pocket != 0 and bet_type == "evenodd":
                # Even/Odd bet - only wins if pocket is not 0 (green)
                if (bet[2] == "evens" and pocket % 2 == 0) or (bet[2] == "odds" and pocket % 2 != 0):
                    payout = bet_amount + (self.multiplier[bet_type] * bet_amount)
                    winnings += payout
                    winning_bets.append({
                        "type": bet_type,
                        "amount": bet_amount,
                        "payout": payout,
                        "selection": bet[2]
                    })
                    is_winning_bet = True
            
            if not is_winning_bet:
                losing_bets.append({
                    "type": bet_type,
                    "amount": bet_amount,
                    "selection": bet[2:] if bet_type not in ["color", "evenodd"] else bet[2]
                })

        return {
            "pocket": pocket,
            "color": self.wheel[pocket],
            "total_winnings": winnings,
            "winning_bets": winning_bets,
            "losing_bets": losing_bets,
            "net_result": winnings - sum(bet[1] for bet in bets)
        }
    
    def get_bet_types(self) -> Dict[str, Any]:
        """Get available bet types and their multipliers"""
        return {
            "multipliers": self.multiplier,
            "wheel": self.wheel
        }
    
    def validate_bet(self, bet: List) -> bool:
        """Validate a single bet"""
        if len(bet) < 3:
            return False
        
        bet_type = bet[0]
        if bet_type not in self.multiplier:
            return False
        
        if bet[1] <= 0:  # bet amount must be positive
            return False
        
        return True
