# coding:utf-8

from typing import Dict

from pycountry import countries
from pycountry import languages
from pycountry import scripts
from pycountry.db import Data


class Entry():
    def __init__(self, data: Data):
        self.__data: Data = data

    def __str__(self) -> str:
        return self.code

    @property
    def code(self) -> str:
        raise NotImplementedError()

    @property
    def data(self) -> Data:
        return self.__data

    @classmethod
    def keyword(cls, value: str) -> Dict[str, str]:
        """generate search feild value pair"""
        assert isinstance(value, str)
        feild = f"alpha_{len(value)}"
        return {feild: value}


class Language(Entry):
    """Language in ISO 639-3"""

    def __init__(self, data: Data):
        super().__init__(data)

    @property
    def code(self) -> str:
        return self.alpha_2

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def alpha_2(self) -> str:
        return self.data.alpha_2

    @property
    def alpha_3(self) -> str:
        return self.data.alpha_3

    @classmethod
    def get(cls, code: str) -> "Language":
        if (data := languages.get(**cls.keyword(code))) is None:  # >=3.8
            raise ValueError(f"No such language: {code}")
        return cls(data)


class Script(Entry):
    """Script in ISO 15924"""

    def __init__(self, data: Data):
        super().__init__(data)

    @property
    def code(self) -> str:
        return self.alpha_4

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def numeric(self) -> int:
        return int(self.data.numeric)

    @property
    def alpha_4(self) -> str:
        return self.data.alpha_4

    @classmethod
    def get(cls, code: str) -> "Script":
        if (data := scripts.get(**cls.keyword(code))) is None:  # >=3.8
            raise ValueError(f"No such script: {code}")
        return cls(data)


class Region(Entry):
    """Country or Region in ISO 3166-1"""

    def __init__(self, data: Data):
        super().__init__(data)

    @property
    def code(self) -> str:
        return self.alpha_2

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def flag(self) -> str:
        return self.data.flag

    @property
    def numeric(self) -> int:
        return int(self.data.numeric)

    @property
    def alpha_2(self) -> str:
        return self.data.alpha_2

    @property
    def alpha_3(self) -> str:
        return self.data.alpha_3

    @property
    def official_name(self) -> str:
        return self.data.official_name

    @classmethod
    def get(cls, code: str) -> "Region":
        if (data := countries.get(**cls.keyword(code))) is None:  # >=3.8
            raise ValueError(f"No such country or region: {code}")
        return cls(data)
