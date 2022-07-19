import datetime
import sqlite3
from time import sleep

from fake_useragent import UserAgent
import requests

ua = UserAgent()

connection = sqlite3.connect('data_anal.db')
q = connection.cursor()


def floor(rarity):
    url = f'https://api-crypto.letmespeak.org/api/escrow?sortBy=LowestPrice&rarity={rarity}&page=1'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('items')
    floor0 = items[0]['price']
    floor1 = items[1]['price']
    floor2 = items[2]['price']
    floor = round((floor0 + floor1 + floor2) / 3, 2)
    return floor


def checking_start():
    while True:
        try:
            floor_uncommon = floor(2)

            sleep(5)

            floor_rare = floor(3)
            sleep(5)
            floor_epic = floor(4)
            sleep(5)
            floor_legendary = floor(5)
            sleep(5)
            now = datetime.datetime.now()
            q.execute(f"INSERT INTO anal (uncommon, rare, epic, legendary, time)"
                      f"VALUES ('{floor_uncommon}', '{floor_rare}', '{floor_epic}', '{floor_legendary}', '{now}')")
            connection.commit()
            sleep(1200)
        except Exception as As:
            print(As)
            sleep(100)


def main():
    checking_start()


if __name__ == '__main__':
    main()
