from news18.base import news18
from pymongo import MongoClient
from redis import Redis
from rq import Queue
from news18 import logger
import time
client = MongoClient('localhost',27017)
db = client.test

redis_conn = Redis()
q = Queue('news18',connection=redis_conn, default_timeout=3600)


def news18_iterator():
    col = db.news18
    try:
        page = 0
        resp = news18(page=str(page))
        if resp['success'] is True:
            for res in resp['data']:
                upsert = col.update({"url": res["url"]},
                                    res,
                                    upsert=True)
                logger.info('data upserted {0}'.format(upsert))
        page = 1
        while page <= int(resp['total_pages']):
            try:
                resp = news18(page=str(page))
                if resp['success'] is False or len(resp['data']) == 0:
                    continue
                if resp['success'] is True:
                    for res in resp["data"]:
                        try:
                            upsert = col.update({"url": res["url"]},
                                       res,
                                       upsert=True)
                            logger.info('data upserted {0}'.format(upsert))
                        except Exception as e:
                            logger.warning('error with the upsert {0}'.format(str(e)))
            except Exception as e:
                logger.warning('error in {0}'.format(str(e)))
            page = page+1
    except Exception as e:
        logger.error('Iterator function failed for news18 {0}'.format(str(e)))
        return None


def news18_jobs():
    job = q.enqueue(news18_iterator)
    time.sleep(2)
    print(job.enqueued_at)