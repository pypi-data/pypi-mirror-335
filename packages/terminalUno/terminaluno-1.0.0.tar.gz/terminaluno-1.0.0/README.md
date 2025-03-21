![Python build & test](https://github.com/software-students-spring2025/3-python-package-se_project3/actions/workflows/build.yaml/badge.svg)
<!-- # Python Package Exercise

An exercise to create a Python package, build it, test it, distribute it, and use it. See [instructions](./instructions.md) for details. -->


## Project Overview

 TerminalUno is a command-line implementation of the classic UNO card game, designed to be played against AI opponents. It provides an interactive, text-based experience, simulating the rules and mechanics of UNO, including draw cards (+2, +4), skips, reverses, wild cards, and stacking rules.

 The game is developed in Python and runs entirely in the terminal, featuring turn-based gameplay, AI-controlled opponents, and special card effects.

## Team Members
- **Haoxuan Lin(Steve)**: [Echoudexigaigu](https://github.com/Echoudexigaigu)
- **Jiaxi Zhang**: [SuQichen777](https://github.com/SuQichen777)
- **Zhiheng Pan**: [pzhiheng](https://github.com/pzhiheng)
- **Henry Yu**: [ky2389](https://github.com/ky2389)

 <!-- ## Pypl Project Link

 [terminalUno 0.0.0](https://test.pypi.org/project/terminalUno/0.0.0/) -->
 <!-- Renew after published -->

 ## Installation & Usage
 - Installation
 ```bash
 pip install terminalUno
 ```
 - Usage

 Method 1(recommanded): Directly run the following command in the terminal to start the game.
 ```bash
 terminalUno
 ```
<br>Method 2: Import the package
```python
import terminalUno as uno
```
And you can implement the game with the following functions in your code.

 ## Code examples

 | **Function** | **Description** | **Example Usage** |
 |-------------|---------------|------------------|
 | `initialize_players(otherPlayerAmount, playerRandom)` | Initializes players. | `players = uno.initialize_players(3, True)` |
 | `initialize_deck_and_discard_pile(cardNumMax, initialCard, players)` | Intializes UNO deck. | `deck, discard_pile, current_color = uno.initialize_deck_and_discard_pile(10, 7, players)` |
 | `display_game_state(player, players, discard_pile, current_color, cheat)` | Prints game state. | `uno.display_game_state(player, players, discard_pile, current_color, False)` |
 | `handle_player_turn(...)` | Processes a player’s turn. | `current_color, direction, skip_flag, game_over = uno.handle_player_turn(...)` |
 | `is_valid_play(selected_card, top_card, current_color)` | Checks if a selected card is playable. | `valid = uno.is_valid_play(card, discard_pile[-1], current_color)` |
 | `apply_card_effect(...)` | Applies special card effects (Skip, Reverse, Draw2, Wild). | `current_color, direction, skip_flag = uno.apply_card_effect(...)` |
 | `check_and_refresh_deck(deck, discard_pile)` | Reshuffles discard pile. | `reshuffled = uno.check_and_refresh_deck(deck, discard_pile)` |

 Some functions above are already implemented in other functions and may not be directly called. Therefore, we highly recommend taking a look at the example program to understand how to use the package: [example_terminaluno.py](examples/example_terminaluno.py) 


 
 ## Steps Needed to Contribute
 - Clone the repo
 ```bash
 git clone https://github.com/software-students-spring2025/3-python-package-se_project3/blob/main/instructions.md
 cd 3-python-package-se_project3
 ```
 - Create a new branch
 ```bash
 git checkout -b <branch-name>
 ```
 - Install pipenv, build, and twine if you don't have them
 ```bash
 python3 -m pip install --user pipenv
 python3 -m pip install --upgrade build
 pip3 install twine
 ```
 - Create a virtual environment and install dependencies
 ```bash
 pipenv install pytest-cov --dev
 ```
 - Activate the virtual environment
 ```bash
 pipenv shell
 ```
 - Exit the virtual environment
 ```bash
 exit
 ```
 
 ## Steps to Run the Tests
 - Activate the virtual environment
 ```bash
 pipenv shell
 ```
 - Run the tests without success output
 ```bash
 pytest
 ```
 - Run the tests with success output
 ```bash
 pytest -s
 ```