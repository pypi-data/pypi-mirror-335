import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import mns_common.utils.cmd_util as cmd_util
import mns_common.utils.data_frame_util as data_frame_util
from loguru import logger
from mns_common.db.MongodbUtil import MongodbUtil
import time

mongodb_util = MongodbUtil('27017')

MAX_NUMBER_KEY = 'max_number_key'
# 定时任务 python名称
REAL_TIME_SCHEDULER_NAME = "sync_realtime_quotes_task"
# 实时同步 python名称
REAL_TIME_TASK_NAME = "realtime_quotes_now_sync"
# 实时同步 bat
REAL_TIME_TASK_NAME_PATH = 'H:\\real_time_task.bat'
# 定时任务 bat
REAL_TIME_SCHEDULER_NAME_PATH = 'H:\\real_time_scheduler.bat'


# 关闭实时行情任务
def real_time_sync_task_close():
    all_cmd_processes = cmd_util.get_all_process()
    if data_frame_util.is_empty(all_cmd_processes):
        return False
    all_cmd_processes_real_time_task = get_real_time_quotes_task(all_cmd_processes)
    if data_frame_util.is_empty(all_cmd_processes_real_time_task):
        return False
    for match_task_one in all_cmd_processes_real_time_task.itertuples():
        try:
            processes_pid = match_task_one.process_pid
            # 关闭当前进程
            cmd_util.kill_process_by_pid(processes_pid)
        except BaseException as e:
            logger.error("关闭实时行情任务异常:{}", e)


# 重开定时任务同步
def real_time_sync_task_open():
    all_cmd_processes = cmd_util.get_all_process()
    if data_frame_util.is_empty(all_cmd_processes):
        return False
    all_cmd_processes_real_time_task = get_real_time_quotes_task(all_cmd_processes)
    if data_frame_util.is_empty(all_cmd_processes_real_time_task):
        # 重开定时任务
        cmd_util.open_bat_file(REAL_TIME_SCHEDULER_NAME_PATH)
        # 防止太快重开多个
        time.sleep(3)


def get_real_time_quotes_task(all_cmd_processes):
    return all_cmd_processes[
        (all_cmd_processes['total_info'].str.contains(REAL_TIME_SCHEDULER_NAME, case=False, na=False))
        | (all_cmd_processes['total_info'].str.contains(REAL_TIME_TASK_NAME, case=False, na=False))]
