# Chess-engine
A chess engine that defines all the rules and mechanics of chess, **generates all valid moves** and then uses negamax recursion combined with alpha beta pruning to choose the best move, upto a customizable depth.
I have been playing chess for a while, and wanted to improve my python skills so I thought of building a chess engine, and came across an exceptional [tutorial](URL "https://www.youtube.com/channel/UCaEohRz5bPHywGBwmR18Qww"), by Eddie Sharick. The codebase is inspired by his tutorials, combined by my own improvements.

# Instructions
Clone this repository.
Select whether you want to play versus computer, against another player locally, or watch the game of engine playing against itself by setting appropriate flags in lines 39 and 40 of main.py.
Run ChessMain.py.
Enjoy the game!

Additional gameplay: Press Z to undo a move, and R to reset the game

# Future improvements
Code cleanup and refactoring
Improved UI
Improve engine speed by implementing : move ordering, keeping track of all possible moves, teaching engine standard openings
