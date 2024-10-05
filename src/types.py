"""
Providing t
"""
import dataclasses
from typing import Dict, Union, List


PageDetails = Dict[str, Union[str, int]]
BooksAndDetails = Dict[str, List[PageDetails]]

dict[str, BooksAndDetails]


@dataclasses
class PageDetails1:
    property: str
    