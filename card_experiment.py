from random import shuffle
from enum import Enum
import plotly.offline as py
import plotly.graph_objs as go
from plotly import tools
import numpy as np
from collections import Counter, defaultdict
from pprint import pprint
from copy import copy
import random
import turtle as ttl
from random import randrange, choice, sample
from heapq import nlargest
from multiprocessing import Pool
import pickle


def xbins(nums):
    return dict(
        start=1,
        end=max(nums) + 1,
        size=1)


class Cards(str, Enum):
    TRIBE_EVENT = 'TRIBE_EVENT'
    RESHUFFLE = 'RESHUFFLE'
    ONLY_STOP = 'ONLY_STOP'
    REMOVE_STOP = 'REMOVE_STOP'
    OTHER = 'OTHER'
    TRIBE = 'TRIBE'

    def __repr__(self):
        return self.name



num = {Cards.TRIBE: 13,
       Cards.RESHUFFLE: 13,
       Cards.REMOVE_STOP: 7,
       Cards.ONLY_STOP: 14,
       Cards.OTHER: 13,
       (Cards.TRIBE_EVENT, 1): 8,
       (Cards.TRIBE_EVENT, 2): 6,
       (Cards.TRIBE_EVENT, 3): 4}


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))


class Card:
    def __init__(self, card_type, direction):
        if isinstance(card_type, tuple):
            self.tribe_affected = card_type[1]
            self.card_type = card_type[0]
        else:
            self.tribe_affected = None
            self.card_type = card_type

        self.drawn = 0
        self.direction = direction

    def mark_drawn(self):
        self.drawn += 1

    @property
    def ldirection(self):
        if self.direction == 0:
            return '←'
        if self.direction == 1:
            return '↓'
        if self.direction == 2:
            return '→'
        if self.direction == 3:
            return '↑'
        if self.direction == 4:
            return '←←'
        if self.direction == 5:
            return '↓↓'
        if self.direction == 6:
            return '→→'
        if self.direction == 7:
            return '↑↑'
        if self.direction == 8:
            return '`'

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

def one_game(directions=None, figs=False):
    cards = []
    for card_type, gc in directions.genetical_code.items():
        for action, repetitions in enumerate(gc):
            for _ in range(repetitions):
                cards.append(Card(card_type, action))



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
    movement = []
    tribes_out = []

    pos = [Pos(5, 5), Pos(5, 0), Pos(5, 5)]
    last_direction = -1
    while True:
        i = 0
        movement.append(['|', '|', '|'])
        this_set = []
        while True:
            if i >= 5:
                break
            drawn = cards.pop()
            if drawn.direction != 4:
                this_set.append(4)
            if len(this_set) > 2:
                penelty += 0.1
            if drawn.direction == last_direction:
                penelty -= 0.02
                if drawn.direction == 4:
                    penelty += 0.1
            if drawn.direction % 2 == last_direction % 2 and drawn.direction != 4:
                if drawn.direction != last_direction:
                    penelty += 0.1
            i += 1
            drawn.mark_drawn()
            m = move(pos, drawn, tribes)
            if m[0] == '.':
                if pos[0].x > 0:
                    penelty += 0.025
            if m[1] == '.':
                if pos[1].y < 5:
                    penelty += 0.025
            if m[2] == '.':
                if pos[2].y > 0:
                    penelty += 0.025
            movement.append(m)

            for t in range(3):
                if pos[t].x == pos[t].y == 3:
                    penelty -= 0.5
            penelty += sum([(2 - p.x) ** 2 + (3 - p.y) ** 2 for p in pos]) / 20

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
            elif drawn == Cards.TRIBE:
                removed.append(drawn)
                if tribes < 3:
                    tribes += 1
                shuffle(discard)
                cards.extend(discard)
                discard.clear()
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
        tribes_out.append(tribes)
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
    return (tribes_out, ii, tribe_events, repeated_cards, tribes, tribes_half_time, discard_pile_length,
            stats, count(removed, Cards.REMOVE_STOP), movement, penelty / sum(ii), start_cards, pos)


def move(pos, card, tribes):
    ret = ['', '', '']
    if card.tribe_affected is None:
        tribes_affected = range(tribes)
    else:
        tribes_affected = [card.tribe_affected - 1]
        if tribes_affected[0] > tribes:
            return ret
    for tribe in tribes_affected:
        if card.direction == 0 and pos[tribe].x > 0:
            pos[tribe].x -= 1
            ret[tribe] = '←'
        elif card.direction == 2 and pos[tribe].x < 5:
            pos[tribe].x += 1
            ret[tribe] = '→'
        elif card.direction == 1 and pos[tribe].y > 0:
            pos[tribe].y -= 1
            ret[tribe] = '↓'
        elif card.direction == 3 and pos[tribe].y < 5:
            pos[tribe].y += 1
            ret[tribe] = '↑'

        if card.direction == 4 and pos[tribe].x > 0:
            pos[tribe].x -= 2
            ret[tribe] = '←←'
        elif card.direction == 6 and pos[tribe].x < 5:
            pos[tribe].x += 2
            ret[tribe] = '→→'
        elif card.direction == 5 and pos[tribe].y > 0:
            pos[tribe].y -= 2
            ret[tribe] = '↓↓'
        elif card.direction == 7 and pos[tribe].y < 5:
            pos[tribe].y += 2
            ret[tribe] = '↑↑'

        elif card.direction == 8:
            ret[tribe] = '`'
        else:
            ret[tribe] = '.'
        pos[tribe].y = pos[tribe].y if pos[tribe].y <= 5 else 5
        pos[tribe].x = pos[tribe].x if pos[tribe].y <= 5 else 5
        pos[tribe].y = pos[tribe].y if pos[tribe].y >= 0 else 0
        pos[tribe].x = pos[tribe].x if pos[tribe].y >= 0 else 0
    return ret


def draw(best):
    if input():
        return
    ttl.setworldcoordinates(0,0,50,50)
    turtles = [ttl.Turtle() for _ in range(3)]
    turtles[0].color('red')
    turtles[1].color('blue')
    turtles[2].color('green')
    for _ in range(10):
        instructions =  one_game(directions=best)[-4]

        turtles[0].setposition(50, 50)
        turtles[1].setposition(50, 0)
        turtles[2].setposition(50, 50)
        turtles[0].clear()
        turtles[1].clear()
        turtles[2].clear()

        for inst in instructions:
            for tribe, t_inst in enumerate(inst):
                if t_inst == '←':
                    turtles[tribe].setx(turtles[tribe].xcor() - 10)
                elif t_inst == '→':
                    turtles[tribe].setx(turtles[tribe].xcor() + 10)
                elif t_inst == '↓':
                    turtles[tribe].sety(turtles[tribe].ycor() - 10)
                elif t_inst == '↑':
                    turtles[tribe].sety(turtles[tribe].ycor() + 10)
                elif t_inst == '←←':
                    turtles[tribe].setx(turtles[tribe].xcor() - 10)
                elif t_inst == '→→':
                    turtles[tribe].setx(turtles[tribe].xcor() + 10)
                elif t_inst == '↓↓':
                    turtles[tribe].sety(turtles[tribe].ycor() - 10)
                elif t_inst == '↑↑':
                    turtles[tribe].sety(turtles[tribe].ycor() + 10)
                else:
                    assert t_inst in ['|', '`', '.', ''], t_inst
        if input():
            ttl.bye()
            return
    ttl.bye()



def run_and_payoff(directions):
    return directions, - sum([one_game(directions=directions)[-3] for _ in range(100)]) / 100

class Directions:
    def __init__(self, actions, genetical_code=None):
        self.actions = actions
        if genetical_code is not None:
            self.genetical_code = genetical_code
        else:
            self.genetical_code = {}
            for card_type in Cards:
                if card_type != Cards.TRIBE_EVENT:
                    example = [randrange(5) for _ in range(num[card_type])]
                    self.genetical_code[card_type] = [example.count(i) for i in range(actions)]
            for i in range(1, 3 + 1):
                example = [randrange(actions) for _ in range(num[(Cards.TRIBE_EVENT, i)])]
                self.genetical_code[(Cards.TRIBE_EVENT, i)] = [example.count(i) for i in range(actions)]


    def __add__(self, other):
        x_over = randrange(len(self.genetical_code))
        x_under = randrange(len(self.genetical_code))
        if x_under > x_over:
            x_under, x_over = x_over, x_under
        child_code = {a[0]: a[1] if x_under <= i <= x_over else b[1]
                      for i, (a, b) in enumerate(zip(self.genetical_code.items(), other.genetical_code.items()))}

        if random.random() < 0.0005:
            gen = choice(list(child_code.keys()))
            shuffle(child_code[gen])
        if random.random() < 0.001:
            gen = choice(list(child_code.keys()))
            child_code[gen][0:4], child_code[gen][4:8] = child_code[gen][4:8], child_code[gen][0:4]
        if random.random() < 0.001:
            gen = choice(list(child_code.keys()))
            a = randrange(self.actions)
            b = randrange(self.actions)
            child_code[gen][a], child_code[gen][b] = child_code[gen][b], child_code[gen][a]
        return Directions(self.actions, genetical_code=child_code)

def train():
    bests = []
    with Pool() as pool:
        population = [Directions(9) for i in range(1500)]

        for iteration in range(100):
            result = dict(pool.map(run_and_payoff, population))
            best = nlargest(30, result, key=result.get)
            print(iteration, max(result.values()))
            randoms = sample(population, 5)
            population = [a + b for a in best + randoms for b in best + randoms]
            bests.append(max(result.values()))
    best = nlargest(1, result, key=result.get)[0]
    for _ in range(5):
        result = one_game(directions=best)

        print(result[-1], [''.join(z) for z in zip(*result[-4])])
    py.plot([go.Scatter(y=bests)])
    pprint([(card.card_type, card.tribe_affected, card.direction) for card in result[-2]])
    move_tag_stats = defaultdict(lambda: defaultdict(int))
    for card in result[-2]:
        if card.tribe_affected is None:
            move_tag_stats[card.card_type][card.ldirection] += 1
        else:
            move_tag_stats[(card.card_type, card.tribe_affected)][card.ldirection] += 1
    for card_type, stats in move_tag_stats.items():
        print(card_type,
              sum(stats.values()),
              ' '.join('%s: %2.2f' % (k, v / sum(stats.values())) for k, v in stats.items()))
    print()
    for card_type, stats in move_tag_stats.items():
        print(card_type,
              sum(stats.values()),
              dict(stats))
    with open('card_directions.pp', 'wb') as fp:
        pickle.dump(best.genetical_code, fp)
    draw(best)


def main():
    with open('card_directions.pp', 'rb') as fp:
        directions = Directions(5, genetical_code=pickle.load(fp))
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
    tribes_out_list = []
    for i in range(repetitions):

        (tribes_out, ii, tribe_events, repeated_cards, tribes, tribes_half_time, discard_pile_length, stats,
         num_remove_stop, movement, penelty, start_cards, pos) = one_game(directions)
        tribe_attacks_list += tribe_events
        iis.append(ii)
        xis.extend(ii)
        tribes_out_list.append(tribes_out)
        tribes_list.append(tribes)
        tribes_ht_list.append(tribes_half_time)
        repeated_cards_list.extend(repeated_cards)
        discard_pile_length_list.append(discard_pile_length)
        num_tribe_events.append(len(tribe_events))
        num_remove_stop_list.append(num_remove_stop)
        if i < 25:
            fig3.append_trace(go.Bar(y=discard_pile_length), i % 5 + 1, i // 5 + 1)

            fig4.append_trace(go.Bar(y=ii,
                                     x=list(range(9 * 4))), i % 5 + 1, i // 5 + 1)

    hist_start_cards, hist_card_stats = hist(start_cards), card_stats(start_cards)

    fig.append_trace(go.Histogram(x=[str(ta) for ta in tribe_attacks_list], histnorm='probability'), 1, 1)
    fig.append_trace(go.Histogram(x=xis, histnorm='probability'), 1, 2)
    fig.append_trace(go.Histogram(x=tribes_list, histnorm='probability'), 1, 3)
    fig.append_trace(go.Histogram(x=tribes_ht_list, histnorm='probability'), 2, 3)
    fig.append_trace(go.Histogram(x=repeated_cards, histnorm='probability'), 2, 2)
    fig.append_trace(go.Histogram(x=repeated_cards_list, histnorm='probability'), 3, 2)
    fig.append_trace(go.Histogram(x=num_tribe_events, histnorm='probability'), 3, 3)

    fig.append_trace(go.Bar(y=[np.mean(ii) for ii in list(zip(*iis))],
                            error_y=dict(
                            type='data',
                            array=[np.std(ii) for ii in list(zip(*iis))]),
                            visible=True),
                     2, 1)


    summary_fig2.append_trace(go.Bar(x=list(hist_start_cards.values()), y=list(hist_start_cards.keys()), orientation = 'h'), 1, 1)
    summary_fig2.append_trace(go.Bar(x=list(hist_card_stats.values()), y=list(hist_card_stats.keys()), orientation = 'h'), 1, 2)
    summary_fig2.append_trace(go.Bar(y=[np.median(to) for to in zip(*tribes_out_list)]), 1, 3)
    summary_fig2.append_trace(go.Bar(y=[to.count(0) / repetitions for to in zip(*tribes_out_list)]), 2, 1)
    summary_fig2.append_trace(go.Bar(y=[to.count(3) / repetitions for to in zip(*tribes_out_list)]), 2, 2)
    for h in range(1, 6):
        fig2.append_trace(go.Bar(y=[Counter(ii)[h] / repetitions for ii in list(zip(*iis))]), 1, h)
    py.plot(fig)
    py.plot(summary_fig2, filename='summary_fig2.html')
    py.plot(fig2, filename='f2.html')
    py.plot(fig3, filename='discard_deck.html')
    py.plot(fig4, filename='cards_drawn.html')
    pprint(dict(stats))
    print('REMOVE_STOP cards drawn on average', np.mean(num_remove_stop_list), np.std(num_remove_stop_list))
    print('cards drawn on average: %f' % (sum(xis) / repetitions))

if __name__ == '__main__':
    train()
    main()
