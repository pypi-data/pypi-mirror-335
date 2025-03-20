# coding:utf-8

import os
from typing import Any
from typing import Dict

from toml import dumps
from toml import loads

from xlc.database import LANGTAGS
from xlc.database.langtags import LangItem
from xlc.database.langtags import LangT  # noqa:H306


class Context():
    def __init__(self, language: str):
        self.__datas: Dict[str, Any] = {"language": language}

    def get(self, index: str) -> Any:
        return self.__datas[index]

    def set(self, index: str, value: Any):
        self.__datas[index] = value

    def all(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__datas.items()}

    def fill(self, **kwargs: Any) -> Dict[str, str]:
        return {k: v.format(**kwargs) if isinstance(v, str) else str(v)
                for k, v in self.__datas.items()}


class Section(Context):
    def __init__(self, language: LangT, title: str = ""):
        lang: LangItem = LANGTAGS[language]
        super().__init__(lang.tag.name)
        self.__sections: Dict[str, Section] = {}
        self.__language: LangItem = lang
        self.__title: str = title

    @property
    def lang(self) -> LangItem:
        return self.__language

    def init(self, index: str, value: Any):
        if isinstance(value, dict):
            for k, v in value.items():
                self.seek(index).init(k, v)
        else:
            self.set(index, value)

    def seek(self, index: str) -> "Section":
        section: Section = self
        for key in index.split("."):
            section = section.find(key)
        return section

    def find(self, index: str) -> "Section":
        if index not in self.__sections:
            title: str = ".".join([self.__title, index])
            section = Section(language=self.lang.tag, title=title)
            self.__sections.setdefault(index, section)
        return self.__sections[index]

    def dump(self) -> Dict[str, Dict[str, Any]]:
        datas: Dict[str, Any] = self.all()
        for k, v in self.__sections.items():
            datas[k] = v.dump()
        return datas


class Segment(Section):
    def __init__(self, lang: LangT):
        super().__init__(language=lang)

    def dumps(self) -> str:
        return dumps(self.dump())

    def dumpf(self, file: str) -> None:
        with open(file, "w", encoding="utf-8") as whdl:
            whdl.write(self.dumps())

    @classmethod
    def load(cls, ltag: LangT, data: Dict[str, Any]) -> "Segment":
        instance: Segment = cls(ltag)
        for k, v in data.items():
            instance.init(k, v)
        return instance

    @classmethod
    def loads(cls, ltag: LangT, data: str) -> "Segment":
        return cls.load(ltag=ltag, data=loads(data))

    @classmethod
    def loadf(cls, file: str) -> "Segment":
        with open(file, "r", encoding="utf-8") as rhdl:
            base: str = os.path.basename(file)
            ltag: str = base[:base.find(".")]
            data: str = rhdl.read()
            return cls.loads(ltag=ltag, data=data)

    @classmethod
    def generate(cls, langtag: LangT) -> "Segment":
        lang: LangItem = LANGTAGS[langtag]
        return Segment.load(lang.tag, {
            "metadata": {
                "languagetag": lang.tag.name,
                "description": lang.description,
                "recognition": lang.recognition
            }
        })
