def chunk_list(lst, chunk_size):
    """Splits a list into chunks of a specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def chunk_list_generator(lst, chunk_size):
    """Generates chunks of a specified size from a list."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
