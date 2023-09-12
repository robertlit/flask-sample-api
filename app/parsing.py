def parse_int_arg(arg_val: str, arg_name: str):
    try:
        return int(arg_val), None
    except ValueError:
        return None, f"{arg_name} must be an integer"


def identity_arg(x, arg_name):
    return x, None
