import requests
import pandas as pd 
from bs4 import BeautifulSoup


class RecipeScraper:
    soup: BeautifulSoup

    def __init__(self) -> None:
        self.data_frame = None

    def scrap_url(self, url: str) -> None:
        response = requests.get(url)
        response.encoding = "utf-8"
        self.soup = BeautifulSoup(response.text, "html.parser")

    def get_table_data(self):
        headers = self.soup.find_all("h2") 

        tables = self.soup.find_all("table")[1:] 

        data_tables = []

        for i, table in enumerate(tables):
            table_rows = table.find_all('tr')[1:] #type:ignore 
            data_tables.append({
                "table_name": headers[i].text,
                "table_data": []
            })

            for row in table_rows:
                cells = row.find_all("td")
                data_tables[i]["table_data"].append({
                    "name": cells[0].text,
                    "ingredients": cells[1].text,
                    "image": cells[2].find("img")['src'], 
                    "description": cells[3].text 
                })
        self.data_frame = pd.DataFrame(data_tables)
        return self.data_frame

