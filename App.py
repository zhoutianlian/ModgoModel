# -*- coding: utf-8 -*-：
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import getopt
# import sys
import traceback
from flask import Flask, request
import gc
import logging

__all__ = ['valuation']

app = Flask(__name__)


@app.route('/valuation/', methods=['GET'])
def valuation():
    vid = 0
    response = 'FAIL'
    try:
        vid = request.args.get('vid')
        vid = int(vid)
        if vid > 0:
            import Main
            response = Main.Valuation(vid).run()
        else:
            logger(2, f'VID {vid} 不合法')
            raise ValueError
    except Exception as err:
        vid = 'MISSING' if vid == 0 else vid
        info = f'## 估值失败 VID: {vid}##'
        logger(2, info+traceback.format_exc())
    finally:
        gc.collect()
        return response


@app.route('/', methods=['GET'])
def index():

    return "首页"


if __name__ == '__main__':
    import Config.Database
    from Report.Log import logger
    opts, args = getopt.getopt(sys.argv[1:], 'e:')
    for key, value in opts:
        if key in ['-e']:
            Config.Database.set_db(value)
    app.run(host='0.0.0.0', port=5004, threaded=True)
    logging.basicConfig(level=logging.INFO,  # 控制台打印的日志级别
                        filename='setting/log.txt',  # 将日志写入log.txt文件中
                        filemode='a',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                        # a是追加模式，默认如果不写的话，就是追加模式
                        format=
                        '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                        # 日志格式
                        )
