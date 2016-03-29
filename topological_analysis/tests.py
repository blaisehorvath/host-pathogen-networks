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

if __name__ == '__main__':
    unittest.main()