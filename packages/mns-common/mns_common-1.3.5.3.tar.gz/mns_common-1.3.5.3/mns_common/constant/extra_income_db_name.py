import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

# db_name

EXTRA_INCOME = 'extraIncome'

# 创业板分钟集合数据
ONE_MINUTE_K_LINE_BFQ_C = 'one_minute_k_line_bfq_c'

# 北交所分钟集合数据
ONE_MINUTE_K_LINE_BFQ_BJ = 'one_minute_k_line_bfq_bj'

# 上海主板分钟集合数据
ONE_MINUTE_K_LINE_BFQ_H = 'one_minute_k_line_bfq_h'

# 科创板分钟集合数据
ONE_MINUTE_K_LINE_BFQ_K = 'one_minute_k_line_bfq_k'

# 深圳主板分钟集合数据
ONE_MINUTE_K_LINE_BFQ_S = 'one_minute_k_line_bfq_s'

# 可转债分钟集合数据
ONE_MINUTE_K_LINE_BFQ_KZZ = 'one_minute_k_line_bfq_kzz'

# ETF分钟集合数据
ONE_MINUTE_K_LINE_BFQ_ETF = 'one_minute_k_line_bfq_etf'

# 沪深主要指数分钟集合数据
ONE_MINUTE_K_LINE_BFQ_MAIN_INDEX = 'one_minute_k_line_bfq_main_index'
# 沪深主要指数前复权k线
INDEX_QFQ_DAILY = 'index_qfq_daily'

# 可转债qfq 日k线
KZZ_QFQ_DAILY = 'kzz_qfq_daily'
# ETF qfq 日k线
ETF_QFQ_DAILY = 'etf_qfq_daily'

# 一分钟同步失败集合

ONE_MINUTE_SYNC_FAIL = 'one_minute_sync_fail'
