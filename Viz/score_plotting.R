# Title     : TODO
# Objective : TODO
# Created by: jdfre
# Created on: 4/18/2021

library(ggplot2)
library(reshape2)

scores = read.csv("scores/score.csv", stringsAsFactors = F, header = F)

colnames(scores) = c("NSscore", "NSbag", "EWscore", "EWbag", "Nbet", "Ebet", "Sbet", "Wbet")

scores$hand = seq(1, nrow(scores))

melted = melt(scores, id.vars = "hand")

ggplot(subset(melted, melted$variable == "NSscore" | melted$variable == "EWscore"), aes(hand, value, color = variable)) +
  geom_line(size = 2)





