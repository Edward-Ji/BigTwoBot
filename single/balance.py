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
    def value(self):
        rank_value = Card.rank_order.index(self.rank)
        suit_value = Card.suit_order.index(self.suit)
        return rank_value * 4 + suit_value

    @classmethod
    def sort(cls, cards):
        return sorted(cards, key=lambda c: Card(c).value)

    @classmethod
    def carried(cls, cards, std):
        lower = 0
        for card in cls.sort(cards):
            if Card(card) > Card(std):
                break
            lower += 1
        higher = len(cards) - lower
        return lower <= higher - 1

    @classmethod
    def other_hand_avg(cls, record):
        other_hand_total = sum(range(52))
        other_hand_count = 52
        for trick in record:
            for player, card in trick:
                if card:
                    card = card[0]
                    other_hand_total -= Card(card).value
                    other_hand_count -= 1
        return other_hand_total / other_hand_count


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
    my_hand = sorted(hand, key=lambda c: Card(c).value)

    # If we are starting a trick, we cannot pass.
    if len(play_to_beat) == 0:
        # If we are the first play in a round, the 3D must be in our hand. Play it.
        # Otherwise, we play a random card from our hand.
        if is_start_of_round:
            play_card = '3D'
        else:
            play_card = my_hand[0]
        return [play_card]

    if min(hand_sizes) == 1:
        if Card(my_hand[-1]) > Card(play_to_beat[0]):
            return [my_hand[-1]]
        else:
            return []

    # find the smallest card that beats opponent's play
    for card in my_hand:
        if Card(card) > Card(play_to_beat[0]):
            play_card = card
            break
    else:
        return []

    my_hand_avg = int(sum([Card(c).value for c in my_hand]) / len(my_hand))
    other_hand_avg = int(Card.other_hand_avg(round_history))
    if Card(card).value < my_hand_avg:
        return [play_card]
    if Card.carried(my_hand, other_hand_avg):
        return [play_card]
    else:
        return []
