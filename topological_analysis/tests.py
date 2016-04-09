import unittest
from analyser import TopologyAnalyser
from fractions import Fraction

edges = [
    'a-e',
    'e-b',
    'e-c',
    'b-f',
    'f-c',
    'f-d'
]

analyzer = TopologyAnalyser(edges)


class TestGraphAnalyser(unittest.TestCase):

    def testGetFirstNeighboursSet(self):
        self.assertEqual(analyzer.getFirstNeighboursSet('e'), set(['a','b','c']))

    def testGetNextNeighbourHood(self):
        self.assertEqual(analyzer.getNextNeighbourhood(set(['e']), set([])), set(['a','b','c']))
        self.assertEqual(analyzer.getNextNeighbourhood(set(['a','b','c']), set([])), set(['e','f']))

    def testGetNthNeighbours(self):
        self.assertEqual(analyzer.getNthNeighbours('e',2), set(['e', 'f']))
        self.assertEqual(analyzer.getNthNeighbours('e', 1), set(['a','b','c']))

    def testPathFinder(self):

        paths = []

        analyzer.pathFinder(3,'e','e', [], paths)

        self.assertIn('e-a-e' , paths)
        self.assertIn('e-b-e', paths)
        self.assertIn('e-c-e', paths)
        self.assertEqual(len(paths), 3)


        paths2 = []

        analyzer.pathFinder(3, 'e', 'f', [], paths2)

        self.assertIn('e-b-f', paths2)
        self.assertIn('e-c-f', paths2)
        self.assertEqual(len(paths2), 2)


    def testGetNthPathwaysForNodes(self):
        pathways = analyzer.getNthPathwaysForNodes(3)
        self.assertIn('e-b-f', pathways['e'])
        self.assertIn('e-c-f',  pathways['e'])
        self.assertIn('e-a-e' , pathways['e'])
        self.assertIn('e-b-e', pathways['e'])
        self.assertIn('e-c-e', pathways['e'])
        self.assertEqual(len(pathways['e']), 5)
        self.assertEqual(len(pathways), 6)

    def testGetEdgeList(self):
        self.assertEqual(analyzer.getEdgesFromPathway('a-b-c'), ['a-b', 'b-c'])

    def testcountPathwayStrength(self):
        self.assertEqual(analyzer.countPathwayStrength('e-a-e'), float(Fraction('1/3')))
        self.assertEqual(analyzer.countPathwayStrength('e-b-f'), float(Fraction('1/6')))

    def testGetNStepPathwaysForNode(self):
        self.assertEqual(analyzer.getPathWaysToNthNeighbours('e',3), ['e-a-e', 'e-c-e', 'e-b-e', 'e-c-f', 'e-b-f'])

    def testCountTI(self):
        self.assertAlmostEqual(analyzer.countTI('e',3), Fraction(1))
        self.assertAlmostEqual(analyzer.countTI('b', 3), Fraction('4/3'))
        self.assertAlmostEqual(analyzer.countTI('a', 3), Fraction('2/3'))

    def testgetNodeDirectStrength(self):
        self.assertEqual(analyzer.getNodeDirectStrengths()['a'], Fraction('1/3'))
        self.assertEqual(analyzer.getNodeDirectStrengths()['b'], Fraction('2/3'))


if __name__ == '__main__':
    unittest.main()