class Card:
    # rank and suit order from low to high
    rank_order = "34567890JQKA2"
    suit_order = "DCHS"

    def __init__(self, rep):
        self.rank, self.suit = rep

    def __repr__(self):
        return self.rank + self.suit

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    @property
    def value(self):
        rank_val = Card.rank_order.index(self.rank)
        suit_val = Card.suit_order.index(self.suit)
        return rank_val * 4 + suit_val

    @classmethod
    def value_to_card(cls, value):
        rank = Card.rank_order[int(value / 4)]
        suit = Card.suit_order[value % 4]
        return cls(rank + suit)

    @classmethod
    def all(cls):
        for rank in cls.rank_order:
            for suit in cls.suit_order:
                yield cls(rank + suit)

    @classmethod
    def play_or_not(cls, my_hand, card, record):
        other_hand_total = 1326
        other_hand_count = 52
        for trick_history in record:
            for trick_play in trick_history:
                if trick_play[1]:
                    other_hand_total -= Card(trick_play[1][0]).value
                    other_hand_count -= 1
        for my_card in my_hand:
            other_hand_total -= Card(my_card).value
            other_hand_count -= 1
        other_hand_avg = other_hand_total / other_hand_count
        my_hand_total = sum([Card(c).value if c is not card else 0 for c in my_hand])
        my_hand_count = len(my_hand) - 1
        my_hand_avg = my_hand_total / my_hand_count
        return my_hand_avg > other_hand_avg - 1 or Card(card).value < my_hand_avg * .6


def play(hand, is_start_of_round, play_to_beat, round_history, player_no, hand_sizes, scores, round_no):
    """
    The parameters to this function are:
    * `hand`: A list of card strings that are the card(s) in your hand.
    * `is_start_of_round`: A Boolean that indicates whether or not the `play` function is being asked to make the first play of a round.
    * `play_to_beat`: The current best play of the trick. If no such play exists (you are the first play in the trick), this will be an empty list.
    * `round_history`: A list of *trick_history* entries.
      A *trick_history* entry is a list of *trick_play* entries.
      Each *trick_play* entry is a `(player_no, play)` 2-tuple, where `player_no` is an integer between 0 and 3 (inclusive) indicating which player made the play, and `play` is the play that said player made, which will be a list of card strings.
    * `player_no`: An integer between 0 and 3 (inclusive) indicating which player number you are in the game.
    * `hand_sizes`: A 4-tuple of integers representing the number of cards each player has in their hand, in player number order.
    * `scores`: A 4-tuple of integers representing the score of each player at the start of this round, in player number order.
    * `round_no`: An integer between 0 and 9 (inclusive) indicating which round number is currently being played.

    This function should return an empty list (`[]`) to indicate a pass (see "Playing a Round"), or a list of card strings, indicating that you want to play these cards to the table as a valid play.
    """
    my_hand = sorted(hand, key=lambda card: Card(card).value)

    # If we are starting a trick, we cannot pass.
    if len(play_to_beat) == 0:
        # If we are the first play in a round, the 3D must be in our hand. Play it.
        # Otherwise, we play a random card from our hand.
        if is_start_of_round:
            play_card = '3D'
        else:
            play_card = my_hand[0]
        return [play_card]

    # Play more aggressive if others have fewer cards
    if min(hand_sizes) == 1:
        if Card(my_hand[-1]) > Card(play_to_beat[0]):
            return [my_hand[-1]]

    # play the highest card if opponent have one card
    if min(hand_sizes) == 1:
        if Card(my_hand[-1]) > Card(play_to_beat[0]):
            return my_hand[-1]
        else:
            return []

    # play the smallest card that beats last play
    for card in my_hand:
        if Card(card) > Card(play_to_beat[0]):
            play_card = card
            break
    else:
        return []

    # play only when you hold the highest unused card
    if len(hand) > 8 or my_hand.index(card) < len(my_hand) - 1:
        return [play_card]
    elif Card.play_or_not(my_hand, play_card, round_history):
        return [play_card]
    else:
        return []


if __name__ == '__main__':
    # Write your own test cases for your `play` function here.
    # These can be run with the Run button and will not affect the tournament or marking.

    # Here's an example test case and testing code to kick you off.
    TESTS = [  # [ expected return value, inputs ]
        [['AS'],
         [['4S', '6D', '6H', '7D', '9D', '9H', 'JS', 'KC', 'KH', 'AD', 'AH', 'AS', '2C'], False, ['4D'],
          [[[1, ['3D']], [2, ['4D']], [3, []]]], 0, [13, 12, 12, 13], [0, 0, 0, 0], 0]],
        # Add more tests here.
    ]

    # This runs the above test cases.
    for i, test in enumerate(TESTS):
        expected_return_value, inputs = test
        actual_return_value = play(*inputs)
        if actual_return_value == expected_return_value:
            print('PASSED {}/{}.'.format(i + 1, len(TESTS)))
        else:
            print('FAILED {}/{}.'.format(i + 1, len(TESTS)))
        print('    inputs:', repr(inputs))
        print('  expected:', repr(expected_return_value))
        print('    actual:', repr(actual_return_value))