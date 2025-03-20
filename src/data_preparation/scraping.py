import requests
from loguru import logger 
from bs4 import BeautifulSoup 


class Scraper:
    def __init__(self, url: str, partial: bool, marker: str | None) -> None:
        self.url: str = url
        self.partial: bool = partial
        self.marker: str | None = marker 

    def execute(self) -> str | None:
        response: requests.Response = requests.get(url=self.url)
        if response.status_code == 200:
            soup = BeautifulSoup(markup=response.text, features="html.parser")
            raw_text: str = soup.text

            if not self.partial:
                return raw_text 

            elif self.partial and (self.marker != None):
                start_point = raw_text.rfind(self.marker)
                return raw_text[start_point:]

            elif self.partial and (self.marker == None):
                raise Exception(f"Partial scraping requested for {self.url} without a marker")

        else:
            raise Exception(f"Unable to make HTTP request. Status code: {response.status_code}") 
            
