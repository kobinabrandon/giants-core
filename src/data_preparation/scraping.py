import requests
from bs4 import BeautifulSoup 


def scrape(
    url: str, 
    initial_marker: str | None = None,
    terminal_marker: str | None = None
) -> str | None:

    response: requests.Response = requests.get(url=url)
    initial_marker_provided: bool = isinstance(initial_marker, str)
    terminal_marker_provided: bool = isinstance(terminal_marker, str)

    if response.status_code == 200:
        soup = BeautifulSoup(markup=response.text, features="html.parser")
        raw_text: str = soup.text

        if (not initial_marker_provided and not terminal_marker_provided):
            return raw_text 

        elif (initial_marker_provided and terminal_marker_provided):
            start_index: int = raw_text.rfind(initial_marker)
            terminal_index: int = raw_text.rfind(terminal_marker)
            return raw_text[start_index:terminal_index]

        else:
            raise Exception(f"Partial scraping requested for {url} without one of the markers")

    else:
        raise Exception(f"Unable to make HTTP request. Status code: {response.status_code}") 
        
