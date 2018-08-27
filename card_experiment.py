from random import shuffle
from enum import Enum, auto
import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools
import numpy as np
from collections import Counter, defaultdict
from pprint import pprint
from copy import copy
import random


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


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))


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

def one_game(figs=False, directions=None):
    cards = ([Card(Cards.RESHUFFLE) for _ in range(Num.reshuffle)] +
             [Card(Cards.ONLY_STOP) for _ in range(Num.only_stop)] +
             [Card(Cards.REMOVE_STOP) for _ in range(Num.stop_remove)] +
             [Card(Cards.TRIBE) for _ in range(Num.tribs)] +
             [Card(Cards.TRIBE_EVENT, t % 3 + 1) for t in range(1)] * 2 +
             [Card(Cards.TRIBE_EVENT, t % 3 + 1) for t in range(2)] * 2 +
             [Card(Cards.TRIBE_EVENT, t % 3 + 1) for t in range(3)] * 2 +
             [Card(Cards.OTHER) for _ in range(Num.other)])

    if directions is not None:
        for card, direction in zip(cards, directions):
            card.direction = direction


    stats = card_stats(cards)
    start_cards = copy(cards)

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
    penelty = 0
    movement = ''

    pos = [Pos(5, 5), Pos(5, 0), Pos(0, 5)]
    last_direction = -1
    while True:
        i = 0
        while True:
            if i >= 5:
                break
            drawn = cards.pop()
            if drawn.direction == last_direction:
                penelty -= 0.01
                if drawn.direction == 4:
                    penelty += 0.025
            if drawn.direction % 2 == last_direction % 2 and drawn.direction != 4:
                penelty += 0.05
            i += 1
            drawn.mark_drawn()

            movement += move(pos, drawn)

            if drawn == Cards.TRIBE_EVENT and drawn.tribe_affected <= tribes:
                tribe_events.append(subround)
                discard.append(drawn)
            elif drawn == Cards.TRIBE_EVENT and drawn.tribe_affected > tribes:
                discard.append(drawn)
            elif drawn == Cards.RESHUFFLE:
                removed.append(drawn)
                shuffle(discard)
                cards.extend(discard)
                discard.clear()
                break
            elif drawn == Cards.REMOVE_STOP:
                removed.append(drawn)
                break
            elif drawn == Cards.TRIBE and tribes < 3:
                removed.append(drawn)
                tribes += 1
                break
            elif drawn == Cards.TRIBE and tribes >= 3:
                break
            elif drawn == Cards.ONLY_STOP:
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
        # print(i, subround, end=' ')
        ii.append(i)
        lastii.append(i)
        discard_pile_length.append(len(discard))
        if figs and subround % (4 * 3) == 0:
                figs.append_trace(go.Histogram(x=lastii, xbins=xbins(lastii)), pos // 5 + 1, pos % 5 + 1)
                pos += 1
                lastii = []
        if subround == 9 * 4:
            break
        if len(cards) == 0:
            print("no more cards")
            break

    repeated_cards = ([card.drawn for card in cards] +
                      [card.drawn for card in discard] +
                      [card.drawn for card in removed])
    return (ii, tribe_events, repeated_cards, tribes, tribes_half_time, discard_pile_length,
            stats, count(removed, Cards.REMOVE_STOP), movement, penelty, start_cards, pos)


def move(pos, card):
    if card.tribe_affected is None:
        tribes_affected = [0, 1, 2]
    else:
        tribes_affected = [card.tribe_affected - 1]
    ret =''
    for tribe in tribes_affected:
        if card.direction == 0 and pos[tribe].x > 0:
            pos[tribe].x -= 1
            if tribe == 1:
                ret = 'l'
        elif card.direction == 2 and pos[tribe].x < 5:
            pos[tribe].x += 1
            if tribe == 1:   
                ret = 'r'
        elif card.direction == 1 and pos[tribe].y > 0:
            pos[tribe].y -= 1
            if tribe == 1:
                ret = 'u'
        elif card.direction == 3 and pos[tribe].y < 5:
            pos[tribe].y += 1
            if tribe == 1:
                ret = 'o'
        elif card.direction == 4:
            if tribe == 1:
                ret = '-'
        else:
            ret = '.'
    return ret
    




def run_and_payoff(directions):
    result = one_game(directions=directions)
    positions = result[-1]
    reward = - sum([(3 - pos.x) ** 2 + (3 - pos.y) ** 2 for pos in positions])
    return reward - result[-3]


def train(n):
    bests = []
    lever = 5
    sets = 72
    learners = [Egreedy(lever, greed=0.985) for r in range(sets)]
    for _ in range(n):
        directions = [learner.propose() for learner in learners]
        reward = 0
        for r in range(20):
            reward += run_and_payoff(directions)
        if _ % 1000 == 0:
            best_choice = [learner.best_choice() for learner in learners]
            best = 0
            for r in range(20):
                best += run_and_payoff(best_choice)
            best = best / 20
            print(_ / 1000, best, best_choice)
            bests.append(best)
        for learner in learners:
            learner.learn(reward)
    for _ in range(5):
        result = one_game(directions=[learner.best_choice() for learner in learners])
        print(result[-1], result[-4])
    py.plot([go.Scatter(y=bests)])
    pprint([(card.card_type, card.tribe_affected, card.direction) for card in result[-2]])
 

class Egreedy:
    def __init__(self, lever, greed):
        self.Q = {}
        self.k = {}
        self.rs = {}
        self.pay_off = 0
        for l in range(lever):
            self.Q[l] = 0.5
            self.rs[l] = 0
            self.k[l] = 0
        self.greed = greed
        self.lever = lever

    def propose(self):
        if random.random() < self.greed:
            self.action = (max(self.Q, key=self.Q.get))
        else:
            self.action = random.randrange(0, self.lever)
        return self.action

    def learn(self, pay_off):
        self.pay_off += pay_off
        self.rs[self.action] += pay_off
        self.k[self.action] += 1
        self.Q[self.action] = self.rs[self.action] / self.k[self.action]

    def best_choice(self):
        return max(self.Q, key=self.Q.get)



def main():
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
         num_remove_stop, start_cards) = one_game()
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

    hist_start_cards, hist_card_stats = hist(start_cards), card_stats(start_cards)

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

if __name__ == '__main__':
    train(200000)
