import os
import srv
import unittest
import tempfile
from freezegun import freeze_time

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

    def _setTimer(self, uid, startTime, stopTime):
        return self.app.post('/index.html', data=dict(
            action="setAlarmTimes",
            UID=str(uid),
            active="true",
            start=startTime,
            stop=stopTime
            ))

    def test_clear_yaml(self):
        self._disableTimer(0)
        rv = self._disableTimer(1)
        assert b'UID0_active false' in rv.data
        assert b'UID1_active false' in rv.data
        assert b'CurrentStatus off' in rv.data
        
    #with freeze_time("2012-01-14 23:00:00", tz_offset=2):
    def test_set01(self):
        with freeze_time("2017-01-01 00:01"):
            uid = 0
            startTime = "00:30"
            stopTime  = "01:00"
            rv = self._setTimer(uid,startTime, stopTime)
            rvascii = rv.data.decode("ascii")
            assert 'UID' + str(uid) + '_active true' in rvascii
            assert 'UID' + str(uid) + '_start ' + startTime in rvascii
            assert 'UID' + str(uid) + '_stop ' + stopTime in rvascii


if __name__ == '__main__':
    unittest.main()
