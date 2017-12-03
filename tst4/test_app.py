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
        assert b'Server-time' in rv.data

    def _disableTimer(self, uid):
        return self.app.post('/index.html', data=dict(
            action="setAlarmTimes",
            UID=str(uid),
            active="false",
            start="",
            stop=""
            ))

    def test_clear_yaml(self):
        self._disableTimer(0)
        rv = self._disableTimer(1)
        assert b'Pin: Off' in rv.data
if __name__ == '__main__':
    unittest.main()
