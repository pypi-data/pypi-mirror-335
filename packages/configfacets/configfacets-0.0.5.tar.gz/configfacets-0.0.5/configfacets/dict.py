import functools


class DictUtils:
    @staticmethod
    def get_by_path(dictionary: dict, path: str):
        keys = path.split(".")
        return functools.reduce(
            lambda d, key: (d.get(key) if isinstance(d, dict) else None) if d else None,
            keys,
            dictionary,
        )
