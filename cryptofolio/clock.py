from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue
from worker import conn
from models import update_all_exchange_balances

sched = BlockingScheduler()
q = Queue('default', connection=conn)

@sched.scheduled_job('interval', minutes=60)
def update_balances_job():
    result = q.enqueue(update_all_exchange_balances)

sched.start()
