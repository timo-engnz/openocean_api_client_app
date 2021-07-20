import logging
from datetime import datetime
import requests
from bson import json_util

from omit_helpers import Application, validate_json, _Database, ConsumerConfigs, SyncConsumer
from omit_helpers.app.loops import LoopEngine
import json

logging.basicConfig(level=logging.INFO)

# Application Scaffolding
from utils import Helpers

application = Application()
logger = application.get_logger(class_name=__name__)
cfg = application.cfg
cache = application.cache

worker = LoopEngine(config={}, sleep_time=1)


def on_start(self):
    helpers = Helpers()

    # Initialize AMQP Channel

    return helpers.get_db_connection(cfg=cfg)


def on_stop(self):
    return None


def purchase_kplc_tokens(**kwargs):
    try:
        url = cfg.get(key="url", path="kplc_cred")
        payload = {
            "RequestParameters": [
                {
                    "AccountNumber": kwargs.get('account_no'),
                    "Amount": kwargs.get('amount', ),
                    "Type": "PREPAID",
                    "Action": "BUY"
                }
            ]
        }
        headers = cfg.get(key="headers", path="kplc_cred")

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        logger.info(response.text.encode('utf8'))
        return response.status_code, response.json()[0]
    except Exception as e:
        return -1, {}


def purchase_airtime(**kwargs):
    try:
        url = cfg.get(key="url", path="airtime_cred")
        payload = {
            "AirtimeParameters": [
                {
                    "Number": kwargs.get('account_no'),
                    "Amount": kwargs.get('amount'),
                }
            ]
        }
        headers = cfg.get(key="headers", path="airtime_cred")

        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
        logger.info(response.text.encode('utf8'))
        return response.status_code, response.json()[0]
    except Exception as e:
        logger.error(e)
        return -1, {}


def process_record(helper, row):
    try:
        # DO STUFF HERE
        fxns = {
            "AIRTIME": ("PurchaseID", purchase_airtime),
            "KPLC_TOKENS": ("RequestID", purchase_kplc_tokens),
        }
        trx_type = row['trx_type']
        status, response = fxns[trx_type][1](**row)
        response_id = response[fxns[trx_type][0]]
        retry_count = 0
        helper.update_pending(id=row['id'], status=status, retry_count=retry_count, response_id=response_id,
                              response=json.dumps(response))


    except Exception as e:
        logger.error(e)
        helper.update_pending(id=row['id'], status=-1, retry_count=1, response_id="",
                              response=json.dumps({}))


def on_every_loop(self: LoopEngine, tracking_id):
    # logger.info('New Loop')
    helper = self.on_start_returns
    helper: Helpers

    try:

        status, results = helper.get_pending(before_sync_seconds=5)
        payloads_to_deploy = []

        try:
            if status:
                logger.info(f"{status}=>({len(results)}){results}")

                for row in results:
                    process_record(helper, row)
        except Exception as e:
            logger.error(e)
            logger.error("Error Fetching and Updating Records")
            helper.db_rollback()
            return

        helper.db_commit()
    except Exception as e:
        logger.exception("Exception occurred:  %s", getattr(e, "__dict__", {}))
        helper.db_rollback()


def init():
    worker.start_loop(on_start_fxn=on_start, on_every_loop=on_every_loop, on_stop_fxn=on_stop)


if __name__ == "__main__":
    worker.start_loop(on_start_fxn=on_start, on_every_loop=on_every_loop, on_stop_fxn=on_stop)
