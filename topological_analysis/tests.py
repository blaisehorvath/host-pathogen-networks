import unittest
from analyser import TopologyAnalyser

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

    def testpathFinder(self):

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



if __name__ == '__main__':
    unittest.main()