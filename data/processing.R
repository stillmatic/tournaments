library(magrittr)
library(dplyr)
library(ggplot2)
library(BradleyTerryScalable)

# ndca
ndca <- read.csv("~/code/thesis/debate/ndca2016.csv")
ndca <- ndca %>% select(team, opponent, win)
# ndca_fit <- BradleyTerry2::BTm(ndca$win, ndca$team, ndca$opponent)
ndca_mat <- BradleyTerryScalable::pairs_to_matrix(ndca)
ndca_fit2 <- BradleyTerryScalable::btfit(ndca_mat, 2)

ndca_fit2$pi %>% hist
coef(ndca_fit) %>%
    data.frame(coefs = .) %>%
    ggplot(aes(coefs)) + geom_histogram(bins = 40) + 
    ggtitle("Estimated coefficients from BT model", "From NDCA pairwise comparisons")

# 2009-2010 data
data09 <- jsonlite::fromJSON("~/code/tournament/data/2009-2010.json")
# rounds09 <- do.call(rbind, data09$debaters)
# judges09 <- purrr::map(data09$judge, rep, each = 4) 
# names(judges09) <- c("judge_school", "judge_ID")
# cbind(judges09, rounds09) %>% head

# data09$debaters %>% magrittr::extract2(1) %>% 
#     rename(speaks = `speaker points`) %>%
#     group_by(position) %>%
#     dplyr::summarize(id = stringr::str_c(ID, collapse = ","), 
#                      speaks = base::sum(as.numeric(speaks))) %>%
#     ungroup %>%
#     summarize(aff = first(id), aff_speaks = first(speaks), 
#               neg = last(id), neg_speaks = last(speaks))

clean <- function(x) {
    x %>% rename(speaks = `speaker points`) %>%
        group_by(position) %>%
        dplyr::summarize(id = stringr::str_c(ID, collapse = ","), 
                         speaks = base::sum(as.numeric(speaks))) %>%
        ungroup %>%
        summarize(aff = first(id), aff_speaks = first(speaks), 
                  neg = last(id), neg_speaks = last(speaks))
}

pairwise09 <- purrr::map_df(data09$debaters, clean)
pairwise09$win <- data09$win
pairwise09 %<>%
    filter(aff != "28417,28417", neg != "28417,28417")
pairwise_mat <- pairwise09 %>%
    dplyr::select(aff, neg, win) %>%
    mutate(aff = factor(aff), neg = factor(neg), win = as.numeric(win)) %>%
    BradleyTerryScalable::pairs_to_matrix()

fit_09 <- BradleyTerryScalable::btfit(
    pairwise_mat, 1.5, maxit = 1000000,
    components = connected_components(pairwise_mat)$components)

fit_09$pi %>% purrr::map(hist)
# btm_fit_09 <- BradleyTerry2::BTm(outcome = pairwise09$win, 
                   # player1 = factor(pairwise09$aff), 
                   # player2 = factor(pairwise09$neg), br = TRUE)
