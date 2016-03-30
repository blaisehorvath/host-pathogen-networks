from fractions import Fraction
import networkx


class TopologyAnalyser:

    def __init__(self,edgelist):

        self.edgeList = edgelist

        self.graph = networkx.Graph()

        for edge in self.edgeList:
            source, target = edge.split('-')
            self.graph.add_edge(source, target)

        self.edgeStrength = self.buildEdgeUnitStrenghtDict()

    def getFirstNeighboursSet(self, nodeName):
        """
        Returns a set that contains the first neighbours of that node.
        :param nodeName:
        :return:
        """
        return set([neighbour for neighbour in self.graph.neighbors_iter(nodeName)])

    def getNextNeighbourhood(self, prevNeighbourhood, neighbours):
        """
        Returns a set that contains the nodes of the next neighbourhood level.
        :param prevNeighbourhood:
        :param neighbours:
        :return:
        """
        if not prevNeighbourhood:
            return neighbours

        else:

            node = prevNeighbourhood.pop()

            mergedNeighbourhood = neighbours.union(self.getFirstNeighboursSet(node))

            return self.getNextNeighbourhood(prevNeighbourhood, mergedNeighbourhood)

    def getNthNeighbours(self, node, n, prevNeighbourhood=set()):
        """
        Returns the nth neighbours of a node
        :param node:
        :param n:
        :return:
        """

        if not prevNeighbourhood:
            prevNeighbourhood = self.getFirstNeighboursSet(node)
            n -= 1

        if n != 0:

            nextNeighbourhood = self.getNextNeighbourhood(prevNeighbourhood, set())

            return self.getNthNeighbours(node, n-1, nextNeighbourhood )

        if n == 0:
            return prevNeighbourhood


    def buildEdgeUnitStrenghtDict(self):
        """
        This function builds the dict that contains the unit stengths and the reverse strength for each edge.
        :return:
        """
        unitStrenghtDict = {}

        for edge in self.edgeList:
            source, target = edge.split('-')

            sourceNeighboursNum = len(self.getFirstNeighboursSet(source))

            targetNeighboursNum = len(self.getFirstNeighboursSet(target))

            edgeStrength = Fraction(1, targetNeighboursNum)

            unitStrenghtDict[source + "-" + target] = edgeStrength

            reverseEdgeStrength = Fraction(1, sourceNeighboursNum)

            unitStrenghtDict[target + "-" + source] = reverseEdgeStrength

        return unitStrenghtDict

    def pathFinder(self, depth, sourceNode, targetNode, path, collectedPathways):
        """
        This function returns every possible pathway between two nodes with a given length.
        :param depth: lenght of the required pathways
        :param sourceNode:
        :param targetNode:
        :param path: needed because of recursion
        :param collectedPathways: dirty solution for imperatively collecting the pathways
        :return: a list of pathways
        """
        if len(path) == 0:
            path.append(sourceNode)
            depth -= 1
        if depth == 0 and sourceNode == targetNode:
            stringPath = '-'.join(path)
            collectedPathways.append(stringPath)
            return path
        if depth == 0 and sourceNode != targetNode:
            return
        for neighbourNode in self.getFirstNeighboursSet(sourceNode):
            path.append(neighbourNode)
            self.pathFinder(depth-1, neighbourNode, targetNode, path, collectedPathways)
            path.pop(-1)

    def getNthPathwaysForNodes(self, steps):
        pathways = {}

        for node in self.graph.nodes():

            pathways[node] = []

            nthNeighbours = self.getNthNeighbours(node, steps-1)

            for neighbour in nthNeighbours:
                collectedPathways = []
                self.pathFinder(steps, node,neighbour,[], collectedPathways)
                pathways[node] += collectedPathways

        return pathways