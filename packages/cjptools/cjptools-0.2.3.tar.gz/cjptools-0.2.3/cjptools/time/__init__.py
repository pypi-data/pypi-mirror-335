import time


def getTime():
    """
    获取当前的高精度时间计数。

    Returns:
        float: 从某个固定时间点（通常是程序启动时）到当前的秒数。
    """
    return time.perf_counter()


# 用于存储上一次 tic() 调用时的时间
theTic = 0


def tic():
    """
    记录当前时间，用于后续计算经过的时间。

    Updates:
        theTic (float): 更新为当前的高精度时间计数。

    Returns:
        float: 当前的高精度时间计数。
    """
    global theTic
    theTic = time.perf_counter()
    return theTic


def toc(timeObj=None):
    """
    计算从上一次 tic() 调用到现在的时间间隔，或从指定时间点到现在的时间间隔。

    Args:
        timeObj (float, optional): 可选参数，指定的起始时间点。

    Returns:
        float: 从 timeObj 或 theTic 到当前的时间间隔。
    """
    if timeObj is not None:
        # 如果提供了 timeObj，则计算从 timeObj 到现在的时间差
        return time.perf_counter() - timeObj
    else:
        # 否则，计算从 theTic 到现在的时间差
        return time.perf_counter() - theTic

