def str_to_bool(s):
    if s == "True" or s == "true" or s == "1":
        return True
    elif s == "False" or s == "false" or s == "0":
        return False
    else:
        raise ValueError("Cannot convert {} to a bool".format(s))