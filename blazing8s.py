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
import pickle

possible_cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13]


class Suite(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4


possible_suite = [Suite.RED, Suite.BLUE, Suite.GREEN, Suite.YELLOW]


class Card:
    def __init__(self, number: int, suite: Suite | None):
        self.number = number
        self.suite = suite

    def __str__(self):
        # color = {1: "Red", 2: "Blue", 3: "Green", 4: "Yellow"}
        number = {1: "Swap", 11: "J", 13: "K"}
        return f"{self.suite.name if self.suite is not None else None} {number[self.number] if self.number in number else self.number}"

    def to_tuple(self):
        if self.suite is None:
            return (self.number, 0)
        return (self.number, self.suite.value)

    @staticmethod
    def from_tuple(tup: tuple):
        return Card(tup[0], tup[1])


def get_random_card():
    num = random.choice(possible_cards)
    suite = random.choice(possible_suite)
    if num == 1 or num == 8:
        return Card(num, None)
    return Card(num, suite)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: list[Card] = []

    def draw(self):
        card = get_random_card()
        self.hand.append(card)

    def play(self, card: Card):
        self.hand.remove(card)

    def choose_card(self, top: Card, enemy_hand_length: int, drew: bool) -> Card:
        print("Your hand:")
        playable_cards = {}
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}", end=" ")
            if (
                card.suite == top.suite
                or card.number == top.number
                or card.number == 8
                or card.number == 1
            ):
                print("Playable")
                playable_cards[i] = card
            else:
                print()
        if drew:
            string = (
                "Which card would you like to play? (Enter the number or 'd' to draw): "
            )
        else:
            string = (
                "Which card would you like to play? (Enter the number or 's' to skip): "
            )
        choice = input(string)
        if drew and choice == "d":
            return None
        elif not drew and choice == "s":
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


class RandomPlayer(Player):
    def choose_card(self, top: Card, enemy_hand_length: int, drew: bool) -> Card:
        playable_cards = [None]
        for card in self.hand:
            if card.number == 8:
                suite = random.choice(possible_suite)
                card.suite = suite
            if (
                card.suite == top.suite
                or card.number == top.number
                or card.number == 8
                or card.number == 1
            ):
                playable_cards.append(card)
        return random.choice(playable_cards)


class Game:
    def __init__(self, player1: Player, player2: Player):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.top = get_random_card()
        self.turns = 0

    def start(self):
        for _ in range(5):
            self.player1.draw()
            self.player2.draw()
        self.top = get_random_card()
        while True:
            # print(f"It's {self.current_player.name}'s turn.")
            # print(f"The top card is {self.top}")
            self.turn()
            self.turns += 1
            if self.turns > 1000:
                print("Too many turns!")
                return 0
            if len(self.current_player.hand) == 0:
                print(f"{self.current_player.name} wins!")
                if self.current_player == self.player1:
                    return 1
                else:
                    return 2
                break
            self.switch_player()

    def turn(self):
        card_played = False
        drew = False
        other_player = (
            self.player1 if self.current_player == self.player2 else self.player2
        )
        curr_player = self.current_player
        while not card_played:
            card = curr_player.choose_card(
                self.top, len(other_player.hand), not drew
            )
            if card is not None:
                curr_player.play(card)
                self.top = self.apply_card_effect(card)
                card_played = True
            elif drew:
                break
            else:
                self.current_player.draw()
                drew = True
            if isinstance(curr_player, AgentPlayer):
                curr_player.update_reward(
                    self.top, len(other_player.hand), drew
                )

    def apply_card_effect(self, card: Card) -> Card:
        new_top_color = card.suite
        new_top_number = card.number
        if card.number == 1:  # Swap
            self.player1.hand, self.player2.hand = self.player2.hand, self.player1.hand
            new_top_color = self.top.suite
            new_top_number = self.top.number
        elif card.number == 8:  # Change color
            new_top_number = self.top.number
        elif card.number == 11:  # Skip
            self.switch_player()
        elif card.number == 13:  # Draw one
            self.switch_player()
            self.current_player.draw()
            self.switch_player()

        return Card(new_top_number, new_top_color)

    def switch_player(self):
        self.current_player = (
            self.player1 if self.current_player == self.player2 else self.player2
        )

    def __str__(self):
        return f"Player 1: {self.player1}\nPlayer 2: {self.player2}"


class Agent:
    def __init__(
        self,
        epsilon: float = 0.01,
        alpha: float = 0.5,
        gamma: float = 0.95,
        file_name: str | None = None,
    ):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = {}
        if file_name is not None:
            path = os.path.join("q_tables", file_name)
            with open(path, "rb") as f:
                self.q_table = pickle.load(f)

    def get_q_value(self, state: tuple, action: tuple) -> float:
        # if state not in self.q_table:
        #     self.q_table[state] = {}
        # if action not in self.q_table[state]:
        #     self.q_table[state][action] = 0
        # return self.q_table[state][action]
        sorting_indices = self.get_sorting_indices(state)
        optimized_state = self.optimize_state(state, sorting_indices)
        if optimized_state not in self.q_table:
            self.q_table[optimized_state] = {}
        optimized_action = self.optimize_action(action, sorting_indices)
        if optimized_action not in self.q_table[optimized_state]:
            self.q_table[optimized_state][optimized_action] = 0
        return self.q_table[optimized_state][optimized_action]

    def update_q_value(
        self, state: tuple, action: tuple, reward: float, next_state: tuple
    ) -> None:
        predict = self.get_q_value(state, action)
        sorting_indices = self.get_sorting_indices(state)
        state = self.optimize_state(state, sorting_indices)
        action = self.optimize_action(action, sorting_indices)
        next_state = self.optimize_state(next_state, sorting_indices)
        if next_state not in self.q_table:
            self.q_table[next_state] = {}
        target = reward + self.gamma * max(self.q_table[next_state].values(), default=0)
        self.q_table[state][action] += self.alpha * (target - predict)

    def choose_action(self, state: tuple, possible_actions: list) -> tuple:
        if random.random() < self.epsilon:
            return random.choice(possible_actions)
        else:
            max_q_value = max(
                [self.get_q_value(state, action) for action in possible_actions]
            )
            best_actions = [
                action
                for action in possible_actions
                if self.get_q_value(state, action) == max_q_value
            ]
            return random.choice(best_actions)
    
    def get_sorting_indices(self, state):
        suite_counts = [0 for _ in range(5)]
        for row in state[3]:
            for i in range(5):
                suite_counts[i] += row[i]
        
        sorting_indices = sorted(range(len(suite_counts)), key=lambda k: suite_counts[k])
        return sorting_indices


    def optimize_state(self, state, sorting_indices):
        top_suite = state[1][1]
        # print(sorting_indices)
        new_top_suite = sorting_indices.index(top_suite)

        new_hand = []
        for card in state[3]:
            new_card = []
            for i in range(4):
                new_card.append(card[sorting_indices[i]])
            new_hand.append(tuple(new_card))        
        return (state[0], (state[1][0], new_top_suite), state[2], tuple(new_hand), state[4])
    
    def optimize_action(self, action, sorting_indices):
        if action == ():
            return ()
        return (action[0], sorting_indices.index(action[1]))

    def reward(self, state: list) -> float:
        """
        return (
            enemy_hand_length,
            top.to_tuple(),
            len(self.hand),
            self.get_hand_state(),
            drew,
        )
        """
        if state[0] == 0:
            # The enemy has no cards left so he won.
            return -100
        if state[2] == 0:
            # The agent has no cards left so he won.
            return 100
        returning = 0
        # More cards in the enemy's hand is better.
        returning += state[0]
        # More cards in the agent's hand is worse.
        returning -= state[2] * 2
        playable_cards = 0  # Get the number of playable cards.
        jackss = 0  # Get the number of J in the agent's hand.
        eights = 0  # Get the number of 8 in the agent's hand.
        swaps = 0  # Get the number of 1 in the agent's hand.
        top = Card.from_tuple(state[1])
        for card in state[3]:
            if card[0] == top.number or card[1] == top.suite:
                playable_cards += 1
            if card[0] == 11:
                jackss += 1
            if card[0] == 8:
                eights += 1
            if card[0] == 1:
                swaps += 1
        returning += playable_cards
        # Get the number of J in the agent's hand.
        returning += jackss * 3
        # Get the number of 8 in the agent's hand.
        returning += eights * 2
        # Get the number of 1 in the agent's hand.
        if swaps == 1:
            returning += 5

        return returning


class AgentPlayer:
    def __init__(self, name: str, file_name: str | None = None):
        self.name = name
        self.hand: list[Card] = []
        self.agent = Agent(file_name=file_name)
        self.last_state = None
        self.last_action = None

    def draw(self):
        card = get_random_card()
        self.hand.append(card)

    def play(self, card: Card):
        self.hand.remove(card)

    def choose_card(self, top: Card, enemy_hand_length: int, drew: bool) -> Card:
        if enemy_hand_length > 10:
            enemy_hand_length = 10
        state = self.get_state(top, enemy_hand_length, drew)
        self.last_state = state
        draw_action = ()
        possible_actions = [draw_action]
        for card in self.hand:
            if (
                card.suite == top.suite
                or card.number == top.number
                or card.number == 8
                or card.number == 1
            ):
                suites = []
                if card.number != 8 and card.number != 1:
                    suites.append(card.suite)
                else:
                    suites = possible_suite
                for suite in suites:
                    play_action = (card.number, suite.value if suite is not None else 0)
                    if play_action not in possible_actions:
                        possible_actions.append(play_action)
        action = self.agent.choose_action(state, possible_actions)
        self.last_action = action
        if action == draw_action:
            return None
        idx = -1
        for i, card in enumerate(self.hand):
            if card.number == action[0] and card.suite == action[1]:
                idx = i
                break
        return self.hand[idx]

    def get_state(self, top: Card, enemy_hand_length: int, drew: bool) -> tuple:
        return (
            enemy_hand_length,
            top.to_tuple(),
            len(self.hand),
            self.get_hand_state(),
            drew,
        )

    def get_hand_state(self) -> tuple:
        # What matters for the hand state is the number of cards of each number and suite.
        # We will represent this as a tuple of the following:
        # ((num_1_suite_1, ..., num_1_suite_4), ..., (num_13_suite_1, ..., num_13_suite_4))
        # where num_i_suite_j is the number of cards of number i and suite j.
        hand_state = [[0 for _ in range(5)] for _ in range(13)]
        for card in self.hand:
            if card.suite is not None:
                hand_state[card.number - 1][card.suite.value] += 1
            else:
                hand_state[card.number - 1][0] += 1

        return tuple(tuple(row) for row in hand_state)

    def choose_color(self) -> str:
        print("Which color would you like to change to?")
        for i, color in enumerate(possible_suite):
            print(f"{i}: {color}")
        choice = input("Which color would you like to change to? (Enter the number): ")
        return possible_suite[int(choice)]

    def update_reward(self, top, enemy_hand_length, drew) -> None:
        new_state = self.get_state(top, enemy_hand_length, drew)
        self.agent.update_q_value(
            self.last_state,
            self.last_action,
            self.agent.reward(new_state),
            new_state,
        )

    def write_q_table(self, file_name: str = "q_table.txt"):
        path = os.path.join("q_tables", file_name)
        # with open(path, "w+") as f:
        #     for key, value in self.agent.q_table.items():
        #         f.write(f"{key}: {value}\n")
        with open(path, "wb+") as f:
            pickle.dump(self.agent.q_table, f)

    def __str__(self):
        return f"{self.name}: {self.hand}"


import os
# import pandas as pd
# import matplotlib.pyplot as plt

if __name__ == "__main__":
    player1 = AgentPlayer("Player 1")
    player1 = AgentPlayer("Player 1", "q_table_mini_01e095g.bin")
    # player1 = AgentPlayer("Player 1", "q_table_mini_01e.bin")
    # player2 = AgentPlayer("Player 2")
    player2 = RandomPlayer("Player 2")
    p1_wins = 0
    p2_wins = 0
    for _ in range(10000):
        game = Game(player1, player2)
        winner = game.start()
        if winner == 1:
            p1_wins += 1
        elif winner == 2:
            p2_wins += 1
    print(f"Player 1 wins: {p1_wins}")
    print(f"Player 2 wins: {p2_wins}")
    # p1 win %
    print(f"Player 1 win %: {p1_wins / (p1_wins + p2_wins)}")
    player1.write_q_table("q_table_mini_01e095g.bin")
    # player2.write_q_table("q_table22.txt")
