import random
from enum import Enum
import time

class Color(Enum):
    RED = "Red"
    GREEN = "Green"
    BLUE = "Blue"
    YELLOW = "Yellow"
    BLACK = "Black"

class Type(Enum):
    NUMBER = "Number"
    SKIP = "Skip"
    REVERSE = "Reverse"
    DRAW2 = "Draw2"
    WILD = "Wild"
    WILD4 = "Wild4"

class Card:
    def __init__(self, color, type, number=None):
        self.color = color
        self.type = type
        self.number = number

    def __repr__(self):
        return f"{self.color.value} {self.type.value} {self.number if self.number is not None else ''}".strip()

class Deck():
    def __init__(self, cardNumMax = 10, initialCard = 7):
        self.cardNumMax = cardNumMax
        self.initialCard = initialCard
        self.cards = []
        self.initialize()


    def initialize(self):
        self.cards = []
        self.discard_pile = []
        colors = [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]
        for color in colors:
            self.cards.append(Card(color, Type.NUMBER, 0))
            for num in range(1, self.cardNumMax):
                self.cards.append(Card(color, Type.NUMBER, num))
                self.cards.append(Card(color, Type.NUMBER, num))
            self.cards.append(Card(color, Type.SKIP))
            self.cards.append(Card(color, Type.SKIP))
            self.cards.append(Card(color, Type.REVERSE))
            self.cards.append(Card(color, Type.REVERSE))
            self.cards.append(Card(color, Type.DRAW2))
            self.cards.append(Card(color, Type.DRAW2))
        for _ in range(4):
            self.cards.append(Card(Color.BLACK, Type.WILD))
            self.cards.append(Card(Color.BLACK, Type.WILD4))
        print("Deck initialized.")
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop() if self.cards else None

    def __len__(self):
        return len(self.cards)
    
    def __contains__(self, card):
        return card in self.cards

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)

    def remove_card(self, index):
        return self.hand.pop(index)

    def __repr__(self):
        return f"{self.name}: {self.hand}"

def is_valid_play(selected_card, top_card, current_color):
    # Wild Cards
    if selected_card.type in [Type.WILD, Type.WILD4]:
        return True
    # Same color
    if selected_card.color == current_color:
        return True
    # Same type
    if selected_card.type == Type.NUMBER and top_card.type == Type.NUMBER:
        if selected_card.number == top_card.number:
            return True
    # Same type for special cards
    if top_card.type != Type.NUMBER and selected_card.type == top_card.type:
        return True
    return False

def initialize_players(otherPlayerAmount, playerRandom):
    players = []
    for i in range (otherPlayerAmount):
        ai_player_name = "AI " + str(i+1)
        players.append(Player(ai_player_name, True))

    position = 0
    if playerRandom:
        position = random.randint(0,otherPlayerAmount)
        players.insert(position, Player("You"))
    else:
        players.insert(0, Player("You"))
    print("You are at position", position+1)
    return players

def initialize_deck_and_discard_pile(cardNumMax, initialCard, players):
    deck = Deck(cardNumMax,initialCard)
    discard_pile = []
    first_colour=None
    # Draw initial cards
    for _ in range(initialCard):
        for player in players:
            card = deck.draw()
            if card is not None:
                player.add_card(card)
            else:
                print("Deck is empty while dealing!")
                return
    initial_discard = deck.draw()
    while initial_discard is not None and initial_discard.type in [Type.WILD, Type.WILD4]:
        deck.cards.insert(0, initial_discard)
        deck.shuffle()
        initial_discard = deck.draw()
    if initial_discard is None:
        print("Deck ran out of cards to start the game!")
        return
    discard_pile.append(initial_discard)
    first_colour=discard_pile[-1].color if discard_pile[-1].type != Type.WILD else random.choice([Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW])
    return deck, discard_pile, first_colour


def display_game_state(player, players, discard_pile, current_color, cheat):
    if not player.is_ai:
        print(f"\n*** Your Turn ***")
    else:
        print(f"\n*** {player.name}'s Turn ***")
    print(f"Current Card: {discard_pile[-1]}")
    if discard_pile[-1].type in [Type.WILD, Type.WILD4]:
        print(f"Current color: {current_color.value}")
    print("Other Players' Hands:")
    for p in players:
        if p != player:
            if cheat and p.is_ai:
                print(f"{p.name}: {p.hand}", end="  ")
            else:
                print(f"{p.name}: {len(p.hand)} cards", end="  ")
            print()
    print("\n")

def display_player_hand(player):
    print("Your Hand:")
    for i, card in enumerate(player.hand):
        print(f"{i+1}: {card}")
    print("0: Draw a Card")

def get_player_card_choice(player, deck, discard_pile, current_color):
    while True:
        try:
            choice = input("Choose a card to play (Enter number): ")
            if not choice.isdigit():
                print("Invalid input. Please enter a number.")
                continue
            
            choice = int(choice)
            
            # Handle special choice
            if choice == 0:
                drawn_card = deck.draw()
                if drawn_card is not None:
                    player.add_card(drawn_card)
                    print("You drew a card.")
                else:
                    print("Deck is empty.")
                return None, choice
            elif choice < 1 or choice > len(player.hand):
                print("Invalid selection. Choose a valid card number.")
                continue
                
            selected_card = player.hand[choice - 1]
            
            if is_valid_play(selected_card, discard_pile[-1], current_color):
                return selected_card, choice - 1
            else:
                print("Invalid card selection. Choose a valid card.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def apply_card_effect(selected_card, player, players, current_player_index, direction, current_color, deck, discard_pile, is_ai=False):
    num_players = len(players)
    skip_flag= False
    
    # Handle Wild cards
    if selected_card.type in [Type.WILD, Type.WILD4]:
        # For player
        if not is_ai:
            new_color_input = input("Choose a new color (Red, Green, Blue or Yellow): ").strip().upper()
            if new_color_input in ["RED", "GREEN", "BLUE", "YELLOW"]:
                current_color = Color[new_color_input]
            else:
                print("Invalid color, system is randomizing one for you.")
                current_color = random.choice([Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW])
            print(f"{player.name} played {selected_card} and changed color to {current_color.value}.")
        # For AI
        else:
            new_color = random.choice([Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW])
            current_color = new_color
            print(f"{player.name} played {selected_card} and changed color to {new_color.value}.")
    
    if selected_card.type == Type.WILD4:
        print("Next player can challenge!")

        # challenge wild4
        next_player = (current_player_index + direction) % num_players
        # For player
        if not players[next_player].is_ai:
            challenge = input(f"{players[next_player].name}, do you want to challenge? (yes/no): ").strip().lower()
        else:
            print(f"{players[next_player].name}, do you want to challenge? (yes/no): ", end = "")
            choice = random.random()
            if choice <= 0.3:
                challenge = "yes"
            else:
                challenge = "no"
            time.sleep(0.5)
            print(f"{challenge}")

        if challenge == "yes":
            # check if possible
            valid_play_exists = any(
                is_valid_play(card, discard_pile[-2], discard_pile[-2].color) and card.type != Type.WILD4
                for card in player.hand
            )
            if valid_play_exists:
                print(f"Challenge successful! {player.name} has other playable cards. {player.name} draws 4 cards instead.")
                for _ in range(4):
                    player.add_card(deck.draw())
            else:
                print(f"Challenge failed! {players[next_player].name} must draw 2 extra cards (total 6).")
                for _ in range(6):
                    players[next_player].add_card(deck.draw())
                skip_flag = True
        else:
            print(f"{players[next_player].name} chose not to challenge. They draw 4 cards and are skipped.")
            for _ in range(4):
                players[next_player].add_card(deck.draw())
            skip_flag = True


    # Handle Reverse cards
    elif selected_card.type == Type.REVERSE:
        current_color = selected_card.color
        direction = -direction
        print(f"{player.name} played {selected_card} and direction is reversed.")

    # Handle Draw2 cards
    elif selected_card.type == Type.DRAW2:
        current_color = selected_card.color
        next_player = (current_player_index + direction) % num_players
        for _ in range(2):
            drawn_card = deck.draw()
            if drawn_card:
                players[next_player].add_card(drawn_card)
        print(f"{player.name} played {selected_card} and next player draws two cards.")
    
    # Handle Skip cards
    elif selected_card.type == Type.SKIP:
        current_color = selected_card.color
        print(f"{player.name} played {selected_card} and next player is skipped.")
        skip_flag= True
    
    # Handle normal cards
    elif selected_card.type == Type.NUMBER:
        # prevent printing wild 
        current_color = selected_card.color
        print(f"{player.name} played {selected_card}.")
    
    return current_color, direction, skip_flag

# Reshuffle if deck is empty
def check_and_refresh_deck(deck, discard_pile):
    if not deck.cards and len(discard_pile) > 1:
        print("Reshuffling the discard pile into the deck...")
        # Keep the top card of the discard pile
        top_card = discard_pile.pop()
        deck.cards = discard_pile.copy()
        discard_pile.clear()
        discard_pile.append(top_card)
        deck.shuffle()
        return True
    return False

def handle_player_turn(player, players, deck, discard_pile, current_color, current_player_index, direction, cheat):
    game_over = False
    skip_flag = False
    
    # player's turn
    if not player.is_ai:
        display_game_state(player, players, discard_pile, current_color, cheat)
        display_player_hand(player)
        selected_card, choice_index = get_player_card_choice(player, deck, discard_pile, current_color)
        
        if selected_card: # If a valid selected card
            player.remove_card(choice_index)
            discard_pile.append(selected_card)
            current_color, direction, skip_flag = apply_card_effect(
                selected_card, player, players, 
                current_player_index, direction, current_color, deck, discard_pile=discard_pile
            )
    
    # AI's turn
    else:
        print(f"\n*** {player.name}'s Turn ***")
        print(f"Current Card: {discard_pile[-1]}")
        if discard_pile[-1].type in [Type.WILD, Type.WILD4]:
            print(f"Current color: {current_color.value}")
        valid_card_found = False
        for i, card in enumerate(player.hand):
            if is_valid_play(card, discard_pile[-1], current_color):
                selected_card = player.hand.pop(i)
                discard_pile.append(selected_card)
                current_color, direction, skip_flag = apply_card_effect(
                    selected_card, player, players, 
                    current_player_index, direction, current_color, deck, discard_pile, is_ai=True, 
                )
                valid_card_found = True
                break
                
        if not valid_card_found:
            drawn_card = deck.draw()
            if drawn_card:
                player.add_card(drawn_card)
                print(f"{player.name} drew a card.")
            else:
                check_and_refresh_deck(deck, discard_pile)
                drawn_card = deck.draw()
                if drawn_card:
                    player.add_card(drawn_card)
                    print(f"{player.name} drew a card after reshuffling.")
                else:
                    print("There's just no card left!")
    # Check for Uno
    if len(player.hand) == 1:
        if player.is_ai:
            print(f"{player.name} says 'Uno'!")
        else:
            print("You say 'Uno'!")
    
    # Check for winner
    if not player.hand:
        if not player.is_ai:
            print ("You win!")
        else:
            print(f"{player.name} wins!")
        game_over = True
    
    return current_color, direction, skip_flag, game_over


def main_game(playerRandom = True, cheat = False, otherPlayerAmount = 3, cardNumMax = 10, initialCard = 7):
    players = initialize_players(otherPlayerAmount, playerRandom)
    num_players = len(players)
    deck, discard_pile, current_color = initialize_deck_and_discard_pile(cardNumMax, initialCard, players)
    
    current_player_index = 0
    direction = 1
    game_over = False

    while not game_over:
        player = players[current_player_index]
        
        # Handle the current player's turn
        current_color, direction, skip_flag, game_over = handle_player_turn(
            player, players, deck, discard_pile, current_color, 
            current_player_index, direction, cheat
        )
        
        if not game_over:
            # Move to next player
            if not skip_flag:
                current_player_index = (current_player_index + direction) % num_players
            else: #already indexed with skip cards
                current_player_index = (current_player_index + direction*2) % num_players
                
            # Animation pause between turns
            for _ in range(3):
                time.sleep(0.5)
                print("  @   ", end="")
                time.sleep(0.5)
            print("\n")

