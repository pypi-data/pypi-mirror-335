import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import tushare as ts
from mns_common.db.v2.MongodbUtilV2 import MongodbUtilV2
from mns_common.db.MongodbUtil import MongodbUtil
import mns_common.component.common_service_fun_api as common_service_fun_api

import pandas as pd
from loguru import logger
import mns_common.utils.data_frame_util as data_frame_util
import mns_common.api.em.east_money_stock_api as east_money_stock_api
import time

mongodb_util_27017 = MongodbUtil('27017')
mongodbUtilV2 = MongodbUtilV2('27019', 'extraIncome')

pro = ts.pro_api('782213d20640249f1dbae50a7f56b22684b8e915a61e435e015579a1')


def get_minute_data(symbol, freq, start_date, end_date):
    # 获取浦发银行60000.SH的历史分钟数据
    df = pro.stk_mins(ts_code=symbol, freq=freq, start_date=start_date, end_date=end_date)
    return df


def sync_all_stock(trade_date_list_df):
    de_list_stock_df = mongodb_util_27017.find_all_data('de_list_stock')
    de_list_stock_df = common_service_fun_api.classify_symbol(de_list_stock_df)
    de_list_stock_df = de_list_stock_df.loc[
        de_list_stock_df['classification'].isin(['K', 'C', 'S', 'H', 'X'])]
    # 对 classification 为 S 或 K 的数据，symbol 列加上 '.SH'，其他加上 '.SZ'

    de_list_stock_df['symbol'] = de_list_stock_df.apply(
        lambda row: row['symbol'] + '.SZ' if row['classification'] in ['S', 'C']
        else row['symbol'] + '.BJ' if row['classification'] in ['X']
        else row['symbol'] + '.SH',
        axis=1
    )

    real_time_quotes_all_stocks_df = east_money_stock_api.get_real_time_quotes_all_stocks()

    # 假设数字格式为 YYYYMMDD
    real_time_quotes_all_stocks_df['list_date'] = pd.to_datetime(real_time_quotes_all_stocks_df['list_date'],
                                                                 format='%Y%m%d')

    # 将日期格式化为字符串（YYYY-MM-DD）
    real_time_quotes_all_stocks_df['list_date'] = real_time_quotes_all_stocks_df['list_date'].dt.strftime('%Y-%m-%d')
    real_time_quotes_all_stocks_df = common_service_fun_api.classify_symbol(real_time_quotes_all_stocks_df)

    # 对 classification 为 S 或 K 的数据，symbol 列加上 '.SH'，其他加上 '.SZ'
    real_time_quotes_all_stocks_df['symbol'] = real_time_quotes_all_stocks_df.apply(
        lambda row: row['symbol'] + '.SZ' if row['classification'] in ['S', 'C']
        else row['symbol'] + '.BJ' if row['classification'] in ['X']
        else row['symbol'] + '.SH',
        axis=1
    )

    real_time_quotes_all_stocks_df['number'] = real_time_quotes_all_stocks_df['chg'].rank(method='first').astype(int)

    for stock_one in real_time_quotes_all_stocks_df.itertuples():
        classification = stock_one.classification
        if classification == 'X':
            db_name = 'one_minute_k_line_bfq_bj'
        elif classification == 'S':
            db_name = 'one_minute_k_line_bfq_s'

        elif classification == 'H':
            db_name = 'one_minute_k_line_bfq_h'
        elif classification == 'K':
            db_name = 'one_minute_k_line_bfq_k'
        elif classification == 'C':
            db_name = 'one_minute_k_line_bfq_c'

        trade_date_list_df_copy = trade_date_list_df.copy()

        list_date = stock_one.list_date
        trade_date_list_df_copy = trade_date_list_df_copy.loc[trade_date_list_df_copy['_id'] >= list_date]

        symbol = stock_one.symbol

        de_list_stock_df_one = de_list_stock_df.loc[de_list_stock_df['symbol'] == symbol]

        if data_frame_util.is_not_empty(de_list_stock_df_one):
            de_list_date = list(de_list_stock_df_one['de_list_date'])[0]
            trade_date_list_df_copy = trade_date_list_df_copy.loc[trade_date_list_df_copy['_id'] <= de_list_date]

        for i in range(0, len(trade_date_list_df_copy), 28):
            try:
                new_df = trade_date_list_df_copy.iloc[i:i + 28]
                first_df = new_df.iloc[0]  # 第一个 DataFrame
                last_df = new_df.iloc[-1]  # 最后一个 DataFrame
                begin_date = first_df.trade_date + ' 09:20:00'
                end_date = last_df.trade_date + ' 15:00:00'

                df = get_minute_data(symbol, '1min', begin_date, end_date)
                if data_frame_util.is_not_empty(df):
                    df = df.rename(columns={
                        "trade_time": "time",
                        "ts_code": "symbol",
                        "vol": "volume",
                    })
                    df['time_tick'] = df['time'].str[11:19]
                    df = df.loc[df['time_tick'] <= '15:00:00']
                    del df['time_tick']
                    df['_id'] = df['symbol'] + '_' + df['time']
                    mongodbUtilV2.insert_mongo(df, db_name)
            except BaseException as e:
                time.sleep(2)
                first_df = new_df.iloc[0]  # 第一个 DataFrame
                last_df = new_df.iloc[-1]  # 最后一个 DataFrame
                begin_date = first_df.trade_date + ' 09:20:00'
                end_date = last_df.trade_date + ' 15:00:00'
                fail_dict = {'begin_date': begin_date,
                             'end_date': end_date,
                             'symbol': symbol,
                             'db_name': db_name
                             }
                fail_df = pd.DataFrame(fail_dict, index=[1])
                mongodbUtilV2.insert_mongo(fail_df, 'one_minute_k_line_bfq_fail')

                logger.error("同步数据出现异常:{},{},{},{}", e, symbol, begin_date, end_date)
        logger.info("同步完数据:{},{}", stock_one.symbol, stock_one.name)


if __name__ == '__main__':
    # get_minute_data('833284.BJ', '1min', '2025-02-28 09:30:00', '2025-02-28 15:00:00')

    query_trade = {"$and": [{"trade_date": {"$gte": "2025-03-08"}}, {"trade_date": {"$lte": "2025-03-18"}}]}
    trade_date_list_df_all = mongodb_util_27017.find_query_data('trade_date_list', query_trade)

    sync_all_stock(trade_date_list_df_all)
