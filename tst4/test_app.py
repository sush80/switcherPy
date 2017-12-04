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


    def _refresh_root(self):
        return self.app.post('/index.html').data.decode("ascii")

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

    def _assert_timer(self, uid_start_stop, asciihtml):
        uid = uid_start_stop[0]
        startTime = uid_start_stop[1]
        stopTime = uid_start_stop[2]
        assert 'UID' + str(uid) + '_active true' in asciihtml
        assert 'UID' + str(uid) + '_start ' + startTime in asciihtml
        assert 'UID' + str(uid) + '_stop ' + stopTime in asciihtml

    def _set_timer(self,uid,startTime, stopTime):
        print("_set_and_verify_timer " + str(uid) + " " + startTime + " " + stopTime)
        rv = self._setTimer(uid,startTime, stopTime)
        rvascii = rv.data.decode("ascii")
        return rvascii

    def _set_and_assert_timer(self,uid,startTime, stopTime):
        asciihtml = self._set_timer(uid,startTime,stopTime)
        self._assert_timer((uid,startTime,stopTime),asciihtml)
        return asciihtml

    def _set_and_assert_timers(self,uid0_start_stop, uid1_start_stop):
        self._set_timer(uid0_start_stop[0], uid0_start_stop[1], uid0_start_stop[2])
        asciihtml = self._set_timer(uid1_start_stop[0], uid1_start_stop[1], uid1_start_stop[2])
        self._assert_timer(uid0_start_stop, asciihtml)
        self._assert_timer(uid1_start_stop, asciihtml)
        return asciihtml


        
    def test_single_sets_01(self):
        with freeze_time("2017-01-01 00:01"):
            testItems = ((0,"00:30", "01:00"),
                         (0,"22:31", "23:01"),
                         (1,"00:31", "01:01"),
                         (1,"23:31", "23:41")
                        )
            for item in testItems:
                self._set_and_assert_timer(item[0],item[1], item[2])
        
    def test_both_sets_01(self):
        with freeze_time("2017-01-01 00:01"):
            self._set_and_assert_timers((0,"00:30", "01:00"), (1,"22:31", "23:01"))
            self._set_and_assert_timers((0,"00:59", "01:00"), (1,"23:00", "23:01"))
            self._set_and_assert_timers((0,"22:30", "23:00"), (1,"00:31", "01:01"))


    def _assert_current_status_on(self):
        assert 'CurrentStatus on' in self._refresh_root()

    def _assert_current_status_off(self):
        assert 'CurrentStatus off' in self._refresh_root()

    def test_timer_and_active_status_01(self):
        with freeze_time("2017-01-01 00:01"):
            asciihtml = self._set_and_assert_timers((0,"00:30", "00:35"), (1,"23:31", "23:41"))
            self._assert_current_status_off()
        with freeze_time("2017-01-01 00:30"):
            self._assert_current_status_on()
        with freeze_time("2017-01-01 00:31"):
            self._assert_current_status_on()
        with freeze_time("2017-01-01 00:35"):
            self._assert_current_status_on()
        with freeze_time("2017-01-01 00:36"):
            self._assert_current_status_off()
        for h in range(1,22):
            for m in range(0,60,15):
                with freeze_time("2017-01-01 " + str(h) + ":" + str(m)):
                    #print (str(h) + " " + str(m))
                    self._assert_current_status_off()
        with freeze_time("2017-01-01 23:30"):
            self._assert_current_status_off()
        with freeze_time("2017-01-01 23:31"):
            self._assert_current_status_on()
        with freeze_time("2017-01-01 23:41"):
            self._assert_current_status_on()
        with freeze_time("2017-01-01 23:42"):
            self._assert_current_status_off()

        

if __name__ == '__main__':
    unittest.main()
