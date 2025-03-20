import logging
import os
import sys
import inspect
from datetime import datetime
from colorama import init, Fore, Style

# 初始化 colorama
init(autoreset=True)

# 创建并配置日志记录器
lyy_logger = logging.getLogger("lyylog")
called_times = 0
called_times_write_log = 0
last_date_dict = {} #记录各个日志等级的最后日期
last_date = None
if not os.path.isdir(r"lyylog2"):
    os.mkdir(r"lyylog2")
# 自定义格式化函数
def format_log_message(level, msg):
    global last_date
    add_enter = ""#是否要在行前插入一行。新日期，或者同日期新日志类型都插入一行
    get_date, current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")#利用日期和时间的间隔分开

    #计算日期字段： 不可省略日期的情况：如果是最初运行时，或者该等级日志今天还是刚运行
    if (get_date != last_date_dict.get(level)):
        add_enter = "\n"
        current_date= "----------" + get_date + "---------\n"
        last_date_dict[level] = get_date
    else:
        current_date = "" #为了节省空间，当天不是第一次运行时，省略日期。

    
    #等级字段放弃，因为就几个字母。
    #计算日志等级字段：如果上次日志等级跟这次不一样，则记录前添加一个换行并更新最后日志等级

    if last_date_dict.get("last_level") != level:
        add_enter = "\n"
        last_date_dict["last_level"] = level

    
    frame = inspect.currentframe().f_back.f_back
    filename = frame.f_code.co_filename
    #print("filename -",filename)
    line_number = frame.f_lineno
    called_log_function_name =  frame.f_code.co_name 
    log_msg = f"{add_enter}{current_date}[{current_time}] {level} [{filename}:{line_number}][{called_log_function_name}] {msg}"

    return log_msg


def get_caller_module_file_name(level=2, debug=False):
    """
    获取模块名，多加一个f_back则往上一级，最高到调用了此log2模块的主模块名
    """
    try:
        frame = sys._getframe(level)
        if debug: print("frame = ", frame)
        module = inspect.getmodule(frame)
        if debug: print("module = ", module)
        if module:
            module_filename = os.path.basename(module.__file__)        
            module_name, _ = os.path.splitext(module_filename)  # 去掉扩展名
            if debug: print("get module_name=" + module_name)
            return module.__file__
        else:
            if debug: print("Caller module name: unknown")
            return "unknown_source"
    except Exception as e:
        if debug: print(f"Error getting caller module: {e}")
        return "unknown_source"

def get_main_module_function_name(level = 2, debug=False):
    """
    主模块main.py中的函数process_data调用了logwarn,则在logwarn中获取到process_data
    """
    frame = inspect.currentframe().f_back.f_back if level==2 else inspect.currentframe().f_back.f_back.f_back
    if debug: print("frame = ", frame)
    print("==called log funname===", frame.f_code.co_name)
    return frame.f_code.co_name

def write_log(text, directory=".",if_print=False):
    """
    简单写文件。

    Args:
    text (str): The text to append to the file.
    directory (str): The directory where the file will be saved. Default is the current directory.

    Returns:
    None
    """
    global called_times_write_log
    # Get the current date
    current_date, current_time  = datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")
   
    # Create the filename with the current date
    filename = f"lyylog2/write_log_{current_date}.txt"
    if called_times_write_log == 0:
        print(f"{Fore.CYAN} ---------- write_log to: {filename} ----------{Style.RESET_ALL}")
        called_times_write_log+=1
    # Create the full file path
    file_path = os.path.join(directory, filename)
    
    text = "["+current_time + "] " + str(text)
    # Open the file in append mode and write the text
    with open(file_path, "a",encoding="utf-8") as file:
        file.write(text + "\n")
    if os.isatty(sys.stdout.fileno()) and if_print:
        print(f"[Write log] : "+text)

def logg(msg,caller_module_file_name, level="info", debug=False, console=True, **kwargs):
    global called_times
    # 将所有参数拼接成一个字符串
    if debug: print("called flname= ",caller_module_file_name)
    if caller_module_file_name is None:
        try:
            # 使用更可靠的路径获取方式
            caller_frame = inspect.currentframe().f_back.f_back
            caller_module = inspect.getmodule(caller_frame)
            caller_module_file_name = getattr(caller_module, "__file__", "unknown_source")
        except Exception as e:
            caller_module_file_name = "unknown_source"
    
    # 安全处理路径
    if caller_module_file_name:
        module_dirname = os.path.dirname(caller_module_file_name)
    else:
        module_dirname = "unknown_directory"

    module_filename = os.path.basename(caller_module_file_name)
    module_basename_only, _ = os.path.splitext(module_filename)#去掉扩展名
    # 根据日志等级设置日志级别和文件名
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    
    level = level.lower()
    log_level = log_levels.get(level, logging.INFO)
    lyy_logger.setLevel(log_level)
    
    # 生成包含日期的日志文件名
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = f"lyylog2/{module_basename_only}_lyylog2_{date_str}.log"
    if called_times == 0:
        print(f"{Fore.CYAN} >>>>>>>>>>>>>>> {log_file} <<<<<<<<<<<<<<< {Style.RESET_ALL}")
        called_times += 1
    # 创建文件处理器以写入日志文件
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(message)s")
    file_handler.setFormatter(formatter)
    lyy_logger.addHandler(file_handler)

    if debug: print("==="*20, "msg="+msg, "\n","module_dirname="+module_dirname)
    # 记录日志
    lyy_logger.log(log_level, msg.replace(module_dirname,"."))
    
    # 关闭文件处理器
    for handler in lyy_logger.handlers:
        handler.flush()
        handler.close()

    # 移除处理器以防止重复记录
    lyy_logger.handlers = []
    
    # 打印到终端，根据日志等级使用不同颜色
    if console:
        console_msg = msg
        color_map = {
            "debug": Fore.BLUE,
            "info": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "critical": Fore.MAGENTA
        }
        color = color_map.get(level, Fore.WHITE)
        print(f"{color}{console_msg}{Style.RESET_ALL}")

def log(*args, **kwargs):
    msg = ' '.join(map(str, args))
    if kwargs:
        msg += ' ' + ' '.join(f"{k}={v}" for k, v in kwargs.items())
    msg = format_log_message("info", msg)
    caller_module_file_name = get_caller_module_file_name(level=1, debug=False)
    logg(msg, caller_module_file_name=caller_module_file_name, level="info", **kwargs)

def logerr(*args, **kwargs):
    msg = ' '.join(map(str, args))
    if kwargs:
        msg += ' ' + ' '.join(f"{k}={v}" for k, v in kwargs.items())
    msg = format_log_message("error", msg)
    caller_module_name = get_caller_module_file_name(level=1, debug=False)
    logg(msg, caller_module_file_name=caller_module_name, level="error", **kwargs)

def logwarn(*args, **kwargs):
    msg = ' '.join(map(str, args))
    if kwargs:
        msg += ' ' + ' '.join(f"{k}={v}" for k, v in kwargs.items())
    msg = format_log_message("warn", msg)
    caller_module_file_name = get_caller_module_file_name(level=1, debug=False)
    logg(msg, caller_module_file_name=caller_module_file_name, level="warning", **kwargs)

logerror = logerr
logdebug = log
log("裸 的")

if __name__ == "__main__":
    list1 = [1, 2, 3]
    log("这是一条info级别的日志信息。", "太好了", list1)
    logerr("这是一条error级别的日志信息。")
    write_log("这是写的日志")