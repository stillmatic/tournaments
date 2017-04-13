"""Tournament modelling class and functions.

Chris Hua / chua@wharton.upenn.edu
"""

import numpy as np
import random
import networkx as nx
import pandas as pd
import seaborn as sns
from functools import lru_cache
from math import floor
from pandas_ply import install_ply, X
import feather
install_ply(pd)


class Tournament:
    """Describes a tournament.

    One key function -- run: Run one round of a tournament.
    Simulations should be done with 'simulation' class.
    """

    def __init__(self, n_teams, n_rounds, **kwargs):
        """Initiate a new tournament."""
        self.n_teams = n_teams
        self.n_rounds = n_rounds
        self.seed = kwargs.get('seed', int(floor(random.uniform(0, 1000))))
        self.dist = kwargs.get('dist', 'lognormal')
        self.dist_params = kwargs.get('dist_params', None)
        self.strengths = self._generate_teams()
        self.wins = [0] * self.n_teams
        self.alpha = kwargs.get('alpha', 3500)
        self.beta = kwargs.get('beta', 35)

    def run(self, summary=False):
        """Run a tournament once."""
        # add wins for first round
        self.wins = [0] * self.n_teams
        self.g = self._generate_base_graph()
        np.random.seed(None)
        for a, b in self._rand_pairing():
            self._add_match(a, b)

        # run rounds
        for i in range(self.n_rounds - 1):
            self._run_round()

        df = pd.DataFrame(list(
            zip(self.strengths, self.wins)), columns=['strength', 'wins'])
        self.results = df
        return(df)

    def _run_round(self):
        """Try each pairing and record results."""
        for a, b in self._next_pairing():
            if(a > b):  # for bidrectionality purposes
                # if(self.g.edge[b][a]['weight'] < 0):
                    # print("ERROR!", self.g.edge[a][b]['weight'])
                self._add_match(b, a)
        self.rebalance()

    def _generate_teams(self):
        """Generate teams from given distribution and parameters."""
        np.random.seed(self.seed)
        # strengths = self.dist_fun(size=self.n_teams)
        if self.dist_params is not None:
            check_param = True
        else:
            check_param = False
        if(self.dist == "exp"):
            def_val = 1.0
            if check_param:
                sc = self.dist_params['scale'] or def_val
            else:
                sc = def_val
            strengths = np.random.exponential(scale=sc, size=self.n_teams)
        elif(self.dist == "unif"):
            if check_param:
                l = self.dist_params['low'] or 0.0
                h = self.dist_params['high'] or 1.0
            else:
                l = 0.0
                h = 1.0
            strengths = np.random.uniform(l, h, size=self.n_teams)
        elif(self.dist == "lognorm"):
            if not check_param:
                mu = 0.0
                sigma = 1.0
            else:
                mu = self.dist_params['mean'] or 0.0
                sigma = self.dist_params['sigma'] or 1.0
            strengths = np.random.lognormal(mu, sigma, size=self.n_teams)
        elif(self.dist == "beta"):
            if not check_param:
                alpha = 2.0
                beta = 5.0
            else:
                alpha = self.dist_params['shape1'] or 2.0
                beta = self.dist_params['shape2'] or 5.0
            strengths = np.random.beta(alpha, beta, size=self.n_teams)
        elif(self.dist == "gamma"):
            if not check_param:
                p1 = 2.0
                p2 = 1.0
            else:
                p1 = self.dist_params['shape'] or 2.0
                p2 = self.dist_params['scale'] or 1.0
            strengths = np.random.gamma(p1, p2, size=self.n_teams)
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
        # self.g.remove_edge(a, b)
        self.g.add_edge(a, b, weight=-10000)
        if(self._win(a, b)):
            self.wins[a] += 1
        else:
            self.wins[b] += 1

    def _next_pairing(self):
        """Find maximum weight perfect matching for given state.

        Returns list of teams and their assignment
        """
        match = nx.max_weight_matching(self.g, True).values()
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
        diff = abs(x - y)
        if(diff > 1):
            return(1)
        else:
            z = self.alpha - (self.beta * diff)**2
            return(int(z))

    def rebalance(self):
        """Rebalance the graph after a round."""
        for (u, v, d) in self.g.edges(data=True):
            if(self.g.edge[u][v]['weight'] > 0):
                cost = self.cost_function(self.wins[u], self.wins[v])
                self.g.edge[u][v]['weight'] = cost

    def print_edges(self):
        """Function to print edges.

        For debug purposes.
        Keyword arguments:
        g -- a graph
        """
        for (u, v, d) in self.g.edges(data=True):
            print(u, v, d)

    def _sum_edges(self):
        """For debug purposes."""
        s = 0
        for (u, v, d) in self.g.edges(data=True):
            s += self.g.edge[u][v]['weight']

    def _top_winner(self):
        res = self.results
        res.wins[which(res.strength == max(res.strength))] = self.n_rounds

    def _summarize(self):
        res = self.results
        # champ should be undefeated
        champ = which(res.strength == max(res.strength))
        found_champion = (res.wins[champ] == self.n_rounds)


class Simulation:
    """Describes a simulation of tournaments."""

    def __init__(self, n_teams, n_rounds, n_sim, **kwargs):
        """Initiate a tournament simulation."""
        self.n_sim = n_sim
        self.n_rounds = n_rounds
        self.dist = kwargs.get('dist', 'lognormal')
        self.tourney = Tournament(n_teams, n_rounds, **kwargs)
        self.df = pd.DataFrame()

    def simulate(self):
        """Run simulation."""
        for i in range(self.n_sim):
            df2 = pd.DataFrame(data=self.tourney.run())
            self.df = self.df.append(df2)

    def get_results(self):
        """Return results of simulation."""
        return(self.df)

    def feather_results(self, path=None):
        """Export results to disk via feather."""
        import time
        now = time.strftime("%d_%m_%Y_%H_%M_%S")
        path = path or "%s.feather" % now
        feather.write_dataframe(self.df, path)

    def plot_distribution(self, **kwargs):
        """Plot distribution of wins.

        Runs simulation if not done yet.
        """
        from matplotlib import rcParams
        rcParams['patch.force_edgecolor'] = True
        rcParams['patch.facecolor'] = 'b'
        if self.df.empty:
            self.simulate()

        self.df.wins = self.df.wins.astype(int)
        graph = sns.distplot(
            self.df.wins, bins=np.arange(0, self.n_rounds + 1), **kwargs)
        title_string = "Distribution of wins: %s" % self.dist
        sns.plt.title(title_string)
        # graph.set_ylim(0, 1)
        graph.set_xlim(0, self.n_rounds)
        return(graph)

    def _get_aggregate(self):
        res_summ = (
            self.df
            .groupby('strength')
            .ply_select(
                strength=X.strength.mean(),
                avg_wins=X.wins.mean(),
                avg_break=X.wins.mean() > self.n_rounds - 1
            ))
        return(res_summ)

    def plot_strengths(self, **kwargs):
        """Plot wins by team strength.

        Runs simulation if not done yet
        """
        if self.df.empty:
            self.simulate()

        res_summ = self._get_aggregate()
        graph = sns.lmplot(
            x='strength', y='avg_wins', data=res_summ, fit_reg=False)
        title_string = "Wins by team strength"
        sns.plt.title(title_string)
        return(graph)


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


def which():
    """Find index of value, similarly to which in R."""
    lambda lst: list(np.where(lst)[0])
