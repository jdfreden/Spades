# Title     : Visualize ICMCTS
# Created by: jdfre
# Created on: 4/14/2021

library(visNetwork)

processFile = function(filepath) {
  lines = c()
  con = file(filepath, "r")
  while ( TRUE ) {
    line = readLines(con, n = 1)
    if ( length(line) == 0 ) {
      break
    }
    print(line)
    lines = c(lines, line)
  }

  close(con)
  return(lines)
}

lines = processFile("example_trees/example_tree_100.txt")

lines = gsub("  *", " ", lines)
r = lines[1]
best.move = lines[startsWith(lines, "#")]
lines = lines[lines != ""]
lines = lines[!startsWith(lines, "#")]

lines = lines[-1]


# Process root
r.stats = unlist(strsplit(r, ": "))[2]
r.stats = gsub("\\]", "", r.stats)
r.stats = gsub(" ", "", r.stats)
r.stats = unlist(strsplit(r.stats, "/"))
r.stats = as.numeric(r.stats)

from = NULL
to = NULL
#level = NULL
val = r.stats[2]
for(i in seq_along(lines)) {
  cont = unlist(strsplit(lines[i], "\\| "))
#  l = sum(cont == "")
  cont = cont[cont != ""]
  info = unlist(strsplit(cont, "\\] "))
  t = gsub("\\[M:", "", unlist(strsplit(info[1], " "))[1])
  v = unlist(strsplit(info[1], "A: "))[2]
  v = as.numeric(unlist(strsplit(v, "/ "))[2])
  f = unlist(strsplit(info[2], " "))[1]
  if(is.na(f)) {
    f = "root"
  }
  from = c(from, f)
  to = c(to, t)
  val = c(val, v)
}

nodes = data.frame(id = unique(c(from, to)))
nodes$label = nodes$id
#nodes$value = val
edges = data.frame(from = from, to = to)

visNetwork(nodes, edges) %>%
  visOptions(collapse = T, highlightNearest = T) %>%
  visHierarchicalLayout(sortMethod = "directed")
