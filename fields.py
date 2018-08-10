from random import gauss


def generate_farm(min_effort_dist_mean, min_effort_std, marginal_effectiveness_mean, marginal_effectiveness_std):
    min_effort = max(0, int(gauss(min_effort_dist_mean / 10 , marginal_effectiveness_std / 100))) * 10
    marg_efectiveness = max(0, gauss(marginal_effectiveness_mean, marginal_effectiveness_std))

    result = []
    effort = min_effort + 10
    harvest = round(2 * (effort - min_effort) * marg_efectiveness, -3) / 2
    print(effort, harvest, 'average payoff per 30: %i' % (harvest / effort * 30))
    result.append((effort * 200, harvest))

    effort = min_effort + 20
    harvest = round(2 * (effort - min_effort) * marg_efectiveness, -3) / 2
    print(effort, harvest, 'average payoff per 30: %i' % (harvest / effort * 30))
    result.append((effort * 200, harvest))

    effort = min_effort + 30
    harvest = round(2 * (25) * marg_efectiveness, -3) / 2
    print(effort, harvest, 'average payoff per 30: %i' % (harvest / effort * 30))
    result.append((effort * 200, harvest))

    return result



if __name__ == '__main__':
    generate_farm(10, 30, 250, 50)
