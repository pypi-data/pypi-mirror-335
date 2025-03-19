import logging
from typing import TypeVar

from apscheduler.schedulers.base import BaseScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI

T = TypeVar('T', bound=BaseScheduler)


def register_scheduler(timer: T, app: FastAPI):
    @app.on_event("startup")
    async def start_event():
        timer.start()
        logging.info("定时任务启动成功")

    @app.on_event("shutdown")
    async def end_event():
        timer.shutdown()
        logging.info("定时任务关闭成功")


class RestCronTrigger(CronTrigger):

    @classmethod
    def from_crontab(cls, expr, timezone=None):
        values = expr.split()
        if len(values) != 7:
            raise ValueError('Wrong number of fields; got {}, expected 7'.format(len(values)))

        return cls(second=values[0], minute=values[1], hour=values[2], day=values[3], month=values[4],
                   day_of_week=values[5], year=values[6], timezone=timezone)
