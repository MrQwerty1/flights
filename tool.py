import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date, timedelta
from lxml import html


dates = ['Price{}'.format((date.today() + timedelta(i)).strftime('%Y-%m-%d')) for i in range(366)]
fieldnames = ['RequestURL', 'ResponseURL', 'OrigName', 'OrigCode', 'DestName', 'DestCode', 'ShownFlights',
              'HiddenFlights', 'Airlines', 'MinStops', 'MaxStops', 'CurrentDate'] + dates

options = Options()
options.headless = True
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
fox = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=options)


w = open('data.csv', 'w', encoding='utf8', newline='')
wr = csv.DictWriter(w, fieldnames)
wr.writeheader()


def parse(source, s_url, e_url):
    tree = html.fromstring(source)
    row = {
        'RequestURL': s_url,
        'ResponseURL': e_url,
        'OrigName': ''.join(tree.xpath("//span[@class='gws-flights-form__location-icon gws-flights-form__origin-icon']/following-sibling::div[1]//span[@class='gws-flights-form__location-list']/span/span[not(@class)]/text()")),
        'OrigCode': ''.join(tree.xpath("//span[@class='gws-flights-form__location-icon gws-flights-form__origin-icon']/following-sibling::div[1]//span[@class='gws-flights-form__iata-code']/text()")),
        'DestName': ''.join(tree.xpath("//span[@class='gws-flights-form__location-icon']/following-sibling::div[1]//span[@class='gws-flights-form__location-list']/span/span[not(@class)]/text()")),
        'DestCode': ''.join(tree.xpath("//span[@class='gws-flights-form__location-icon']/following-sibling::div[1]//span[@class='gws-flights-form__iata-code']/text()")),
        'ShownFlights': len(tree.xpath("//li[.//span[contains(@class, 'gws-flights-results__more')]]")),
        'Airlines': '|'.join(tree.xpath("//section[@class='gws-flights-filter__airline-list']/ol[@class='gws-flights__list']/li/span[not(@role)]/text()")),
        'CurrentDate': date.today().strftime('%Y-%m-%d')
    }
    try:
        row['HiddenFlights'] = tree.xpath("//a[@class='gws-flights-results__dominated-link']//span/text()")[0].split()[0]
    except:
        row['HiddenFlights'] = ''
    try:
        row['MinStops'] = tree.xpath("//ol[@class='gws-flights__list']/li[@class='gws-flights__list-radio-item']/jsl/text()")[0]
    except:
        row['MinStops'] = ''
    try:
        row['MaxStops'] = tree.xpath("//ol[@class='gws-flights__list']/li[@class='gws-flights__list-radio-item']/jsl/text()")[-1].replace(' stops or fewer', '')
    except:
        row['MaxStops'] = ''

    for i in range(366):
        d = (date.today() + timedelta(i)).strftime('%Y-%m-%d')
        key = 'Price{}'.format(d)
        try:
            row[key] = tree.xpath("//calendar-day[@data-day='{}']//span/text()".format(d))[0]
        except:
            pass

    wr.writerow(row)
    print(e_url)


def airlines():
    fox.find_element_by_xpath("//filter-chip[@data-chip='airlines']").click()
    time.sleep(1.5)
    fox.find_element_by_xpath("//filter-chip[@data-chip='airlines']").click()
    time.sleep(3)
    fox.find_element_by_xpath("//filter-chip[@data-chip='stops']").click()
    time.sleep(1.5)
    fox.find_element_by_xpath("//filter-chip[@data-chip='stops']").click()
    time.sleep(3)


def scroll():
    fox.find_element_by_xpath("//div[@class='flt-input gws-flights__flex-box gws-flights__flex-filler gws-flights-form__departure-input gws-flights-form__round-trip']").click()
    time.sleep(3)
    while True:
        try:
            time.sleep(5)
            fox.find_element_by_xpath("//div[@class='gws-travel-calendar__flipper gws-travel-calendar__prev']").click()
        except:
            break
    while True:
        try:
            time.sleep(5)
            fox.find_element_by_xpath("//div[@class='gws-travel-calendar__flipper gws-travel-calendar__next']").click()
        except:
            break
    time.sleep(2)
    fox.find_element_by_xpath("//g-raised-button[@data-flt-ve='done']").click()
    time.sleep(2)


cnt = 0
with open('links.txt') as urls:
    for url in urls.read().split('\n'):
        fox.get(url)
        time.sleep(10)
        airlines()
        scroll()
        with open('html/{}.html'.format(cnt), 'w', encoding='utf8') as qq:
            qq.write(fox.page_source)
        parse(fox.page_source, url, fox.current_url)
        cnt += 1


