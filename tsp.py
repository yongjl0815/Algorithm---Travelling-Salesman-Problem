#!/usr/bin/python

import sys, os, getopt, math, time
from collections import deque
from UnionFind import UnionFind

def printHelp():
  print
  print os.path.basename(sys.argv[0]) + " input.txt",
  print
  print "Enter the name of program followed by the name of the input file."
  print
  print "Options"
  print "\t--help,-h\tprint this help message"
  print
  print "The input file must be in formatted as 3 integers per line separated "
  print "by a space. The first integer is the id of the city. The second and "
  print "third integers should be the coordinates of the city."
  print

def distance(a,b):
    # a and b are integer pairs (each representing a point in a 2D, integer grid)
    # Euclidean distance rounded to the nearest integer:
    dx = a[0]-b[0]
    dy = a[1]-b[1]
    #return int(math.sqrt(dx*dx + dy*dy)+0.5) # equivalent to the next line
    return int(round(math.sqrt(dx*dx + dy*dy)))

def buildGraphDistanceTable(points):
  # points - list of 3 element lists (id, x, y)
  graph = {}
  for pointA in points:
    graph[pointA[0]] = {}
    for pointB in points:
      if pointA[0] == pointB[0]:
        graph[pointA[0]][pointB[0]] = sys.maxint
      else:
        graph[pointA[0]][pointB[0]] = distance([pointA[1], pointA[2]], (pointB[1], pointB[2]))
  return graph

def calculatePathCost(graph, nodes):

  cost = 0
  for i in range(len(nodes)):
    cost = cost + graph[nodes[i]][nodes[i-1]]

  return cost


def main(argv):

  try:
    opts, args = getopt.getopt(argv, "hm:", ["help", "minutes="])
  except getopt.GetoptError:
    printHelp()
    exit(2)

  minutes = 5

  for opt in opts:
    if opt[0] == "--help" or opt[0] == "-h":
      printHelp()
      exit(1)
    elif opt[0] == "--minutes" or opt[0] == "-m":
      minutes = int(opt[1])
    else:
      print "Invalid option: ", opt[0]
      printHel()
      exit(2)

  if len(args) < 1:
    printHelp()
    exit(1)

 
  points = []
  inputFile = open(args[0])

  while 1:

    line = inputFile.readline()
    if not line:
      break

    (pointid, xcoord, ycoord) = line.rsplit()
    points.append([int(pointid), int(xcoord), int(ycoord)])

  inputFile.close()

  print "Starting run on", len(points), "data points."
  startTime = time.clock()

  print "Bulding memo table of distances..."
  graph = buildGraphDistanceTable(points)

  print "Building MST to generate initial path..."
  # Use Kruskal's to build the MST
  subtrees = UnionFind()
  tree = []
  for W,u,v in sorted((graph[u][v],u,v) for u in graph for v in graph[u]):
    if subtrees[u] != subtrees[v]:
      tree.append((u,v))
      subtrees.union(u,v)

  # Preorder traverse the MST
  queue = deque()
  queue.append(points[0][0])
  mstPath = []

  alreadyInMst = {}
  for point in points:
    alreadyInMst[point[0]] = False

  while len(queue) > 0:

    pointA = queue.pop()
    mstPath.append(pointA)
    alreadyInMst[pointA] = True

    for edge in tree:
      if edge[0] == pointA and not alreadyInMst[edge[1]]:
        queue.append(edge[1])
      elif edge[1] == pointA and not alreadyInMst[edge[0]]:
        queue.append(edge[0])


  path = mstPath
  pathCost = calculatePathCost(graph, path)

  print "Starting 2-opt hueristics to improve MST path..."

  while True:

    if (time.clock() - startTime) > (minutes * 60):
      print "Hitting time limit. Returning best so far."
      break

    hasChanged = False

    for i in range(0, len(path) - 1):

      for j in range(i + 1, len(path)):

        if i != j:

          newPath = path[i:j]
          tmpPath = path[j:]
          tmpPath.reverse()
          newPath.extend(tmpPath)
          newPath.extend(path[:i])
          newPathCost = calculatePathCost(graph, newPath)

          if newPathCost < pathCost:

            path = newPath
            pathCost = newPathCost
            hasChanged = True
            break

        if hasChanged:
          break

    if not hasChanged:
      break

  print "Final path:", path
  print "Final path cost:", pathCost
  print "Finished in ", (time.clock() - startTime)

  outputFile = open(args[0] + ".tour", "w")
  outputFile.write(str(pathCost) + os.linesep)

  for point in path:
    outputFile.write(str(point) + os.linesep)

  outputFile.close()

if __name__ == '__main__':
	main(sys.argv[1:])
