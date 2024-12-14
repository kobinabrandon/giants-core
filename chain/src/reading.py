"""
Module contains code that reads the code so that Langchain's text processing modules can make use of them.
We load could load the text using the pdf loader that is native to langchain, but it isn't working. So I 
used my alternative. 
"""
import requests

from general.reading import merge_books
from general.books import Book


def get_text(books: list[Book]) -> str:
    return merge_books(books=books, from_scratch=False, general=False)


