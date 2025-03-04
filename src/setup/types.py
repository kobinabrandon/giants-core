from typing import TypeAlias

BatchArchive: TypeAlias = list[dict[str, str]]
BookArchive: TypeAlias = dict[str, list[dict[str, str | bool | int | None ] | BatchArchive]] 

