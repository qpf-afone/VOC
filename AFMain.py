import sys
from AFStaff import AFStaff

def main():

    staff = AFStaff()
    staff.start(sys.argv)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as msg:
        print(msg)
        sys.exit(1)
