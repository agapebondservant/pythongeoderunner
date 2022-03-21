import unittest
from pygeoderunner import PyGeodeSession


class TestPyGeodeRunner(unittest.TestCase):

    def test_sync_context(self):
        geode_session = PyGeodeSession(region='claims', server_side_function='PythonRunner')
        with geode_session.create():
            def main():
                x = 10
                x *= x
        results = geode_session.execute(main)
        self.assertEqual(100, results['x'])


if __name__ == '__main__':
    unittest.main()
