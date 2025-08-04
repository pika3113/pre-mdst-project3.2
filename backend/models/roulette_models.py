import random

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
    1 : "red",
    2 : "black",
    3 : "red",
    4 : "black",
    5 : "red",
    6 : "black",
    7 : "red",
    8 : "black",
    9 : "red",
    10 : "black",
    11 : "black",
    12 : "red",
    13 : "black",
    14 : "red",
    15 : "black",
    16 : "red",
    17 : "black",
    18 : "red",
    19 : "red",
    20 : "black",
    21 : "red",
    22 : "black",
    23 : "red",
    24 : "black",
    25 : "red",
    26 : "black",
    27 : "red",
    28 : "black",
    29 : "black",
    30 : "red",
    31 : "black",
    32 : "red",
    33 : "black",
    34 : "red",
    35 : "black",
    36 : "red"
}

# this is the user input. they select on the roulette table on screen. click on a bet type, then enter how much they want to bet. can have multiple bets - store each bet as a list in a list
bets = [
  ["single", 100, 23], 
  ["double", 100, 9, 32], 
  ["dozens", 100, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
  ["evenodd", 100, "evens"],
  ["column", 100, 1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
  ["color", 100, "red"]
]

# when the user places a bet, remove the amount of money they bet from their personal money bank.
# index[0] is multiplier/bet type   |   index[1] is how much money they bet   |     the rest is the numbers they bet on / red black even odd.
# after running the function roulette() the winnings gets moved into their personal money bank.
def roulette(bets):
  winnings = 0
  pocket = random.randint(0, 36)

  for bet in bets:
    if bet[0] not in ["color", "evenodd"]:
      if pocket in bet[2:]:
        winnings += bet[1] + (multiplier[bet[0]] * bet[1])
        print(f"normal {winnings}")
        continue
    elif pocket != 0 and bet[0] == "color":
      if bet[2] == wheel[pocket]:
        winnings += bet[1] + (multiplier[bet[0]] * bet[1])
        continue
    elif pocket != 0 and bet[0] == "evenodd":
      if bet[2] == "evens" and pocket % 2 == 0:
        winnings += bet[1] + (multiplier[bet[0]] * bet[1])
        continue
      elif bet[2] == "odds" and pocket % 2 != 0:
        winnings += bet[1] + (multiplier[bet[0]] * bet[1])
        continue

  print(pocket, wheel[pocket])
  print(winnings)