# coding:utf-8

import os
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypeVar

from toml import load

from xlc.database.subtags import Entry
from xlc.database.subtags import Language
from xlc.database.subtags import Region
from xlc.database.subtags import Script

BASE: str = os.path.dirname(__file__)


class LangTag:
    """Language tag

    The syntax of the language tag in BCP47 is:
        langtag       = language["-" script]["-" region]

        language      = 2*3ALPHA            ; shortest ISO 639 code
                        ["-" extlang]       ; sometimes followed by
                                            ; extended language subtags
                      / 4ALPHA              ; or reserved for future use
                      / 5*8ALPHA            ; or registered language subtag

        extlang       = 3ALPHA              ; selected ISO 639 codes
                        *2("-" 3ALPHA)      ; permanently reserved

        script        = 4ALPHA              ; ISO 15924 code

        region        = 2ALPHA              ; ISO 3166-1 code
                      / 3DIGIT              ; UN M.49 codes

    The order of language tags is:
        1. language-script-region
        2. language-script
        3. language-region
        4. language
    """
    HYPHEN: str = "-"

    def __init__(self, langtag: str):
        tags: List[str] = langtag.replace("_", self.HYPHEN).split(self.HYPHEN)
        self.__language: Language = Language.get(tags.pop(0))
        self.__script: Optional[Script] = None
        self.__region: Optional[Region] = None
        if len(tags) == 1:
            key = tags.pop()  # region or script
            try:
                script = Script.get(key)
                self.__script = script
            except KeyError:
                region = Region.get(key)
                self.__region = region
        elif len(tags) == 2:
            self.__region = Region.get(tags.pop())
            self.__script = Script.get(tags.pop())
        full = self.filter(self.language, self.script, self.region)
        self.__name: str = self.join(*full)
        self.__tags: List[str] = []
        if len(full) == 3:
            self.__tags.append(self.join(full[0], full[1]))
            self.__tags.append(self.join(full[0], full[2]))
            self.__tags.append(self.join(full[0]))
        elif len(full) == 2:
            self.__tags.append(self.join(full[0]))

    def __iter__(self) -> Iterator[str]:
        return iter(self.__tags)

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: "LangT") -> bool:
        return self.name == str(other)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tags(self) -> List[str]:
        """Replaceable subtags"""
        return self.__tags

    @property
    def language(self) -> Language:
        """Language in ISO 639"""
        return self.__language

    @property
    def script(self) -> Optional[Script]:
        """Script in ISO 15924"""
        return self.__script

    @property
    def region(self) -> Optional[Region]:
        """Country or Region in ISO 3166-1"""
        return self.__region

    @classmethod
    def filter(cls, *tags: Optional[Entry]) -> Tuple[Entry, ...]:
        return tuple(filter(None, tags))

    @classmethod
    def join(cls, *tags: Optional[Entry]) -> str:
        return cls.HYPHEN.join(str(tag) for tag in cls.filter(*tags))


LangT = TypeVar("LangT", str, LangTag)


class LangTagDict(Dict[str, LangTag]):
    def __init__(self):
        super().__init__()

    def __getitem__(self, index: str) -> LangTag:
        return self.lookup(index)

    def lookup(self, langtag: LangT) -> LangTag:
        lang: str = langtag.name if isinstance(langtag, LangTag) else langtag
        if lang not in self:
            ltag: LangTag = LangTag(lang)
            self.setdefault(lang, ltag)
        return super().__getitem__(lang)


LANGUAGES: LangTagDict = LangTagDict()


class LangMark(Dict[str, str]):
    def __init__(self, langtag: LangTag, regions: Dict[str, str]):
        super().__init__()
        self.__langtag: LangTag = langtag
        for region, recognition in regions.items():
            self[region] = recognition

    @property
    def tag(self) -> LangTag:
        return self.__langtag


class LangMarks(Dict[LangTag, LangMark]):
    CONFIG: str = os.path.join(BASE, "langmark.toml")

    def __init__(self):
        super().__init__()

    def __getitem__(self, langtag: LangT) -> LangMark:
        ltag: LangTag = LANGUAGES.lookup(langtag)
        return super().__getitem__(ltag)

    def append(self, item: LangMark) -> None:
        self[item.tag] = item

    def lookup(self, langtag: LangT) -> str:
        ltag: LangTag = LANGUAGES.lookup(langtag)
        mark: LangMark = self[LangTag.join(ltag.language, ltag.script)]
        code: Optional[str] = ltag.region.code if ltag.region else None
        return mark[code] if code else mark[""]

    @classmethod
    def load_config(cls) -> Tuple[LangMark, ...]:
        with open(cls.CONFIG, "r", encoding="utf-8") as rhdl:
            return tuple(LangMark(langtag=LANGUAGES.lookup(lang), regions=data)
                         for lang, data in load(rhdl).items())

    @classmethod
    def from_config(cls) -> "LangMarks":
        instance = cls()
        for item in cls.load_config():
            instance.append(item)
        return instance


LANGMARKS: LangMarks = LangMarks.from_config()


class LangItem():
    def __init__(self, langtag: LangTag, aliases: Iterable[str] = [], description: str = ""):  # noqa:E501
        self.__langtag: LangTag = langtag
        self.__aliases: Tuple[LangTag, ...] = tuple(LANGUAGES[a] for a in aliases)  # noqa:E501
        self.__description: str = description or langtag.language.name
        self.__recognition: str = LANGMARKS.lookup(langtag)

    @property
    def tag(self) -> LangTag:
        return self.__langtag

    @property
    def aliases(self) -> Tuple[LangTag, ...]:
        return self.__aliases

    @property
    def description(self) -> str:
        return self.__description

    @property
    def recognition(self) -> str:
        return self.__recognition


class LangTags():
    """Language tags"""
    CONFIG: str = os.path.join(BASE, "langtags.toml")

    def __init__(self):
        self.__tags: Dict[LangTag, LangItem] = {}

    def __iter__(self) -> Iterator[LangTag]:
        return iter(self.__tags)

    def __len__(self) -> int:
        return len(self.__tags)

    def __contains__(self, langtag: LangT) -> bool:
        return LANGUAGES.lookup(langtag) in self.__tags

    def __getitem__(self, langtag: LangT) -> LangItem:
        ltag: LangTag = LANGUAGES.lookup(langtag)
        return self.__tags[ltag]

    def __setitem__(self, langtag: LangT, item: LangItem) -> None:
        assert item.tag == langtag
        self.append(item)

    def append(self, item: LangItem) -> None:
        for alias in item.aliases:
            value = LangItem(langtag=alias, aliases=[], description=item.description)  # noqa:E501
            self.__tags.setdefault(alias, value)
        self.__tags[item.tag] = item

    def lookup(self, langtag: LangT) -> LangItem:
        """Lookup language tag or replaceable subtags"""
        ltag: LangTag = LANGUAGES.lookup(langtag)
        if ltag in self.__tags:
            return self.__tags[ltag]
        for _tag in ltag.tags:
            ltag = LANGUAGES[_tag]
            if ltag in self.__tags:
                return self.__tags[ltag]
        raise LookupError(f"No such language tag: {langtag}")

    @classmethod
    def load_config(cls) -> Tuple[LangItem, ...]:
        with open(cls.CONFIG, "r", encoding="utf-8") as rhdl:
            return tuple(LangItem(langtag=LANGUAGES.lookup(lang),
                                  aliases=data.get("aliases", []),
                                  description=data.get("description", ""))
                         for lang, data in load(rhdl).items())

    @classmethod
    def from_config(cls) -> "LangTags":
        instance = cls()
        for item in cls.load_config():
            instance[item.tag] = item
        return instance


LANGTAGS: LangTags = LangTags.from_config()
