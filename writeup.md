---
title: "The Swiss Tournament Model"
author: 
- name: Chris Hua
  affiliation: "Wharton School, University of Pennsylvania"
# - name: Linda Zhao 
#   affiliation: "Professor of Statistics, Wharton School, University of Pennsylvania"
date: "14 April 2017"
output:
  pdf_document: 
    keep_tex: yes
    latex_engine: xelatex
    template: ~/code/thesis/writeup/templates/latex-ms.tex
subtitle: "CIS 700-04: Machine Learning and Econometrics"
fontfamily: mathpazo
bibliography: thesis.bib
geometry: margin=1in
# toc: true
spacing: double
thanks: "Contact: chua@wharton.upenn.edu"
# abstract: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi rhoncus est metus, porttitor scelerisque nisi tincidunt at. Fusce pretium mi nibh, pulvinar hendrerit turpis scelerisque nec. Etiam vitae auctor erat, eget molestie massa. Morbi magna dolor, tincidunt quis iaculis et, suscipit nec leo. Aenean et lectus lorem. Nullam suscipit eros et mi eleifend, id eleifend enim ullamcorper. Aenean molestie vulputate urna, non aliquet mi pellentesque eget."
# keywords: "performance persistence, baseball, sports analytics"
fontsize: 11pt
header-includes:
  - \usepackage{amsmath}
---
```{r setup, include=FALSE}
library(dplyr)
knitr::opts_chunk$set(echo = FALSE)
```

# Introduction

An important goal of tournaments is to find an overall winner, but it is often important to find the top-$k$ contestants as well. A simple example of where this is useful is a preliminary tournament used for seeding purposes, prior to an elimination tournament. In some cases, knowing an exact ranking within this top subgroup is important, such as when a tournament will pay out monetary rewards based on finishing place; in other cases, knowing the exact ranking is not as important. 

We present the case of American high school policy debate, in which teams compete in 'regular-season' tournaments throughout the year in order to win 'bids' to the Tournament of Championships, the de facto culminating championship. Each round has two teams of two debaters, one "affirmative" (aff) and one "negative" (neg), and a judge. The affirmative side argues a policy-based plan which affirms that year's debate resolution, and the negative argues against the affirmative. For example, the 2012-13 resolution was "The United States federal government should substantially increase its transportation infrastructure investment in the United States."

All tournaments are structured in two parts, with a preliminary Swiss-system tournament and then a knockout/single-elimination tournament. Within the preliminary tournament, he first two rounds are randomly paired, and subsequent rounds are power-matched, which means teams are paired with teams that have similar records (i.e. similar number of wins). These are subject to the constraints that teams cannot debate teams from the same school, and they cannot debate teams who they have been paired with in earlier rounds.

The ultimate goal of "regular season" tournaments is to earn a bid to the "championship" tournament, the Tournament of Champions. These are allocated to tournaments roughly on the basis of tournament size and strength; the effect is that tournaments with more bids attract stronger teams. The bids are set up so that teams who make it to a given round of the tournament get the bid, e.g. octafinals means 16 bids, semifinals is 4 bids, etc. A perverse result of this bid system is that rounds after the bid round are treated as unimportant - teams routinely forfeit rounds or run less serious arguments - but the bid round and rounds before have enormous strategic investment. 

A previous study of the Swiss-style tournament, and specifically its power-matching procedure, claimed that ranks based on team winrates did not match ranks based on team speaker points. Speaker points are assigned by judges and intended to reflect a debater's performance within the round, with higher scores better. Variation in the points is to be expected, just as there is variation in if teams beat each other.

This setup leads us to consider the efficacy of the Swiss-tournament design, in this instance.

# Problem Statement

Does the Swiss-style tournament structure effectively find top-$k$ teams?

# Solution Approach/Main Results

Tournaments are repeated sets of paired comparisons, and we employ what is known as the Bradley-Terry model to understand the comparisons [**CITE**]. It is given by:

$$\Pr(Y_{i,j} = 1) = \frac{\theta_i}{\theta_i + \theta_j}$$

Here, $Y_{i,j}$ is an indicator for the outcome of the pairwise comparison between competitors $i$ and $j$, and $\theta_i$ and $\theta_j$ represent the underlying strength of competitors $i$ and $j$. These $\theta$ values are relatively unconstrained, though under the traditional B-T assumptions they are positive numbers.

[**MLE ESTIMATION??**]

For simplicity, in our simulations, we drew the team strengths from probability distributions. The core distribution we use is the beta distribution. The PDF of the beta distribution is 

$${\displaystyle {\frac {x^{\alpha -1}(1-x)^{\beta -1}}{\mathrm {B} (\alpha ,\beta )}}\!}$$

where: ${\displaystyle \mathrm {B} (\alpha ,\beta )={\frac {\Gamma (\alpha )\Gamma (\beta )}{\Gamma (\alpha +\beta )}}}$

See the appendix for other distributions which our code and model supports.

## Tournament simulation procedure

As described above, teams compete in 6 or 7 rounds, with the first two rounds randomly paired and the following rounds power-matched. We implement this procedure using an adaption of the technique presented in [**Olaffson 1990**]. 

Our process is as follows:

1. Team strengths are generated according to the given distribution, parameters, and random seed. Teams are represented as nodes in a symmetric directed graph, and edges are possible pairings.
2. A first round is paired randomly.
3. Results for the round are simulated and recorded, following the Bradley-Terry model for pairwise comparisons.
4. All rounds after the second are paired using maximum weight perfect matching. 
5. After the second round, we reweight the graph.

The maximum weight perfect matching procedure is an ingenious method to guarantee good pairings. We have several desirable characteristics in pairings: first, that teams which play each other should not meet in further rounds, and that teams should prefer teams which have the same win total, but if necessary, play teams with a difference of 1 win. We can represent these characteristics within our graph model of a tournament by assigning weights to edges which reflect the desirability of the pairing. Our exact formula for weighting a possible pairing between teams $i$ and $j$ is as follows:

$$W_{i,j} = $\alpha - (\beta * \abs{I}(s_i - s_j))^2 $$

Here, $\alpha$ and $\beta$ are constants which can be thought of as a location and scale parameter, respectively. We also present a delta value, $\abs{I}(s_i - s_j)$, which is the absolute value of the the difference between the two teams' wins. To make computation easier, we avoid negative weights by first checking the win delta and setting the pairing to a weight of 1 if the difference is greater than 1 win. When a particular pairing is done, we assign the pairing a weight of 0. This method lends itself to a maximum weight method because the larger a weight is on a particular pairing the more desirable it is in a pairing.

Weights are rebalanced at the end of each round, i.e. when all pairings are simulated. We then develop a pairing for the next round, which is represented as a maximum weight perfect matching. We use Edmond's blossom algorithm [[**CITE**]], as implemented in Python by [**CITE NetworkX**]. For more precise details of the algorithm, see for example [**CITE Galil**]. All edges that have not been picked are rebalanced, since even if a pairing is undesirable after $k$ rounds, it could be desirable for the $k+1$ round. 

Note that the algorithm is used to find pairings for round 2, since the round is intended to be randomly paired. At this point the graph is initialized with equal weights for every pairing except those which have occured, which have a 0 weighting. Then, since we have no other constraints, the maximum weight perfect matching returns an acceptable pairing which conveniently guarantees no repeat matches. 

## Comparisons

We consider alternative tournament designs, focused around the same goal as the original tournament.

* Totally random pairings.

## Reported statistics

* percent of top-k teams correctly selected
* whether 'winner wins'
* squared difference in rank
* confidence intervals of team winrate

# Validation

We present a measure of loss that is centered on the number of top-$k$ teams which are not selected. We also consider if the top-ranked team finishes the tournament as the first ranked team.

# Conclusion

# Appendix

* define: speaker points
* other distributions
* link to code, etc

# papers

https://papers.nips.cc/paper/3879-statistical-consistency-of-top-k-ranking.pdf
Bradley Terry 1952	
http://www.jstor.org/stable/2582935?seq=1#page_scan_tab_contents
 Edmonds, Jack (1965). "Paths, trees, and flowers". Canad. J. Math. 17: 449–467. doi:10.4153/CJM-1965-045-4.
 “Efficient Algorithms for Finding Maximum Matching in Graphs”, Zvi Galil, ACM Computing Surveys, 1986.
 https://networkx.github.io/