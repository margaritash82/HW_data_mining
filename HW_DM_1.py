import json
import requests
from pathlib import Path
import time

class Parse5ka:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    }

    def __init__(self, start_url_cat: str, start_url_pars: str, save_dir: Path):
        self.start_url_pars = start_url_pars
        self.save_dir = save_dir
        self.start_url_cat = start_url_cat

    def _get_response_categories(self, url_categories) -> requests.Response:
        while True:
            response_categories = requests.get(url_categories, headers=self.headers)
            if response_categories.status_code == 200:
                return response_categories
            time.sleep(0.2)


    def _parse_categories (self, url_categories, url):
        response_categories = self._get_response_categories(url_categories)
        data = response_categories.json()

        for element in data:
            code = int(element.setdefault("parent_group_code", None))
            name = element.setdefault("parent_group_name",None)
            param = {"categories": code}
            response = requests.get(url, params=param, headers=self.headers)
            data2 = response.json()
            products = []
            for product in data2:
                product = data2.get('results')
                products.append(product)
            category = {"name": name, "code": code, "products": products}
            yield category


    def run(self):
        for category in self._parse_categories(self.start_url_pars, self.start_url_cat):
            file_name = f"{category['code']}.json"
            file_path = self.save_dir.joinpath(file_name)
            self._save(category, file_path)

    def _save(self, data: dict, file_path: Path):
        with open(f"{file_path}", "w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False)

def get_dir_path(dir_name: str) -> Path:
    dir_path = Path(__file__).parent.joinpath(dir_name)
    if not dir_path.exists():
        dir_path.mkdir()
    return dir_path


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    url_categories = "https://5ka.ru/api/v2/categories/"
    save_dir = get_dir_path("categories")
    parser = Parse5ka(url, url_categories, save_dir)
    parser.run()



