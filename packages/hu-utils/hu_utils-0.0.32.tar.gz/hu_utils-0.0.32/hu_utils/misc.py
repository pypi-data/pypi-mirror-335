# 导入所需的标准库
import datetime  # 处理日期和时间
import functools  # 提供高阶函数和操作可调用对象的工具
import glob      # 提供Unix风格路径名模式扩展
import os        # 提供操作系统相关的功能
import subprocess  # 提供创建子进程的功能
import sys         # 提供Python运行时环境的变量和函数
import time        # 提供时间相关的函数
from collections import defaultdict, deque  # 导入默认字典和双端队列
from typing import Iterator, List, Tuple    # 导入类型提示相关的类型

# 导入第三方库
import numpy as np      # 科学计算库
import pytz            # 时区处理库

# 导入本地模块
# from . import dist_util           # 使用相对导入从当前包导入dist模块
# from utils import arg_util  # 参数处理工具

# 创建一个偏函数,将subprocess.call的shell参数固定为True
os_system = functools.partial(subprocess.call, shell=True)

def echo(info):
    """打印带有时间戳和代码位置信息的日志
    没用到, 测试是否可行的. 
    """
    # 使用echo命令打印信息,包含:
    # - 当前时间戳
    # - 调用该函数的文件名
    # - 调用该函数的代码行号
    # - 实际信息内容
    # os_system(f'echo "[$(date "+%m-%d-%H:%M:%S")] ({os.path.basename(sys._getframe().f_back.f_code.co_filename)}, line{sys._getframe().f_back.f_lineno})=> {info}"')
    os_system(f'echo "[$(date "+%m-%d-%H:%M:%S")] ({os.path.basename(sys._getframe().f_back.f_code.co_filename)}, line{sys._getframe().f_back.f_lineno})=> {info}"')

def os_system_get_stdout(cmd):
    """执行系统命令并返回标准输出"""
    # 执行shell命令并捕获其标准输出
    # shell=True 允许执行shell命令
    # stdout=subprocess.PIPE 捕获标准输出
    # decode('utf-8') 将bytes转换为字符串
    return subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

def os_system_get_stdout_stderr(cmd):
    """执行系统命令并返回标准输出和错误输出,带有超时重试机制"""
    cnt = 0  # 超时计数器
    while True:
        try:
            # 执行命令,设置30秒超时
            sp = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        except subprocess.TimeoutExpired:  # 捕获超时异常
            cnt += 1  # 增加超时计数
            print(f'[fetch free_port file] timeout cnt={cnt}')  # 打印超时信息
        else:
            # 成功执行则返回标准输出和错误输出
            return sp.stdout.decode('utf-8'), sp.stderr.decode('utf-8')

def time_str(fmt='[%m-%d %H:%M:%S]'):
    """返回上海时区的格式化时间字符串"""
    # 获取当前时间,设置时区为上海
    # 按照指定格式返回时间字符串
    return datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai')).strftime(fmt)


def _change_builtin_print(is_master):
    # 导入 builtins 模块
    import builtins as __builtin__
    
    # 保存原始的 print 函数
    builtin_print = __builtin__.print
    # 如果 builtin_print 不是函数类型,直接返回
    if type(builtin_print) != type(open):
        return
    
    # 定义新的 print 函数
    def prt(*args, **kwargs):
        # 从 kwargs 中提取特殊参数
        force = kwargs.pop('force', False)     # 是否强制打印
        clean = kwargs.pop('clean', False)     # 是否不添加额外信息
        deeper = kwargs.pop('deeper', False)   # 是否获取更深层的调用栈信息
        
        # 只有主进程或强制打印时才执行打印
        if is_master or force:
            if not clean:
                # 获取调用栈信息
                f_back = sys._getframe().f_back
                if deeper and f_back.f_back is not None:
                    f_back = f_back.f_back
                # 获取文件名(取最后24个字符)
                file_desc = f'{f_back.f_code.co_filename:25s}'[-25:]
                # 打印格式: [时间] (文件名, 行号)=> 实际内容
                builtin_print(f'{time_str()} ({file_desc}, line{f_back.f_lineno:-4d})=>', *args, **kwargs)
            else:
                # clean 模式下直接打印,不添加额外信息
                builtin_print(*args, **kwargs)
    
    # 替换 builtins 模块中的 print 函数
    __builtin__.print = prt

class SyncPrint(object):
    """
    同步打印类,将输出同时写入终端和文件
    用于记录训练日志
    """
    def __init__(self, local_output_dir, sync_stdout=True):
        self.sync_stdout = sync_stdout
        self.terminal_stream = sys.stdout if sync_stdout else sys.stderr
        fname = os.path.join(local_output_dir, 'stdout.log' if sync_stdout else 'stderr.txt')
        existing = os.path.exists(fname)
        self.file_stream = open(fname, 'a')
        if existing:
            self.file_stream.write('\n'*7 + '='*55 + f'   RESTART {time_str()}   ' + '='*55 + '\n')
        self.file_stream.flush()
        self.enabled = True
    
    def write(self, message):
        self.terminal_stream.write(message)
        self.file_stream.write(message)
    
    def flush(self):
        self.terminal_stream.flush()
        self.file_stream.flush()
    
    def close(self):
        if not self.enabled:
            return
        self.enabled = False
        self.file_stream.flush()
        self.file_stream.close()
        if self.sync_stdout:
            sys.stdout = self.terminal_stream
            sys.stdout.flush()
        else:
            sys.stderr = self.terminal_stream
            sys.stderr.flush()
    
    def __del__(self):
        self.close()

class DistLogger(object):
    def __init__(self, lg, verbose):
        self._lg, self._verbose = lg, verbose
    
    @staticmethod
    def do_nothing(*args, **kwargs):
        pass
    
    def __getattr__(self, attr: str):
        return getattr(self._lg, attr) if self._verbose else DistLogger.do_nothing

class SmoothedValue(object):
    """Track a series of values and provide access to smoothed values over a
    window or the global series average.
    用于跟踪一系列值并提供滑动窗口的平均值等统计信息
    常用于训练过程中记录损失值等指标
    """
    def __init__(self, window_size=30, fmt=None):
        if fmt is None:
            fmt = "{median:.4f} ({global_avg:.4f})"
        self.deque = deque(maxlen=window_size)  # 使用双端队列存储最近的值
        self.total = 0.0  # 所有值的总和
        self.count = 0    # 值的总数
        self.fmt = fmt    # 输出格式
    
    def update(self, value, n=1):
        self.deque.append(value)
        self.count += n
        self.total += value * n
    
    @property
    def median(self):
        return np.median(self.deque) if len(self.deque) else 0
    
    @property
    def avg(self):
        return sum(self.deque) / (len(self.deque) or 1)
    
    @property
    def global_avg(self):
        return self.total / (self.count or 1)
    
    @property
    def max(self):
        return max(self.deque)
    
    @property
    def value(self):
        return self.deque[-1] if len(self.deque) else 0
    
    def time_preds(self, counts) -> Tuple[float, str, str]:
        remain_secs = counts * self.median
        return remain_secs, str(datetime.timedelta(seconds=round(remain_secs))), time.strftime("%Y-%m-%d %H:%M", time.localtime(time.time() + remain_secs))
    
    def __str__(self):
        return self.fmt.format(
            median=self.median,
            avg=self.avg,
            global_avg=self.global_avg,
            max=self.max,
            value=self.value)

class MetricLogger(object):
    """
    指标记录器,用于训练过程中记录和打印各种指标
    包括损失值、时间统计等
    """
    def __init__(self, delimiter='  '):
        self.meters = defaultdict(SmoothedValue)  # 存储不同指标的SmoothedValue对象
        self.delimiter = delimiter
        self.iter_end_t = time.time()
        self.log_iters = []
    
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v is None:
                continue
            if hasattr(v, 'item'): v = v.item()
            # assert isinstance(v, (float, int)), type(v)
            assert isinstance(v, (float, int))
            self.meters[k].update(v)
    
    def __getattr__(self, attr):
        if attr in self.meters:
            return self.meters[attr]
        if attr in self.__dict__:
            return self.__dict__[attr]
        raise AttributeError("'{}' object has no attribute '{}'".format(
            type(self).__name__, attr))
    
    def __str__(self):
        loss_str = []
        for name, meter in self.meters.items():
            if len(meter.deque):
                loss_str.append(
                    "{}: {}".format(name, str(meter))
                )
        return self.delimiter.join(loss_str)
    
    def add_meter(self, name, meter):
        self.meters[name] = meter
    
    def log_every(self, start_it, max_iters, itrt, print_freq, header=None):
        self.log_iters = set(np.linspace(0, max_iters-1, print_freq, dtype=int).tolist())
        self.log_iters.add(start_it)
        if not header:
            header = ''
        start_time = time.time()
        self.iter_end_t = time.time()
        self.iter_time = SmoothedValue(fmt='{avg:.4f}')
        self.data_time = SmoothedValue(fmt='{avg:.4f}')
        space_fmt = ':' + str(len(str(max_iters))) + 'd'
        log_msg = [
            header,
            '[{0' + space_fmt + '}/{1}]',
            'eta: {eta}',
            '{meters}',
            'time: {time}',
            'data: {data}'
        ]
        log_msg = self.delimiter.join(log_msg)
        
        if isinstance(itrt, Iterator) and not hasattr(itrt, 'preload') and not hasattr(itrt, 'set_epoch'):
            for i in range(start_it, max_iters):
                obj = next(itrt)
                self.data_time.update(time.time() - self.iter_end_t)
                yield i, obj
                self.iter_time.update(time.time() - self.iter_end_t)
                if i in self.log_iters:
                    eta_seconds = self.iter_time.global_avg * (max_iters - i)
                    eta_string = str(datetime.timedelta(seconds=int(eta_seconds)))
                    print(log_msg.format(
                        i, max_iters, eta=eta_string,
                        meters=str(self),
                        time=str(self.iter_time), data=str(self.data_time)), flush=True)
                self.iter_end_t = time.time()
        else:
            if isinstance(itrt, int): itrt = range(itrt)
            for i, obj in enumerate(itrt):
                self.data_time.update(time.time() - self.iter_end_t)
                yield i, obj
                self.iter_time.update(time.time() - self.iter_end_t)
                if i in self.log_iters:
                    eta_seconds = self.iter_time.global_avg * (max_iters - i)
                    eta_string = str(datetime.timedelta(seconds=int(eta_seconds)))
                    print(log_msg.format(
                        i, max_iters, eta=eta_string,
                        meters=str(self),
                        time=str(self.iter_time), data=str(self.data_time)), flush=True)
                self.iter_end_t = time.time()
        
        total_time = time.time() - start_time
        total_time_str = str(datetime.timedelta(seconds=int(total_time)))
        print('{}   Total time:      {}   ({:.3f} s / it)'.format(
            header, total_time_str, total_time / max_iters), flush=True)

def glob_with_latest_modified_first(pattern, recursive=False):
    return sorted(glob.glob(pattern, recursive=recursive), key=os.path.getmtime, reverse=True)

def create_npz_from_sample_folder(sample_folder: str):
    """
    Builds a single .npz file from a folder of .png samples. Refer to DiT.
    """
    import os, glob
    import numpy as np
    from tqdm import tqdm
    from PIL import Image
    
    samples = []
    pngs = glob.glob(os.path.join(sample_folder, '*.png')) + glob.glob(os.path.join(sample_folder, '*.PNG'))
    assert len(pngs) == 50_000, f'{len(pngs)} png files found in {sample_folder}, but expected 50,000'
    for png in tqdm(pngs, desc='Building .npz file from samples (png only)'):
        with Image.open(png) as sample_pil:
            sample_np = np.asarray(sample_pil).astype(np.uint8)
        samples.append(sample_np)
    samples = np.stack(samples)
    assert samples.shape == (50_000, samples.shape[1], samples.shape[2], 3)
    npz_path = f'{sample_folder}.npz'
    np.savez(npz_path, arr_0=samples)
    print(f'Saved .npz file to {npz_path} [shape={samples.shape}].')
    return npz_path