from argparse import ArgumentParser

import psycopg2
import random
import bs4 as bs
import requests
import re
from datetime import timedelta, datetime
from Tools.scripts.treesync import raw_input

# Connect with the database
try:
    connection = psycopg2.connect(user="cs421g32",
                                  password="KashmirForPakistan98",
                                  host="comp421.cs.mcgill.ca",
                                  port="5432",
                                  database="cs421")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to Postgres Database", error)


def scrape_phones():
    resp = requests.get('https://en.wikipedia.org/wiki/Comparison_of_smartphones')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    product_list = []
    phone_list = []
    row_count = 0
    for table in soup.findAll('table', {'class': 'wikitable sortable collapsible'}):
        for row in table.findAll('tr')[1:]:
            row_count = row_count + 1
            if len(row.findAll('td')) == 17:  # in the website, some rows share the same column data, so
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
    return product_list, phone_list


def populate_phones():
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


def find_inactive(months):
    try:
        cursor = connection.cursor()
        postgres_fetch_query_inactive = """SELECT c.email FROM Customer c, Basket b
                                            WHERE b.email = c.email
                                            AND (DATE_PART('year', NOW()) - DATE_PART('year', time) ) * 12 
                                        + (DATE_PART('month', NOW()) - DATE_PART('month', time)) > %s """
        cursor.execute(postgres_fetch_query_inactive, months)
        customer_records = cursor.fetchall()
        if (len(customer_records) == 0):
            print("No inactive customers emails for the specified period")
        else:
            print('Inactive Customers email(s) for the specified period are: ')
            for row in customer_records:
                print(row[0])

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching Customer records from PostgreSQL: ", error)

    finally:
        cursor.close()

def add_phone(brand, price, barcode, cpu, battery, model, storage, ram):

    postgres_insert_query_phone = """INSERT INTO Phone (barcode_no, cpu, battery, model, storage, ram)  
                                     VALUES (%s, %s, %s, %s, %s, %s)"""

    postgres_insert_query_product = """ INSERT INTO Product (barcode_no, brand, unit_price) 
                                        VALUES (%s, %s, %s)"""

    cursor = connection.cursor()

    try:
        cursor.execute(postgres_insert_query_product, (barcode, brand, price))
        connection.commit()
        cursor.execute(postgres_insert_query_phone, (barcode, cpu, battery, model, storage, ram))
        connection.commit()
        count = cursor.rowcount
        print(count, "Phone record successfully inserted into the database")
    except (Exception, psycopg2.Error) as error:
        print("Error while inserting Phone record into the database: ", error)

    finally:
        cursor.close()


def check_shift_time():
    try:
        cursor = connection.cursor()
        postgreSQL_select_Query = "SELECT eid, start_time, end_time FROM Shift;"

        cursor.execute(postgreSQL_select_Query)
        shift_records = cursor.fetchall()

        for row in shift_records:
            if abs(row[1] - row[2]) > timedelta(hours = 4) and datetime.now() < row[1]:
                try:
                    postgreSQL_update_Query = "UPDATE Shift " \
                                              "SET end_time = (start_time  + interval '1h' * 4) " \
                                              "WHERE eid = %s AND start_time = %s AND end_time = %s ;"
                    cursor.execute(postgreSQL_update_Query, (row[0], row[1], row[2]))
                    connection.commit()
                    print("Successfully updated shift time for employee ", row[0])
                except (Exception, psycopg2.Error) as error:
                    print("Error while updating data into PostgreSQL")
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL: ", error)

    finally:
        cursor.close()

def main():
        # Scrape the web to populate the Phones relation
        # populate_phones()

        # Enforce a constraint by searching your database for violations and fixing them in some way.
        # check_shift_time()

        while True:

            print ("""
                                    Command                                                     Description
            ---------------------------------------------------------------------------------------------------------------
            findInactive t                                                          Look up emails of customers inactive for t months
            addPhone brand price barcode_no cpu battery model storage ram    Add a phone to the database
            Ketan
            Aakarsh
            Shayan
            exit                                                                    Exit program
            """)

            ans = raw_input("What would you like to do? ").split()

            if ans[0] == "findInactive" and len(ans) == 2:
                find_inactive(ans[1])

            elif ans[0] == "addPhone" and len(ans) == 9:
                add_phone(ans[1], ans[2], ans[3], ans[4], ans[5], ans[6], ans[7], ans[8])

            elif ans[0] == "Ketan":
                print("Ketan's Part")

            elif ans[0] == "Aakarsh":
                print("Aakarsh's Part")

            elif ans[0] == "Shayan":
                print("Shayan's Part")

            elif ans[0] == "exit":
                connection.close()
                exit()

            elif ans != "":
                print("\n Not Valid Choice Try again")

main()

'''
Sample Commands:

addPhone Apple 130 1234543 42 4200 iPhoneX 64 32

'''
