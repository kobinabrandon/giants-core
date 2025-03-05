import requests
from bs4 import BeautifulSoup 


def scrape_page(url: str) -> str:
    response: requests.Response = requests.get(url=url)
    if response.status_code == 200:
        soup = BeautifulSoup(markup=response.text)
        return soup.text
    else:
        raise Exception(f"Unable to make HTTP request. Status code: {response.status_code}") 

