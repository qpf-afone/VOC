import sys
from AFStaff_server import AFStaff_server   # 把project文件夹没用的全删掉
from AFLogging import logGetError

def main():
    staff=AFStaff_server()
    staff.start(sys.argv)

if __name__ == "__main__":
    try:    
        # 调用web版的程序
        main()
        sys.exit(0)
    except Exception as msg:
        logGetError(msg)  # 使用日志记录异常
        sys.exit(1)

