import psycopg2
from random import seed
from random import random
import bs4 as bs
import pickle
import requests

def make_connection():
    connection = psycopg2.connect(user="cs421g32",
                              password="KashmirForPakistan98",
                              host="comp421.cs.mcgill.ca",
                              port="5432",
                              database="cs421")
    return connection


def scrape_phones():

    resp = requests.get('https://en.wikipedia.org/wiki/Comparison_of_smartphones')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    product_list = []
    phone_list = []
    for table in soup.findAll('table', {'class': 'wikitable sortable collapsible'}):
        for row in table.findAll('tr')[1:]:
            if len(row.findAll('td')) == 17:        # in the website, some rows share the same column data, so
                                                    # will skip them to make sure each row is "complete"
                seed(1)
                barcode_no = round(random() * 10**12)
                model = row.findAll('td')[0].text.strip()
                brand = model.split(' ', 1)[0]
                cpu = row.findAll('td')[2].text.strip()
                storage = row.findAll('td')[4].text.strip().split(' ', 1)[0]
                ram = row.findAll('td')[6].text.strip()
                battery = row.findAll('td')[11].text.strip()
                product_list.append((barcode_no, brand, 0))
                phone_list.append((barcode_no, cpu, battery, model, storage, ram))

    return (product_list, phone_list)


def main():
    connection = make_connection()
    postgres_insert_query_product = """ INSERT INTO Product (barcode_no, color, unit_price, brand) 
                                        VALUES (%s,%s,%s,%s)"""
    postgres_insert_query_phone = """INSERT INTO Phone (barcode_no, cpu_speed, battery, model, storage, ram)  
                                     VALUES (%s, %s, %s, %s, %s, %s)"""

    (product_list, phone_list) = scrape_phones()
    cursor = connection.cursor()

    cursor.executemany(postgres_insert_query_product, product_list)
    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into product table")

    cursor.executemany(postgres_insert_query_phone, phone_list)
    connection.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into phone table")

    return 0


main()
