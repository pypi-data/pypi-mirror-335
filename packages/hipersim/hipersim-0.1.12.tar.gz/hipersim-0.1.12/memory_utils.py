import numpy as np
import linecache
import os
import tracemalloc


try:
    profile
except BaseException:
    def dummy_profile(f):
        return f

    profile = dummy_profile


def set_line_profile():
    global profile
    from memory_profiler import profile as memprofile
    profile = memprofile


def tag(name):
    try:
        def f():
            pass
        f.__name__ = name.replace(" ", '_')
        profile(f)()
    except BaseException:
        pass


def display_top(key_type='lineno', limit=10):
    snapshot = tracemalloc.take_snapshot()
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    print("Top %s lines" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        frame = stat.traceback[0]
        print("#%s: %s:%s: %.1f MB"
              % (index, frame.filename, frame.lineno, stat.size / 1024**2))
        line = linecache.getline(frame.filename, frame.lineno).strip()
        if line:
            print('    %s' % line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f MB" % (total / 1024**2))


def get_memory_usage():
    import gc
    import ctypes
    import os
    import psutil
    gc.collect()
    try:
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except Exception:
        pass
    pid = os.getpid()
    python_process = psutil.Process(pid)
    return python_process.memory_info()[0] / 1024**2


def start_trace():
    import tracemalloc
    tracemalloc.start()


def test():
    start_trace()
    # ... run your application ...
    N1, N2, N3 = 8192, 64, 64
    N1r = N1 // 2 + 1
    tmp = np.zeros((3, 3, N1r, N2, N3), dtype=np.float32) + 0
    tmp = 0

    sqrtphi = np.zeros((3, 3, N1r, N2, N3), dtype=np.float32) + 0
    Cxyz = np.zeros((3, N1r, N2, N3), dtype=np.complex64) + 0
    n = np.zeros((3, N1r, N2, N3), dtype=np.complex64) + 0
    print(get_memory_usage())

    display_top()


if __name__ == '__main__':
    test()
