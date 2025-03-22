import unittest
import polymap
import pathlib, shutil, logging, sys

TEST_DIR = pathlib.Path(__file__).with_name("data")

logging.basicConfig(
    format="%(asctime)s - %(name)-8s - %(levelname)-8s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)
logger = logging.getLogger("polymap.test")

if "-v" in sys.argv:
    logger.setLevel(logging.INFO)


def setUpModule():
    """Download data for testing"""
    TEST_DIR.mkdir(exist_ok=True)
    # we will have various data download code here


def tearDownModule():
    """Remove test data"""

    logger.info("teardown - Removing test data...")
    shutil.rmtree(TEST_DIR)


class Testpolymap(unittest.TestCase):
    def test_answer_to_life(self):
        tmp = polymap.PolyMap()
        self.assertEqual(tmp.answer_to_life(), 42)
