from random import shuffle
from enum import Enum, auto
import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools
import numpy as np
from collections import Counter, defaultdict
from pprint import pprint
from copy import copy


def xbins(nums):
    return dict(
        start=1,
        end=max(nums) + 1,
        size=1)


class Cards(Enum):
    TRIBE_EVENT = auto()
    RESHUFFLE = auto()
    ONLY_STOP = auto()
    REMOVE_STOP = auto()
    OTHER = auto()
    TRIBE = auto()

    def __repr__(self):
        return str(self)


class Num:
    tribs = 7
    reshuffle = 16
    stop_remove = 7
    only_stop = 10
    other = 20


class Card:
    def __init__(self, card_type, tribe_affected=None):
        self.card_type = card_type
        self.drawn = 0
        self.tribe_affected = tribe_affected

    def mark_drawn(self):
        self.drawn += 1

    def __eq__(self, card_type):
        return self.card_type is card_type

    def __str__ (self):
        return "<%s, %s>" % (str(self.card_type), str(self.tribe_affected))


def card_stats(cards):
    stats = defaultdict(int)
    for card in cards:
        stats[str(card.card_type)] += 1
        stats['total number'] += 1
    return stats


def count(cards, card_type):
    return sum([1 for card in cards if card == card_type])

def hist(cards):
    hist = defaultdict(int)
    for card in cards:
        hist[str(card.card_type)] += card.drawn
        hist['total number'] += card.drawn
    return hist

def one_game(figs=False):
    cards = ([Card(Cards.RESHUFFLE) for _ in range(Num.reshuffle)] +
             [Card(Cards.ONLY_STOP) for _ in range(Num.only_stop)] +
             [Card(Cards.REMOVE_STOP) for _ in range(Num.stop_remove)] +
             [Card(Cards.TRIBE) for _ in range(Num.tribs)] +
             [Card(Cards.TRIBE_EVENT, t % 3 + 1) for t in range(1)] * 2 +
             [Card(Cards.TRIBE_EVENT, t % 3 + 1) for t in range(2)] * 2 +
             [Card(Cards.TRIBE_EVENT, t % 3 + 1) for t in range(3)] * 2 +
             [Card(Cards.OTHER) for _ in range(Num.other)])

    stats = card_stats(cards)
    start_cards = copy(cards)
    print('number cards', len(cards))

    shuffle(cards)

    removed = []
    discard = []
    ii = []
    lastii = []
    subround = 0
    pos = 0
    tribes = 0
    tribe_events = []
    discard_pile_length = []

    while True:
        i = 0
        while True:
            if i >= 5:
                break
            drawn = cards.pop()
            i += 1
            drawn.mark_drawn()
            if drawn == Cards.TRIBE_EVENT and drawn.tribe_affected <= tribes:
                tribe_events.append(subround)
                print('Attack tribe 1')
                discard.append(drawn)
            elif drawn == Cards.TRIBE_EVENT and drawn.tribe_affected > tribes:
                discard.append(drawn)
            elif drawn == Cards.RESHUFFLE:
                removed.append(drawn)
                shuffle(discard)
                cards.extend(discard)
                discard.clear()
                print("reshuffle")
                break
            elif drawn == Cards.REMOVE_STOP:
                removed.append(drawn)
                print("Remove")
                break
            elif drawn == Cards.TRIBE and tribes < 3:
                removed.append(drawn)
                tribes += 1
                print('TRIBES', tribes)
                break
            elif drawn == Cards.TRIBE and tribes >= 3:
                break
            elif drawn == Cards.ONLY_STOP:
                print("Stop")
                discard.append(drawn)
                break
            elif drawn == Cards.OTHER:
                discard.append(drawn)
            else:
                raise Exception(str(drawn))
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
    return (ii, tribe_events, repeated_cards, tribes, tribes_half_time, discard_pile_length,
            stats, count(removed, Cards.REMOVE_STOP), hist(start_cards), card_stats(start_cards))


if __name__ == '__main__':
    repetitions = 10000
    fig = tools.make_subplots(rows=3, cols=3,
                              subplot_titles=['tribe_events', 'mean number of cards', 'num tribes',
                                              'mean number of cards', 'repeated_cards', 'num tribes half time',
                                              'number of cards discard pile', 'repeated_cards', 'num_tribe_events'])
    summary_fig2 = tools.make_subplots(rows=3, cols=3,
                                       subplot_titles=['cards drawn', 'card_stats'])
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
    num_tribe_events = []
    num_remove_stop_list = []
    for i in range(repetitions):
        (ii, tribe_events, repeated_cards, tribes, tribes_half_time, discard_pile_length, stats,
         num_remove_stop, hist_start_cards, hist_card_stats) = one_game()
        tribe_attacks_list += tribe_events
        iis.append(ii)
        xis.extend(ii)
        tribes_list.append(tribes)
        tribes_ht_list.append(tribes_half_time)
        repeated_cards_list.extend(repeated_cards)
        discard_pile_length_list.append(discard_pile_length)
        num_tribe_events.append(len(tribe_events))
        num_remove_stop_list.append(num_remove_stop)
        if i < 25:
            fig3.append_trace(go.Bar(y=[tribe_events.count(j)
                                        for j in range(9 * 4)],
                                     x=list(range(9 * 4))), i % 5 + 1, i // 5 + 1)
            fig4.append_trace(go.Bar(y=ii,
                                     x=list(range(9 * 4))), i % 5 + 1, i // 5 + 1)

    fig.append_trace(go.Histogram(x=[str(ta) for ta in tribe_attacks_list], histnorm='probability'), 1, 1)
    fig.append_trace(go.Histogram(x=xis, histnorm='probability'), 1, 2)
    fig.append_trace(go.Histogram(x=tribes_list, histnorm='probability'), 1, 3)
    fig.append_trace(go.Histogram(x=tribes_ht_list, histnorm='probability'), 2, 3)
    fig.append_trace(go.Histogram(x=repeated_cards, histnorm='probability'), 2, 2)
    fig.append_trace(go.Histogram(x=repeated_cards_list, histnorm='probability'), 3, 2)
    fig.append_trace(go.Bar(y=discard_pile_length), 3, 1)
    fig.append_trace(go.Bar(y=[np.mean(r) for r in list(zip(*discard_pile_length_list))]), 3, 1)
    fig.append_trace(go.Histogram(x=num_tribe_events, histnorm='probability'), 3, 3)

    fig.append_trace(go.Bar(y=[np.mean(ii) for ii in list(zip(*iis))],
                            error_y=dict(
                            type='data',
                            array=[np.std(ii) for ii in list(zip(*iis))]),
                            visible=True),
                     2, 1)

    summary_fig2.append_trace(go.Bar(x=list(hist_start_cards.values()), y=list(hist_start_cards.keys()), orientation = 'h'), 1, 1)
    summary_fig2.append_trace(go.Bar(x=list(hist_card_stats.values()), y=list(hist_card_stats.keys()), orientation = 'h'), 1, 2)

    for h in range(1, 6):
        fig2.append_trace(go.Bar(y=[Counter(ii)[h] / repetitions for ii in list(zip(*iis))]), 1, h)
    py.plot(fig)
    py.plot(summary_fig2, filename='summary_fig2')
    py.plot(fig2, filename='f2')
    py.plot(fig3, filename='indian_events')
    py.plot(fig4, filename='cards_drawn')
    pprint(dict(stats))
    print('REMOVE_STOP cards drawn on average', np.mean(num_remove_stop_list), np.std(num_remove_stop_list))
    print('cards drawn on average: %f' % (sum(xis) / repetitions))
