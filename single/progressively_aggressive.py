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
            my_play = '3D'
        else:
            my_play = my_hand[0]
        return [my_play]

    # Play more aggressive if others have fewer cards
    my_hand_size = len(hand)
    other_hand_sizes = hand_sizes.copy()
    other_hand_sizes.remove(my_hand_size)
    least = my_hand_size - min(other_hand_sizes) - 30

    # Play the smallest card that beats last play
    for i in range(len(my_hand)):
        if i < least:
            continue
        if Card(my_hand[i]) > Card(play_to_beat[0]):
            return [my_hand[i]]
    else:
        return []


if __name__ == '__main__':
    # Write your own test cases for your `play` function here.
    # These can be run with the Run button and will not affect the tournament or marking.

    # Here's an example test case and testing code to kick you off.
    TESTS = [  # [ expected return value, inputs ]
        [['3D'],
         [['3D', '4D', '4H', '7D', '8D', '8H', '0D', '0C', 'JH', 'QC', 'QS', 'KH', 'AS'], False, ['3D'], [[]], 0,
          [1, 12, 4, 13], [0, 0, 0, 0], 0]],
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