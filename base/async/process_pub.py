from base import db, app
from huey import RedisHuey, crontab

huey = RedisHuey('snippets',
                 connection_pool=app.config['REDIS_CONNECTION_POOL'])


@huey.task(include_task=True)
def process_pub(data, task=None):
    # Import possible tasks
    print(data)
    print(task)

