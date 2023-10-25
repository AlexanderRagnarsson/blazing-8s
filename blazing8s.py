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

# easy memoization
from functools import lru_cache


HAND_SIZE_CUTOFF = 11

possible_cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13]


class Suite(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4


suite_map = {0: None, 1: Suite.RED, 2: Suite.BLUE, 3: Suite.GREEN, 4: Suite.YELLOW}
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

    def choose_card(
        self, top: Card, enemy_hand_length: int, drew: bool, last_player_played
    ) -> Card:
        print(f"\nIt's {self.name}'s turn.")
        print(f"The top card is {top}")
        print(f"Enemy hand length: {enemy_hand_length} cards")
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
        if not drew:
            string = (
                "Which card would you like to play? (Enter the number or 'd' to draw): "
            )
        else:
            string = (
                "Which card would you like to play? (Enter the number or 's' to skip): "
            )
        choice = ""
        while choice not in [str(i) for i in playable_cards.keys()] + [
            "d" if not drew else "s"
        ]:
            choice = input(string)
        if not drew and choice == "d":
            return None
        elif drew and choice == "s":
            return None
        choice = self.hand[int(choice)]
        if choice.number == 8:
            suite = self.choose_color()
            choice.suite = suite
        return choice

    def choose_color(self) -> str:
        print("Which color would you like to change to?")
        for i, color in enumerate(possible_suite):
            print(f"{i}: {color}")
        choice = input("Which color would you like to change to? (Enter the number): ")
        while choice not in [str(i) for i in range(4)]:
            choice = input(
                "Which color would you like to change to? (Enter the number): "
            )
        return possible_suite[int(choice)]

    def __str__(self):
        return f"{self.name}: {self.hand}"


class RandomPlayer(Player):
    def __init__(self, name: str, GOOD_RANDOM: bool = True):
        super().__init__(name)
        self.GOOD_RANDOM = GOOD_RANDOM

    def choose_card(
        self, top: Card, enemy_hand_length: int, drew: bool, last_player_played
    ) -> Card:
        playable_cards = [] if self.GOOD_RANDOM else [None]
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
        if len(playable_cards) == 0:
            return None
        return random.choice(playable_cards)


class SimpleStrategyPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)

    def choose_card(
        self, top: Card, enemy_hand_length: int, drew: bool, last_player_played
    ) -> Card:
        playable_cards = []
        for card in self.hand:
            if card.number == 8:
                # suite = random.choice(possible_suite)
                # card.suite = suite
                pass
            if (
                card.suite == top.suite
                or card.number == top.number
                or card.number == 8
                or card.number == 1
            ):
                playable_cards.append(card)
        if len(playable_cards) == 0:
            return None
        # First try to play the king of the same suite.
        other_suite_king = None
        same_suite = None
        other_suite = None
        suite_counts = [0 for _ in range(5)]
        for card in playable_cards:
            if card.number == 13:
                if card.suite == top.suite:
                    return card
                other_suite_king = card
            if card.number not in [1, 8, 11]:
                if card.suite == top.suite:
                    same_suite = card
                else:
                    other_suite = card
            suite = card.suite.value if card.suite is not None else 0
            suite_counts[suite] += 1
        if other_suite_king is not None:
            return other_suite_king
        if same_suite is not None:
            return same_suite
        if other_suite is not None:
            return other_suite
        # If there are no normal cards of the same suite, play a 8 and swap to the suite with the most cards.
        if 8 in [card.number for card in playable_cards]:
            max_count = max(suite_counts)
            max_idx = suite_counts.index(max_count)
            card.suite = suite_map[max_idx]
            return card
        # Otherwise, play a random card.
        return random.choice(playable_cards)


class Game:
    def __init__(self, player1: Player, player2: Player, verbose: bool = False):
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1 if random.random() < 0.5 else player2
        self.top = get_random_card()
        self.turns = 0
        self.verbose = verbose
        self.last_player_played = False

    def start(self):
        self.player1.hand = []
        self.player2.hand = []
        for _ in range(5):
            self.player1.draw()
            self.player2.draw()
        self.top = get_random_card()
        while self.top.number in [1, 8]:
            self.top = get_random_card()
        self.last_player_played = False
        while True:
            # print(f"It's {self.current_player.name}'s turn.")
            # print(f"The top card is {self.top}")
            winner = self.turn()
            self.turns += 1
            if self.turns > 1000:
                if self.verbose:
                    print("Too many turns!")
                return 0
            if winner != 0:
                return winner
            self.switch_player()

    def turn(self):
        card_played = False
        drew = False
        other_player = (
            self.player1 if self.current_player == self.player2 else self.player2
        )
        curr_player = self.current_player
        new_last_player_played = False
        card = None
        will_break = False
        to_print = "\n"
        while not card_played:
            card = curr_player.choose_card(
                self.top, len(other_player.hand), drew, self.last_player_played
            )
            if card is not None:
                if self.verbose:
                    print(f"{curr_player.name} played {card}")
                curr_player.play(card)
                self.top = self.apply_card_effect(card)
                card_played = True
                new_last_player_played = True
            elif drew:
                if self.verbose:
                    print(f"{curr_player.name} skipped.")
                will_break = True
            else:
                if self.verbose:
                    print(f"{curr_player.name} drew.")
                self.current_player.draw()
                drew = True
            if isinstance(curr_player, AgentPlayer):
                curr_player.update_reward(
                    self.top, len(other_player.hand), drew, self.last_player_played
                )
                to_print += "updated reward"
            if will_break:
                break
        if card is not None and card.number != 11:
            self.last_player_played = new_last_player_played
        if len(curr_player.hand) == 0:
            if isinstance(other_player, AgentPlayer):
                other_player.update_reward(
                    self.top, len(curr_player.hand), drew, self.last_player_played
                )
                to_print += "updated reward"
            # print(to_print)
            if self.verbose:
                print(f"{curr_player.name} wins!")
            return 1 if curr_player == self.player1 else 2
        return 0

    def apply_card_effect(self, card: Card) -> Card:
        new_top_color = card.suite
        new_top_number = card.number
        if card.number == 1:  # Swap
            if len(self.player1.hand) != 0 and len(self.player2.hand) != 0:
                self.player1.hand, self.player2.hand = (
                    self.player2.hand,
                    self.player1.hand,
                )
                new_top_color = self.top.suite
                new_top_number = self.top.number
        elif card.number == 8:  # Change color
            new_top_number = self.top.number
        elif card.number == 11:  # Skip
            if len(self.player1.hand) != 0 and len(self.player2.hand) != 0:
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
        self.q_table_attempts = 0
        self.q_table_hits = 0
        if file_name is not None:
            path = os.path.join("q_tables", file_name)
            with open(path, "rb") as f:
                self.q_table = pickle.load(f)
            # Drop items in q_table where the hand_size is greater than 50.
            to_delete = []
            for k in self.q_table:
                if k[2] > HAND_SIZE_CUTOFF:
                    to_delete.append(k)
            print(f"Cut {len(to_delete)} items from q_table")
            print(f"That is {len(to_delete) / len(self.q_table) * 100}%")
            # Display a histogram of the hand sizes.
            hand_sizes = [k[2] for k in self.q_table]
            plt.hist(hand_sizes, bins=max(hand_sizes) - min(hand_sizes))
            plt.show()
            for k in to_delete:
                del self.q_table[k]

    def get_q_value(self, state: tuple, action: tuple) -> float:
        # if state not in self.q_table:
        #     self.q_table[state] = {}
        # if action not in self.q_table[state]:
        #     self.q_table[state][action] = 0
        # return self.q_table[state][action]
        self.q_table_attempts += 1
        hit = 1
        sorting_indices = self.get_sorting_indices(state)
        optimized_state = self.optimize_state(state, sorting_indices)
        if optimized_state not in self.q_table:
            self.q_table[optimized_state] = {}
            hit = 0
        optimized_action = self.optimize_action(action, sorting_indices)
        if optimized_action not in self.q_table[optimized_state]:
            self.q_table[optimized_state][optimized_action] = 0
            hit = 0
        self.q_table_hits += hit
        return self.q_table[optimized_state][optimized_action]

    def update_q_value(self, state: tuple, action: tuple, next_state: tuple) -> None:
        reward = self.reward(next_state)
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

    def get_sorting_indices(self, state) -> tuple:
        suite_counts = [0 for _ in range(5)]
        for row in state[3]:
            for i in range(5):
                suite_counts[i] += row[i]

        sorting_indices = sorted(
            range(len(suite_counts)), key=lambda k: suite_counts[k]
        )
        return tuple(sorting_indices)

    @lru_cache(maxsize=1000)
    def optimize_state(self, state, sorting_indices):
        # new_hand = []
        # for j, card in enumerate(state[3]):
        #     new_card = []
        #     for i in sorting_indices:
        #         value = card[i]
        #         if value == 0:
        #             continue
        #         new_card.append(value)
        #     new_hand.append(tuple(new_card))
        # new_hand = tuple(new_hand)

        new_hand = tuple(state[3][j][i] for i in sorting_indices for j in range(13))

        new_state = list(state)
        new_state[1] = (state[1][0], sorting_indices.index(state[1][1]))
        new_state[3] = new_hand
        return tuple(new_state)

    def optimize_action(self, action, sorting_indices):
        # return action
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
            enemy_last_played_last,
        )
        """

        def inner(state):
            if state[0] == 0:
                # The enemy has no cards left so he won.
                # print('lost')
                return -100
            if state[2] == 0:
                # The agent has no cards left so he won.
                # print('won')
                return 100
            # return 0
            returning = 0
            # More cards in the enemy's hand is better.
            returning += state[0] * 2
            # More cards in the agent's hand is worse.
            returning -= state[2] * 3
            playable_cards = 0  # Get the number of playable cards.
            jackss = 0  # Get the number of J in the agent's hand.
            eights = 0  # Get the number of 8 in the agent's hand.
            swaps = 0  # Get the number of 1 in the agent's hand.
            top_num = state[1][0]
            top_suite = state[1][1]

            for card_num in range(1, 14):
                for card_suite in range(5):
                    if state[3][card_num - 1][card_suite] == 0:
                        continue
                    if (
                        card_num == top_num
                        or card_suite == top_suite
                        or card_num == 8
                        or card_num == 1
                    ):
                        playable_cards += 1
                    if card_num == 11:
                        jackss += 1
                    if card_num == 8:
                        eights += 1
                    if card_num == 1:
                        swaps += 1
            # print(len(state[3]))
            # print(playable_cards)
            # print(returning)
            # print(returning)
            # print()
            returning += playable_cards
            # Get the number of J in the agent's hand.
            returning += jackss * 6
            # Get the number of 8 in the agent's hand.
            returning += eights * 5
            # Get the number of 1 in the agent's hand.
            if swaps == 1:
                returning += 10

            # If the enemy agent didn't play last, that's good.
            if not state[5]:
                returning += 10
            else:
                pass
            return returning

            return returning

        # i = inner(state)
        # if abs(i) > 100:
        #     print(i)
        #     print(state)
        #     print()
        return inner(state)


class AgentPlayer:
    def __init__(
        self,
        name: str,
        file_name: str | None = None,
        alpha: float = 0.5,
        gamma: float = 0.95,
        epsilon: float = 0.1,
    ):
        self.name = name
        self.hand: list[Card] = []
        self.agent = Agent(
            alpha=alpha, gamma=gamma, epsilon=epsilon, file_name=file_name
        )
        self.last_state = None
        self.last_action = None

    def draw(self):
        card = get_random_card()
        self.hand.append(card)

    def play(self, card: Card):
        self.hand.remove(card)

    def choose_card(
        self, top: Card, enemy_hand_length: int, drew: bool, last_player_played
    ) -> Card:
        if enemy_hand_length > 10:
            enemy_hand_length = 10
        state = self.get_state(top, enemy_hand_length, drew, last_player_played)
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

    def get_state(
        self, top: Card, enemy_hand_length: int, drew: bool, last_player_played
    ) -> tuple:
        return (
            enemy_hand_length,
            top.to_tuple(),
            len(self.hand),
            self.get_hand_state(),
            drew,
            last_player_played,
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

    def update_reward(self, top, enemy_hand_length, drew, last_player_played) -> None:
        new_state = self.get_state(top, enemy_hand_length, drew, last_player_played)
        self.agent.update_q_value(
            self.last_state,
            self.last_action,
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


class BetterAgentPlayer(AgentPlayer):
    def choose_card(
        self, top: Card, enemy_hand_length: int, drew: bool, last_player_played
    ) -> Card:
        # if enemy_hand_length > 20:
        #     enemy_hand_length = 20
        state = self.get_state(top, enemy_hand_length, drew, last_player_played)
        self.last_state = state
        if len(self.hand) == 0:
            self.last_action = None
            print("Len is 0")
            return None
        draw_action = ()
        possible_actions = []
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
                elif card.number == 1:
                    suites = [None]
                else:
                    suites = possible_suite
                for suite in suites:
                    play_action = (card.number, suite.value if suite is not None else 0)
                    if play_action not in possible_actions:
                        possible_actions.append(play_action)
        if len(possible_actions) == 0:
            self.last_action = draw_action
            return None

        action = self.agent.choose_action(state, possible_actions)

        # # IF the agent chose to play a Swap, 8, or J, let them choose between playing it or drawing.
        if action[0] in [1, 11]:
            possible_actions.append(draw_action)
            action = self.agent.choose_action(state, possible_actions)

        self.last_action = action
        if action == draw_action:
            return None
        idx = -1
        for i, card in enumerate(self.hand):
            if card.number == action[0] and card.number in [1, 8]:
                # print("Playing a J or 8")
                # print(card)
                if card.number == 8:
                    # Set the correct suite
                    card.suite = suite_map[action[1]]
                # print(card)
                # print(action[1])
                idx = i
                break
            suite = card.suite.value if card.suite is not None else 0
            if card.number == action[0] and suite == action[1]:
                idx = i
                break
        return self.hand[idx]


import os

import pandas as pd
import matplotlib.pyplot as plt

# timing
from time import perf_counter

if __name__ == "__main__":
    # epsilons = [0.025, 0.01]
    # gammas = [0.95, 0.975, 0.99]
    # alphas = [0.4, 0.5, 0.6]
    # epsilons = [0.02, 0.015, 0.01]
    # epsilons = [0.02, 0.01]
    # gammas = [0.97, 0.98, 0.99]
    file_prefix = "q_table_draw_or_action_"
    training = True
    gammas = [0.975]
    epsilons = [0.9 if training else 0.005988571720948768]
    epsilon_multiplier = 0.995
    # gammas = [1]
    alphas = [0.4 if training else 0]
    best_win_percent = 0
    best_epsilon = None
    best_gamma = None
    best_alpha = None

    df = pd.DataFrame(
        columns=["games", "win_percent", "epsilon", "gamma", "alpha", "q_table_len"]
    )

    # profiling:
    import cProfile
    import pstats

    profiling = False

    if profiling:
        pr = cProfile.Profile()
        pr.enable()
    t1 = perf_counter()

    for original_epsilon in epsilons:
        for gamma in gammas:
            for alpha in alphas:
                print(f"epsilon: {original_epsilon}, gamma: {gamma}, alpha: {alpha}")
                try:
                    player1 = BetterAgentPlayer(
                        "Player 1",
                        alpha=alpha,
                        gamma=gamma,
                        epsilon=original_epsilon,
                        file_name=f"{file_prefix}{original_epsilon}e{gamma}g{alpha}a.bin",
                    )
                except FileNotFoundError as e:
                    print("Failed to load q table")
                    player1 = BetterAgentPlayer(
                        "Player 1", alpha=alpha, gamma=gamma, epsilon=original_epsilon
                    )
                # player1 = Player("Player 1")
                # player1.agent = Agent()
                # table_len = len(player1.agent.q_table)
                if training:
                    # player2 = RandomPlayer("Player 2", GOOD_RANDOM=False)
                    # player2 = RandomPlayer("Player 2", GOOD_RANDOM=True)
                    player2 = SimpleStrategyPlayer("Player 2")
                else:
                    player2 = Player("Player 2")
                total_p1_wins = 0
                total_p2_wins = 0
                outer = 2000
                inner = 100
                epsilon = original_epsilon
                for j in range(outer):
                    epsilon = epsilon * epsilon_multiplier
                    player1.agent.epsilon = epsilon
                    table_len = len(player1.agent.q_table)
                    p1_wins = 0
                    p2_wins = 0
                    for i in range(inner):
                        game = Game(
                            player1, player2, verbose=False if training else True
                        )
                        winner = game.start()
                        if winner == 1:
                            p1_wins += 1
                        elif winner == 2:
                            p2_wins += 1
                    win_percent = p1_wins / (p1_wins + p2_wins)
                    extra_in_table = len(player1.agent.q_table) - table_len
                    # print(f"First {(j + 1)*inner} games")
                    # print(f"Extra in table: {extra_in_table}")
                    # print(f"Player 1 win %: {win_percent}")
                    total_p1_wins += p1_wins
                    total_p2_wins += p2_wins
                    win_percent = total_p1_wins / (total_p1_wins + total_p2_wins)
                    curr_win_percent = p1_wins / (p1_wins + p2_wins)
                    if win_percent > best_win_percent:
                        best_win_percent = win_percent
                        best_epsilon = epsilon
                        best_gamma = gamma
                        best_alpha = alpha
                    df = df._append(
                        {
                            "games": (j + 1) * inner,
                            "win_percent": curr_win_percent,
                            "epsilon": epsilon,
                            "gamma": gamma,
                            "alpha": alpha,
                            "q_table_len": len(player1.agent.q_table),
                        },
                        ignore_index=True,
                    )
                print(
                    f"Player 1 total win %: {total_p1_wins/(total_p1_wins + total_p2_wins)}"
                )
                print(f"epsilon: {epsilon}, gamma: {gamma}, alpha: {alpha}")
                if training:
                    print("Writing into file")
                    print(f"{file_prefix}{original_epsilon}e{gamma}g{alpha}a.bin")
                    player1.write_q_table(
                        f"{file_prefix}{original_epsilon}e{gamma}g{alpha}a.bin"
                    )
                    print("Q table written into file")
                    print("Q table hits: ", player1.agent.q_table_hits)
                    print("Q table attempts: ", player1.agent.q_table_attempts)
                    print(
                        "Q table hit %: ",
                        player1.agent.q_table_hits / player1.agent.q_table_attempts,
                    )
    print(
        f"Best epsilon: {best_epsilon}, best gamma: {best_gamma}, best alpha: {best_alpha}"
    )
    print("Winning %: ", best_win_percent)

    t2 = perf_counter()
    print(f"Time taken: {t2 - t1}")

    if profiling:
        pr.disable()
        ps = pstats.Stats(pr).sort_stats("cumulative")
        # print into file
        ps.print_stats()

    df.plot(x="games", y="win_percent")
    df.plot(x="games", y="q_table_len")
    plt.show()

    # player1.write_q_table("q_table_mini_01e095g.bin")
    # player1.write_q_table("q_table_2_1e975g4a_1.bin")
