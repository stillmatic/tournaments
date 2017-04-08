# Introduction

An important goal of tournaments is to find an overall winner, but it is often important to find the top-$k$ contestants as well. A simple example of where this is useful is a preliminary tournament used for seeding purposes, prior to an elimination tournament. In some cases, knowing an exact ranking within this top subgroup is important, such as when a tournament will pay out monetary rewards based on finishing place; in other cases, knowing the exact ranking is not as important. 

We present the case of American high school policy debate, in which teams compete in 'regular-season' tournaments throughout the year in order to win 'bids' to the Tournament of Championships, the de facto culminating championship. Each round has two teams of two debaters, one "affirmative" (aff) and one "negative" (neg), and a judge. The affirmative side argues a policy-based plan which affirms that year's debate resolution, and the negative argues against the affirmative. For example, the 2012-13 resolution was "The United States federal government should substantially increase its transportation infrastructure investment in the United States."

All tournaments are structured in two parts, with a preliminary Swiss-system tournament and then a knockout/single-elimination tournament. Within the preliminary tournament, he first two rounds are randomly paired, and subsequent rounds are power-matched, which means teams are paired with teams that have similar records (i.e. similar number of wins). These are subject to the constraints that teams cannot debate teams from the same school, and they cannot debate teams who they have been paired with in earlier rounds.

The ultimate goal of "regular season" tournaments is to earn a bid to the "championship" tournament, the Tournament of Champions. These are allocated to tournaments roughly on the basis of tournament size and strength; the effect is that tournaments with more bids attract stronger teams. The bids are set up so that teams who make it to a given round of the tournament get the bid, e.g. octafinals means 16 bids, semifinals is 4 bids, etc. A perverse result of this bid system is that rounds after the bid round are treated as unimportant - teams routinely forfeit rounds or run less serious arguments - but the bid round and rounds before have enormous strategic investment. 

This setup leads us to consider the efficacy of the Swiss-tournament design, in this instance.

# Problem Statement

Does the Swiss-style tournament structure effectively find top-$k$ teams?

# Solution Approach/Main Results

We approach the process using simulation.

## Simulation procedure

## Comparisons

# Validation

We present a measure of loss that is centered on the number of top-$k$ teams which are not selected. We also consider if the top-ranked team finishes the tournament as the first ranked team.

# Conclusion

# papers

https://papers.nips.cc/paper/3879-statistical-consistency-of-top-k-ranking.pdf