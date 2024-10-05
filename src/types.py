"""
Providing t
"""
from dataclasses import dataclass
from typing import Union, List


@dataclass
class SectionDetails:
    name: str
    value: Union[str, int]
    

@dataclass
class BooksAndDetails:
    titles: str
    details: List[SectionDetails]