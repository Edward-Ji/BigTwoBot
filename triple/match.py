import random
import time
import reserve_card
import balance
import organise


"""
Score keeping is different from normal big two game!
The player who wins in a round will gain one point. 
After game is finished, a win rate will be calculated.
"""

# === testing variable begins ===

test_val = [None, None, None, None]  # fill in None if you need no testing value
games = int(input("Play this many rounds: "))
# functions that represent four players
player_func = [reserve_card.play,
               organise.play,
               balance.play,
               reserve_card.play]

# === testing variable ends ===
# Do NOT edit the code below!

rank_order = "34567890JQKA2"
suit_order = "DCHS"


def get_deck():
    for rank in rank_order:
        for suit in suit_order:
            yield rank + suit


# start game
deck = [c for c in get_deck()]

win_count = [0, 0, 0, 0]

for round_no in range(games):

    print("\n\n===== Round {} =====\n".format(round_no))

    # start round
    random.seed(time.time())
    random.shuffle(deck)

    # initiate variables
    score = [0, 0, 0, 0]
    hands = []
    hand_size = [13, 13, 13, 13]
    is_start_of_round = True
    for player_no in range(4):
        hand = deck[player_no * 13:(player_no+1) * 13]
        hand = sorted(hand, key=lambda card: reserve_card.Card(card).value)
        print("Player {} hand: {}".format(player_no, ' '.join(hand)))
        if '3D' in hand:
            play_order = [no % 4 for no in range(player_no, player_no + 4)]
        hands.append(hand)

    player = 0
    play_to_beat = []
    last_player = 0
    round_record = [[]]

    while not any(map(lambda h: not h, hands)):

        if is_start_of_round:
            is_start_of_round = False
        else:
            player += 1
            player %= 4

        player_no = play_order[player]

        if player_no == last_player:
            print("--- start of new trick ---")
            play_to_beat = []
            round_record.append([])

        hand = hands[player_no]
        args = [hand, is_start_of_round, play_to_beat, round_record, player_no, hand_size, score, round_no]
        if test_val[player_no]:
            args.append(test_val[player_no])
        played = player_func[player_no](*args)
        if played:
            for card in played:
                hands[player_no].remove(card)
            last_player = player_no
            play_to_beat = played
            hand_size[player_no] -= len(played)
        round_record[-1].append([player_no, played])

        print("Player {} played {} have {} in hand".format(player_no, played, ' '.join(hand)))

    print("Player {} won!".format(player_no))
    win_count[player_no] += 1

print("===== Overall statistics =====")
for player_no in range(4):
    print("Player {} won {} games in total with winning rate of {:.3f}".format(player_no,
                                                                               win_count[player_no],
                                                                               win_count[player_no] / games))
