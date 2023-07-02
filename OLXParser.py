import time
from time import sleep

import bs4
import requests
from bs4 import BeautifulSoup as bs
from init_xlsx import OLXWorkBook

class Basic():
    def __init__(self, soup):
        if soup is not bs4.BeautifulSoup: Exception("soup isn't BeautifulSoup")
        self.TITLE = soup.findAll("div", class_="css-sg1fy9")[1].text
        self.PRICE = soup.find("h3", class_="css-ddweki er34gjf0").text
        self.DESCRIPTION = soup.find("div", class_="css-bgzo2k er34gjf0").text
        self.PUBLISH_DATE = soup.findAll("div", class_="css-sg1fy9")[0].text
        self.URL = "None"


    def getValues(self):
        return [self.TITLE, self.PRICE, self.DESCRIPTION, self.PUBLISH_DATE, self.URL]

class Details():
    def __init__(self, soup):
        if soup is not bs4.BeautifulSoup: Exception("soup isn't BeautifulSoup")
        details = soup.findAll("li", class_="css-1r0si1e")

        self.PRIVATE = details[0].text if details[0] is not None else "None"
        self.STATE = details[1].text if details[1] is not None else "None"
        self.WITH_FURNITURE = details[2].text if details[2] is not None else "None"
        self.KIND_OF_BUILT = details[3].text if details[3] is not None else "None"
        self.SQUAD_METERS = details[4].text if details[4] is not None else "None"
        self.NUMBER_ROOMS = details[5].text if details[5] is not None else "None"
        self.PART = details[6].text if details[6] is not None else "None"

    def getValues(self):
        return [self.PRIVATE, self.STATE, self.WITH_FURNITURE,
                self.KIND_OF_BUILT, self.SQUAD_METERS,
                self.NUMBER_ROOMS, self.PART]

class RoomPage:
    __find_methods = dict()

    def __init__(self, page_url):
        self.__soup = bs(self.get_site(page_url).text, "html.parser")

        self.__basic = Basic(self.__soup)
        self.__details = Details(self.__soup)

        self.__basic.URL = page_url

    def get_basic(self):
        return self.__basic

    def get_detail(self):
        return self.__details

    def get_site(self, url):
        return requests.get(url)

class XLSXLoader():
    def __init__(self, site, xlsx_name = None):
        self.olxWorkBook = OLXWorkBook(xlsx_name) if not xlsx_name else OLXWorkBook()
        self.sheet = self.olxWorkBook.workBook.active

        self.all_offers = self.get_all_offers(site)
        self.basicTemplates = {"A": lambda b: b.TITLE,
                              "B": lambda b: b.PRICE,
                              "C": lambda b: b.DESCRIPTION,
                              "D": lambda b: b.URL,
                              "E": lambda b: b.PUBLISH_DATE}

        self.detailsTemplates = {"F": lambda b: b.PART,
                              "G": lambda b: b.NUMBER_ROOMS,
                              "H": lambda b: b.SQUAD_METERS,
                              "I": lambda b: b.KIND_OF_BUILT,
                              "J": lambda b: b.WITH_FURNITURE,
                              "K": lambda b: b.STATE,
                              "L": lambda b: b.PRIVATE}

        # title,price,des,pub,url

    def get_all_offers(self, url):
        offers_url = []
        soup = bs(requests.get(url).text, "html.parser")
        for offer in soup.findAll("a", class_="css-rc5s2u"):
            offers_url.append("https://www.olx.pl" + offer["href"])
        return offers_url

    def get_data(self, max_offer = None, print_information = False):
        current_id = int(self.sheet["B1"].value) + 2
        all_offer = max_offer if max_offer is not None else len(self.all_offers)
        for url_index in range(all_offer):
            try:
                current_offer = self.all_offers[url_index]
                rp = RoomPage(current_offer)

                base = rp.get_basic()
                details = rp.get_detail()

                if print_information:
                    print("|" + str(current_id) + "| Title: " + base.TITLE)

                for key in self.basicTemplates.keys():
                    self.sheet[key + str(current_id)] = self.basicTemplates[key](base)

                for key in self.detailsTemplates.keys():
                    self.sheet[key + str(current_id)] = self.detailsTemplates[key](details)

            except:
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                sleep(5)
                print("Was a nice sleep, now let me continue...")

            current_id += 1
        self.sheet["B2"] = str(current_id)

    def load_data(self, filename):
        self.olxWorkBook.load(filename)

    def save_data(self, filename):
        self.olxWorkBook.save(filename)