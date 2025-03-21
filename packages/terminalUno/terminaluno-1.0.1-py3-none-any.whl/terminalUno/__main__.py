"""
In Python packages, this file called __main__.py is run when the package is run
directly from command line, as opposed to importing it into another program.
"""

import terminalUno.uno as uno
import time

def main():
    print("---------------------------------------------------------------------------------------")
    print("Welcome to Terminal Uno! (*≧ω≦)")
    time.sleep(1)
    print("Please enter the following information to initialize the game ㄟ(￣▽￣ㄟ)")
    time.sleep(1)
    print("Press Enter ↵ to use default values: randomize player position,\nno cheat,3 AI players, max number for the digit on cards is 9,\nand 7 initial cards in hand.")
    time.sleep(1)
    print("---------------------------------------------------------------------------------------")
    playerRandom = input("(Default y) Randomize player position? (y/n): ")
    cheat = input("(Default n) Cheat? (y/n): ")
    otherPlayerAmount = int(input("(Default 3 AI player) Number of AI players: ") or 3)
    cardNumMax = int(input("(Default 9) Max number for the digit on cards: ") or 9)
    cardNumMax += 1
    initialCard = int(input("(Default 7)Number of initial card in hand: ") or 7)

    if playerRandom == "n" or playerRandom == "N":
        playerRandom = False
    else:
        playerRandom = True
    if cheat == "y" or cheat == "Y":
        cheat = True
    else:
        cheat = False
    if (otherPlayerAmount == 0):
        otherPlayerAmount = 3
    if (cardNumMax == 1):
        cardNumMax = 10
    if (initialCard == 0):
        initialCard = 7

    print ("\n")
    print ("Player Random: ", playerRandom, end = " ")
    print (", Cheat: ", cheat, end = " ")
    print (", Number of AI players: ", otherPlayerAmount)
    print ("Max number for the digit on cards: ", cardNumMax - 1, end = " ")
    print (", Number of initial card in hand: ", initialCard, end = " ")
    print ("\n")
    uno.main_game(playerRandom, cheat, otherPlayerAmount, cardNumMax, initialCard)

if __name__ == "__main__":
    main()