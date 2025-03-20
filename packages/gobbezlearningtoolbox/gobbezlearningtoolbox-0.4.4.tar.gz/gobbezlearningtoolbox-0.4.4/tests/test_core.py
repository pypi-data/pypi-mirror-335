import unittest
from gobbezlearningtoolbox.core import start
from gobbezlearningtoolbox.listall import ListAll
from gobbezlearningtoolbox.datascience import DataScience
from gobbezlearningtoolbox.deeplearning import DeepLearning

class TestStart(unittest.TestCase):
    def test_start(self):
        self.assertEqual(start(), "gobbezlearningtoolbox.core success!")
        self.assertEqual(ListAll(), "gobbezlearningtoolbox.listall success!")
        self.assertEqual(DataScience(), "gobbezlearningtoolbox.datascience success!")
        self.assertEqual(DeepLearning(), "gobbezlearningtoolbox.deeplearning success!")

# Esegui i test
if __name__ == '__main__':
    unittest.main()
