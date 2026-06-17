from dataclasses import dataclass, astuple

@dataclass
class CurrencyEntry:
    mid: float

@dataclass
class SessionResult:
    rising: int
    falling: int
    unchanged: int

    def __iter__(self):
        return iter(astuple(self))

@dataclass
class StatisticalResult:
    median: float
    mode: float
    standard_deviation: float
    coefficient_of_variation: float

    def __getitem__(self, key):
        return getattr(self, key)

@dataclass
class DistributionRange:
    start: float
    end: float
    count: int

    def __getitem__(self, key):
        return getattr(self, key)