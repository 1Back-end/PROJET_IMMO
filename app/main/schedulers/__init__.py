from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError

from app.main.schedulers.test_scheduler import test_scheduler
from app.main.utils import logger


class Scheduler:

    # constructor for add tasks to scheduler
    def __init__(self):
        self.scheduler = BackgroundScheduler({
            'apscheduler.jobstores.default': {
                'type': 'sqlalchemy',
                'url': 'sqlite:///jobs.sqlite'
            },
            'apscheduler.executors.default': {
                'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
                'max_workers': '20'
            },
            'apscheduler.executors.processpool': {
                'type': 'processpool',
                'max_workers': '5'
            },
            'apscheduler.job_defaults.coalesce': 'false',
            'apscheduler.job_defaults.max_instances': '3',
            'apscheduler.timezone': 'UTC',
        })
        self.add_job(test_scheduler, 'interval', seconds=60 * 2, id='test_scheduler')

    def add_job(self, func, trigger, **kwargs):
        try:
            self.scheduler.add_job(func, trigger, replace_existing=True, **kwargs)
        except ConflictingIdError as e:
            logger.error("Error: ", e)

    def start(self):
        self.scheduler.start()


scheduler = Scheduler()
