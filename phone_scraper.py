import psycopg2
import random
import bs4 as bs
import requests
import re
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
    row_count = 0
    for table in soup.findAll('table', {'class': 'wikitable sortable collapsible'}):
        for row in table.findAll('tr')[1:]:
            row_count = row_count +1
            if len(row.findAll('td')) == 17:        # in the website, some rows share the same column data, so
                # will skip them to make sure each row is "complete"
                barcode_no = random.randint(100000000000, 999999999999)
                model = row.findAll('td')[0].text.strip()
                brand = model.split(' ', 1)[0]
                cpu = row.findAll('td')[2].text.strip()
                storage = row.findAll('td')[4].text.strip().split(' ')[0].split('/')[0].split('\xa0')[0]
                if re.search("[a-zA-Z,:]", storage):
                    continue
                ram = row.findAll('td')[6].text.strip().split(' GB')[0].split(' ')[0].split('\xa0')[0].split('/')[0]
                if re.search("[a-zA-Z,:]", ram):
                    continue
                battery = row.findAll('td')[11].text.strip().split(' ')[0].split('m')[0]
                if re.search("[a-zA-Z,:]", battery):
                    continue
                product_list.append((barcode_no, brand, 0))
                phone_list.append((barcode_no, cpu, battery, model, storage, ram))
    return (product_list, phone_list)


def main():
    connection = make_connection()
    postgres_insert_query_product = """ INSERT INTO Product (barcode_no, brand, unit_price) 
                                        VALUES (%s,%s,%s)"""
    postgres_insert_query_phone = """INSERT INTO Phone (barcode_no, cpu, battery, model, storage, ram)  
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
