import typing
import requests
from urllib.parse import urljoin
import bs4
import time
import pymongo
import datetime


class GbBlogParse_Margarita:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    __parse_time = 0

    def __init__(self, start_url, db, delay=1.0):
        self.start_url = start_url
        self.db = db
        self.delay = delay
        self.done_url: typing.Set[str] = set()
        self.tasks: typing.List[typing.Callable] = []
        self.task_creator({self.start_url,}, self.parse_feed)


    def _get_response(self, url):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            print(f"RESPONSE: {response.url}")
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            response = self._get_response(url)
            return callback(response)

        return task

    def run(self):
        while True:
            try:
                task = self.tasks.pop(0)
                task()
            except IndexError:
                break

    def task_creator(self, urls: set, callback):
        urls_set = urls - self.done_url
        for url in urls_set:
            self.tasks.append(self.get_task(url, callback))
            self.done_url.add(url)

    def parse_feed(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, "lxml")
        ul_pagination = soup.find("ul", attrs={"class": "gb__pagination"})
        self.task_creator(
            {
                urljoin(response.url, a_tag.attrs["href"])
                for a_tag in ul_pagination.find_all("a")
                if a_tag.attrs.get("href")
            },
            self.parse_feed,
        )
        post_wrapper = soup.find("div", attrs={"class": "post-items-wrapper"})
        self.task_creator(
            {
                urljoin(response.url, a_tag.attrs["href"])
                for a_tag in post_wrapper.find_all("a", attrs={"class": "post-item__title"})
                if a_tag.attrs.get("href")
            },

            self.parse_post,
        )
    def get_comment(self, id_com):
        url_com = 'https://gb.ru/api/v2/comments'
        params = {"commentable_type": "Post",
                  "commentable_id": id_com}
        response_com = requests.get(url_com, params=params, headers=self.headers)
        data = response_com.json()
        comments = []
        for element in data:
            val_com = element.values()
            comment = {}
            for elem in val_com:
                user_dict = elem.get('user', None)
                user_com = user_dict.get('full_name', None)
                text_com = elem.get('body', None)
                comment = {"comment_author": user_com, "comment_text": text_com}
            comments.append(comment)
        return comments

    def parse_post(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, "lxml")
        author_name_tag = soup.find("div", itemprop="author")
        year = int(soup.find("time", attrs={"class": "m-r-md"}).attrs.get("datetime")[0:4])
        month = int(soup.find("time", attrs={"class": "m-r-md"}).attrs.get("datetime")[5:7])
        day = int(soup.find("time", attrs={"class": "m-r-md"}).attrs.get("datetime")[8:10])
        hour = int(int(soup.find("time", attrs={"class": "m-r-md"}).attrs.get("datetime")[11:13]))
        minute = int(int(soup.find("time", attrs={"class": "m-r-md"}).attrs.get("datetime")[14:16]))
        second = int(int(soup.find("time", attrs={"class": "m-r-md"}).attrs.get("datetime")[17:19]))
        id_com = soup.find("div", attrs={"class": "referrals-social-buttons-small-wrapper"}).attrs.get("data-minifiable-id")
        data_comm = self.get_comment(id_com)

        data = {
            "url": response.url,
            "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
            "date": datetime.datetime(year, month, day, hour, minute, second),
            "img": soup.find("img").attrs.get("src"),
            "author": {
                "url": urljoin(response.url, author_name_tag.parent.attrs.get("href")),
                "name": author_name_tag.text},

            "comment": data_comm
        }
        self._save(data)


    def _save(self, data):
        collection = self.db["gb_parse_Margarita"]["gb_parse_24.05"]
        collection.insert_one(data)


if __name__ == "__main__":
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    parser = GbBlogParse_Margarita("https://gb.ru/posts", db_client, 0.5)
    parser.run()