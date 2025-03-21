import os
import sys
import importlib
import functools
import inspect
import asyncio
import nest_asyncio

nest_asyncio.apply() 

def call_func(func, args=None, kwargs=None):
    """
        args:是一个元组
        kwargs:是一个字典
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}

    if inspect.isgeneratorfunction(func):
        return list(func(*args, **kwargs))
    elif inspect.isasyncgenfunction(func):
        async def collect_async_gen():
            return [item async for item in func(*args, **kwargs)]
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(collect_async_gen())
        else:
            async def run_async_gen():
                return await collect_async_gen()
            future = asyncio.ensure_future(run_async_gen())
            while not future.done():
                loop.run_until_complete(asyncio.sleep(0.1))  # 避免阻塞
            return future.result()
    elif inspect.iscoroutinefunction(func):
        coro = func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        else:
            async def run_coro():
                return await coro
            future = asyncio.ensure_future(run_coro())
            while not future.done():
                loop.run_until_complete(asyncio.sleep(0.1))  # 避免阻塞
            return future.result()
    else:
        return func(*args, **kwargs)
    
class ChangeDirectoryAndPath:
    """Context manager to change the current working directory and sys.path."""

    def __init__(self, module_path):
        self.module_path = module_path
        self.old_path = None

    def __enter__(self):
        self.old_path = os.getcwd()
        sys.path.insert(0, self.module_path)
        os.chdir(self.module_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.module_path in sys.path:
            sys.path.remove(self.module_path)
        os.chdir(self.old_path)
        

class ModuleManager:
    """Context manager for handling module imports and sys.modules state."""

    def __init__(self, module_path):
        self.module_path = module_path
        self.original_modules = sys.modules.copy()

    def __enter__(self):
        """Enter the runtime context related to this object."""
        self.change_dir = ChangeDirectoryAndPath(self.module_path)
        self.change_dir.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.change_dir.__exit__(exc_type, exc_value, traceback)
        self.cleanup_modules()

    def cleanup_modules(self):
        """Restore the original sys.modules state."""
        importlib.invalidate_caches()
        for key in list(sys.modules.keys()):
            if key not in self.original_modules:
                del sys.modules[key]
                

def wrapped_func(func, module_path):

    def _wrapped(*args, **kwargs):
        try:
            print(f"调用了 {func.__name__}")
        except:
            print(f"called unknown")
        with ChangeDirectoryAndPath(module_path):
            try:
                result = call_func(func, args, kwargs)
            except Exception as e:
                print(f"调用 {func.__name__} 时发生错误: {str(e)}")
                raise
        
        print(f"{func.__name__} 调用完毕")

        return result
    
    wrapped_function = functools.wraps(func)(_wrapped)
    return wrapped_function

