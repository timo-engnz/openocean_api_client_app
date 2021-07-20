import json
import logging
import os

from flask import Flask, request
from flask import jsonify
from omit_helpers import Application

from utils import Helpers

args_1 = os.environ.get('ENV_NAME')

env = args_1 if args_1 else "development"

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.NOTSET)
# logging.getLogger('suds.transport').setLevel(logging.DEBUG)
# logging.getLogger('suds.xsd.schema').setLevel(logging.NOTSET)
# logging.getLogger('suds.xsd.query').setLevel(logging.NOTSET)
# logging.getLogger('suds.xsd.schema').setLevel(logging.NOTSET)
# logging.getLogger('suds.wsdl').setLevel(logging.NOTSET)

application = Application()
logger = application.get_logger(class_name=__name__)
cfg = application.cfg
cache = application.cache

_cfg = cfg.get('connection', path='mysql')

helpers = Helpers()

dbService = helpers.get_db_connection(cfg=cfg)


@app.route('/')
def index():
    return "Core Api is Activeeeeetooooo!!!"


@app.route('/callback', methods=['POST'])
def requestSmsSend():
    try:
        if authorise(request):
            return jsonify(processRequest(request))
        return jsonify({"ResponseCode": "-1", "ResponseMessage": "Unauthorized Request"})
    except Exception as e:
        logger.error(e)
        return jsonify({"ResponseCode": "1",
                        "ResponseMessage": "Possible Errors: Invalid Request | Missing the 3 Params| Wrong Parameters "
                                           "| Reference Code Exists",
                        "error": str(e)})


def authorise(incoming_request):
    # auth = incoming_request.headers.get('Authorization')
    # if incoming_request.get_json():
    #     if auth:
    #         if auth in AUTH:
    #             return True
    #     return True
    # else:
    #     return False
    return True


# noinspection PyBroadException
def processRequest(in_request):
    try:

        payload = in_request.get_json(force=True)
        logger.info(payload)

        metaData = payload['MetaData']
        response_id = metaData['MessageId']
        status = payload['Status']

        dbService.callback_update(
            response_id=response_id,
            callback_data=json.dumps(payload),
            status=status,
            idepodency_key=1 if status == '200' else -1
        )

        responseCode, responseMessage = 0, "Success"

        dbService.db_commit()
        return {
            "ResponseCode": responseCode,
            "ResponseMessage": responseMessage
        }

    except Exception as e:
        dbService.db_rollback()
        raise e


def init():
    app.run(debug=True if env == "development" else False, host='0.0.0.0')


if __name__ == '__main__':
    init()
