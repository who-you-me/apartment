# -*- coding: utf-8 -*-

import pathlib
import random
import time

import click
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager


DOWNLOAD_URL = 'https://www.land.mlit.go.jp/webland/servlet/DownloadServlet'


@click.command()
@click.argument('prefecture')
@click.argument('city')
@click.argument('output_path')
def download(prefecture: str, city: str, output_path: str):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {'download.default_directory': str(pathlib.Path(output_path).resolve())})
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        driver.get(DOWNLOAD_URL)
        select_from = Select(driver.find_element(by=By.ID, value='TDIDFrom'))
        select_from.select_by_index(len(select_from.options) - 1)

        select_prefecture = Select(driver.find_element(by=By.ID, value='TDK'))
        select_prefecture.select_by_visible_text(prefecture)

        if city:
            cities = [option.text
                      for option in Select(driver.find_element(by=By.ID, value='SKC')).options
                      if option.text.startswith(city)]
        else:
            cities = [option.text for option in Select(driver.find_element(by=By.ID, value='SKC')).options][1:]
        for city in cities:
            select_city = Select(driver.find_element(by=By.ID, value='SKC'))
            select_city.select_by_visible_text(city)
            button = driver.find_element(by=By.ID, value='download_button')
            button.click()
            time.sleep(3 + random.random())
    finally:
        driver.close()


if __name__ == '__main__':
    download()
