
# Introduction

An important goal of tournaments is to find an overall winner, but it is often important to find the top-$k$ contestants as well. A simple example of where this is useful is a preliminary tournament used for seeding purposes, prior to an elimination tournament. In some cases, knowing an exact ranking within this top subgroup is important, such as when a tournament will pay out monetary rewards based on finishing place; in other cases, knowing the exact ranking is not as important. 

We present the case of American high school policy debate, in which teams compete in "regular-season" tournaments throughout the year in order to win 'bids' to the Tournament of Championships, the de facto culminating championship. Each round has two teams of two debaters, one "affirmative" (aff) and one "negative" (neg), and a judge. The affirmative side argues a policy-based plan which affirms that year's debate resolution, and the negative argues against the affirmative. For example, the 2012-13 resolution was "The United States federal government should substantially increase its transportation infrastructure investment in the United States."

All tournaments are structured in two parts, with a preliminary Swiss-system tournament and then a knockout/single-elimination tournament. Within the preliminary tournament, he first two rounds are randomly paired, and subsequent rounds are power-matched, which means teams are paired with teams that have similar records (i.e. similar number of wins). These are subject to the constraints that teams cannot debate teams from the same school, and they cannot debate teams who they have been paired with in earlier rounds.

The ultimate goal of "regular season" tournaments is to earn a bid to the "championship" tournament, the Tournament of Champions. These are allocated to tournaments roughly on the basis of tournament size and strength; the effect is that tournaments with more bids attract stronger teams. The bids are set up so that teams who make it to a given round of the tournament get the bid, e.g. octafinals means 16 bids, semifinals is 4 bids, etc. A perverse result of this bid system is that rounds after the bid round, containing the best teams, are treated as unimportant - teams routinely run less serious arguments or simply forfeit rounds- but the bid round and rounds before have enormous strategic investment. 

This setup leads us to consider the efficacy of the Swiss-tournament design, in this instance.

# Problem Statement

Does the Swiss-style tournament structure effectively find top-$k$ teams?

# Literature Review

Previous research has been done into creating tournament structures, and considering the various desirable aspects to optimize for.

Part of the simulation process involves finding pairings, which are directly analogous to a matching, which is a set of $n$ disjoint pairs of participants. 

In particular, the Swiss tournament structure is considered in [**Olafsson 1990**]. Ólafsson considers the Swiss tournament structure and various chess-specific considerations; however, he focuses on an algorithm to create pairings which fulfill chess's requirements. He presents a method using maximum weight perfect matching to perform the pairing matching. Under this method, we employ a graph structure to represent the teams (nodes) and the possible pairings (edges). The graph is initialized as a complete graph with equal weights; that is, all possible pairings are equally desirable, which fits the structure of a random initial pairing. The graph is complete because any team *could* play each other, and we represent desirability via edge weights. At the conclusion of each round, the edges are reweighted to fit the desirability of the pairing. These weights are functions of various competitive factors, including the difference in wins, how many rounds they have played on white/black, whether the pairing has already occured, and others. The general idea is that a higher weight represents a higher preference. Then, the maximum weight perfect matching algorithm finds a matching among the possible pairs.

The weighted perfect matching algorithm is a well-studied problem in computer science and graph theory. The first polynomial time algorithm for the problem was found by [**Edmonds 1965**], known as Edmond's blossom algorithm, and improved on by numerous others, including [**Cooke and Rowe 1999**] and most recently by [**Kolmogorov 2009**]. The implementation used in this paper follows most directly [**Galil**], which runs with time complexity $O(nm \log n)$, where $n$ is the number of nodes and $m$ is the number of edges in the graph. Exact details on the method can be found in any of these papers, or from examining the source code of the open-source programs used for simulation.

In a similar vein, [**Kujansuu et al 1999**] present a method for pairing players, as an extension of the stable roommates problem. For further reference, the canonical reference for the stable roommates problem is [**Gusfield and Irving, 1989**]. In the stable roommates problem, each "roommate" creates a preference ranking of the others (full ranking is assumed). Then, the matching is stable if there are no potential roommates $i$ and $j$ who prefer each other to their matched roommate. In the tournament context, after each round, each team has a preference list constructed for them of the teams available to play. The weights can be assigned in a similar manner to Olafsson and have a relatively analogous meaning, representing how preferable a possible pairing between two teams is.

To my knowledge, very few other studies have considered the effectiveness of the Swiss tournament structure.

Research by [**Glickman and Jensen**] has considered alternative tournament formulations from a more theoretical basis. Specifically, Glickman and Jensen present a tournament structure where rounds are matched by maximizing expected Kullback-Leibler distance, a measure of difference between distributions. The pairings are picked such that they maximize the expected Kullback-Leibler distance between the prior and posterior distributions of $\theta$, the distribution of player strengths. This model is heavily influenced by Bayesian optimal design. Notably, Swiss tournaments out-perform their model for small numbers of rounds. 

[**Hanes**] researched the effect of power matching in policy debate tournaments, comparing the outcomes from the win rankings with the speaker points assigned to teams. He finds a disparity between the two rankings, and argues that we should prefer the results given by speaker point rankings instead, or at minimum a combination of wins and speaker points. It is worth noting that he considers the implications across a full season, while we focus on the effects on a tournament level.


# Solution Approach/Main Results

Tournaments are repeated sets of paired comparisons, and we employ what is known as the Bradley-Terry model to understand the comparisons [**CITE**]. It is given by:

$$\Pr(Y_{i,j} = 1) = \frac{\theta_i}{\theta_i + \theta_j}$$

Here, $Y_{i,j}$ is an indicator for the outcome of the pairwise comparison between competitors $i$ and $j$, and $\theta_i$ and $\theta_j$ represent the underlying strength of competitors $i$ and $j$. These $\theta$ values are relatively unconstrained, though under the traditional B-T assumptions they are positive numbers. 

The Bradley-Terry model belongs to a family of models known as linear paired comparison models, where win probabilities are only affected by player strengths in terms of the delta between the pairs.

For simplicity, in our simulations, we drew the team strengths from probability distributions. The core distribution we use is the beta distribution. The PDF of the beta distribution is 

$${\displaystyle {\frac {x^{\alpha -1}(1-x)^{\beta -1}}{\mathrm {B} (\alpha ,\beta )}}\!}$$

where: ${\displaystyle \mathrm {B} (\alpha ,\beta )={\frac {\Gamma (\alpha )\Gamma (\beta )}{\Gamma (\alpha +\beta )}}}$

See the appendix for other distributions which our code and model supports.

## Tournament simulation procedure

As described above, teams compete in 6 or 7 rounds, with the first two rounds randomly paired and the following rounds power-matched. We implement this procedure using an adaption of the technique presented in [**CITE Olafsson 1990**]. 

Our process is as follows:

1. Team strengths are generated according to the given distribution, parameters, and random seed. Teams are represented as nodes in a symmetric directed graph, and edges are possible pairings.
2. A first round is paired randomly.
3. Results for the round are simulated and recorded, following the Bradley-Terry model for pairwise comparisons.
4. All rounds after the second are paired using maximum weight perfect matching. 
5. After the second round, we reweight the graph.

The maximum weight perfect matching procedure is an ingenious method to guarantee good pairings. We have several desirable characteristics in pairings: first, that teams which play each other should not meet in further rounds, and that teams should prefer teams which have the same win total, but if necessary, play teams with a difference of 1 win. We can represent these characteristics within our graph model of a tournament by assigning weights to edges which reflect the desirability of the pairing. Our exact formula for weighting a possible pairing between teams $i$ and $j$ is as follows:

$$W_{i,j} = \alpha - (\beta * \lvert s_i - s_j \rvert)^2 $$

Here, $\alpha$ and $\beta$ are constants which can be thought of as a location and scale parameter, respectively. We also present a delta value, $\lvert s_i - s_j \rvert$, which is the absolute value of the the difference between the two teams' wins. To make computation easier, we avoid negative weights by first checking the win delta and setting the pairing to a weight of 1 if the difference is greater than 1 win. When a particular pairing is done, we assign the pairing a weight of 0. This method lends itself to a maximum weight method because the larger a weight is on a particular pairing the more desirable it is in a pairing.

Weights are rebalanced at the end of each round, i.e. when all pairings are simulated. We then develop a pairing for the next round, which is represented as a maximum weight perfect matching. We use Edmond's blossom algorithm [[**CITE**]], as implemented in Python by [**CITE NetworkX**]. For more precise details of the algorithm, see for example [**CITE Galil**]. All edges that have not been picked are rebalanced, since even if a pairing is undesirable after $k$ rounds, it could be desirable for the $k+1$ round. 

Note that the algorithm is used to find pairings for round 2, since the round is intended to be randomly paired. At this point the graph is initialized with equal weights for every pairing except those which have occured, which have a 0 weighting. Then, since we have no other constraints, the maximum weight perfect matching returns an acceptable pairing which conveniently guarantees no repeat matches. 

We consider several different tournament configurations, and run 500 simulations for each of them.

1. Small tournament: 32 teams with 5 rounds. This setup is picked because $2^5 = 32$. 
1. Medium tournament: 68 teams with 6 rounds. Note that $\log_2 68 = 6.09$.
2. Large tournament: 114 teams with 7 rounds. Note that $\log_2 114 = 6.83$.
3. Very large tournament: 208 teams with 6 rounds. Note that $\log_2 208 = 7.70$.

These tournaments are, in order, modeled after a local tournament, the NDCA tournament, the Blake tournament, and the Berkeley tournament. We add the log base 2 of the number of teams because with fewer than $log_2 n$, it is possible to have multiple teams with perfect records.

## Comparisons

We consider alternative tournament designs, focused around the same goal as the original tournament.

* Totally random pairings.

## Reported statistics

* percent of top-k teams correctly selected
* whether 'winner wins'
* squared difference in rank
* confidence intervals of team winrate

# Validation

In addition to individually scraped tournaments, we also have 2 yearlong datasets, covering multiple tournaments in the 2009-2010 and 2010-2011 seasons. Using these datasets and their final results, we can estimate Bradley-Terry parameters for the teams participating in those tournaments. We can then rerun our experiments using these empirically determined parameters instead. 

Our MLE estimation is done using the \textbf{\textsf{R}} language, in particular, using the \textbf{\textsf{BradleyTerryScalable}} package [**CITE Firth and Kaye 2017**]. This package follows the procedure laid out in [**Caron and Doucet 2012**] for maximum likelihood estimation of Bradley-Terry parameters when Ford's assumption does not hold. Ford's assumption is: in every possible partition of players into two non-empty subsets, some individual in the second set beats some individual in the first set at least once [**Ford 1957**]. Our datasets are very sparse and cover a wide range of teams, meaning that Ford's assumption does not hold; in particular, this means that the more traditional MLE estimation methods of minorization-maximization [**Hunter 2004**] and Iterative-Luce Spectral Ranking [**Maystre and Grossglauser 2015**] cannot be used.

## 2009-2010 data

This dataset consists of 13310 debated rounds by 1424 teams. There are 3 connected components [**??**] 

**Actually do this lol**

We present a measure of loss that is centered on the number of top-$k$ teams which are not selected. We also consider if the top-ranked team finishes the tournament as the first ranked team.

# Discussion

One particular consideration unique to debate is that rounds are adjudicated by judges, who are human and have human tendencies. In contrast to games such as chess where winners are well-defined and easily verifiable, having variation in outcome decisions makes it desirable to have multiple judges (usually 3) on a panel. Staffing limitations make this difficult to achieve for all but elimination rounds in most tournaments (the college debate championship has 3 judges per round in preliminary rounds, but this is the exception). 

TODO:

* speaker points
* different models instead of Bradley Terry
* better incorporation of priors

# Conclusion

[...]




# Appendix

* define: speaker points
* other distributions
* link to code, etc

# papers

* https://papers.nips.cc/paper/3879-statistical-consistency-of-top-k-ranking.pdf
* Bradley Terry 1952	
* http://www.jstor.org/stable/2582935?seq=1#page_scan_tab_contents
* Edmonds, Jack (1965). "Paths, trees, and flowers". Canad. J. Math. 17: 449–467. doi:10.4153/CJM-1965-045-4.
* “Efficient Algorithms for Finding Maximum Matching in Graphs”, Zvi Galil, ACM Computing Surveys, 1986.
* https://networkx.github.io/
* http://emis.ams.org/journals/DM/v71/art3.pdf - Kujansuu
* Gusfield, D., Irving, R. W., The Stable Marriage Problem. Structure and
Algorithms, The MIT Press, 1989
* http://art-of-logic.blogspot.com/2015/07/study-of-speaker-points-and-power.html - Hanes
* http://www.glicko.net/research/gj.pdf - glickman
* http://pubsonline.informs.org/doi/pdf/10.1287/ijoc.11.2.138 - Cook and Rowe
* https://link.springer.com/article/10.1007%2Fs12532-009-0002-8?LI=true - Kolmogorov
* https://github.com/EllaKaye/BradleyTerryScalable
* https://cran.r-project.org/web/packages/BradleyTerry2/vignettes/BradleyTerry.pdf
* Caron, F. and Doucet, A. (2012) Efficient Bayesian Inference for Generalized Bradley-Terry Models. Journal of Computational and Graphical Statistics, 21(1), 174-196.
* Hunter, D. R. (2004) MM Algorithms for Generalized Bradley-Terry Models. The Annals of Statistics, 32(1), 384-406.
* Maystre, L. and Grossglauser, M. (2015) Fast and accurate inference of Plackett-Luce models. In Advances in Neural Information Processing Systems 28 (NIPS 28).
* Ford, L. R. (1957) Solution of a Ranking Problem from Binary Comparisons. The American Mathematical Monthly, 64(8, Part 2), 28-33.

