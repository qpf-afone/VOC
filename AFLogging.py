# -*- coding: utf-8 -*-
import logging
import sys
from AFSystem  import SOFTWARE_NAME

# 统一日志文件名，使用软件名
myLogPath = f'{SOFTWARE_NAME}.log'

INFO_TO_USER_Staff = (
"\n[{}] Copyright 2025 Qipengfei. All rights reserved. Version 202X.XX XX. Email: qipengfei79@gmail.com".format(
    SOFTWARE_NAME),
)

INFO_TO_USER_FLOW1 = [
    f'\n[{SOFTWARE_NAME}] <Flow1> 正在检查环境…',
    f'\n[{SOFTWARE_NAME}] <Flow1> 正在读取图片…',
    f'\n[{SOFTWARE_NAME}] <Flow1> 正在进行预测…',
    f'\n[{SOFTWARE_NAME}] <Flow1> 正在导出结果…',
]
INFO_TO_USER_FLOW2 = [
    f'\n[{SOFTWARE_NAME}] <Flow2> 正在检查环境…',
    f'\n[{SOFTWARE_NAME}] <Flow2> 正在训练模型…',
]

INFO_TO_USER_FLOW3 = [
    f'\n[{SOFTWARE_NAME}] <Flow3> 正在检查环境…',
    f'\n[{SOFTWARE_NAME}] <Flow3> 正在验证模型…',
]


def logToUser(strInfo):
    # if os.access[myLogPath, os.W_OK):  # 当文件被excel打开时，这个东东没啥用

    try:
        print(strInfo)
        f_w = open(myLogPath, 'a', encoding='utf8')
        f_w.write(strInfo + '\n')
        f_w.close()
    except IOError:
        print("MSMonitor.log is opened! Please close it and run the program again!")
        sys.exit(0)


def logGetError(info):
    print(info)

    logging.basicConfig(filename=myLogPath,
                        filemode='a',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                        )
    logging.error(info)
    sys.exit(0)


def logGetWarning(info):
    print(info)

    logging.basicConfig(filename=myLogPath,
                        filemode='a',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                        )
    logging.warning(info)

