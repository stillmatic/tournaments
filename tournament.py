"""Tournament modelling functions.

Chris Hua / chua@wharton.upenn.edu
"""

import random

from itertools import zip_longest

import networkx as nx

import numpy as np

import pandas as pd

import seaborn as sns


def print_edges(g):
    """Function to print edges.

    For debug purposes.
    Keyword arguments:
    g -- a graph
    """
    for (u, v, d) in g.edges(data=True):
        print(u, v, d)


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    Taken from itertools recipes:
    https://docs.python.org/2/library/itertools.html#recipes
    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    """
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def rand_pairing(teams, s=None):
    """Generate random pairing of teams.

    Used for first round of pairing. Subsequent rounds are paired via MW-PM.
    """
    random.seed(s)
    shuffled = random.sample(teams, len(teams))
    return grouper(shuffled, 2)


def win_prob(a, b, strengths):
    """Win probability for a team, per BTL model.

    Keyword arguments:
    a -- number of Team A (returns prob A wins)
    b -- number of Team B
    strengths - vector
    """
    return(strengths[a] / (strengths[a] + strengths[b]))


def win(a, b, strengths):
    """Whether team A wins a round, given opponent's strength.

    True if A wins vs B, given their probability of winning.
    Uses a random roll to decide.
    Keyword arguments:
    a -- number of Team A
    b -- number of Team B
    strengths - vector of team strengths
    """
    roll = np.random.uniform()
    return roll < win_prob(a, b, strengths)


def add_match(a, b, wins, g, strengths):
    """Add a match and its result to our data structures.

    Adds the match to the graph, rolls to find winner, increments win counter.
    Keyword arguments:
    a -- number of Team A
    b -- number of Team B
    strengths - vector of team strengths
    """
    if(a > b):
        g.remove_edge(b, a)
    else:
        g.remove_edge(a, b)
    if(win(a, b, strengths)):
        wins[a] += 1
    else:
        wins[b] += 1


def next_pairing(n_teams, g):
    """Find maximum weight perfect matching for given state.

    Returns list of teams and their assignment
    """
    pairs = list(zip(range(n_teams), nx.max_weight_matching(g).values()))
    return(pairs)


def cost_function(x, y, alpha=2500, beta=35):
    r"""Cost or weight mechanism for edges.

    If a possible pairing has a difference of more than 1 win,
    then we weight it very low.
    Otherwise, we return $\alpha - (\beta * \abs(x - y))^2$.
    Keyword arguments:
    x - wins for team A
    y - wins for team B
    alpha - scale parameter
    beta - dispersion parameter
    """
    diff = x - y
    if(diff > 1):
        return 1
    z = alpha - (beta * abs(diff))**2
    return z


def rebalance(g, wins, beta=10, alpha=250):
    """Rebalance the graph after a round."""
    for (u, v, d) in g.edges(data=True):
        if(g.edge[u][v]['weight'] > 0):
            g.edge[u][v]['weight'] = (
                cost_function(wins[u], wins[v], alpha, beta))


def run_round(n_teams, g, wins, strengths):
    """For given parameters, run a round."""
    for a, b in next_pairing(n_teams, g):
        if(a > b):
            add_match(b, a, wins, g, strengths)

    rebalance(g, wins)


def run_tournament(n_teams=48, n_rounds=6, seed=None, dist="lognorm"):
    """Run the complete tournament.

    Keyword arguments
    n_teams -- number of teams in tournament
    n_rounds -- number of rounds in tournament
    seed -- seed to use in generating strengths *only*.
    """
    # initiate complete graph
    g = nx.complete_graph(n_teams)

    # initiate teams, strengths, wins
    teams = list(range(n_teams))
    np.random.seed(seed)  # reproducible strength
    if(dist == "exp"):
        strengths = np.random.exponential(size=n_teams)
    elif(dist == "uniform"):
        strengths = np.random.exponential(size=n_teams)
    else:
        print("unknown distribution provided, using lognormal")
        strengths = np.random.lognormal(size=n_teams)
    wins = [0] * n_teams

    # initiate edges
    for (u, v, d) in g.edges(data=True):
        g.add_edge(u, v, weight=1)

    # add wins for first round
    np.random.seed(None)
    for a, b in rand_pairing(teams, seed):
        add_match(a, b, wins, g, strengths)

    for i in range(n_rounds - 1):
        # reset edges
        for (u, v, d) in g.edges(data=True):
            g.add_edge(u, v, weight=1)
        run_round(n_teams, g, wins, strengths)

    df = pd.DataFrame(list(zip(strengths, wins)), columns=['strength', 'wins'])
    return(df)


def simulate_tournament(n_teams, n_rounds, seed, n_simul=100):
    """Simulate tournament for given parameters.

    keyword arguments:
    n_teams -- number of teams
    n_rounds -- number of rounds
    seed -- seed to use to generate team strengths
    n_simul -- number of simulations to run
    """
    df = pd.DataFrame()
    for i in range(n_simul):
        # print(i)
        df = df.append(pd.DataFrame(
            data=run_tournament(n_teams, n_rounds, seed)))
    return df


def plot_results(n_teams=48, n_rounds=6, seed=None):
    """Plot results of a round."""
    lm = sns.lmplot(x="strength", y="wins", data=run_tournament(
        n_teams, n_rounds, seed), palette="muted")
    axes = lm.axes
    axes[0, 0].set_ylim(0, 6)
    axes[0, 0].set_xlim(0, 1)
    sns.plt.title("Average wins by team strength")
    lm.set_xlabels("True Team Strength")
    lm.set_ylabels("Average Wins")
