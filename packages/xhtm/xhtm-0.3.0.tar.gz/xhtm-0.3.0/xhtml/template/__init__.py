# coding:utf-8

from os.path import abspath
from os.path import dirname
from os.path import isdir
from os.path import join
from typing import Optional

from xlc import Message
from xlc import Section

from xhtml.header import AcceptLanguage
from xhtml.resource import Resource

BASE_DIR = dirname(abspath(__file__))


class Template(Resource):
    FAVICON: str = "favicon.ico"

    def __init__(self, base: Optional[str] = None):
        super().__init__(base if base and isdir(base) else BASE_DIR)


class LocaleTemplate(Template):
    def __init__(self, base: str):
        self.__message: Message = Message.load(join(base, "locale"))
        super().__init__(base)

    def search(self, accept_language: str, section: str) -> Section:
        language: AcceptLanguage = AcceptLanguage(accept_language)
        return language.choice(self.__message).seek(section)
