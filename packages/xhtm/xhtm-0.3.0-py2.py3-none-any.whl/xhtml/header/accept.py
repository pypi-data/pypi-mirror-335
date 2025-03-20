# coding:utf-8

from typing import Iterable
from typing import Iterator
from typing import List
from typing import Union

from xlc import LANGUAGES
from xlc import LangT  # noqa:H306
from xlc import LangTag
from xlc import Message
from xlc import Segment


class LanguageQ():
    def __init__(self, language: Union[Iterable[str], str], q: Union[float, str]) -> None:  # noqa:E501
        languages: List[str] = language.split(",") if isinstance(language, str) else [lang for lang in language]  # noqa:E501
        self.__languages: List[LangTag] = [LANGUAGES[language] for language in languages]  # noqa:E501
        self.__quality: float = float(q)

    def __str__(self) -> str:
        language: str = ",".join(langtag.name for langtag in self)
        return f"{language};q={self.quality}"

    def __len__(self) -> int:
        return len(self.__languages)

    def __iter__(self) -> Iterator[LangTag]:
        return iter(self.__languages)

    @property
    def quality(self) -> float:
        return self.__quality


class AcceptLanguage():

    def __init__(self, language: str) -> None:
        self.__languageq: List[LanguageQ] = self.parse(language)
        self.__languages: List[LangTag] = [langtag for languageq in self.__languageq for langtag in languageq]  # noqa:E501

    def __contains__(self, langtag: LangT) -> bool:
        return LANGUAGES.lookup(langtag) in self.__languages

    def __iter__(self) -> Iterator[LangTag]:
        return iter(self.__languages)

    def __len__(self) -> int:
        return len(self.__languages)

    def choice(self, message: Message) -> Segment:
        for langtag in self:
            try:
                return message.lookup(langtag)
            except LookupError:
                continue
        return message["en"]  # default English

    @classmethod
    def parse(cls, language: str) -> List[LanguageQ]:
        languages: List[str] = []
        languageq: List[LanguageQ] = []
        substring: List[str] = language.split(";q=")
        if len(substring) <= 1:
            return [LanguageQ(language, 1.0)]
        languages.append(substring.pop(0))
        while len(substring) > 1:
            languages.extend(substring.pop(0).split(",", 1))
        languages.append(substring.pop())
        while len(languages) > 0:
            languageq.append(LanguageQ(languages.pop(0), languages.pop(0)))
        return sorted(languageq, key=lambda x: x.quality, reverse=True)
