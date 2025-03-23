import unittest
from src import stdem
# from stdem import Stdem

stdem.Stdem.stdem("tests/json", "tests/excel")

class TestMain(unittest.TestCase):
    pass