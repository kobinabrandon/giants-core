"""
Providing custom types to manage the details of our texts or sections therefrom.
"""
from dataclasses import dataclass


@dataclass
class SectionDetails:
    name: str
    value: str | int
    

@dataclass
class BooksAndDetails:
    titles: str
    details: list[SectionDetails]
