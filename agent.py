"""This contains the reinforcement learning agent for blazing 8s."""

# First let's define the state space.
# We will represent the state as a tuple of the following:
# 1. The number of cards in the enemy's hand.
# 2. The number top card of the game in the format (number, suite).
# 3. The number of cards in the agent's hand. Up to 10.
# 4-13. The number of cards in the agent's hand of each number. Up to 10.


# The action space is a tuple of the following:
# 1. The index of the card to play. If the agent chooses to draw, this is None.
# 2. If the agent chooses to play an 8, the suite to change to. Otherwise, this is None.
# 3. If the agent drew a card, the index of the card to play. Otherwise None to end the turn.
# 4. If the agent drew a card and played an 8, the suite to change to. Otherwise None.

import random
from blazing8s import Card, Suite, possible_cards, possible_suite, get_random_card

# TODO: Calculate the reward and update the q table after each move. This requires a change to the game loop.
# TODO: Make sure we don't draw too often. - Maybe we don't need this if we have a good reward function.
# Reward function ideas:
# Reward for winning. - This is the most important.
# Penalty for losing?
# Reward for the number of cards in the enemy's hand.
# Penalty for the number of cards in the agent's hand?
# Reward for the number of playable cards ?
# Reward for the number of J in the agent's hand.
# Reward for the number of 8 in the agent's hand?


class Agent:
    def __init__(self, epsilon: float = 0.1, alpha: float = 0.5, gamma: float = 0.9):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.q_table = {}

    def get_q_value(self, state: tuple, action: tuple) -> float:
        if state not in self.q_table:
            self.q_table[state] = {}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0
        return self.q_table[state][action]

    def update_q_value(
        self, state: tuple, action: tuple, reward: float, next_state: tuple
    ) -> None:
        predict = self.get_q_value(state, action)
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


class AgentPlayer:
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.agent = Agent()

    def draw(self):
        card = get_random_card()
        self.hand.append(card)

    def play(self, card: Card):
        self.hand.remove(card)

    def choose_card(self, top: Card, enemy_hand_length: int, draw: bool) -> Card:
        state = self.get_state(top, enemy_hand_length, False)
        draw_action = ()
        possible_actions = [draw_action]
        for card in self.hand:
            if card.suite == top.suite or card.number == top.number or card.number == 8 or card.number == 1:
                suite = None
                if card.number != 8 and card.number != 1:
                    suite = card.suite
                play_action = (card.number, suite)
                if play_action not in possible_actions:
                    possible_actions.append(play_action)
        action = self.agent.choose_action(state, possible_actions)
        if action == draw_action:
            return None
        idx = -1
        for i, card in enumerate(self.hand):
            if card.number == action[0] and card.suite == action[1]:
                idx = i
                break
        return self.hand[idx]

    def get_state(self, top: Card, enemy_hand_length: int, draw: bool) -> tuple:
        return (
            enemy_hand_length,
            top.to_tuple(),
            len(self.hand),
            self.get_hand_state(),
            draw,
        )

    def get_hand_state(self) -> tuple:
        # What matters for the hand state is the number of cards of each number and suite.
        # We will represent this as a tuple of the following:
        # ((num_1_suite_1, ..., num_1_suite_4), ..., (num_13_suite_1, ..., num_13_suite_4))
        # where num_i_suite_j is the number of cards of number i and suite j.
        hand_state = [[0 for _ in range(4)] for _ in range(13)]
        for card in self.hand:
            hand_state[card.number - 1][card.suite.value - 1] += 1
        return tuple(tuple(row) for row in hand_state)

    def choose_color(self) -> str:
        print("Which color would you like to change to?")
        for i, color in enumerate(possible_suite):
            print(f"{i}: {color}")
        choice = input("Which color would you like to change to? (Enter the number): ")
        return possible_suite[int(choice)]

    def __str__(self):
        return f"{self.name}: {self.hand}"
