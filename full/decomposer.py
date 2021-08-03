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
    type_rank = ["single", "pair", "triple",
                 "straight", "flush", "full house", "four of a kind", "straight flush"]

    def __init__(self, cards):
        self.cards = list(Card.sort(cards))

    def __len__(self):
        return len(self.cards)

    def _compare(self, sign, other):

        if len(self) != len(other):
            return False

        # compare trick type for five-card combos
        if len(self) == len(other) == 5:
            if self.type != other.type:
                if sign == '<':
                    return self.type_rank.index(self.type) < self.type_rank.index(other.type)
                elif sign == '>':
                    return self.type_rank.index(self.type) > self.type_rank.index(other.type)

        self_card, other_card = self.cards[-1], other.cards[-1]
        # suit compare priority for flush only
        if self.type == "flush":
            if Card(self_card).suit_value != Card(other_card).suit_value:
                if sign == '<':
                    return Card(self_card).suit_value < Card(other_card).suit_value
                elif sign == '>':
                    return Card(self_card).suit_value > Card(other_card).suit_value

        # compare trick for all other circumstances
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

        # check for more complex five card combinations
        elif len(self) == 5:

            # check straight and flush
            result = ''
            # check for straight
            last_card_rank = Card(self[0]).rank_value
            for card in self.cards[1:]:
                if Card(card).rank_value != last_card_rank + 1:
                    break
                last_card_rank += 1
            else:
                result += "straight"
            # check for flush
            card_suit = Card(self[0]).suit
            for card in self.cards:
                if Card(card).suit != card_suit:
                    break
            else:
                if result:
                    result += ' '
                result += "flush"
            # return one or both of straight and flush
            if result:
                return result

            # check for full house
            for triplet in itertools.combinations(self.cards, 3):
                if Trick(triplet).type == "triple":
                    double = list(filter(lambda c: c not in triplet, self.cards))
                    if Trick(double).type == "pair":
                        self.cards = double + list(triplet)
                        return "full house"

            # check for four of a kind
            for quadruplet in itertools.combinations(self.cards, 4):
                card_rank = Card(quadruplet[0]).rank_value
                for card in quadruplet[1:]:
                    if Card(card).rank_value != card_rank:
                        break
                else:
                    single = list(filter(lambda c: c not in quadruplet, self.cards))
                    self.cards = single + list(quadruplet)
                    return "four of a kind"

        # if none is satisfied then combination is invalid
        return "invalid play"


class Hand:

    def __init__(self, cards):
        self.cards = Card.sort(cards)
        self.strategies = []

    def organise(self, length_limit):
        unused_cards = self.cards.copy()
        self.strategies = []
        for size in [5, 3, 2, 1]:
            if size > length_limit:
                continue

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

    def beats(self, other, edge=False):
        available = []
        for trick in self.strategies:
            if Trick(trick) > Trick(other):
                available.append(trick)
        if not available:
            self.organise(len(other))
            for trick in self.strategies:
                if Trick(trick) > Trick(other):
                    available.append(trick)
            if not available:
                return []
        if edge:
            return available[-1]
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
    my_hand.organise(5)

    # start of a trick
    if len(play_to_beat) == 0:

        if is_start_of_round:
            # return trick that contains 3D for the first trick of the round
            for trick in my_hand.strategies:
                if '3D' in trick:
                    return trick
        # starting a trick in the middle of a round
        else:
            print(my_hand.strategies)
            return my_hand.strategies[0]

    # Play more aggressive if others may win with one play
    if min(hand_sizes) == len(play_to_beat):
        play_card = my_hand.beats(play_to_beat, edge=True)
    else:
        # find the smallest card trick that beats last play
        play_card = my_hand.beats(play_to_beat)
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
