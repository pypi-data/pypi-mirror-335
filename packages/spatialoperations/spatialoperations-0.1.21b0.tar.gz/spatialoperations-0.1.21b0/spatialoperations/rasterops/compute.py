from enum import Enum
import joblib
import dask
from dask.distributed import Client, progress
from dataclasses import dataclass
from typing import List, Dict, Any, Callable
from .rasterops import DataCube
import logging


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    JOBLIB = "joblib"
    DASK = "dask"
    
    
@dataclass
class Args:
    args: List[Any] | None = None
    kwargs: Dict[str, Any] | None = None
    
    def parse(self):
        if self.args is None:
            args = []
        else:
            args = self.args
            
        if self.kwargs is None:
            kwargs = dict()
        else:
            kwargs = self.kwargs
            
        return args, kwargs


class Compute:
    _execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    
    def __init__(self, dc: DataCube, execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL, show_progress: bool = False):
        self._execution_mode = execution_mode
        self.dc = dc
        self.show_progress = show_progress
        self.downstream_args = {
            "show_progress": show_progress
        }
        self.executor = self.get_executor(execution_mode)
    def __repr__(self):
        return f"Compute(execution_mode={self.execution_mode})"
    
    @property
    def execution_mode(self):
        return self._execution_mode
    
    def get_executor(self, execution_mode: ExecutionMode, **kwargs):
        if execution_mode == ExecutionMode.SEQUENTIAL:
            return SequentialCompute(**{**self.downstream_args, **kwargs})
        elif execution_mode == ExecutionMode.JOBLIB:
            return JoblibCompute(**{**self.downstream_args, **kwargs})
        elif execution_mode == ExecutionMode.DASK:
            return DaskCompute(**{**self.downstream_args, **kwargs})
    
    def set_execution_mode(self, execution_mode: ExecutionMode, **kwargs):
        self._execution_mode = execution_mode
        self.executor = self.get_executor(execution_mode, **kwargs)
        self.downstream_args.update(kwargs)

    def execute(self, func: Callable, items: List[Args]):
        logging.info(f"Executing {func.__name__} with {self.execution_mode} mode")
        return self.executor.execute(func, items)
    
    def get_xarray_tiles(self,
        var: str,   
        group: str = None,
        idxs: list[tuple[int, int]] = []):
        if len(idxs) == 0:
            idxs = self.dc.storage.get_active_idxs(var, group)
        
        compute_items = [Args(args=[var, idx, group]) for idx in idxs]
        to_return = self.execute(self.dc.get_single_xarray_tile, compute_items)
        return [i for i in to_return if i is not None]


class SequentialCompute(Compute):
    def __init__(self, show_progress: bool = False):
        self.show_progress = show_progress
        
    def execute(self, func: Callable, items: List[Args]):
        buff = []
        if self.show_progress:
            from tqdm import tqdm
            for item in tqdm(items):
                args, kwargs = item.parse()
                buff.append(func(*args, **kwargs))
        else:
            for item in items:
                args, kwargs = item.parse()
                buff.append(func(*args, **kwargs))
        return buff


class JoblibCompute(Compute):
    def __init__(self, n_jobs: int = -1, show_progress: bool = False):
        self.n_jobs = n_jobs
        self.show_progress = show_progress
    
    def execute(self, func: Callable, items: List[Args]):
        if self.show_progress:
            from tqdm import tqdm
            return joblib.Parallel(n_jobs=self.n_jobs)(
                joblib.delayed(func)(*item.parse()[0], **item.parse()[1]) for item in tqdm(items)
            )
        else:
            return joblib.Parallel(n_jobs=self.n_jobs)(
                joblib.delayed(func)(*item.parse()[0], **item.parse()[1]) for item in items
            )

class DaskCompute(Compute):
    
    @property
    def client(self):
        return self._client
    
    @client.setter
    def client(self, client: Client):
        self._client = client
        
    def __init__(self, client: Client | None = None, show_progress: bool = True, dask_logging: bool = False):
        if client is None:
            self.client = Client()
        else:
            self.client = client
        self.show_progress = show_progress
        self.dask_logging = dask_logging
        
    def execute(self, func: Callable, items: List[Args]):
        def set_logs(logLevel = logging.WARNING):
            logging.getLogger("Client").setLevel(logLevel)
            logging.getLogger("distributed").setLevel(logLevel)
            logging.getLogger("dask").setLevel(logLevel)
            logging.getLogger("distributed.scheduler").setLevel(logLevel)
        
        if not self.dask_logging:
            set_logs()
        else:
            set_logs(logging.INFO)
            
        delayed_func = dask.delayed(func)
        delayed_items = [delayed_func(*item.parse()[0], **item.parse()[1]) for item in items]
        futures = self.client.compute(delayed_items)

        if self.show_progress:
            progress(futures, notebook=False)

        # Get results and handle None values
        results = self.client.gather(futures)
        if results is None:
            print("Computation returned None")
            return []

        return [r for r in results if r is not None]



class ApplyFunction:
    def __init__(self, dc, func: Callable, output_var: str | None = None, output_group: str | None = None):
        self.dc = dc
        self.func = func
        self.output_var = output_var
        self.output_group = output_group
        

    def apply(self, 
              idxs: list[tuple[int, int]], 
              compute_source: Compute = SequentialCompute(),
              compute_items: list[Args] = []):
        
        results = compute_source.execute(self.func, compute_items)
        
        if self.output_var is not None:
            from rasterops import intake
            intake.Intake.set_tiles(self.dc, [(idx, result) for idx, result in zip(idxs, results)], self.output_var, group=self.output_group)
        return results