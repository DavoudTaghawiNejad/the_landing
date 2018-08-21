from random import shuffle
from enum import Enum, auto
import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools
import numpy as np
from collections import Counter, defaultdict
from pprint import pprint

def xbins(nums):
    return dict(
        start=1,
        end=max(nums) + 1,
        size=1)

class Cards(Enum):
    t1 = 1
    t2 = 2
    t3 = 3
    td1 = 4
    td2 = auto()
    td3 = auto()
    tr1 = auto()
    tr2 = auto()
    tr3 = auto()
    RESHUFFLE = auto()
    ONLY_STOP = auto()
    REMOVE_STOP = auto()
    OTHER = auto()
    TRIBE = auto()

    def __repr__(self):
        return str(self)


class Num:
    tribs = 8
    reshuffle = 16
    supply = 4
    stop_remove = 4
    only_stop = 35 - reshuffle - supply
    other = 51 - only_stop - supply - reshuffle


class Card:
    def __init__(self, card_type):
        self.card_type = card_type
        self.drawn = 0

    def mark_drawn(self):
        self.drawn += 1

    def __eq__(self, card_type):
        return self.card_type is card_type

def card_stats(cards):
    stats = defaultdict(int)
    for card in cards:
        stats[card.card_type] += 1
    stats['total number'] = len(cards)
    return stats


def one_game(figs=False):
    cards = ([Card(Cards.RESHUFFLE) for _ in range(Num.reshuffle)] +
             [Card(Cards.ONLY_STOP) for _ in range(Num.only_stop)] +
             [Card(Cards.REMOVE_STOP) for _ in range(Num.supply + Num.stop_remove)] +
             [Card(Cards.TRIBE) for _ in range(Num.tribs)] +
             [Card(Cards.tr1), Card(Cards.tr2), Card(Cards.t2), Card(Cards.t3), Card(Cards.td2), Card(Cards.tr2), Card(Cards.td3), Card(Cards.tr2)] +
             [Card(Cards.OTHER) for _ in range(Num.other)])

    stats = card_stats(cards)
    print('number cards', len(cards))

    shuffle(cards)

    removed = []
    discard = []
    ii = []
    lastii = []
    subround = 0
    pos = 0
    tribes = 0
    tribe_attacks = []
    discard_pile_length = []

    while True:
        i = 0
        while True:
            if i >= 5:
                break
            drawn = cards.pop()
            i += 1
            drawn.mark_drawn()
            if drawn == Cards.t1 and tribes > 0:
                tribe_attacks.append(subround)
                print('Attack tribe 1')
            if drawn == Cards.t2 and tribes > 1:
                tribe_attacks.append(subround)
                print('Attack tribe 2')
            if drawn == Cards.t3 and tribes > 2:
                tribe_attacks.append(subround)
                print('Attack tribe 3')
            if drawn == Cards.td1 and tribes > 0:
                tribe_attacks.append(subround)
                print('Sudden D6 attack tribe 1')
            if drawn == Cards.td2 and tribes > 1:
                tribe_attacks.append(subround)
                print('Sudden D6 attack tribe 2')
            if drawn == Cards.td3 and tribes > 2:
                print('Sudden D6 attack tribe 3')
                tribe_attacks.append(subround)
            if drawn == Cards.tr1 and tribes > 0:
                print('Sudden D6 attack tribe 3')
                tribe_attacks.append(subround)
                continue
            if drawn == Cards.tr2 and tribes > 1:
                print('Sudden D6 attack tribe 3')
                tribe_attacks.append(subround)
                continue
            if drawn == Cards.tr3 and tribes > 2:
                print('Sudden D6 attack tribe 3')
                tribe_attacks.append(subround)
                continue
            if drawn == Cards.RESHUFFLE:
                removed.append(drawn)
                shuffle(discard)
                cards.extend(discard)
                discard.clear()
                print("reshuffle")
                break
            if drawn == Cards.REMOVE_STOP:
                removed.append(drawn)
                print("Remove")
                break
            if drawn == Cards.TRIBE and tribes < 3:
                removed.append(drawn)
                tribes += 1
                print('TRIBES', tribes)
                break
            discard.append(drawn)

            if drawn == Cards.ONLY_STOP:
                print("Stop")
                break
            if len(cards) == 0:
                break
        subround += 1
        if subround == 9 * 2:
            tribes_half_time = tribes
        print(i, subround, end=' ')
        ii.append(i)
        lastii.append(i)
        discard_pile_length.append(len(discard))
        if figs and subround % (4 * 3) == 0:
                fig.append_trace(go.Histogram(x=lastii, xbins=xbins(lastii)), pos // 5 + 1, pos % 5 + 1)
                pos += 1
                lastii = []
        if subround == 9 * 4:
            print("end of game")
            break
        if len(cards) == 0:
            print("no more cards")
            break

    repeated_cards = ([card.drawn for card in cards] +
                      [card.drawn for card in discard] +
                      [card.drawn for card in removed])
    return ii, tribe_attacks, repeated_cards, tribes, tribes_half_time, discard_pile_length, stats


if __name__ == '__main__':
    repetitions = 10000
    fig = tools.make_subplots(rows=3, cols=3,
                              subplot_titles=['tribe_attacks', 'mean number of cards', 'num tribes',
                                              'mean number of cards', 'repeated_cards', 'num tribes half time',
                                              'number of cards discard pile', 'repeated_cards', 'num_tribe_attacks'])
    fig2 = tools.make_subplots(rows=1, cols=5)
    fig3 = tools.make_subplots(rows=5, cols=5)
    fig4 = tools.make_subplots(rows=5, cols=5)

    tribe_attacks_list = []
    iis = []
    xis = []
    repeated_cards_list = []
    tribes_list = []
    tribes_ht_list = []
    discard_pile_length_list = []
    num_tribe_attacks = []
    for i in range(repetitions):
        ii, tribe_attacks, repeated_cards, tribes, tribes_half_time, discard_pile_length, stats = one_game()
        tribe_attacks_list += tribe_attacks
        iis.append(ii)
        xis.extend(ii)
        tribes_list.append(tribes)
        tribes_ht_list.append(tribes_half_time)
        repeated_cards_list.extend(repeated_cards)
        discard_pile_length_list.append(discard_pile_length)
        num_tribe_attacks.append(len(tribe_attacks))
        if i < 25:
            fig3.append_trace(go.Bar(y=[tribe_attacks.count(j)
                                        for j in range(9 * 4)],
                                     x=list(range(9 * 4))), i % 5 + 1, i // 5 + 1)
            fig4.append_trace(go.Bar(y=ii,
                                     x=list(range(9 * 4))), i % 5 + 1, i // 5 + 1)
    print(tribe_attacks_list)
    fig.append_trace(go.Histogram(x=[str(ta) for ta in tribe_attacks_list], histnorm='probability'), 1, 1)
    fig.append_trace(go.Histogram(x=xis, histnorm='probability'), 1, 2)
    fig.append_trace(go.Histogram(x=tribes_list, histnorm='probability'), 1, 3)
    fig.append_trace(go.Histogram(x=tribes_ht_list, histnorm='probability'), 2, 3)
    fig.append_trace(go.Histogram(x=repeated_cards, histnorm='probability'), 2, 2)
    fig.append_trace(go.Histogram(x=repeated_cards_list, histnorm='probability'), 3, 2)
    fig.append_trace(go.Bar(y=discard_pile_length), 3, 1)
    fig.append_trace(go.Bar(y=[np.mean(r) for r in list(zip(*discard_pile_length_list))]), 3, 1)
    fig.append_trace(go.Histogram(x=num_tribe_attacks, histnorm='probability'), 3, 3)

    fig.append_trace(go.Bar(y=[np.mean(ii) - 1 for ii in list(zip(*iis))],
                            error_y=dict(
                            type='data',
                            array=[np.std(ii) for ii in list(zip(*iis))]),
                            visible=True),
                     2, 1)

    print([Counter(ii)[5] for ii in list(zip(*iis))][0])
    # for i in range(9):
    #     for h in range(1, 5):
    #         fig2.append_trace(go.Bar(y=[Counter(ii[i * 4: (i + 1) * 4])[h] / repetitions * 9
    #                                     for ii in list(zip(*iis))]), i + 1, h)

    for h in range(1, 6):
        fig2.append_trace(go.Bar(y=[Counter(ii)[h] / repetitions for ii in list(zip(*iis))]), 1, h)
    py.plot(fig)
    py.plot(fig2, filename='f2')
    py.plot(fig3, filename='indian_attacks')
    py.plot(fig4, filename='cards_drawn')
    pprint(dict(stats))
