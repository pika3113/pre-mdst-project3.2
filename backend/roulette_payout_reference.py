"""
ROULETTE PAYOUT REFERENCE
Based on multipliers from roulette_models.py

=== BET TYPES AND PAYOUTS ===

1. SINGLE NUMBER (35:1)
   - Bet on one specific number (0-36)
   - Bet $100 → Win $3,600 total ($3,500 profit + $100 original bet)
   - Example: Bet $100 on number 23, if 23 hits, you get $3,600

2. DOZENS (2:1) 
   - Bet on 1st 12 (1-12), 2nd 12 (13-24), or 3rd 12 (25-36)
   - Bet $100 → Win $300 total ($200 profit + $100 original bet)
   - Example: Bet $100 on "1st 12", if any number 1-12 hits, you get $300

3. COLUMN (2:1)
   - Bet on 1st column (1,4,7,10,13,16,19,22,25,28,31,34)
   - Bet on 2nd column (2,5,8,11,14,17,20,23,26,29,32,35)  
   - Bet on 3rd column (3,6,9,12,15,18,21,24,27,30,33,36)
   - Bet $100 → Win $300 total ($200 profit + $100 original bet)

4. EIGHTEENS (1:1)
   - Bet on 1-18 or 19-36
   - Bet $100 → Win $200 total ($100 profit + $100 original bet)

5. COLOR (1:1)
   - Bet on Red or Black (Green 0 loses)
   - Bet $100 → Win $200 total ($100 profit + $100 original bet)

6. EVEN/ODD (1:1)
   - Bet on Even or Odd numbers (Green 0 loses)
   - Bet $100 → Win $200 total ($100 profit + $100 original bet)

=== ADDITIONAL BET TYPES (Not yet implemented in UI) ===

7. DOUBLE (17:1) - Split bet on two adjacent numbers
8. THREE (11:1) - Street bet on three numbers in a row
9. FOUR (8:1) - Corner bet on four numbers in a square
10. FIVE (6:1) - Top line bet (0,00,1,2,3)
11. SIX (5:1) - Double street bet on six numbers

=== IMPORTANT NOTES ===

- Green 0 wins ONLY for single number bets on 0
- Green 0 makes COLOR and EVEN/ODD bets lose (house edge)
- Payouts include your original bet amount
- Formula: Total Payout = Bet Amount + (Multiplier × Bet Amount)
- Net Profit = Multiplier × Bet Amount

=== HOUSE EDGE ===

The house edge comes from the Green 0:
- Single number: 1/37 chance = 2.7% house edge
- Outside bets: Green 0 causes losses = 2.7% house edge
"""

print(__doc__)
