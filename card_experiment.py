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

num_min = {Cards.TRIBE: 7,
           Cards.RESHUFFLE: 0,
           Cards.REMOVE_STOP: 3,
           Cards.ONLY_STOP: 3,
           Cards.OTHER: 9,
           (Cards.TRIBE_EVENT, 1): 7,
           (Cards.TRIBE_EVENT, 2): 5,
           (Cards.TRIBE_EVENT, 3): 4}


num_max = {Cards.TRIBE: 13,
           Cards.RESHUFFLE: 1,
           Cards.REMOVE_STOP: 20,
           Cards.ONLY_STOP: 20,
           Cards.OTHER: 20,
           (Cards.TRIBE_EVENT, 1): 20,
           (Cards.TRIBE_EVENT, 2): 20,
           (Cards.TRIBE_EVENT, 3): 20}

num_start = {Cards.TRIBE: 12,
             Cards.RESHUFFLE: 0,
             Cards.REMOVE_STOP: 10,
             Cards.ONLY_STOP: 10,
             Cards.OTHER: 10,
             (Cards.TRIBE_EVENT, 1): 10,
             (Cards.TRIBE_EVENT, 2): 10,
             (Cards.TRIBE_EVENT, 3): 10}

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return str((self.x, self.y))

    def __hash__(self):
        return self.x + 100 * self.y


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
        return number_to_dicection(self.direction)

    def __eq__(self, card_type):
        return self.card_type is card_type

    def __str__(self):
        return "<%s, %s>" % (str(self.card_type), str(self.tribe_affected))


def number_to_dicection(number):
        if number == 0:
            return '←'
        if number == 1:
            return '↓'
        if number == 2:
            return '→'
        if number == 3:
            return '↑'
        if number == 4:
            return '_←←_'
        if number == 5:
            return '_↓↓_'
        if number == 6:
            return '_→→_'
        if number == 7:
            return '_↑↑_'
        if number == 8:
            return '`'


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


def generate_map(mountains=2, lakes=2, steppe=3, x=5, y=5):
    obstacles = {}
    for _ in range(steppe):
        obstacles[Pos(randrange(x), randrange(y))] = 'steppe'
    for _ in range(mountains):
        obstacles[Pos(randrange(x), randrange(y))] = 'mountain'
    for _ in range(lakes):
        obstacles[Pos(randrange(x), randrange(y))] = 'lakes'
    return obstacles


def one_game(directions=None, figs=False):
    cards = []
    for card_type, gc in directions.genetical_code.items():
        for action, repetitions in enumerate(gc):
            for _ in range(repetitions):
                cards.append(Card(card_type, action))


    obstacles = generate_map()
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

    pos = [Pos(4, 4), Pos(4, 0), Pos(4, 4)]
    last_direction = -1
    while True:
        cards_drawn_this_set = 0
        movement.append(['|', '|', '|'])
        while True:
            drawn = cards.pop()
            if drawn.direction == last_direction:
                penelty -= 0.5
            if drawn.direction % 2 == last_direction % 2 and drawn.direction != 4:
                if drawn.direction != last_direction:
                    penelty += 1
            cards_drawn_this_set += 1
            drawn.mark_drawn()
            m = move(pos, drawn, obstacles, tribes)
            if m[0] == '.':
                penelty += 0.1
            if m[1] == '.':
                penelty += 0.1
            if m[2] == '.':
                penelty += 0.1
            movement.append(m)
            if subround <= 3 * 0.5:
                penelty += 2 * sum([(0 - p.x) ** 2 + (2.5 - p.y) ** 2 for p in pos]) * 2
            elif subround <= 3 * 1.5:
                penelty += 2 * sum([(1 - p.x) ** 2 + (2.5 - p.y) ** 2 for p in pos]) * 1.5
            else:
                penelty += 2 * sum([(2.5 - p.x) ** 2 + (2.5 - p.y) ** 2 for p in pos])
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
            if cards_drawn_this_set >= 5:
                break
        tribes_out.append(tribes)
        subround += 1
        if subround == 3 * 2:
            tribes_half_time = tribes
        # print(cards_drawn_this_set, subround, end=' ')
        ii.append(cards_drawn_this_set)
        lastii.append(cards_drawn_this_set)
        discard_pile_length.append(len(discard))
        if figs and subround % (4 * 3) == 0:
                figs.append_trace(go.Histogram(x=lastii, xbins=xbins(lastii)), pos // 5 + 1, pos % 5 + 1)
                pos += 1
                lastii = []
        if subround == 3 * 4:
            break
        if len(cards) == 0:
            print("no cards,", end='')
            penelty += 0.5
            break

        penelty += (cards_drawn_this_set - 2.25) ** 2 * 2

    repeated_cards = ([card.drawn for card in cards] +
                      [card.drawn for card in discard] +
                      [card.drawn for card in removed])
    return (tribes_out, ii, tribe_events, repeated_cards, tribes, tribes_half_time, discard_pile_length,
            stats, count(removed, Cards.REMOVE_STOP), movement, penelty / sum(ii), start_cards, pos)


def move(pos, card, obstacles, tribes):

    ret = ['', '', '']
    if card.tribe_affected is None:
        tribes_affected = range(tribes)
    else:
        tribes_affected = [card.tribe_affected - 1]
        if tribes_affected[0] > tribes:
            return ret
    for tribe in tribes_affected:
        old_pos = pos[tribe]
        if card.direction == 0 and pos[tribe].x > 0:
            pos[tribe].x -= 1
            ret[tribe] = '←'
        elif card.direction == 2 and pos[tribe].x < 4:
            pos[tribe].x += 1
            ret[tribe] = '→'
        elif card.direction == 1 and pos[tribe].y > 0:
            pos[tribe].y -= 1
            ret[tribe] = '↓'
        elif card.direction == 3 and pos[tribe].y < 4:
            pos[tribe].y += 1
            ret[tribe] = '↑'

        elif card.direction == 4:
            if pos[tribe].x > 1:
                pos[tribe].x -= 2
                ret[tribe] = '_←←_'
            elif pos[tribe].x > 0:
                pos[tribe].x -= 1
                ret[tribe] = '_←←_'
            else:
                ret[tribe] = '.'
        elif card.direction == 6:
            if pos[tribe].x < 3:
                pos[tribe].x += 2
                ret[tribe] = '_→→_'
            elif pos[tribe].x < 4:
                pos[tribe].x += 1
                ret[tribe] = '_→→_'
            else:
                ret[tribe] = '.'
        elif card.direction == 5:
            if pos[tribe].y > 1:
                pos[tribe].y -= 2
                ret[tribe] = '_↓↓_'
            elif pos[tribe].y > 0:
                pos[tribe].y -= 1
                ret[tribe] = '_↓↓_'
            else:
                ret[tribe] = '.'
        elif card.direction == 7:
            if pos[tribe].y < 3:
                pos[tribe].y += 2
                ret[tribe] = '_↑↑_'
            elif pos[tribe].y < 4:
                pos[tribe].y += 1
                ret[tribe] = '_↑↑_'
            else:
                ret[tribe] = '.'

        elif card.direction == 8:
            ret[tribe] = '`'
        else:
            ret[tribe] = '.'

        if pos[tribe] in obstacles:
            pos[tribe] = old_pos
    return ret


def draw(best):
    if input('turtle?'):
        return
    ttl.setworldcoordinates(0, 0, 60, 60)
    turtles = [ttl.Turtle() for _ in range(3)]
    turtles[0].color('red')
    turtles[1].color('blue')
    turtles[2].color('green')
    for _ in range(10):
        instructions =  one_game(directions=best)[-4]

        turtles[0].setposition(50, 50)
        turtles[1].setposition(50, 10)
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
                elif t_inst == '_←←_':
                    turtles[tribe].setx(turtles[tribe].xcor() - 20)
                elif t_inst == '_→→_':
                    turtles[tribe].setx(turtles[tribe].xcor() + 20)
                elif t_inst == '_↓↓_':
                    turtles[tribe].sety(turtles[tribe].ycor() - 20)
                elif t_inst == '_↑↑_':
                    turtles[tribe].sety(turtles[tribe].ycor() + 20)
                else:
                    assert t_inst in ['|', '`', '.', ''], t_inst
                if turtles[tribe].ycor() < 0:
                    turtles[tribe].sety(0)
                if turtles[tribe].xcor() < 0:
                    turtles[tribe].setx(0)
                if turtles[tribe].ycor() > 50:
                    turtles[tribe].sety(50)
                if turtles[tribe].xcor() > 50:
                    turtles[tribe].setx(50)
        if input('turtle?'):
            ttl.bye()
            return
    ttl.bye()



def run_and_payoff(directions):
    random.seed(0)
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
                    example = [randrange(actions) for _ in range(int(num_start[card_type]))]
                    self.genetical_code[card_type] = [example.count(i) for i in range(actions)]
            for i in range(1, 3 + 1):
                example = [randrange(actions)
                           for _ in range(int(num_start[(Cards.TRIBE_EVENT, i)]))]
                self.genetical_code[(Cards.TRIBE_EVENT, i)] = [example.count(i) for i in range(actions)]

    def __add__(self, other):
        child_code = {a[0]: choice([a[1], b[1]])
                      for a, b in zip(self.genetical_code.items(), other.genetical_code.items())}
        if random.random() < 0.02:
            gen = choice(list(child_code.keys()))
            a = randrange(self.actions)
            if child_code[gen][a] > 0:
                child_code[gen][a] -= 1
                if sum(child_code[gen]) < num_min[gen]:
                    b = randrange(self.actions)
                    child_code[gen][b] += 1
            assert sum(child_code[gen]) >= 0
            assert sum(child_code[gen]) >= num_min[gen]

        if random.random() < 0.02:
            gen = choice(list(child_code.keys()))
            a = randrange(self.actions)
            child_code[gen][a] += 1
            if sum(child_code[gen]) > num_max[gen]:
                b = randrange(self.actions)
                if child_code[gen][b] > 0:
                    child_code[gen][b] -= 1
                else:
                    child_code[gen][a] -= 1
            assert sum(child_code[gen]) <= num_max[gen]


        return Directions(self.actions, genetical_code=child_code)


def train(iterations=0):
    bests = []
    with Pool() as pool:
        population = [Directions(9) for i in range(1500)]
        for iteration in range(iterations):
            result = dict(pool.map(run_and_payoff, population))
            best = nlargest(30, result, key=result.get)
            print(iteration, max(result.values()))
            randoms = sample(population, 5)
            population = [a + b for a in best + randoms for b in best + randoms] + best
            bests.append(max(result.values()))
    best = nlargest(1, result, key=result.get)[0]
    for _ in range(5):
        result = one_game(directions=best)

        print(result[-1], [''.join(z) for z in zip(*result[-4])])
    #py.plot([go.Scatter(y=bests)])
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

def load_and_draw():
    with open('card_directions.pp', 'rb') as fp:
        genetical_code = pickle.load(fp)
        directions = Directions(9, genetical_code=genetical_code)
    print_gen_code(genetical_code)
    draw(directions)

def print_gen_code(genetical_code):
    for card_type, code in genetical_code.items():
        print(card_type, end='')
        print([(number_to_dicection(gc), times) for gc, times in enumerate(code)])

def load_and_draw():
    with open('card_directions.pp', 'rb') as fp:
        genetical_code = pickle.load(fp)
        directions = Directions(5, genetical_code=genetical_code)
    print_gen_code(genetical_code)
    draw(directions)


def main():
    with open('card_directions.pp', 'rb') as fp:
        directions = Directions(9, genetical_code=pickle.load(fp))
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
    #load_and_draw()
    train(150)
    main()


# gcloud compute --project "thelanding-1533847703792" scp --zone "us-east1-b" instance-1:/home/davoudtaghawinejad/the_landing/card_directions.pp ~/card_directions.pp
