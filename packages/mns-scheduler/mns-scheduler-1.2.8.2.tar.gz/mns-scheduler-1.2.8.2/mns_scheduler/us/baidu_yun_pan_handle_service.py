import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
from bypy import ByPy
from mns_common.db.MongodbUtil import MongodbUtil
import tempfile
from loguru import logger
import akshare as ak

mongodb_util = MongodbUtil('27017')

import subprocess


def get_file_list(path):
    """
    获取百度网盘指定路径下的文件列表
    :param path: 百度网盘中的路径，例如 '/我的资源'
    :return: 文件列表
    """
    try:
        # 调用 bypy list 命令
        result = subprocess.run(['bypy', 'list', path], capture_output=True, text=True, check=True)

        # 输出结果
        if result.returncode == 0:
            file_list = result.stdout.splitlines()  # 按行分割结果
            return file_list
        else:
            logger.error("获取文件路径异常:{}", result.stderr)
            return []
    except subprocess.CalledProcessError as e:
        logger.error("获取文件路径异常:{}", e)
        return []


def upload_to_baidu(file_name, folder_name, data_df):
    bp = ByPy()
    file_name = file_name + '.csv'
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        data_df.to_csv(temp_file, index=False)
        temp_file_path = temp_file.name  # 获取临时文件的路径

    # 上传临时文件到百度云
    remote_path = f'/{folder_name}/{file_name}'
    result = bp.upload(temp_file_path, remote_path)
    if result == 0:
        logger.info("上传成功:{}", file_name)
    else:
        logger.error("上传失败:{}", file_name)
    return result


def mkdir_baidu_new_folder(remote_path):
    bp = ByPy()
    try:
        # 调用 mkdir 方法创建文件夹
        result = bp.mkdir(remote_path)

        if result == 0:
            logger.info("成功创建文件夹:{}", remote_path)
        else:
            logger.error("创建文件夹失败:{}", result)

    except Exception as e:
        logger.error("创建文件夹失败:{}", e)


def del_baidu_old_folder(remote_path):
    bp = ByPy()
    try:
        # 调用 mkdir 方法创建文件夹
        result = bp.delete(remote_path)

        if result == 0:
            logger.info("成功删除文件夹:{}", remote_path)
        else:
            logger.error("删除文件夹失败:{}", result)

    except Exception as e:
        logger.error("删除文件夹失败:{}", e)


if __name__ == '__main__':
    folder_name1 = '/美股/不复权日线'
    mkdir_baidu_new_folder(folder_name1)
    # get_file_list(folder_name1)
    stock_us_spot_em_df = ak.stock_us_spot_em()
    stock_us_spot_em_df = stock_us_spot_em_df.rename(columns={
        "序号": "index",
        "代码": "symbol",
        "名称": "name",
        "涨跌额": "change_price",
        "涨跌幅": "chg",
        "开盘价": "open",
        "最高价": "high",
        "最低价": "low",
        "最新价": "now_price",
        "昨收价": "last_price",
        "总市值": "total_mv",
        "市盈率": "pe",
        "成交量": "volume",
        "成交额": "amount",
        "振幅": "pct_chg",
        "换手率": "exchange"
    })
    stock_us_spot_em_df = stock_us_spot_em_df.sort_values(by=['amount'], ascending=False)
    stock_us_spot_em_df = stock_us_spot_em_df.fillna(0)
    stock_us_spot_em_df = stock_us_spot_em_df.loc[stock_us_spot_em_df['total_mv'] != 0]
    for stock_one in stock_us_spot_em_df.itertuples():
        try:
            symbol = stock_one.symbol
            name = stock_one.name
            query = {'symbol': symbol, 'amount': {"$gt": 0}}
            us_stock_bfq_daily_df_one = mongodb_util.find_query_data('us_stock_bfq_daily', query)
            del us_stock_bfq_daily_df_one['_id']
            del us_stock_bfq_daily_df_one['name']
            file_name_one = name + '_' + symbol
            upload_to_baidu(file_name_one, folder_name1, us_stock_bfq_daily_df_one)

        except BaseException as e:
            logger.error("同步数据发生异常:{}", e)

# data_df = mongodb_util.find_query_data('us_stock_bfq_daily', query={'name': file_name1})
# upload_to_baidu(file_name1, folder_name1, data_df)


