"""This contains the reinforcement learning agent for blazing 8s."""

"""
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
from blazing8s import Card, possible_suite, get_random_card

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
# Reward if we have one swap card.
