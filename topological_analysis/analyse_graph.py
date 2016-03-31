"""
This script takes an edgelist file (1 column = source, 2. column = target), and counts the
TI values(topological importance) for each node. The results are saved to a file. Most things
like separators are hardcoded...
"""
import sys

__author__ = 'blaise'

# parsing arguments
import argparse
from analyser import TopologyAnalyser

parser = argparse.ArgumentParser(description='Convert downloaded RNA files to Mitab SQLite')
parser.add_argument('--edgelist-file', required=True, metavar="EdgeFile", type=str,
                    help="The location of the source file for edges")
parser.add_argument('--outfile', required=True, metavar="EdgeFile", type=str,
                    help="The location where results should be put")

args = parser.parse_args()

edgeList = []

with open(args.edgelist_file) as edgefile:
    print "Parsing edgelist file"

    # skipping the header
    edgefile.readline()

    for line in edgefile:
        source, target, source_db = line.strip().split(',')
        edgeList.append(source + "-" + target)

print "Parsing completed, building network"
analyser = TopologyAnalyser(edgeList)

print "Started parsing nodes"
with open(args.outfile,'w') as outFile:
    numOfNodes = len(analyser.graph.nodes())
    ii = 0
    for node in analyser.graph.nodes():

        if (ii % 50) == 0:
            sys.stdout.write("Parsing node %d/%d \r" % (ii, numOfNodes))
            sys.stdout.flush()
        ii += 1

        ti = analyser.countTI(node,3)

        outFile.write(node+","+str(ti)+"\n")
print("Finished writing content to file")