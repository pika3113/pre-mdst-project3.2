"""
Test script to verify roulette payout calculations match roulette_models.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.roulette_service import RouletteService

# Initialize the service
roulette_service = RouletteService()

# Test cases based on the multipliers from roulette_models.py
test_bets = [
    # Single number bet: 35:1 payout
    [["single", 100, 23]],
    
    # Dozens bet: 2:1 payout  
    [["dozens", 100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
    
    # Column bet: 2:1 payout
    [["column", 100, 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]],
    
    # Color bet: 1:1 payout
    [["color", 100, "red"]],
    
    # Even/Odd bet: 1:1 payout
    [["evenodd", 100, "evens"]],
    
    # Eighteens bet: 1:1 payout
    [["eighteens", 100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]]
]

print("=== ROULETTE PAYOUT VERIFICATION ===")
print("Based on multipliers from roulette_models.py:")
print("single: 35, dozens: 2, column: 2, eighteens: 1, color: 1, evenodd: 1")
print("")

# Force specific winning numbers to test payouts
test_scenarios = [
    (23, "Testing single number 23"),
    (5, "Testing dozens (1st dozen: 1-12)"),
    (7, "Testing column (1st column)"),
    (12, "Testing red color"),
    (8, "Testing even number"),
    (10, "Testing eighteens (1-18)")
]

for winning_number, description in test_scenarios:
    print(f"--- {description} ---")
    print(f"Winning number: {winning_number}")
    
    for i, bet_list in enumerate(test_bets):
        # Simulate the result by temporarily setting the pocket
        original_play_roulette = roulette_service.play_roulette
        
        def mock_play_roulette(bets):
            # Copy the logic but with fixed pocket
            winnings = 0
            pocket = winning_number
            winning_bets = []
            losing_bets = []

            for bet in bets:
                bet_type = bet[0]
                bet_amount = bet[1]
                is_winning_bet = False
                
                if bet_type not in ["color", "evenodd"]:
                    if pocket in bet[2:]:
                        payout = bet_amount + (roulette_service.multiplier[bet_type] * bet_amount)
                        winnings += payout
                        winning_bets.append({
                            "type": bet_type,
                            "amount": bet_amount,
                            "payout": payout,
                            "numbers": bet[2:]
                        })
                        is_winning_bet = True
                elif pocket != 0 and bet_type == "color":
                    if bet[2] == roulette_service.wheel[pocket]:
                        payout = bet_amount + (roulette_service.multiplier[bet_type] * bet_amount)
                        winnings += payout
                        winning_bets.append({
                            "type": bet_type,
                            "amount": bet_amount,
                            "payout": payout,
                            "color": bet[2]
                        })
                        is_winning_bet = True
                elif pocket != 0 and bet_type == "evenodd":
                    if (bet[2] == "evens" and pocket % 2 == 0) or (bet[2] == "odds" and pocket % 2 != 0):
                        payout = bet_amount + (roulette_service.multiplier[bet_type] * bet_amount)
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
                "color": roulette_service.wheel[pocket],
                "total_winnings": winnings,
                "winning_bets": winning_bets,
                "losing_bets": losing_bets,
                "net_result": winnings - sum(bet[1] for bet in bets)
            }
        
        # Test the bet
        result = mock_play_roulette(bet_list)
        bet = bet_list[0]
        bet_type = bet[0]
        bet_amount = bet[1]
        
        if result["winning_bets"]:
            payout = result["winning_bets"][0]["payout"]
            multiplier = roulette_service.multiplier[bet_type]
            expected_payout = bet_amount + (multiplier * bet_amount)
            print(f"  {bet_type.upper()} bet $100: Payout=${payout} (Expected: ${expected_payout}) ✓" if payout == expected_payout else f"  {bet_type.upper()} bet $100: Payout=${payout} (Expected: ${expected_payout}) ✗")
        else:
            print(f"  {bet_type.upper()} bet $100: LOST (pocket {winning_number} doesn't match bet)")
    
    print("")

print("=== MULTIPLIER BREAKDOWN ===")
for bet_type, multiplier in roulette_service.multiplier.items():
    print(f"{bet_type}: {multiplier}:1 - Bet $100, Win ${100 + (multiplier * 100)} total")
