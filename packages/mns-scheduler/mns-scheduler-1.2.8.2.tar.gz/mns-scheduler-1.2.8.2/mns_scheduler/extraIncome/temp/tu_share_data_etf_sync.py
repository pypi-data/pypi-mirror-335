import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_common.api.em.east_money_etf_api as east_money_etf_api
import pandas as pd
from loguru import logger
import time
import mns_common.utils.data_frame_util as data_frame_util
from mns_common.db.MongodbUtil import MongodbUtil
import tushare as ts
from mns_common.db.v2.MongodbUtilV2 import MongodbUtilV2
import mns_scheduler.extraIncome.one_minute.common.db_create_index as db_create_index
import mns_common.constant.extra_income_db_name as extra_income_db_name

mongodb_util_27017 = MongodbUtil('27017')
mongodbUtilV2_27019 = MongodbUtilV2('27019', extra_income_db_name.EXTRA_INCOME)
pro = ts.pro_api('782213d20640249f1dbae50a7f56b22684b8e915a61e435e015579a1')


def get_minute_data(symbol, freq, start_date, end_date):
    # 获取浦发银行60000.SH的历史分钟数据
    df = pro.stk_mins(ts_code=symbol, freq=freq, start_date=start_date, end_date=end_date)
    return df


def sync_etf_one_minute(trade_date_list_df):
    etf_real_time_quotes_df = east_money_etf_api.get_etf_real_time_quotes()
    etf_real_time_quotes_df = classify_symbol(etf_real_time_quotes_df)
    etf_real_time_quotes_df['symbol'] = etf_real_time_quotes_df.apply(
        lambda row: row['symbol'] + '.SZ' if row['classification'] in ['S', 'C']
        else row['symbol'] + '.BJ' if row['classification'] in ['X']
        else row['symbol'] + '.SH',
        axis=1
    )

    db_name = extra_income_db_name.ONE_MINUTE_K_LINE_BFQ_ETF
    db_create_index.create_index(mongodbUtilV2_27019, db_name)
    for stock_one in etf_real_time_quotes_df.itertuples():
        trade_date_list_df_copy = trade_date_list_df.copy()
        symbol = stock_one.symbol
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
                    mongodbUtilV2_27019.insert_mongo(df, db_name)
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
                mongodbUtilV2_27019.insert_mongo(fail_df, db_name + '_fail')

                logger.error("同步数据出现异常:{},{},{},{}", e, symbol, begin_date, end_date)
        logger.info("同步完数据:{},{}", stock_one.symbol, stock_one.name)

    return etf_real_time_quotes_df


def classify_symbol(debt_real_time_quotes_df):
    debt_real_time_quotes_df['classification'] = debt_real_time_quotes_df['market'].apply(
        lambda market: classify_symbol_one(market))
    return debt_real_time_quotes_df


# 单个股票分类
def classify_symbol_one(market):
    if market == 0:
        return 'S'
    else:
        return 'H'


if __name__ == '__main__':
    query_trade = {"$and": [{"trade_date": {"$gte": "2025-03-08"}}, {"trade_date": {"$lte": "2025-03-16"}}]}
    trade_date_list_df_all = mongodb_util_27017.find_query_data('trade_date_list', query_trade)

    sync_etf_one_minute(trade_date_list_df_all)
