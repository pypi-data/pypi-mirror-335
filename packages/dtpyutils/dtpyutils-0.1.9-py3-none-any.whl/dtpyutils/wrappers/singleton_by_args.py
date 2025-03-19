def singleton_by_args(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        # Create a unique key based on the arguments
        key = (args, frozenset(kwargs.items()))
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return get_instance
