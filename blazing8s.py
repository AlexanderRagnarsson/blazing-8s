"""
This is en engine for the game of two players Blazing 8s.
We will use this to test our AI.
The rules of the game are as follows:
1. Each player starts with 5 cards.
2. There is an equal probability of each card being dealt.
3. The cards are as follows:
  - Normal cards: 2-7, 9, and 10 are normal cards.
  - 8: This cards can be played on any card and allows the player to select the color. It mirrors the number of the card it is played on.
  - J (11): This is a skip card. It skips the next player's turn.
  - Q (12): This is a reverse card. It reverses the order of play. In a two player game it does not exist.
  - K (13): This makes the other player draw one card.
  - Swap (1): This swaps the player's hand with the other player's hand. If it is the last card played, the player who played it wins. It can be played on any card. It mirrors the color and number of the card it is played on.
  - Each card has a color: red, blue, green, and yellow.
  - Each card has to either be played on a card of the same color or the same number. The only exception is the 8 card and the swap card. W
4. A players turn consists of either playing a card or drawing a card. I player may draw a card even if they have a card they can play. A player may play a card after drawing. After a player draws he may also end his turn.
5. The game ends when a player has no cards left in his hand.
6. The player with no cards left in his hand wins.
"""

import random
from enum import Enum
from typing import Self

possible_cards = [1,2,3,4,5,6,7,8,9,10,11,13]

class Suite(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4

possible_suite = [Suite.RED, Suite.BLUE, Suite.GREEN, Suite.YELLOW]


class Card:
    def __init__(self, number: int, suite: Suite):
        self.number = number
        self.suite = suite
    
    def __str__(self):
        # color = {1: "Red", 2: "Blue", 3: "Green", 4: "Yellow"}
        number = {1: "Swap", 11: "J", 13: "K"}
        return f"{self.suite.name} {number[self.number] if self.number in number else self.number}"
    
    def to_tuple(self):
        return (self.number, self.suite)

def get_random_card():
    num = random.choice(possible_cards)
    suite = random.choice(possible_suite)
    return Card(num, suite)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand = []
    
    def draw(self):
        card = get_random_card()
        self.hand.append(card)
    
    def play(self, card: Card):
        self.hand.remove(card)
    
    def choose_card(self, top: Card, enemy_hand_length: int, draw: bool) -> Card:
        print("Your hand:")
        playable_cards = {}
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}", end=" ")
            if card.suite == top.suite or card.number == top.number or card.number == 8 or card.number == 1:
                print("Playable")
                playable_cards[i] = card
            else:
                print()
        if draw:
            string = "Which card would you like to play? (Enter the number or 'd' to draw): "
        else:
            string = "Which card would you like to play? (Enter the number or 's' to skip): "
        choice = input(string)
        if draw and choice == "d":
            return None
        elif not draw and choice == "s":
            return None
        return self.hand[int(choice)]

    def choose_color(self) -> str:
        print("Which color would you like to change to?")
        for i, color in enumerate(possible_suite):
            print(f"{i}: {color}")
        choice = input("Which color would you like to change to? (Enter the number): ")
        return possible_suite[int(choice)]
    
    def __str__(self):
        return f"{self.name}: {self.hand}"

class Game:
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.top = get_random_card()

    def start(self):
        for i in range(5):
            self.player1.draw()
            self.player2.draw()
        self.top = get_random_card()
        while True:
            print(f"It's {self.current_player.name}'s turn.")
            print(f"The top card is {self.top}")
            self.turn()
            if len(self.current_player.hand) == 0:
                print(f"{self.current_player.name} wins!")
                break
            self.switch_player()

    def turn(self):
        card_played = False
        drew = False
        other_player = self.player1 if self.current_player == self.player2 else self.player2
        while not card_played:
            card = self.current_player.choose_card(self.top, len(other_player.hand), not drew)
            if card is not None:
                self.current_player.play(card)
                self.top = self.apply_card_effect(card)
                card_played = True
            elif drew:
                break
            else:
                self.current_player.draw()
                drew = True
    
    def apply_card_effect(self, card: Card) -> Card:
        new_top_color = card.suite
        new_top_number = card.number
        if card.number == 1:  # Swap
            self.player1.hand, self.player2.hand = self.player2.hand, self.player1.hand
            new_top_color = self.top.suite
            new_top_number = self.top.number
        elif card.number == 8:  # Change color
            new_color = self.current_player.choose_color()
            new_top_color = new_color
            new_top_number = self.top.number
        elif card.number == 11:  # Skip
            self.switch_player()
        elif card.number == 13:  # Draw one
            self.switch_player()
            self.current_player.draw()
            self.switch_player()
        
        return Card(new_top_number, new_top_color)


    def switch_player(self):
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2

    def __str__(self):
        return f"Player 1: {self.player1}\nPlayer 2: {self.player2}"

if __name__ == "__main__":
    player1 = Player("Player 1")
    player2 = Player("Player 2")
    game = Game(player1, player2)
    game.start()
