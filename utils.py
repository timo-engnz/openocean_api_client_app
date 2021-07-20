import logging
import json
from datetime import datetime

import requests

from omit_helpers import _Database


class Helpers:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = None

    def db_commit(self):
        self.db.commit()

    def db_rollback(self):
        self.db.rollback()

    def get_db_connection(self, cfg):
        _cfg = cfg.get('connection', path='mysql')

        self.db: _Database = _Database(host=_cfg['host'], port=_cfg['port'],
                                       user=_cfg['username'], password=_cfg['password'], db=_cfg['database'])
        return self

    def get_pending(self, timezone="Africa/Nairobi", before_sync_seconds=30):
        sql = f"select * from va_transactions WHERE status =%s"
        params = (0)
        result = self.db.retrieve_all_data_params(sql, params)
        # self.logger.info(f"MYSQL RESULTS:{result}")

        if result:
            return True, result
        else:
            return False, ''

    def update_pending(self, id, status, response, retry_count, response_id):
        sql = "update va_transactions set status=%s,response=%s,retry_count=%s, response_id=%s where id=%s"
        params = (status, response, retry_count, response_id, id)
        result = self.db.execute_query(sql, params)
        # self.logger.info(f"MYSQL RESULTS:{result}")

        if result:
            return True, result
        else:
            return False, ''

    def callback_update(self, response_id, status, idepodency_key, callback_data):
        sql = "update va_transactions set status=%s,idepodency_key=%s,callback_data=%s where response_id=%s"
        params = (status, idepodency_key, callback_data, response_id)
        result = self.db.execute_query(sql, params)
        # self.logger.info(f"MYSQL RESULTS:{result}")

        if result:
            return True, result
        else:
            return False, ''
