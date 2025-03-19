import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from mns_common.db.MongodbUtil import MongodbUtil

mongodb_util = MongodbUtil('27017')

from functools import lru_cache


@lru_cache(maxsize=None)
def get_ths_cookie():
    stock_account_info = mongodb_util.find_query_data('stock_account_info', {"type": "ths_cookie", })
    ths_cookie = list(stock_account_info['cookie'])[0]
    return ths_cookie


@lru_cache(maxsize=None)
def get_em_cookie():
    stock_account_info = mongodb_util.find_query_data('stock_account_info', {"type": "em_cookie", })
    em_cookie = list(stock_account_info['cookie'])[0]
    return em_cookie
