from cache import Cache
from datetime import datetime, timedelta
from random import randint
from scheduler import Scheduler
from utils import Config, Logger


class Tester:
    def __init__(self):
        pass

    def schedule(self):
        timestamp = datetime.now().replace(hour=randint(10, 21), minute=0, second=0, microsecond=0) \
                    + timedelta(days=randint(1, 7))
        delta = timestamp - datetime.now()
        print("Target %s, Delta %s" % (timestamp, delta))
        sleeps = [timedelta(days=1), timedelta(hours=8), timedelta(hours=2), timedelta(hours=1),
                  timedelta(minutes=20), timedelta(minutes=5), timedelta(minutes=1)]
        if delta > timedelta(hours=1) * 1.2:
            sleep_delta = delta % timedelta(hours=1)
            print('First try: Timestamp %s, Delta %s, Sleep %s' % (timestamp, delta, sleep_delta))
            # sleep
            timestamp += sleep_delta
            delta -= sleep_delta
        while delta > timedelta(minutes=1) * 1.2:
            sleep_delta = timedelta(seconds=0)
            for sleep_delta in sleeps:
                if delta > sleep_delta * 1.2:
                    break
            print('New try: Timestamp %s, Delta %s, Sleep %s' % (timestamp, delta, sleep_delta))
            # sleep
            timestamp += sleep_delta
            delta -= sleep_delta
        print('Final: Timestamp %s, Delta %s' % (timestamp, delta))

    def test(self):
        Logger()
        cache = Cache()
        timestamp = datetime.strptime('2023-04-07 11', '%Y-%m-%d %H')
        Scheduler(timestamp, 1, cache).start()


if __name__ == "__main__":
    tester = Tester()
    tester.schedule()
