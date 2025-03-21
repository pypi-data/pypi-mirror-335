from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, final

T = TypeVar("T")


class SingletonHubMeta(ABC, type, Generic[T]):
    @property
    def __key_cache(cls) -> Dict[str, str]:
        return cls.__get("__key_cache", {})

    @property
    def __value_cache(cls) -> Dict[str, T]:
        return cls.__get("__value_cache", {})

    def __get(cls, key: str, default):
        if not hasattr(cls, key):
            setattr(cls, key, default)

        return getattr(cls, key)

    def _name_selector(cls, name: str):
        return name

    @abstractmethod
    def _value_selector(cls, name: str) -> T:
        pass

    def _on_clear(cls, key: str, value: T) -> None:
        pass

    @final
    def clear(cls, name: str):
        """
        Clear the cached value associated with the given name.

        This method first checks if the name exists in the key cache. If it
        does, it retrieves the corresponding key. If not, it returns a tuple
        of `(None, None)`.

        Then, it checks if the key exists in the value cache. If it does, it
        retrieves the corresponding value, calls the `_on_clear` method with
        the key and value, and then removes the key from the value cache. If
        not, it returns a tuple of `(key, None)`.

        :param name: The name used to retrieve or create the value.
        :return: A tuple of `(key, value)` where `value` is the cleared value
            associated with the given name, or `(key, None)` if the key does
            not exist in the value cache.
        """
        if name not in cls.__key_cache:
            return None, None

        key = cls.__key_cache[name]

        if key not in cls.__value_cache:
            return key, None

        value = cls.__value_cache[key]

        cls._on_clear(key, value)

        del cls.__value_cache[key]

        return key, value

    @final
    def clear_all(cls):
        """
        Clear all cached values and return them in a dictionary.

        :return: A dictionary mapping key names to the cleared values
        :rtype: Dict[str, T]
        """
        result: Dict[str, T] = {}

        for key, value in cls.__value_cache.items():
            result[key] = value

            cls._on_clear(key, value)

        cls.__value_cache.clear()

        return result

    @final
    def get(
        cls,
        name: str = "",
    ):
        """
        Retrieve or create a value associated with the given name.

        This method first checks if the name exists in the key cache. If it
        does, it retrieves the corresponding key. If not, it generates a key
        using the `_name_selector` method and caches it. Then, it checks if
        the key exists in the value cache. If it does, it returns the
        corresponding value. If not, it creates the value using the
        `_value_selector` method, caches it, and returns it.

        :param name: The name used to retrieve or create the value.
        :return: The value associated with the given name.
        """

        if name in cls.__key_cache:
            key = cls.__key_cache[name]
        else:
            key = cls.__key_cache[name] = cls._name_selector(name)

        if key in cls.__value_cache:
            return cls.__value_cache[key]

        value = cls.__value_cache[key] = cls._value_selector(key)

        return value

    def __getattr__(cls, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)

        return cls.get(name)
