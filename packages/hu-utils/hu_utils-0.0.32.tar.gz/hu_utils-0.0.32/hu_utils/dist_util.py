import datetime
import functools
import os
import sys
import time
import builtins
from collections import defaultdict, deque
from pathlib import Path
from typing import List, Union, Tuple

import torch
import torch.distributed as tdist
import torch.multiprocessing as mp
import numpy as np
from .misc import SyncPrint, _change_builtin_print

__rank, __local_rank, __world_size, __device = 0, 0, 1, 'cuda' if torch.cuda.is_available() else 'cpu'
__initialized = False


def initialized():
    return __initialized


def initialize(fork=False, backend='nccl', gpu_id_if_not_distibuted=0, timeout=30):
    global __device
    if not torch.cuda.is_available():
        print(f'[dist initialize] cuda is not available, use cpu instead', file=sys.stderr)
        return
    elif 'RANK' not in os.environ:
        torch.cuda.set_device(gpu_id_if_not_distibuted)
        __device = torch.empty(1).cuda().device
        print(f'[dist initialize] env variable "RANK" is not set, use {__device} as the device', file=sys.stderr)
        return
    # then 'RANK' must exist
    global_rank, num_gpus = int(os.environ['RANK']), torch.cuda.device_count()
    local_rank = global_rank % num_gpus
    torch.cuda.set_device(local_rank)
    
    # ref: https://github.com/open-mmlab/mmcv/blob/master/mmcv/runner/dist_utils.py#L29
    if mp.get_start_method(allow_none=True) is None:
        method = 'fork' if fork else 'spawn'
        print(f'[dist initialize] mp method={method}')
        mp.set_start_method(method)
    tdist.init_process_group(backend=backend, timeout=datetime.timedelta(seconds=timeout*60))
    
    global __rank, __local_rank, __world_size, __initialized
    __local_rank = local_rank
    __rank, __world_size = tdist.get_rank(), tdist.get_world_size()
    __device = torch.empty(1).cuda().device
    __initialized = True
    
    assert tdist.is_initialized(), 'torch.distributed is not initialized!'
    print(f'[lrk={get_local_rank()}, rk={get_rank()}]')


def get_rank():
    return __rank


def get_local_rank():
    return __local_rank


def get_world_size():
    return __world_size


def get_device():
    return __device


def set_gpu_id(gpu_id: int):
    if gpu_id is None: return
    global __device
    if isinstance(gpu_id, (str, int)):
        torch.cuda.set_device(int(gpu_id))
        __device = torch.empty(1).cuda().device
    else:
        raise NotImplementedError


def is_master():
    return __rank == 0


def is_local_master():
    return __local_rank == 0


def new_group(ranks: List[int]):
    if __initialized:
        return tdist.new_group(ranks=ranks)
    return None


def barrier():
    if __initialized:
        tdist.barrier()


def allreduce(t: torch.Tensor, async_op=False):
    if __initialized:
        if not t.is_cuda:
            cu = t.detach().cuda()
            ret = tdist.all_reduce(cu, async_op=async_op)
            t.copy_(cu.cpu())
        else:
            ret = tdist.all_reduce(t, async_op=async_op)
        return ret
    return None


def allgather(t: torch.Tensor, cat=True) -> Union[List[torch.Tensor], torch.Tensor]:
    if __initialized:
        if not t.is_cuda:
            t = t.cuda()
        ls = [torch.empty_like(t) for _ in range(__world_size)]
        tdist.all_gather(ls, t)
    else:
        ls = [t]
    if cat:
        ls = torch.cat(ls, dim=0)
    return ls


def allgather_diff_shape(t: torch.Tensor, cat=True) -> Union[List[torch.Tensor], torch.Tensor]:
    if __initialized:
        if not t.is_cuda:
            t = t.cuda()
        
        t_size = torch.tensor(t.size(), device=t.device)
        ls_size = [torch.empty_like(t_size) for _ in range(__world_size)]
        tdist.all_gather(ls_size, t_size)
        
        max_B = max(size[0].item() for size in ls_size)
        pad = max_B - t_size[0].item()
        if pad:
            pad_size = (pad, *t.size()[1:])
            t = torch.cat((t, t.new_empty(pad_size)), dim=0)
        
        ls_padded = [torch.empty_like(t) for _ in range(__world_size)]
        tdist.all_gather(ls_padded, t)
        ls = []
        for t, size in zip(ls_padded, ls_size):
            ls.append(t[:size[0].item()])
    else:
        ls = [t]
    if cat:
        ls = torch.cat(ls, dim=0)
    return ls


def broadcast(t: torch.Tensor, src_rank) -> None:
    if __initialized:
        if not t.is_cuda:
            cu = t.detach().cuda()
            tdist.broadcast(cu, src=src_rank)
            t.copy_(cu.cpu())
        else:
            tdist.broadcast(t, src=src_rank)


def dist_fmt_vals(val: float, fmt: Union[str, None] = '%.2f') -> Union[torch.Tensor, List]:
    if not initialized():
        return torch.tensor([val]) if fmt is None else [fmt % val]
    
    ts = torch.zeros(__world_size)
    ts[__rank] = val
    allreduce(ts)
    if fmt is None:
        return ts
    return [fmt % v for v in ts.cpu().numpy().tolist()]


def master_only(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        force = kwargs.pop('force', False)
        if force or is_master():
            ret = func(*args, **kwargs)
        else:
            ret = None
        barrier()
        return ret
    return wrapper


def local_master_only(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        force = kwargs.pop('force', False)
        if force or is_local_master():
            ret = func(*args, **kwargs)
        else:
            ret = None
        barrier()
        return ret
    return wrapper


def for_visualize(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if is_master():
            # with torch.no_grad():
            ret = func(*args, **kwargs)
        else:
            ret = None
        return ret
    return wrapper


def finalize():
    if __initialized:
        tdist.destroy_process_group()


# 以下是torch相关的功能类和函数
class TensorboardLogger(object):
    """
    Tensorboard日志记录器
    用于将训练过程中的各种指标记录到Tensorboard中可视化
    """
    def __init__(self, log_dir, filename_suffix):
        try: import tensorflow_io as tfio
        except: pass
        from torch.utils.tensorboard import SummaryWriter
        self.writer = SummaryWriter(log_dir=log_dir, filename_suffix=filename_suffix)
        self.step = 0
    
    def set_step(self, step=None):
        if step is not None:
            self.step = step
        else:
            self.step += 1
    
    def update(self, head='scalar', step=None, **kwargs):
        for k, v in kwargs.items():
            if v is None:
                continue
            if step is None:  # iter wise
                it = self.step
                if it == 0 or (it + 1) % 500 == 0:
                    if hasattr(v, 'item'): v = v.item()
                    self.writer.add_scalar(f'{head}/{k}', v, it)
            else:  # epoch wise
                if hasattr(v, 'item'): v = v.item()
                self.writer.add_scalar(f'{head}/{k}', v, step)
    
    def log_tensor_as_distri(self, tag, tensor1d, step=None):
        if step is None:  # iter wise
            step = self.step
            loggable = step == 0 or (step + 1) % 500 == 0
        else:  # epoch wise
            loggable = True
        if loggable:
            try:
                self.writer.add_histogram(tag=tag, values=tensor1d, global_step=step)
            except Exception as e:
                print(f'[log_tensor_as_distri writer.add_histogram failed]: {e}')
    
    def log_image(self, tag, img_chw, step=None):
        if step is None:  # iter wise
            step = self.step
            loggable = step == 0 or (step + 1) % 500 == 0
        else:  # epoch wise
            loggable = True
        if loggable:
            self.writer.add_image(tag, img_chw, step, dataformats='CHW')
    
    def flush(self):
        self.writer.flush()
    
    def close(self):
        self.writer.close()


class SmoothedValueWithTorch(object):
    """带有torch支持的SmoothedValue版本"""
    def __init__(self, window_size=20, fmt=None):
        if fmt is None:
            fmt = "{median:.4f} ({global_avg:.4f})"
        self.deque = deque(maxlen=window_size)
        self.total = 0.0
        self.count = 0
        self.fmt = fmt

    def update(self, value, n=1):
        self.deque.append(value)
        self.count += n
        self.total += value * n

    def synchronize_between_processes(self):
        """
        Warning: does not synchronize the deque!
        """
        if not is_dist_avail_and_initialized():
            return
        t = torch.tensor([self.count, self.total], dtype=torch.float64, device='cuda')
        tdist.barrier()
        tdist.all_reduce(t)
        t = t.tolist()
        self.count = int(t[0])
        self.total = t[1]

    @property
    def median(self):
        d = torch.tensor(list(self.deque))
        return d.median().item()

    @property
    def avg(self):
        d = torch.tensor(list(self.deque), dtype=torch.float32)
        return d.mean().item()

    @property
    def global_avg(self):
        return self.total / self.count

    @property
    def max(self):
        return max(self.deque)

    @property
    def value(self):
        return self.deque[-1]

    def __str__(self):
        return self.fmt.format(
            median=self.median,
            avg=self.avg,
            global_avg=self.global_avg,
            max=self.max,
            value=self.value)


class MetricLoggerWithTorch(object):
    """带有torch支持的MetricLogger版本"""
    def __init__(self, delimiter="\t"):
        self.meters = defaultdict(SmoothedValueWithTorch)
        self.delimiter = delimiter

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v is None:
                continue
            if isinstance(v, torch.Tensor):
                v = v.item()
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
            loss_str.append(
                "{}: {}".format(name, str(meter))
            )
        return self.delimiter.join(loss_str)

    def synchronize_between_processes(self):
        for meter in self.meters.values():
            meter.synchronize_between_processes()

    def add_meter(self, name, meter):
        self.meters[name] = meter

    def log_every(self, iterable, print_freq, header=None):
        i = 0
        if not header:
            header = ''
        start_time = time.time()
        end = time.time()
        iter_time = SmoothedValueWithTorch(fmt='{avg:.4f}')
        data_time = SmoothedValueWithTorch(fmt='{avg:.4f}')
        space_fmt = ':' + str(len(str(len(iterable)))) + 'd'
        log_msg = [
            header,
            '[{0' + space_fmt + '}/{1}]',
            'eta: {eta}',
            '{meters}',
            'time: {time}',
            'data: {data}'
        ]
        if torch.cuda.is_available():
            log_msg.append('max mem: {memory:.0f}')
        log_msg = self.delimiter.join(log_msg)
        MB = 1024.0 * 1024.0
        for obj in iterable:
            data_time.update(time.time() - end)
            yield obj
            iter_time.update(time.time() - end)
            if i % print_freq == 0 or i == len(iterable) - 1:
                eta_seconds = iter_time.global_avg * (len(iterable) - i)
                eta_string = str(datetime.timedelta(seconds=int(eta_seconds)))
                if torch.cuda.is_available():
                    print(log_msg.format(
                        i, len(iterable), eta=eta_string,
                        meters=str(self),
                        time=str(iter_time), data=str(data_time),
                        memory=torch.cuda.max_memory_allocated() / MB))
                else:
                    print(log_msg.format(
                        i, len(iterable), eta=eta_string,
                        meters=str(self),
                        time=str(iter_time), data=str(data_time)))
            i += 1
            end = time.time()
        total_time = time.time() - start_time
        total_time_str = str(datetime.timedelta(seconds=int(total_time)))
        print('{} Total time: {} ({:.4f} s / it)'.format(
            header, total_time_str, total_time / len(iterable)))


def setup_for_distributed(is_master):
    """
    This function disables printing when not in master process
    """
    builtin_print = builtins.print

    def print(*args, **kwargs):
        force = kwargs.pop('force', False)
        force = force or (get_world_size() > 8)
        if is_master or force:
            now = datetime.datetime.now().time()
            builtin_print('[{}] '.format(now), end='')  # print with time stamp
            builtin_print(*args, **kwargs)

    builtins.print = print


def is_dist_avail_and_initialized():
    if not tdist.is_available():
        return False
    if not tdist.is_initialized():
        return False
    return True


def get_world_size():
    if not is_dist_avail_and_initialized():
        return 1
    return tdist.get_world_size()


def is_main_process():
    return get_rank() == 0


def save_on_master(*args, **kwargs):
    if is_main_process():
        torch.save(*args, **kwargs)


def init_distributed_mode(local_out_path, only_sync_master=False, timeout=30):
    """初始化分布式训练环境"""
    try:
        # 初始化分布式环境
        initialize(fork=False, timeout=timeout)
        barrier()  # 同步所有进程
    except RuntimeError:
        # 如果发生NCCL错误,打印错误信息并等待
        print(f'{">"*75}  NCCL Error  {"<"*75}', flush=True)
        time.sleep(10)
    
    # 创建输出目录
    if local_out_path is not None: 
        os.makedirs(local_out_path, exist_ok=True)
    
    # 修改print函数的行为
    _change_builtin_print(is_local_master())
    
    # 对主进程设置输出重定向
    if (is_master() if only_sync_master else is_local_master()) and local_out_path is not None and len(local_out_path):
        sys.stdout, sys.stderr = SyncPrint(local_out_path, sync_stdout=True), SyncPrint(local_out_path, sync_stdout=False)


class NativeScalerWithGradNormCount:
    state_dict_key = "amp_scaler"

    def __init__(self):
        self._scaler = torch.cuda.amp.GradScaler()

    def __call__(self, loss, optimizer, clip_grad=None, parameters=None, create_graph=False, update_grad=True):
        self._scaler.scale(loss).backward(create_graph=create_graph)
        if update_grad:
            if clip_grad is not None:
                assert parameters is not None
                self._scaler.unscale_(optimizer)  # unscale the gradients of optimizer's assigned params in-place
                norm = torch.nn.utils.clip_grad_norm_(parameters, clip_grad)
            else:
                self._scaler.unscale_(optimizer)
                norm = get_grad_norm_(parameters)
            self._scaler.step(optimizer)
            self._scaler.update()
        else:
            norm = None
        return norm

    def state_dict(self):
        return self._scaler.state_dict()

    def load_state_dict(self, state_dict):
        self._scaler.load_state_dict(state_dict)


def get_grad_norm_(parameters, norm_type: float = 2.0) -> torch.Tensor:
    if isinstance(parameters, torch.Tensor):
        parameters = [parameters]
    parameters = [p for p in parameters if p.grad is not None]
    norm_type = float(norm_type)
    if len(parameters) == 0:
        return torch.tensor(0.)
    device = parameters[0].grad.device
    if norm_type == float('inf'):
        total_norm = max(p.grad.detach().abs().max().to(device) for p in parameters)
    else:
        total_norm = torch.norm(torch.stack([torch.norm(p.grad.detach(), norm_type).to(device) for p in parameters]), norm_type)
    return total_norm


def add_weight_decay(model, weight_decay=1e-5, skip_list=()):
    decay = []
    no_decay = []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue  # frozen weights
        if len(param.shape) == 1 or name.endswith(".bias") or name in skip_list or 'diffloss' in name:
            no_decay.append(param)  # no weight decay on bias, norm and diffloss
        else:
            decay.append(param)
    return [
        {'params': no_decay, 'weight_decay': 0.},
        {'params': decay, 'weight_decay': weight_decay}]


def save_model(args, epoch, model_without_ddp, optimizer, loss_scaler, epoch_name=None):
    if epoch_name is None:
        epoch_name = str(epoch)
    output_dir = Path(args.output_dir)
    checkpoint_path = output_dir / ('checkpoint-%s.pth' % epoch_name)

    to_save = {
        'model': model_without_ddp.state_dict(),
        'optimizer': optimizer.state_dict(),
        'epoch': epoch,
        'scaler': loss_scaler.state_dict(),
        'args': args,
    }
    save_on_master(to_save, checkpoint_path)


def all_reduce_mean(x):
    world_size = get_world_size()
    if world_size > 1:
        x_reduce = torch.tensor(x).cuda()
        tdist.all_reduce(x_reduce)
        x_reduce /= world_size
        return x_reduce.item()
    else:
        return x