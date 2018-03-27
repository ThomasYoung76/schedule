# -*- coding:utf-8 -*-
"""
    Function        :    Script scheduler
    Author          :
    Create time     :
    Function List   :

"""
import os
import sys
import re
import time
import datetime
import getopt
import random
import subprocess

# backup logs
def backup():
    pass

SCRIPT_PATH = r"E:\workspace\tdsql\script"
CONFIG_PATH = r"E:\workspace\tdsql\config\script.txt"


def get_args():
    times = 1
    is_random = False
    execute_time = None

    help_info = """Usage: python execute.py {casename} [-t <times>] [-r <is_random>] [-e <execute_time>]
or: python execute.py {casename} [--times=<times>] [--is_random=<is_random>] [--execute_time=<execute_time>] 
{casename}  : first parameter and required. it means case_id. and support asterisk wildcard. if it is '*', then it will execute all scripts
-t  : times(int). scripts will be execute many times. default 1. if times equals 0 means scripts will be executed forever.
-r  : is_random(bool). whether execute scripts in random order or not. default False, means execute scripts in normal order. 
-e  : execute_time(str, formatted like "10:10"). scripts will be executed on execute_time referred. """

    # the first parameter must exist and not start with '-'
    try:
        case_name = sys.argv[1]
        # 支持写法 python scripts -h, 同时也支持python scripts casename -h
        if case_name == '-h':
            sys.argv.insert(1, 'casename')
        else:
            assert not case_name.startswith('-')
    except:
        print("Error: parameter {casename} is needed or parameter {casename} cannot start with '-'")
        sys.exit(1002)

    try:
        # h 就表示该选项无参数，r:表示 r 选项后需要有参数
        opts, args = getopt.getopt(sys.argv[2:], "ht:r:e:", ["times=", "is_random=", "execute_time="])
    except getopt.GetoptError:
        print ('Error: execute.py {casename} [-t <times>] [-r <is_random>] [-e <execute_time>]')
        print ('   or: execute.py {casename} [--times=<times>] [--is_random=<is_random>] [--execute_time=<execute_time>]')
        sys.exit(1001)

    # 获取选项及对应的参数
    for opt, arg in opts:
        if opt == "-h":
            print(help_info)
            sys.exit(0)
        elif opt in ("-t", "--times"):
            try:
                times = int(arg)
                assert times >= 0
            except:
                print("Error, parameter <times> must be integers")
                sys.exit(1003)
        elif opt in ("-r", "--is_random"):
            try:
                assert arg.title() in ["True", "False"]
            except:
                print("Error, parameter <is_random> must be True or False")
                sys.exit(1004)
            is_random = eval(arg.title())
        elif opt in ("-e", "--execute_time"):
            try:
                datetime.datetime.strptime(arg, "%H:%M")
            except:
                print("Error. parameter <execute_time> is not time data, cannot match format '%H:%M")
                sys.exit(1005)
            execute_time = arg
    return (case_name, times, is_random, execute_time)

def str_to_time(str_execute_time):
    """
    format "%H:%M" to datetime
    :param str_execute_time: str , format '%H:%M', eg: "10:00"
    :return:
    """
    start_time = datetime.datetime.now()
    nyear, nmonth, nday = start_time.year, start_time.month, start_time.day
    execute_time = datetime.datetime.strptime("%s-%s-%s %s" % (nyear, nmonth, nday, str_execute_time), "%Y-%m-%d %H:%M")
    # 若设定的执行时间早于当前时间，则天数加1
    if execute_time < datetime.datetime.now():
        execute_time = execute_time + datetime.timedelta(days=1)
    return execute_time


# # generate scripts tree
# # it can get whole tree on Unit. on Windows it not include files floor.
# with open(CONFIG_PATH, 'w') as wf:
#     result = subprocess.Popen('tree %s'%SCRIPT_PATH, shell=True, stdout=wf)

def scan_dir(dir_path, is_write=True):
    """
    scan directiry and get all python scripts
    :param dir_path: str, script path
    :param is_write: bool, write scripts to file
    :return:
    """
    list_file_path = []    # to store script files path
    # scan directory and get all python scripts
    for root, dirs, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith('.py'):
                list_file_path.append(os.path.join(root, file_name))

    # writes all python scripts to configuration file
    if is_write:
        with open(CONFIG_PATH, 'w') as wf:
            for str_file in list_file_path:
                wf.write(str_file + '\n')
    return list_file_path

def filter_case(str_case_name, script_path):
    """
    filter case to be excuted from case path which referred by param dir_path
    :param str_case_name: str, casename. the first parameter of the command to excute script
    :param script_path: str, script path
    :return: list. [(case_id1, case_path1), (case_id2, case_path2)]
    """
    # sys.arg[0] is script name，sys.arg[1] is the first parameter {casename}
    list_all_cases = scan_dir(script_path)
    list_execute_cases = [] # cases to be executed
    # casename 支持Unit的通配符*
    str_case_pattern = str_case_name.replace('*', '.*')
    for case in list_all_cases:
        # case 格式为E:\workspace\tdsql\script\02.GroupShrad\02_2.py， 过滤出其中的case_id
        list_case_id = re.findall(r'(\w+)\.py', case)
        if not list_case_id:
            print("Warning: did not find case_id in case_path. case_path : %s" % case)
            continue
        try:
            case_id = list_case_id[0]
        except:
            print("Error: case is not illegal. case_path is : %s" % case)
            sys.exit(2001)
        # 匹配case_id，获得期望待执行的case_id
        list_expect_case = re.findall(str_case_pattern, case_id)
        if not list_expect_case:
            continue    # 未匹配到待执行的case_id跳过继续向下查找
        try:
            str_expect_case = list_expect_case[0]
        except:
            print("Error: get expect case id error. match case pattern: %s. case id: %s. "%(str_case_pattern, case_id))
            sys.exit(2002)
        list_execute_cases.append((str_expect_case, case))
    return list_execute_cases

def filter_case_by_file(case_id_file, script_path):
    """ 从用例ID文件中过滤用例"""
    list_all_cases = scan_dir(script_path)
    dict_all_cases = {}
    list_execute_cases = []  # cases to be executed

    with open(case_id_file) as rf:
        list_case_id = rf.readlines()
    list_case_id = list(map(lambda x:x.strip(), list_case_id)) # 去除左右两边的换行符和空格等
    # list_case_id = list(set(list_case_id))      # 去除重复case_id

    for case in list_all_cases:
        list_case = re.findall(r'(\w+)\.py', case)
        if not list_case:
            print("Warning: did not find case_id in case_path. case_path : %s" % case)
            continue
        try:
            raw_case_id = list_case[0]
        except:
            print("Error: case is not illegal. case_path is : %s" % case)
            sys.exit(2001)
        dict_all_cases[raw_case_id] = case
    # 遍历文件中case_id，存在的id加入list_eecute_cases, （不存在则打印出来，暂时这么处理）
    for case_id in list_case_id:
        if case_id in dict_all_cases.keys():
            list_execute_cases.append((case_id, dict_all_cases.get(case_id)))
        else:
            print("Warn: case_id %s is not found"%case_id)
    return list_execute_cases

def execute_script(str_case_name, int_times, is_rand):
    # 若包含路径分隔符，则认为casename是路径，从路径文件中读取case_id并执行
    if os.sep in str_case_name:
        list_execute_cases = filter_case_by_file(str_case_name, SCRIPT_PATH)
    else:
        list_execute_cases = filter_case(str_case_name, SCRIPT_PATH)
    if int_times == 0:  # 若times为0，则死循环执行脚本。
        int_times = -1
    while int_times:
        # 打乱列表顺序
        if is_rand:
            random.shuffle(list_execute_cases)
        # 执行脚本
        for str_case_id, str_case_path in list_execute_cases:
            subprocess.Popen('python %s' % str_case_path, shell=True)
            time.sleep(1)
        int_times -= 1

def main():
    # step1：get args
    str_case_name, int_times, is_rand, str_execute_time = get_args()
    # 当前时间小于执行时间则进入等待，到了预定时间后执行，执行完之后execute_time的日期增加了1天，便继续等到下一天再执行
    # 这里设置linux craontab命令应该会更好些
    crontab = True
    while crontab:
        if str_execute_time:
            execute_time = str_to_time(str_execute_time)
            while datetime.datetime.now() < execute_time:
                time.sleep(1)
        else:
            crontab = False
        # execute cases
        execute_script(*get_args()[:3])



if __name__ == "__main__":
    main()
