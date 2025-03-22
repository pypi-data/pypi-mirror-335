# Tourneyket

Package to let you easily represent and progress Bracket-style single elimination Tournaments,
allowing you to focus on matchup logic and analysis without worrying about the boilerplate. 
Supports 2, 4, 8, 16, 32, 64...n^2 starting teams.

The Bracket object accepts an initial bracket and a function to select matchup winner.
Automatically fills out the rest of the bracket using whatever logic you provide, 
and implements a method to print out the final bracket to console in a nice, bracket shaped format. 

Example:
```python
from tourneyket import Bracket

# List of competitors. 1 plays 2, 3 plays 4... and so on. Likewise, inner of 1v2 plays winner of 3v4, etc.
my_tournament = [{"name": "Kitten State", "power_level": 9001},
                {"name": "Bunnyville", "power_level": 6000},
                {"name": "Muscle Hamsters", "power_level": 2},
                {"name": "Doggy Dog World", "power_level": 8500},
                {"name": "Horsies", "power_level": 8934},
                {"name": "Lizard Wizards", "power_level": 7800},
                {"name": "Ole Penguin", "power_level": 8300},
                {"name": "Pigchamps", "power_level": 7500}]

def pick_by_power_level(a, b):
    if a["power_level"] > b["power_level"]:
        return a 
    else: 
        return b

MyBracket = Bracket(my_tournament)
# play_out_bracket accepts an optional pick_winner parameter. 
# Default just picks a random winner in each matchup.
MyBracket.play_out_bracket(pick_winner=pick_by_power_level)
# Optional formatting= parameter lets you specify what to print instead of just printing the whole dictionary
# Can also specify spacing for how it is printed. Default is 20.
MyBracket.print_bracket(formatting=lambda t: t["name"], spaces=20)
```

Which outputs: 

```

Kitten State
 |----------------- Kitten State
Bunnyville
                     |----------------- Kitten State
Muscle Hamsters
 |----------------- Doggy Dog World
Doggy Dog World
                                         |----------------- Kitten State
Horsies
 |----------------- Horsies
Lizard Wizards
                     |----------------- Horsies
Ole Penguin
 |----------------- Ole Penguin
Pigchamps

```
