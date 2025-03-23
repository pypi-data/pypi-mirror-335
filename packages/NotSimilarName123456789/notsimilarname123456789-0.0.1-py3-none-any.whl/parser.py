import pandas as pd
import requests
from bs4 import BeautifulSoup

class RecipeScraper:
    def __init__(self) -> None:
        self.soup = None
        self.data_frame = None

    def scrap_url(self, url:str) -> None:
        responce = requests.get(url)
        responce.encoding = 'utf-8'
        self.soup = BeautifulSoup(responce.text, "html.parser")
        print(self.soup)

    def get_table_data(self) ->pd.DataFrame:
        headers = self.soup.find_all('h2')
        tables = self.soup.find_all('table')[1:]
        dataTables = []
        for i, table in enumerate(tables):
            tabel_rows = table.find_all('tr')[1:]
            dataTables.append({
                "table_name": headers[i].text,
                "table_data": []
            })

            for row in tabel_rows:
                cells = row.find_all('td')
                dataTables[i]['table_data'].append({
                    'name':cells[0].text,
                    'ingridients': cells[1].text,
                    'image':cells[2].find('img')['src'],
                    'description':cells[3].text

                })


        self.data_frame = pd.DataFrame(dataTables)
        return self.data_frame
