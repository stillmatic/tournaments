"""Tournament modelling class and functions.

Chris Hua / chua@wharton.upenn.edu
"""

import numpy as np
import random
import networkx as nx
import pandas as pd
from functools import lru_cache


class Tournament:
    """Describes a tournament.

    One key function -- run: Run one round of a tournament.
    Simulations should be done with 'simulation' class.
    """

    def __init__(self, n_teams, n_rounds, **kwargs):
        """Initiate a new tournament."""
        self.n_teams = n_teams
        self.n_rounds = n_rounds
        self.seed = kwargs.get('seed', random.uniform(0, 1000))
        self.dist = kwargs.get('dist', 'lognormal')
        self.strengths = self._generate_teams()
        self.wins = [0] * self.n_teams
        self.alpha = kwargs.get('alpha', 3500)
        self.beta = kwargs.get('beta', 35)

    def run(self):
        """Run a tournament once."""
        # add wins for first round
        self.g = self._generate_base_graph()
        np.random.seed(None)
        for a, b in self._rand_pairing():
            self._add_match(a, b)

        # run rounds
        for i in range(self.n_rounds - 1):
            # self.g = self._generate_base_graph()
            self._run_round()

        df = pd.DataFrame(list(
            zip(self.strengths, self.wins)), columns=['strength', 'wins'])
        return(df)

    def _run_round(self):
        """For given parameters, run a round."""
        for a, b in self._next_pairing():
            # for bidrectionality purposes
            if(a > b):
                self._add_match(b, a)
        self.rebalance()

    def _generate_teams(self):
        np.random.seed(self.seed)
        # strengths = self.dist_fun(size=self.n_teams)
        if(self.dist == "exp"):
            strengths = np.random.exponential(size=self.n_teams)
        elif(self.dist == "unif"):
            strengths = np.random.uniform(size=self.n_teams)
        elif(self.dist == "lognorm"):
            strengths = np.random.lognormal(size=self.n_teams)
        else:
            print("unknown distribution provided, using lognormal")
            strengths = np.random.lognormal(size=self.n_teams)
        return(strengths)

    @lru_cache(maxsize=32)
    def _generate_base_graph(self):
        g = nx.complete_graph(self.n_teams)

        # initiate edges
        for (u, v, d) in g.edges(data=True):
            g.add_edge(u, v, weight=1)
        return(g)

    def _rand_pairing(self):
        """Generate random pairing of teams.

        Used for first round of pairing.
        Subsequent rounds are paired via MW-PM.
        """
        teams = list(range(self.n_teams))
        random.seed(self.seed)
        shuffled = random.sample(teams, len(teams))
        return _grouper(shuffled, 2)

    def _win(self, a, b):
        """Whether team A wins a round, given respective strengths.

        True if A wins vs B, given their probability of winning.
        Uses a random roll to decide.
        Keyword arguments:
        a -- number of Team A
        b -- number of Team B
        strengths - vector of team strengths
        """
        roll = np.random.uniform()
        s_a = self.strengths[a]
        s_b = self.strengths[b]
        prob = s_a / (s_a + s_b)
        return roll < prob

    def _add_match(self, a, b):
        """Add a match and its result to our data structures.

        Adds the match to the graph, rolls to find winner,
        increments win counter.
        Keyword arguments:
        a -- number of Team A
        b -- number of Team B
        strengths - vector of team strengths
        """
        if(a > b):
            self.g.remove_edge(b, a)
        else:
            self.g.remove_edge(a, b)
        if(self._win(a, b)):
            self.wins[a] += 1
        else:
            self.wins[b] += 1

    def _next_pairing(self):
        """Find maximum weight perfect matching for given state.

        Returns list of teams and their assignment
        """
        match = nx.max_weight_matching(self.g).values()
        pairs = list(zip(range(self.n_teams), (match)))
        return(pairs)

    def cost_function(self, x, y):
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
        z = self.alpha - (self.beta * abs(diff))**2
        return z

    def rebalance(self):
        """Rebalance the graph after a round."""
        for (u, v, d) in self.g.edges(data=True):
            cost = self.cost_function(self.wins[u], self.wins[v])
            self.g.edge[u][v]['weight'] = cost

# utility helpers


def _grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    Taken from itertools recipes:
    https://docs.python.org/2/library/itertools.html#recipes
    grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    """
    from itertools import zip_longest
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
