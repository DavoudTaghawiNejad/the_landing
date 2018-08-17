from random import gauss


def generate_farm(min_effort_dist_mean, min_effort_std, marginal_effectiveness_mean, marginal_effectiveness_std):
    min_effort = gauss(min_effort_dist_mean, min_effort_std)
    marginal_effectiveness = max(0, gauss(marginal_effectiveness_mean, marginal_effectiveness_std))

    result = []
    effort = min_effort
    harvest = xround(marginal_effectiveness * min_effort, 1000)
    result.append((xround(effort, 2), harvest))

    effort = min_effort + 2
    harvest = xround(marginal_effectiveness * min_effort + 2 * marginal_effectiveness * 2, 1000)
    result.append((xround(effort, 2), harvest))

    effort = min_effort + 4
    harvest = xround(marginal_effectiveness * min_effort + 4 * marginal_effectiveness * 1.5, 1000)
    result.append((xround(effort, 2), harvest))

    return result


def xround(x, r):
    return max(r, round(x / r) * r)


if __name__ == '__main__':
    print(generate_farm(8, 3, 2, 0.5))
