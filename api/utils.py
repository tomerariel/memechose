from typing import Generator, Iterable


def iterate_in_batches(
    items: Iterable,
    total: int,
    batch_size: int = 1000,
) -> Generator:
    """
    Iterate over a lazy collection in batches.

    Args:
        items (Iterable): A lazy collection.
        total (int): Number of items in the collection.
        batch_size (int, optional): The batch size. Defaults to 1000.

    Yields:
        Generator: A concrete sequence of length batch_size (or less in the last iteration).
    """
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield items[start:end]
