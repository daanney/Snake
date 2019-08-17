# Snake
Python - Retro snake game including deep learning AI

You can start the game to play with arrow keys by running:
> python3 GameUI.py

Or let the AI play with following:
> python3 AIUI.py


## Model:
.               input    hidden   output: vote for
object-left         O
object-straight     O      O
object-right        O      O
distance-left       O      O      O  > turn left  
distance-straight   O      O      O  > go straight
distance-right      O      O      O  > turn right
current-pos         O      O
current-distance    O
