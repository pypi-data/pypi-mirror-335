import inspect

def filter_func_params(func, args):
    """
    从 'args' 中提取与 'func' 参数匹配的键值对。

    :param func: 需要匹配参数的函数。
    :param args: 包含参数的字典。
    :return: 仅包含与 'func' 参数匹配的字典。
    """
    # 初始化一个空字典用于存储匹配的参数
    matched_args = {}

    # 如果 'args' 为 None，则返回空字典
    if args is None:
        return matched_args

    # 获取函数的签名以访问其参数
    signature = inspect.signature(func)
    parameters = signature.parameters

    # 遍历函数的参数名，检查它们是否存在于 'args' 中
    for param_name in parameters:
        if param_name in args:
            matched_args[param_name] = args[param_name]

    return matched_args

# 示例用法：
# def example_func(a, b, c): pass
# args = {'a': 1, 'b': 2, 'd': 4}
# print(filter_func_params(example_func, args))  # 输出: {'a': 1, 'b': 2}
