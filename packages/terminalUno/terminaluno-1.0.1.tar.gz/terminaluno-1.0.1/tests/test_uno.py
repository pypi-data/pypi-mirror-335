import pytest
from terminalUno import Card, Color, Type, Deck, Player, is_valid_play, uno
from unittest.mock import patch
# for now run "PYTHONPATH=src pytest tests/test_uno.py" to activate tests

class TestUno:

    def test_sanity(self):
        expected = True
        actual = True
        assert expected == actual, "Test failed"
        print("Pytest is running as expected")
    
    def test_card_creation(self): 
        card = Card(Color.RED, Type.NUMBER, 5)
        assert card.color == Color.RED, f"Card color should be RED, not {card.color}"
        assert card.type == Type.NUMBER, f"Card type should be NUMBER, not {card.type}"
        assert card.number == 5, f"Card number should be 5, not {card.number}"
        print("Normal Card creation test passed")

    def test_card_representation(self): 
        card = Card(Color.BLUE, Type.SKIP)
        assert repr(card) == "Blue Skip", f"Card representation should be 'Blue Skip', not {repr(card)}"
        print("Special Card representation test passed")

    def test_deck_shuffle(self):
        deck1 = Deck(3, 7)
        deck2 = Deck(3, 7)
        deck1.shuffle()
        assert deck1.cards != deck2.cards 

    def test_deck_draw(self):
        deck = Deck(3, 7)
        size = len(deck.cards)
        card = deck.draw()
        while card is not None:
            size -= 1
            assert len(deck.cards) == size
            card = deck.draw()

    def test_initialize_players(self):
         players = uno.initialize_players(2, True)
         assert len(players) == 3, f"the number of players when 2 AI players are initialized should be 3, not {len(players)}"
         players2 = uno.initialize_players(3, False)
         assert len(players2) == 4, f"the number of players when 3 AI players are initialized should be 4, not {len(players2)}"
         players4 = uno.initialize_players(4, False)
         assert players4[0].name == "You", f"the first player should be named 'You', not {players4[0].name}"
         print("Initialize players test passed")

    def test_initialize_deck(self):
         players = uno.initialize_players(2, True)
         deck, discard_pile, first_colour = uno.initialize_deck_and_discard_pile(cardNumMax = 10, initialCard = 7, players = players)
         right_length = 108 - 21 - 1
         assert len(deck) == right_length, f"the number of cards in the deck after initial draw should be 86, not {len(deck)}"
         print("Initialize deck test passed")
         assert len(discard_pile) == 1, f"the number of cards in the discard pile should be 1, not {len(discard_pile)}"
         print("Initialize discard pile test1 : only 1 card in the discard_pile passed")
         assert discard_pile[0] not in deck, f"the discard pile should not be in the deck"
         print("Initialize discard pile test2 : initial_discard not in deck passed")

    def test_valid_play_same_color(self):
        top_card = Card(Color.RED, Type.NUMBER, 5)
        selected_card = Card(Color.RED, Type.SKIP)
        assert is_valid_play(selected_card, top_card, Color.RED) is True, f"Same Color Test failed"
        print("Same Color Test passed")

    def test_valid_play_same_number(self):
        top_card = Card(Color.GREEN, Type.NUMBER, 3)
        selected_card = Card(Color.RED, Type.NUMBER, 3)
        assert is_valid_play(selected_card, top_card, Color.RED) is True, f"Same Number Test failed"
        print("Same Number Test passed")

    def test_valid_play_wild_card(self):
        top_card = Card(Color.BLUE, Type.NUMBER, 7)
        selected_card = Card(Color.BLACK, Type.WILD)
        assert is_valid_play(selected_card, top_card, Color.BLUE) is True, f"Wild Card Test failed"
        print("Wild Card Test passed")

    def test_invalid_play(self):
        top_card = Card(Color.YELLOW, Type.NUMBER, 8)
        selected_card = Card(Color.BLUE, Type.NUMBER, 2)
        assert is_valid_play(selected_card, top_card, Color.YELLOW) is False, f"Invalid Play Test failed"
        print("Invalid Play Test passed")

    def test_skip_card(self):
        # Setup a game scenario with 3 players
        players = [Player("Player1"), Player("Player2"), Player("Player3")]
        deck = Deck(10,7)  # Smaller deck for testing
        # Initial state
        current_player_index = 0
        direction = 1
        current_color = Color.RED

        target_card = Card(Color.RED, Type.SKIP)
        
        # Apply the effect
        current_color, direction, skip_next = uno.apply_card_effect(
            target_card, players[0], players, current_player_index, 
            direction, current_color, deck, discard_pile=[]
        )
        
        # Check that skip_next is True
        assert skip_next == True, "Skip card should set skip_next to True"

        print("Skip card functionality test passed")


    #divide into 4 situtation, honest and dishonest play, challenge or not
    def test_wild4_honest_no_challenge(self):
        # Player 1 plays Wild4 honestly (no matching color). Player 2 does not challenge.
        players = [Player("Player1"), Player("Player2")]
        deck = Deck(10,7)
        test_red_card = Card(Color.RED, Type.NUMBER, 5)
        discard_pile = [test_red_card]
        current_color = Color.RED
        direction = 1
        current_player_index = 0
        wild4_card = Card(Color.BLACK, Type.WILD4)
        players[0].hand = [Card(Color.BLUE, Type.NUMBER, 3), wild4_card]
        players[1].hand = [Card(Color.YELLOW, Type.NUMBER, 6), Card(Color.GREEN, Type.NUMBER, 2)]

        with patch('builtins.input', return_value='no'):
            players[0].remove_card(1)
            discard_pile.append(wild4_card)
            current_color, direction, skip_next = uno.apply_card_effect(
                wild4_card, players[0], players, current_player_index, direction, current_color, deck, discard_pile
            )
        
        assert len(players[1].hand) == 6, "Next player should have drawn 4 cards"
        assert skip_next is True, "Next player should be skipped"
        print("Wild4 honest play, no challenge test passed")
    
    def test_wild4_honest_challenge(self):
        #Player 1 plays Wild4 honestly (no matching color). Player 2 challenges and fails.
        players = [Player("Player1"), Player("Player2")]
        deck = Deck(10,7)
        test_red_card = Card(Color.RED, Type.NUMBER, 5)
        discard_pile = [test_red_card]
        current_color = Color.RED
        direction = 1
        current_player_index = 0

        wild4_card = Card(Color.BLACK, Type.WILD4)
        players[0].hand = [Card(Color.BLUE, Type.NUMBER, 3), wild4_card]
        players[1].hand = [Card(Color.YELLOW, Type.NUMBER, 6), Card(Color.GREEN, Type.NUMBER, 2)]

        with patch('builtins.input', return_value='yes'):
            players[0].remove_card(1)
            discard_pile.append(wild4_card)
            current_color, direction, skip_next = uno.apply_card_effect(
                wild4_card, players[0], players, current_player_index, direction, current_color, deck, discard_pile
            )
        
        assert len(players[1].hand) == 8, "Next player should have drawn 6 cards (challenge failed)"
        assert skip_next is True, "Next player should be skipped"
        print("Wild4 honest play, challenge failed test passed")
    
    def test_wild4_dishonest_no_challenge(self):
        #Player 1 plays Wild4 dishonestly (has matching color). Player 2 does not challenge.
        players = [Player("Player1"), Player("Player2")]
        deck = Deck(10,7)
        test_red_card = Card(Color.RED, Type.NUMBER, 5)
        discard_pile = [test_red_card]
        current_color = Color.RED
        direction = 1
        current_player_index = 0

        wild4_card = Card(Color.BLACK, Type.WILD4)
        legal_card = Card(Color.RED, Type.NUMBER, 5)
        players[0].hand = [legal_card, wild4_card]
        players[1].hand = [Card(Color.YELLOW, Type.NUMBER, 6), Card(Color.GREEN, Type.NUMBER, 2)]

        with patch('builtins.input', return_value='no'):
            players[0].remove_card(1)
            discard_pile.append(wild4_card)
            current_color, direction, skip_next = uno.apply_card_effect(
                wild4_card, players[0], players, current_player_index, direction, current_color, deck, discard_pile
            )
        
        assert len(players[1].hand) == 6, "Next player should have drawn 4 cards"
        assert skip_next is True, "Next player should be skipped"
        print("Wild4 dishonest play, no challenge test passed")
    
    def test_wild4_dishonest_challenge(self):
        #Player 1 plays Wild4 dishonestly (has matching color). Player 2 challenges and succeeds.
        players = [Player("Player1"), Player("Player2")]
        deck = Deck(10,7)
        test_red_card = Card(Color.RED, Type.NUMBER, 5)
        discard_pile = [test_red_card]
        current_color = Color.RED
        direction = 1
        current_player_index = 0

        wild4_card = Card(Color.BLACK, Type.WILD4)
        legal_card = Card(Color.RED, Type.NUMBER, 5)
        players[0].hand = [legal_card, wild4_card]
        players[1].hand = [Card(Color.YELLOW, Type.NUMBER, 6), Card(Color.GREEN, Type.NUMBER, 2)]

        with patch('builtins.input', return_value='yes'):
            players[0].remove_card(1) # Remove wild4 card, so now hand only has legal card
            discard_pile.append(wild4_card)
            current_color, direction, skip_next = uno.apply_card_effect(
                wild4_card, players[0], players, current_player_index, direction, current_color, deck, discard_pile
            )
        
        assert len(players[0].hand) == 5, "Challenged player should draw 4 cards, now has 5 cards"
        assert skip_next is False, "Next player should not be skipped"
        print("Wild4 dishonest play, challenge success test passed")
        