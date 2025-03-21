from typing import Any


def _get_hdf5_name(location: str, index: str) -> str:
    from os.path import join

    return join(location, index + ".h5")


def _get_pickle_name(location: str, index: str, item: str) -> str:
    from os.path import join

    return join(location, index, item + ".pkl")


def read_hdf5_data(location: str, index: str, items: list[str] | str) -> dict[str, Any]:
    """Read mixture, target, or noise data from an HDF5 file

    :param location: Location of the file
    :param index: Mixture, target, or noise index
    :param items: String(s) of data to retrieve
    :return: Dictionary of name: data
    """
    from os.path import exists
    from typing import Any

    import h5py
    import numpy as np

    def _get_dataset(file: h5py.File, d_name: str) -> Any:
        if d_name in file:
            data = np.array(file[d_name])
            if data.size == 1:
                item = data.item()
                if isinstance(item, bytes):
                    return item.decode("utf-8")
                return item
            return data
        return None

    if not isinstance(items, list):
        items = [items]

    h5_name = _get_hdf5_name(location, index)
    if exists(h5_name):
        try:
            with h5py.File(h5_name, "r") as f:
                result = {item: _get_dataset(f, item) for item in items}
        except Exception as e:
            raise OSError(f"Error reading {h5_name}: {e}") from e
    else:
        result = {item: None for item in items}

    return result


def write_hdf5_data(location: str, index: str, items: dict[str, Any]) -> None:
    """Write mixture, target, or noise data to an HDF5 file

    :param location: Location of the file
    :param index: Mixture, target, or noise index
    :param items: Dictionary of name: data
    """
    import h5py

    h5_name = _get_hdf5_name(location, index)
    with h5py.File(h5_name, "a") as f:
        for name, data in items.items():
            if name in f:
                del f[name]
            f.create_dataset(name=name, data=data)


def read_pickle_data(location: str, index: str, items: list[str] | str) -> dict[str, Any]:
    """Read mixture, target, or noise data from a pickle file

    :param location: Location of the file
    :param index: Mixture, target, or noise index
    :param items: String(s) of data to retrieve
    :return: Dictionary of name: data
    """
    import pickle
    from os.path import exists
    from typing import Any

    if not isinstance(items, list):
        items = [items]

    result: dict[str, Any] = {}
    for item in items:
        pkl_name = _get_pickle_name(location, index, item)
        if exists(pkl_name):
            with open(pkl_name, "rb") as f:
                result[item] = pickle.load(f)  # noqa: S301
        else:
            result[item] = None

    return result


def write_pickle_data(location: str, index: str, items: dict[str, Any]) -> None:
    """Write mixture, target, or noise data to a pickle file

    :param location: Location of the file
    :param index: Mixture, target, or noise index
    :param items: Dictionary of name: data
    """
    import pickle
    from os import makedirs
    from os.path import join

    directory = join(location, index)
    makedirs(directory, exist_ok=True)
    for name, data in items.items():
        pkl_name = _get_pickle_name(location, index, name)
        with open(pkl_name, "wb") as f:
            f.write(pickle.dumps(data))


def clear_pickle_data(location: str, index: str, items: list[str] | str) -> None:
    """Clear mixture, target, or noise data pickle file

    :param location: Location of the file
    :param index: Mixture, target, or noise index
    :param items: String(s) of data to retrieve
    """
    from pathlib import Path

    if not isinstance(items, list):
        items = [items]

    for item in items:
        Path(_get_pickle_name(location, index, item)).unlink(missing_ok=True)


def read_cached_data(location: str, name: str, index: str, items: list[str] | str) -> dict[str, Any]:
    """Read cached data from a file

    :param location: Location of the mixture database
    :param name: Data name ('mixture', 'target', or 'noise')
    :param index: Data index (mixture, target, or noise ID)
    :param items: String(s) of data to retrieve
    :return: Data (or tuple of data)
    """
    from os.path import join

    return read_pickle_data(join(location, name), index, items)


def write_cached_data(location: str, name: str, index: str, items: dict[str, Any]) -> None:
    """Write data to a file

    :param location: Location of the mixture database
    :param name: Data name ('mixture', 'target', or 'noise')
    :param index: Data index (mixture, target, or noise ID)
    :param items: Dictionary of name: data
    """
    from os.path import join

    write_pickle_data(join(location, name), index, items)


def clear_cached_data(location: str, name: str, index: str, items: list[str] | str) -> None:
    """Remove cached data file(s)

    :param location: Location of the mixture database
    :param name: Data name ('mixture', 'target', or 'noise')
    :param index: Data index (mixture, target, or noise ID)
    :param items: String(s) of data to clear
    """
    from os.path import join

    clear_pickle_data(join(location, name), index, items)
