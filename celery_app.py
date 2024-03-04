from celery import Celery
# import tasks

CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 100

app = Celery('currency_trading_tasks',
             broker='amqp://pouria:P1755063881k@192.168.12.10',  # این آدرس برای RabbitMQ محلی است. در صورت نیاز تغییر دهید.
             backend='rpc://',
             include=['tasks']) 

