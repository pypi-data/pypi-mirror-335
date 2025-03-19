import json
import os.path as osp

import numpy as np


class NumpyArrayEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)


def load_json(file_path, backend='builtin'):
    """Load json function.

    Parameters
    ----------
    file_path : str or pathlib.PosixPath
        json file path

    Returns
    -------
    data : dict
        loaded json data
    """
    if not osp.exists(str(file_path)):
        raise OSError(f'{file_path!s} not exists')
    with open(str(file_path)) as f:
        if backend == 'builtin':
            try:
                return json.load(f)
            except Exception as e:
                raise OSError(f'Error {e!s}. Not valid json file {file_path!s}')
        elif backend == 'orjson':
            import orjson
            try:
                return orjson.loads(f.read())
            except Exception as e:
                raise OSError(f'Error {e!s}. Not valid json file {file_path!s}')
        else:
            raise NotImplementedError(
                f"Not supported backend {backend}")


def save_json(data, filename,
              save_pretty=True,
              sort_keys=True,
              ensure_ascii=True,
              save_as_jsonlines=False,
              backend='builtin'):
    """Save json function.

    Parameters
    ----------
    data : dict or list[dict]
        save data
    filename : str
        save path
    """
    filename = str(filename)
    if save_as_jsonlines:
        import jsonlines
        with jsonlines.open(filename, mode='w') as writer:
            if isinstance(data, list):
                for d in data:
                    writer.write(d)
            else:
                writer.write(data)
    elif backend == 'builtin':
        with open(filename, "w") as f:
            if save_pretty:
                f.write(json.dumps(data, indent=4,
                                   ensure_ascii=ensure_ascii,
                                   sort_keys=sort_keys,
                                   separators=(',', ': '),
                                   cls=NumpyArrayEncoder))
            else:
                json.dump(data, f)
            f.write('\n')
    elif backend == 'orjson':
        import orjson
        with open(filename, "wb") as f:
            if save_pretty:
                f.write(orjson.dumps(
                    data,
                    option=orjson.OPT_SORT_KEYS | orjson.OPT_INDENT_2))
            else:
                f.write(orjson.dumps(data))
            f.write(b'\n')
    else:
        raise NotImplementedError(f"Not supported backend {backend}")
