"""
This is how the game of blazing 8 in discord actually works.
Main difference is that the draw is not random but instead gotten from a resetting list. 
"""

import random
from enum import Enum
from typing import Self


class Suite(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    NO_COLOR = 5

    @staticmethod
    def from_int(i: int) -> Self:
        if i == 0:
            return Suite.RED
        elif i == 1:
            return Suite.BLUE
        elif i == 2:
            return Suite.GREEN
        elif i == 3:
            return Suite.YELLOW
        elif i == 4:
            return Suite.NO_COLOR
        else:
            raise Exception("Invalid suite")


class Card:
    def __init__(self, value: int, suite: Suite | None):
        self.value = value
        self.suite = suite

    def __str__(self):
        # color = {1: "Red", 2: "Blue", 3: "Green", 4: "Yellow"}
        number = {1: "Swap", 11: "J", 13: "K"}
        return f"{self.suite.name if self.suite is not None else 'None':7} {number[self.value] if self.value in number else self.value}"


class Skip:
    def __init__(self):
        pass

    def __str__(self):
        return "Skip"

    def __eq__(self, other):
        if isinstance(other, Skip):
            return True
        return False


class Draw:
    def __init__(self):
        pass

    def __str__(self):
        return "Draw"

    def __eq__(self, other):
        if isinstance(other, Draw):
            return True
        return False


class Player:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def get_play(
        self,
        hand: list[Card],
        playable_cards: list[Card | Skip | Draw],
        top_card: Card,
        cards_in_enemy_hand: int,
    ) -> Card | Skip | Draw:
        raise NotImplementedError("This is an abstract class")


class DiscordGame:
    TWO_PLAYER = True

    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.player1_hand = []
        self.player2_hand = []
        self.deck = []
        self.deal()
        self.top_card = self.draw()
        while self.top_card.suite == Suite.NO_COLOR:
            self.deck.append(self.top_card)
            random.shuffle(self.deck)
            self.top_card = self.draw()
        self.current_player = (
            self.player1 if random.randint(0, 1) == 0 else self.player2
        )
        self.skip_next_player = False

    def reset_deck(self):
        self.deck = []
        for i in range(1, 14):
            if i == 12 and self.TWO_PLAYER:
                continue
            if i == 1:
                # Only 50% chance of getting a swap card
                if random.randint(0, 1) == 0:
                    continue
            for j in range(4):
                if i == 1 or i == 8:
                    self.deck.append(Card(i, Suite.from_int(4)))
                else:
                    suite = Suite.from_int(j)
                    self.deck.append(Card(i, suite))

        random.shuffle(self.deck)

    def draw(self):
        if len(self.deck) == 0:
            self.reset_deck()
        return self.deck.pop()

    def give_card(self, player_hand):
        player_hand.append(self.draw())

    def deal(self):
        self.reset_deck()
        self.player1_hand = []
        self.player2_hand = []
        for i in range(5):
            self.give_card(self.player1_hand)
            self.give_card(self.player2_hand)

    def get_player_hand(self, player):
        if player == self.player1:
            return self.player1_hand
        elif player == self.player2:
            return self.player2_hand
        else:
            return None

    def get_playable_cards(self, player) -> list[Card | Skip | Draw]:
        playable_cards = []
        for card in self.get_player_hand(player):
            if (
                card.suite == self.top_card.suite
                or card.value == self.top_card.value
                or card.value == 1
                or card.value == 8
            ):
                playable_cards.append(card)
        return playable_cards

    def play_card(self, player, card: Card):
        if card not in self.get_playable_cards(player):
            return False
        self.get_player_hand(player).remove(card)
        self.skip_next_player = False
        if card.value == 1:
            # Swap hands
            self.player1_hand, self.player2_hand = self.player2_hand, self.player1_hand
            return True
        if card.value == 8:
            if card.suite == None:
                return False  # Should set the suite before playing the card
            self.top_card.suite = card.suite
            return True
        if card.value == 11:
            # Need to skip the next player
            self.skip_next_player = True
        if card.value == 12:
            # If this is not a two player game, then we would invert the order of play
            return False
        if card.value == 13:
            # Make the other player draw 1 card
            self.give_card(
                self.get_player_hand(
                    self.player2 if player == self.player1 else self.player1
                )
            )
        self.top_card = card
        return True

    def loop(self):
        while True:
            if len(self.player1_hand) == 0:
                return self.player1
            if len(self.player2_hand) == 0:
                return self.player2
            if self.skip_next_player:
                self.skip_next_player = False
                self.current_player = (
                    self.player1
                    if self.current_player == self.player2
                    else self.player2
                )

            has_drawn = False
            while True:
                playable_cards = self.get_playable_cards(self.current_player)

                if has_drawn:
                    playable_cards.append(Skip())
                else:
                    playable_cards.append(Draw())

                enemy_hand = self.get_player_hand(
                    self.player2
                    if self.current_player == self.player1
                    else self.player1
                )
                play = self.current_player.get_play(
                    self.get_player_hand(self.current_player),
                    playable_cards,
                    self.top_card,
                    len(enemy_hand),
                )
                if play == Skip():
                    break
                elif play == Draw():
                    self.give_card(self.get_player_hand(self.current_player))
                    has_drawn = True
                else:
                    if not self.play_card(self.current_player, play):
                        raise Exception("Invalid play")
                    break

            self.current_player = (
                self.player1 if self.current_player == self.player2 else self.player2
            )


def sort_hand(hand: list[Card | Skip | Draw]) -> list[Card | Skip | Draw]:
    # return sorted(hand, key=lambda x: -1 if isinstance(x, Skip) or isinstance(x, Draw) else x.value)
    # Sort by suite first, then by value, keeping skips and draws at the end
    return sorted(
        hand,
        key=lambda x: (
            5 if isinstance(x, Skip) else 4 if isinstance(x, Draw) else 0,
            x.suite.value if isinstance(x, Card) else 0,
            x.value if isinstance(x, Card) else 0,
        ),
    )


class TUIPlayer(Player):
    """A way to play the game using a text based interface"""

    def __init__(self, name):
        super().__init__(name)

    def get_play(
        self,
        hand: list[Card],
        playable_cards: list[Card | Skip | Draw],
        top_card: Card,
        cards_in_enemy_hand: int,
    ) -> Card | Skip | Draw:
        print(f"{self.name}'s turn")
        print("Your hand:")
        hand = sort_hand(hand)
        for i, card in enumerate(hand):
            print(f"{i+1}. {card}")
        print("Top card:")
        print(top_card)
        print("Playable cards:")
        playable_cards = sort_hand(playable_cards)
        for i, card in enumerate(playable_cards):
            print(f"{i+1}. {card}")

        def get_playable():
            while True:
                try:
                    choice = int(input("Enter your choice: "))
                    if choice < 1 or choice > len(playable_cards):
                        raise Exception("Invalid choice")
                    return playable_cards[choice - 1]
                except Exception as e:
                    print(e)
                    print("Invalid choice")

        play = get_playable()
        if isinstance(play, Card) and play.value == 8:
            while True:
                try:
                    suites = "1. Red\n2. Blue\n3. Green\n4. Yellow\n"
                    choice = int(input(f"Enter the suite you want to set: \n{suites}"))
                    if choice < 1 or choice > 4:
                        raise Exception("Invalid choice")
                    play.suite = Suite.from_int(choice - 1)
                    break
                except Exception as e:
                    print(e)
        return play


class AgentPlayer(Player):
    def __init__(self, name):
        super().__init__(name)
        # TODO: Add agent from blazing8s.py


if __name__ == "__main__":
    game = DiscordGame(TUIPlayer("Player 1"), TUIPlayer("Player 2"))
    winner = game.loop()
    print(f"{winner.name} won!")
