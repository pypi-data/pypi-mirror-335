
def safe_access(func, default_value=None):
    try:
        return func()
    except:
        return default_value


def convert_to_int_or_float(string_num):
    try:
        float_num = float(string_num)
        if float_num.is_integer():
            return int(float_num)
        else:
            return float_num
    except ValueError:
        return None
