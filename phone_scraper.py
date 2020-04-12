import numpy as np
import psycopg2
import random
import bs4 as bs
import requests
import re
from datetime import timedelta, datetime
from Tools.scripts.treesync import raw_input
import matplotlib.pyplot as plt
import csv

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
    resp = requests.get('https://en.wikipedia.org/w/index.php?title=Comparison_of_smartphones&diff=943525120&oldid=943523606')
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

                product_list.append((barcode_no, brand, random.randint(500, 1000)))
                phone_list.append((barcode_no, cpu, battery, model, storage, ram))
    return product_list, phone_list


def populate_purchases():
    try:

        postgres_insert_query_basket = "INSERT INTO Basket(order_num, order_total, email, time)" \
                                       "VALUES(%s, %s, %s, %s);"

        # Preparing Baskets Entries
        order_no = [x for x in range(1000, 1050)]
        random_dates = []
        start_date = datetime(2019, 1, 1)
        end_date = datetime(2020, 1, 1)
        for i in range(50):
            random_dates.append(start_date + timedelta(
                # Get a random amount of seconds between `start` and `end`
                seconds=random.randint(0, int((end_date - start_date).total_seconds())),
            ))

        baskets = []
        for i in range(50):
            baskets.append((order_no[i], 1, "alain.daccache@mail.mcgill.ca",random_dates[i]))

        cursor = connection.cursor()
        cursor.executemany(postgres_insert_query_basket, baskets)
        connection.commit()
        print("50 records inserted into basket table")

        postgres_update_query_product =  """UPDATE Product
                                            SET order_num = %s
                                            WHERE barcode_no in (SELECT barcode_no FROM Product LIMIT 50); """

        for i in range(50):
            cursor.execute(postgres_update_query_product, [order_no[i]])
            connection.commit()

        print("Updated 50 products purchased")

        # cursor.execute("SELECT barcode_no FROM Product LIMIT 50")
        # barcodes = cursor.fetchall()
        # print(barcodes)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching Customer records from PostgreSQL: ", error)

    finally:
        cursor.close()


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

def cheapest_and_expensive_product(brand):

    try:
        cursor = connection.cursor()
        postgres_fetch_query_prod = """SELECT * FROM product
                                                WHERE brand = %s
                                                AND ( unit_price <= ALL
                                                (
                                                  SELECT unit_price FROM product
                                                  WHERE brand = %s
                                                )
                                                OR unit_price >= ALL
                                                (
                                                  SELECT unit_price FROM product
                                                  WHERE brand = %s
                                                ))
                                                ORDER BY unit_price ASC; """
        cursor.execute(postgres_fetch_query_prod, brand, brand, brand)
        record = cursor.fetchall()
        if (len(record) == 0):
            print("No product from " + str(brand))
        else:
            print('Cheapest product from ' + str(brand) + ': ')
            print(record[0])
            print('Most expensive product from ' + str(brand) + ': ')
            print(record[1])

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching records from PostgreSQL: ", error)

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

'''
Export the brand distribution data to CSV and draw a piechart depicting the percentage of the products owned by each brand
SQL used, PNG image and the CSV file have been included
'''
def export_brand_distribution_csv():
    try:
        cursor = connection.cursor()
        # need superuser access
        postgreSQL_copy_Query = "\copy (SELECT brand, COUNT(*) FROM Product GROUP BY brand) TO 'brand_distribution.csv' WITH CSV;"
        cursor.execute(postgreSQL_copy_Query)

    except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL: ", error)

    finally:
        cursor.close()

'''
Export the overall sales data to CSV and draw a barchart of sales for each month
SQL used, PNG image and the CSV file have been included
'''
def export_overall_sales_csv():
    try:
        cursor = connection.cursor()
        # need superuser access
        postgreSQL_copy_Query = "\copy (SELECT EXTRACT(month from time) as Month, COALESCE(SUM(unit_price), 0) as Sales FROM Basket b LEFT OUTER JOIN Product p ON b.order_num = p.order_num GROUP BY Month ORDER BY Month) TO 'overall_sales.csv' WITH CSV;"
        cursor.execute(postgreSQL_copy_Query)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL: ", error)

    finally:
        cursor.close()

'''
Read the CSV data (change the location of the CSV file as per your device) of brand distribution data and plot using matplotlib
'''
def draw_brand_distribution():
    brand=[]
    product_count=[]
    with open('/home/cs421g32/brand_distribution.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            brand.append(row[0])
            product_count.append(row[1])

    fig1, ax1 = plt.subplots()
    ax1.pie(product_count, labels=brand, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.show()

'''
Read the CSV data (change the location of the CSV file as per your device) of overall sales and plot using matplotlib
'''
def draw_overall_sales():
    y_pos=[]
    sales=[]
    with open('/home/cs421g32/overall_sales.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            y_pos.append(row[0])
            sales.append(row[1])

    months = [datetime(2020, i+1, 1).strftime('%b') for i in range(12)]
    plt.bar(y_pos, sales, align='center', alpha=0.5)
    plt.xticks(y_pos, months)
    plt.ylabel('Sales (in $)')
    plt.title('Overall Sales per Month')
    plt.show()



def run_app():
    while True:

        print ("""
                                    Command                                                     Description
            ---------------------------------------------------------------------------------------------------------------
            findInactive t                                                          Look up emails of customers inactive for t months
            addPhone brand price barcode_no cpu battery model storage ram    Add a phone to the database
            Ketan
            describeBrandProducts brand                                            List cheapest and most expensive product from brand
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

        elif ans[0] == "describeBrandProducts":
            cheapest_and_expensive_product(ans[1])

        elif ans[0] == "Shayan":
            print("Shayan's Part")

        elif ans[0] == "exit":
            connection.close()
            exit()

        elif ans != "":
            print("\n Not Valid Choice Try again")

def main():

    # Question 1:
    # Enforce a constraint by searching your database for violations and fixing them in some way.
    check_shift_time()

    # Question 2:
    # run_app()

    # Question 4 (a)
    # Scrape the web to populate the Phones relation
    populate_phones()
    # Visualize products by brand in a piechart
    export_brand_distribution_csv()

    # Question 4 (b)
    # Populate purchases to be able to visualize
    # (will give error if you run again since the records are already stored
    populate_purchases()
    # Visualize overall sales per month
    export_overall_sales_csv()

    # Question 5 (for creativity points)
    #loading data using CSV into the program and visualizing it
    draw_brand_distribution()
    draw_overall_sales()


main()

'''
Sample Commands:

addPhone Apple 130 1234543 42 4200 iPhoneX 64 32

'''
