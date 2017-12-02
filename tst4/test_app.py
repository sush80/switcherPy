import os
import srv
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, srv.app.config['DATABASE'] = tempfile.mkstemp()
        srv.app.testing = True
        self.app = srv.app.test_client()
        #with srv.app.app_context():
        #    srv.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(srv.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

if __name__ == '__main__':
    unittest.main()
