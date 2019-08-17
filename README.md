# Snake
Python - Retro snake game including deep learning AI

## How to run
You can start the game to play with arrow keys by running:
> python3 GameUI.py

Or let the AI play with following:
> python3 AIUI.py

## How it's made
The core elements of the game are divided into
> Apple.py

> Snake.py

> SnakeGame.py

> SVector.py

There is a config file where you can change things like speed, board size and stuff
> SConfig.py

## Model:
```
               input    hidden   output: vote for
object-left         O
object-straight     O      O
object-right        O      O
distance-left       O      O      O  > turn left  
distance-straight   O      O      O  > go straight
distance-right      O      O      O  > turn right
current-pos         O      O
current-distance    O
```

## Training statistics .. 
```
average steps 669.52
average score 31.42
max steps 2192
max score 82
total of 66952 steps

average steps 872.3
average score 39.57
max steps 2440
max score 90
total of 154182 steps

average steps 901.41
average score 40.71
max steps 2266
max score 84
total of 244323 steps

average steps 927.04
average score 41.12
max steps 2868
max score 96
total of 337027 steps

average steps 970.32
average score 43.43
max steps 2437
max score 98
total of 434059 steps

average steps 586.61
average score 26.08
max steps 1315
max score 52
total of 492720 steps

average steps 661.63
average score 29.71
max steps 1902
max score 75
total of 558883 steps

average steps 688.1
average score 31.75
max steps 2058
max score 77
total of 627693 steps

# +1000 games
average steps 704.246
average score 32.399
max steps 2347
max score 88
total of 1331939 steps

average steps 676.14
average score 30.51
max steps 1635
max score 68
total of 1399553 steps
