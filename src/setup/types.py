from typing import TypeAlias

# Data Preparation 
ScrapedArchive: TypeAlias = dict[str, list[dict[str, str]]]
HTTPArchive: TypeAlias = dict[str, list[dict[str, str | bool | int | None]]]
TorrentArchive: TypeAlias = list[dict[str, str | bool | int | None ] | HTTPArchive] 
AuthorArchive: TypeAlias = tuple[HTTPArchive, TorrentArchive, ScrapedArchive] | tuple[HTTPArchive, TorrentArchive] | tuple[HTTPArchive, ScrapedArchive] | HTTPArchive | ScrapedArchive | TorrentArchive | None 

