# coding:utf-8

from os.path import abspath
from os.path import dirname
from os.path import isdir
from os.path import isfile
from os.path import join
from os.path import splitext
from typing import Optional

BASE_DIR = dirname(abspath(__file__))


class FileResource():
    def __init__(self, path: str):
        if not isinstance(path, str) or not isfile(path):
            message = f"No such file: {path}"
            raise FileNotFoundError(message)
        self.__ext: str = splitext(path)[1]
        self.__path: str = path

    @property
    def ext(self) -> str:
        return self.__ext

    @property
    def path(self) -> str:
        return self.__path

    def loads(self) -> str:
        with open(self.path, "r", encoding="utf-8") as rhdl:
            return rhdl.read()

    def loadb(self) -> bytes:
        with open(self.path, "rb") as rhdl:
            return rhdl.read()


class Resource():
    FAVICON: str = "favicon.ico"

    def __init__(self, base: Optional[str] = None):
        self.__base: str = base if base and isdir(base) else BASE_DIR

    @property
    def base(self) -> str:
        return self.__base

    @property
    def favicon(self) -> FileResource:
        return self.seek(self.FAVICON)

    def find(self, *args: str) -> Optional[str]:
        def check(base: str, real: str) -> Optional[str]:
            return path if isfile(path := join(base, real)) else check(BASE_DIR, real) if base != BASE_DIR else None  # noqa:E501
        return check(self.base, join(*args))

    def seek(self, *args: str) -> FileResource:
        path: Optional[str] = self.find(*args)
        if not isinstance(path, str):
            raise FileNotFoundError(f"No such file: {join(*args)}")
        return FileResource(path)
