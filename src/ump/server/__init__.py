# (c) 2021, xanthus tan <tanxk@neusoft.com>

from abc import ABC, abstractmethod


class Command(ABC):

    @abstractmethod
    def run(self): pass


class Translate(ABC):
    @abstractmethod
    def to_json(self, cmd): pass

