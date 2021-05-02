
library(ggplot2)
library(dplyr)
library(plotly)

normal = read.csv("benchmark/normal.csv", stringsAsFactors = F, header = F)
para = read.csv("benchmark/para_5Workers.csv", stringsAsFactors = F, header = F)



rownames(normal) = normal[,ncol(normal)]; normal[,ncol(normal)] = NULL
rownames(para) = para[,ncol(para)]; para[,ncol(para)] = NULL


normal = t(normal)
rownames(normal) = NULL

para = t(para)
rownames(para) = NULL


a = reshape2::melt(normal)
b = reshape2::melt(para)



ggplot(a, aes(log10(Var2), log10(value), group = Var2)) + geom_boxplot()
ggplot(b, aes(factor(Var2), value, group = Var2)) + geom_boxplot()

se = function(x) sd(x)/sqrt(length(x))
normal.stats = a %>% group_by(Var2) %>% summarise(mean = mean(value), se = se(value), median = median(value), mad = mad(value))

normal.stats$func = "NORMAL"

para.stats = b %>% group_by(Var2) %>% summarise(mean = mean(value), se = se(value), median = median(value), mad = mad(value))

para.stats$func = "PARA"

stats = rbind(para.stats, normal.stats)

pl = ggplot(stats, aes(log10(Var2), log10(mean), color = func)) +
        geom_point()
#+        geom_errorbar(aes(ymin = mean - se, ymax = mean + se))

ggplotly(pl)


ggplot(normal.stats, aes(log10(Var2), median)) +
  geom_point() +
  geom_point(data = para.stats, aes(Var2, median))