import logging
import multiprocessing
import os
import sys
from asyncio import get_event_loop, ensure_future, wait
from signal import SIGINT
logging.getLogger('pika').setLevel(logging.NOTSET)
logging.getLogger('aio_pika').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)

all_modules = [
            'va_transaction_worker',
            'flaskApp',
        ]
def start_module(module):
    def t():
        try:
            mod = __import__(module, fromlist=['init'])
            init = getattr(mod, 'init')
            LOGGER.info(f"<<----- {module} READY----->>")
            init()

        except Exception as e:
            LOGGER.error(f'Check RabbitMQ Connection {e}')
            raise e

    return t


def start():
    """
    SELECTED_GROUP Can be One of these:
        ALL,BASE_ONLY,MPESA_BASE,MPESA_ONLY,AIRTEL_BASE,AIRTEL_ONLY
    or
    SELECTED_MODULES Comma separated modules
        app.tss.archive_consumer,app.tss.requests_consumer,app.tss.fulfilment_consumer,app.tss.mpesa.stk_waiting_consumer,app.tss.mpesa.stk_callback_waiting_consumer,app.tss.mpesa.c2b_waiting_consumer,app.tss.mpesa.pull_request,app.tss.mpesa.pull_waiting_consumer,app.tss.mpesa.pull_done_consumer,app.tss.mpesa.b2c_waiting_consumer,app.tss.mpesa.b2c_processed_consumer,app.tss.tasks.stk_waiting_consumer,app.tss.tasks.stk_callback_waiting_consumer,app.tss.tasks.c2b_waiting_consumer,app.tss.tasks.b2c_waiting_consumer

    @return:
    """
    selected_group = os.environ.get("SELECTED_GROUP", False)
    x = os.environ.get("SELECTED_MODULES", "")

    if ',' in x:
        selected_to_run_apps = x.split(',')
    else:
        selected_to_run_apps = all_modules


    logging.info(selected_to_run_apps)

    if len(selected_to_run_apps) == 0:
        logging.info("Existing. No SELECTED_MODULES found or No SELECTED_GROUP found")
        exit(3)
    for app_module_name in selected_to_run_apps:
        if app_module_name not in all_modules:
            logging.info(f"Existing. Invalid App Module Found({app_module_name}).\nAccepted Modules:\n{all_modules}")
            exit(3)

    tasks = []

    for app_module_name in selected_to_run_apps:
        tasks.append(multiprocessing.Process(target=start_module(app_module_name), args=()))

    for j in tasks:
        j.start()

    # Ensure all of the processes have finished
    for j in tasks:
        j.join()


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')

LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    try:
        start()
    except Exception as e:
        logging.info("Application Exception. Apps Stopped")
