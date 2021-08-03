import itertools


class Card:
    # rank and suit order from low to high
    rank_order = "34567890JQKA2"
    suit_order = "DCHS"

    def __init__(self, rep):
        if type(rep) == str:
            self.rank, self.suit = rep
        elif type(rep) == int:
            self.rank = Card.rank_order[int(rep / 4)]
            self.suit = Card.suit_order[rep % 4]
        else:
            raise ValueError("the representation of the card is not of a valid type")

    def __str__(self):
        return self.rank + self.suit

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    @property
    def rank_value(self):
        return Card.rank_order.index(self.rank)

    @property
    def suit_value(self):
        return Card.suit_order.index(self.suit)

    @property
    def value(self):
        return self.rank_value * 4 + self.suit_value

    @classmethod
    def sort(cls, cards):
        return sorted(cards, key=lambda c: Card(c).value)

    @classmethod
    def all(cls):
        for rank in cls.rank_order:
            for suit in cls.suit_order:
                yield cls(rank + suit)


class Trick:

    sign_func = {'<': Card.__lt__, "==": Card.__eq__, '>': Card.__gt__}

    def __init__(self, cards):
        self.cards = list(Card.sort(cards))

    def __len__(self):
        return len(self.cards)

    def _compare(self, sign, other):

        if len(self) != len(other):
            return False

        # compare trick for all other circumstances
        self_card, other_card = self.cards[-1], other.cards[-1]
        return self.sign_func[sign](Card(self_card), Card(other_card))

    def __lt__(self, other):
        return self._compare('<', other)

    def __eq__(self, other):
        return self._compare("==", other)

    def __gt__(self, other):
        return self._compare('>', other)

    def __getitem__(self, item):
        return self.cards[item]

    def __setitem__(self, key, value):
        self.cards[key] = value

    @property
    def type(self):

        # check for single, pair and triple of the same rank
        if len(self) == 1:
            return "single"
        elif len(self) == 2:
            if Card(self[0]).rank == Card(self[1]).rank:
                return "pair"
        elif len(self) == 3:
            if Card(self[0]).rank == Card(self[1]).rank == Card(self[2]).rank:
                return "triple"

        # if none is satisfied then combination is invalid
        return "invalid play"

    @property
    def value(self):
        card_values = [Card(c).value for c in self.cards]
        return sum(card_values) / len(card_values)


class Hand:

    def __init__(self, cards):
        self.cards = Card.sort(cards)
        self.strategies = []

    @property
    def type_count(self):
        type_no = {"single": 1, "pair": 2, "triple": 3}
        count = {"single": [0, 0], "pair": [0, 0], "triple": [0, 0]}
        for cards in self.strategies:
            if Trick(cards).value < 25.5:
                count[Trick(cards).type][0] += 1
            else:
                count[Trick(cards).type][1] += 1
        type_rank = sorted(["single", "pair", "triple"], key=lambda k: count[k][0] / count[k][1] if count[k][1] != 0 else 99)
        return list(map(lambda k: type_no[k], type_rank))[::-1]

    def organise(self, size_limit=None):
        unused_cards = self.cards.copy()
        self.strategies = []
        if size_limit:
            size_limit = [size_limit]
        else:
            size_limit = range(3, 0, -1)
        for size in size_limit:

            # loop to recalculate after discovery of each trick
            loop = True
            while loop:
                for cards in itertools.combinations(unused_cards, size):
                    if Trick(cards).type != "invalid play":
                        for card in cards:
                            unused_cards.remove(card)
                        self.strategies.append(list(cards))
                        break
                else:
                    loop = False

    def beats(self, other, hand_size):
        available = []

        # find available trick that beats the play
        for trick in self.strategies:
            if Trick(trick) > Trick(other):
                available.append(trick)

        # further separate hand if there is no available trick
        if not available:
            self.organise(len(other))
            for trick in self.strategies:
                if Trick(trick) > Trick(other):
                    available.append(trick)
        if not available:
            return []

        # play card according to priority
        if min(hand_size) == len(other):
            return available[-1]
        elif min(hand_size) >= 7 and Trick(available[0]).value >= 44:
            return []
        else:
            return available[0]


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
    my_hand = Hand(hand)
    my_hand.organise()

    # start of a trick
    if len(play_to_beat) == 0:

        if is_start_of_round:
            # return trick that contains 3D for the first trick of the round
            for trick in my_hand.strategies:
                if '3D' in trick:
                    return trick
        # starting a trick in the middle of a round
        else:
            for size in my_hand.type_count:
                for cards in my_hand.strategies:
                    if len(cards) == size:
                        return cards

    # Play more aggressive if others may win with one play
    other_hand_sizes = hand_sizes.copy()
    del other_hand_sizes[player_no]
    play_card = my_hand.beats(play_to_beat, other_hand_sizes)
    return play_card


if __name__ == '__main__':

    # Write your own test cases for your `play` function here.
    # These can be run with the Run button and will not affect the tournament or marking.
    # Here's an example test case and testing code to kick you off.

    TESTS = [  # [ expected return value, inputs ]
        [[],
         ["6D 6C 8D 8H 0C JD QC QH KH KS AD".split(), False, ['4D'], [], 0, [7, 13, 13, 9], [-9, -6, -39, 54], 1]],
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
