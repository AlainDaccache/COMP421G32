/* Part One:
The updated ER is attached as a pdf in the zipped submission
*/

/* Part Two:
Write a SQL database schema for the relational schema you have designed using the CREATE TABLE
command and enter it in the database. Choose suitable data types for your attributes. Indicate primary keys,
foreign keys or any other integrity constraints that you can express with the commands learnt. Indicate the
constraints you cannot express. The Online Information contains detailed information about data types, and
the CREATE TABLE statement
*/

CREATE table Customer (
                          email VARCHAR NOT NULL,
                          PRIMARY KEY (email)
);

CREATE TABLE Basket (
                        order_num INTEGER NOT NULL,
                        order_total INTEGER NOT NULL,
                        email VARCHAR NOT NULL,
                        time TIMESTAMP DEFAULT NOW(),
                        PRIMARY KEY (order_num),
                        Foreign KEY (email) REFERENCES Customer(email)
);

CREATE TABLE Product (
                         barcode_no VARCHAR NOT NULL,
                         brand VARCHAR NOT NULL,
                         color VARCHAR,
                         unit_price FLOAT NOT NULL,
                         order_num INT,
                         PRIMARY KEY (barcode_no),
                         foreign key (order_num) REFERENCES Basket(order_num)
);

CREATE table Employees (
                           eid INT NOT NULL,
                           home_address VARCHAR NOT NULL,
                           salary FLOAT NOT NULL,
                           PRIMARY KEY (eid)
);

CREATE table Warehouse (
                           address VARCHAR NOT NULL,
                           eid INT NOT NULL,
                           Primary Key (address),
                           FOREIGN KEY (eid) REFERENCES Employees(eid)
);

CREATE TABLE Phone (
                       barcode_no VARCHAR NOT NULL,
                       cpu VARCHAR NOT NULL,
                       battery Int NOT NULL,
                       model VARCHAR NOT NULL,
                       storage INT NOT NULL,
                       ram INT NOT NULL,
                       PRIMARY KEY (barcode_no),
                       FOREIGN KEY (barcode_no) REFERENCES Product(barcode_no)
);

CREATE TABLE Accessories (
                             barcode_no VARCHAR NOT NULL,
                             type VARCHAR NOT NULL,
                             PRIMARY KEY (barcode_no),
                             FOREIGN KEY (barcode_no) REFERENCES Product(barcode_no)
);

/* What it would have been without the feedback
CREATE TABLE Payment (
  order_num INT NOT NULL,
  email VARCHAR NOT NULL,
  payment_time TIMESTAMP NOT NULL,
  PRIMARY KEY (order_num, email),
  FOREIGN KEY (order_num) REFERENCES Basket(order_num),
  FOREIGN KEY (email) REFERENCES Customer(email)
);
*/

CREATE TABLE Stock(
                      barcode_no VARCHAR NOT NULL,
                      address VARCHAR NOT NULL,
                      PRIMARY KEY (barcode_no),
                      FOREIGN KEY (address) REFERENCES Warehouse(address)
);

CREATE TABLE Shift (
                       date VARCHAR NOT NULL,
                       start_time TIMESTAMP NOT NULL,
                       end_time TIMESTAMP NOT NULL,
                       shift_responsibility VARCHAR NOT NULL,
                       eid INT NOT NULL,
                       PRIMARY KEY (start_time, end_time, eid),
                       FOREIGN KEY (eid) REFERENCES Employees(eid)
);

CREATE TABLE PhoneAccessories(
                                 id INT,
                                 pBarcode VARCHAR NOT NULL,
                                 aBarcode VARCHAR NOT NULL,
                                 PRIMARY KEY (id),
                                 FOREIGN KEY (pBarcode) REFERENCES Phone(barcode_no),
                                 FOREIGN KEY (aBarcode) REFERENCES Accessories(barcode_no)
);

/*
The constraints that are not shown are
- The spinoff Employees =Manager=> Supervision -salesperson- Employees
- Some participation constraints. In fact, in relationships, it is possible
  to specify if there is a primary key constraint. For example, since the existence of
  a product isn't dependent on the existence of an order, we should be able to insert a
  product tuple without necessarily entering a order_id. Therefore, order_id, a foreign key
  to order, should not be specified NOT NULL in Product. If we do, then we should always specify
  an order id. However, this means that we cannot differentiate between an 'exactly one'
  and 'at least one'.

  It is possible to add the same phone to two different orders without warning?

*/

-- Turn in your CREATE TABLE statements.Furthermore, (i) for DB2 use command line processor command
-- DESCRIBE tablename (ii) for PostgreSQL use \d table name (prints the description of the relation on the
-- screen) for each of your relations, print the result and turn it in


-- \d Stock;
-- \d Warehouse;
-- \d Shift;
-- \d Employees;
-- \d Phone;
-- \d Accessories;
-- \d Product;
-- \d Basket;
-- \d Customer;



/* Part Three:
Execute five INSERT commands to insert tuples into one of your relations.
Turn in your INSERT statements. Furthermore, print and turn in the response of CPL/psql
when you type the INSERT commands.
*/

INSERT INTO Product (barcode_no, color, unit_price, brand)
VALUES
('03243234543', 'Gold', 699.99, 'Apple'),
('23456787654', 'White', 999.99, 'Samsung'),
('87654567876', 'Black', 39.99, 'Apple'),
('54323456722', 'Transparent', 15.99, 'Samsung'),
('23456789876', 'Pink', 399.99, 'Huawei');

-- Print and turn in the result when you issue a SELECT * FROM relationname command.
-- SELECT *
-- FROM Product;

/* Part Four:
Insert in all your tables enough meaningful information so that the queries that you create provide
meaningful results. The results of the following queries that you develop should have a reasonable number of
results so that we can be convinced that your queries are correct (maybe 5-10 tuples). If you have real-world
data, feel free to import it (but do not insert more than 500 records in a table). Information of how to import
data into DB2 tables is provided on my courses
*/

INSERT INTO Customer(email)
VALUES
('alain.daccache@mail.mcgill.ca'),
('aakarsh.shekhar@mail.mcgill.ca'),
('ketan.rampurkar@mail.mcgill.ca'),
('shayan.sheikh@mail.mcgill.ca'),
('hisham.hawara@mail.mcgill.ca');

INSERT INTO Employees(eid, salary, home_address)
VALUES
(1, 1000, '425 Backlemore Avenue, Montreal, Canada'),
(2, 2000, '843 Sherbrooke Street, Montreal, Canada'),
(3, 3000, '521 Milton Street, Montreal, Canada');

INSERT INTO Shift(date, start_time, end_time, shift_responsibility, eid)
VALUES
('02/21/2020', '2020-02-21 19:00:00-07', '2020-02-21 21:00:00-07', 'Cleanup', 1),
('02/22/2020', '2020-02-22 16:00:00-07', '2020-02-22 22:00:00-07', 'On help desk', 2),
('02/22/2020', '2020-02-22 12:00:00-07', '2020-02-22 14:00:00-07', 'On sales', 3),
('03/22/2020', '2020-03-22 12:00:00-07', '2020-03-22 20:00:00-07', 'On sales', 1)
;

INSERT INTO Phone (barcode_no, cpu, battery, model, storage, ram)
VALUES
('03243234543', 'ee', 3240, '0372A', 64, 16),
('23456787654', 'ee', 4120, '23BCA', 32, 8),
('23456789876', 'ee', 2350, '52XBY', 16, 4);

INSERT INTO Accessories(barcode_no, type)
VALUES
('54323456722', 'Samsung Screen Protector'),
('87654567876', 'iPhone Lightning to USB Charging Cable');

INSERT INTO Basket (order_num, order_total, email, time)
VALUES
(001, 2, 'alain.daccache@mail.mcgill.ca', NOW()),
(002, 1, 'ketan.rampurkar@mail.mcgill.ca', '2018-01-08 04:05:06');

UPDATE Product
SET order_num = 001
WHERE barcode_no = '03243234543';

UPDATE Product
SET order_num = 001
WHERE barcode_no = '54323456722';

UPDATE Product
SET order_num = 002
WHERE barcode_no = '87654567876';


-- For each table show the output, truncated to the first 5-10 tuples, that are returned when you
-- issue a SELECT * FROM relationname command
SELECT * FROM Product LIMIT 5;
SELECT * FROM Phone LIMIT 5;
SELECT * FROM Accessories LIMIT 5;
SELECT * FROM Basket LIMIT 5;
SELECT * FROM Customer LIMIT 5;
SELECT * FROM Shift LIMIT 5;
SELECT * FROM Stock LIMIT 5;
SELECT * FROM Warehouse LIMIT 5;
SELECT * FROM Employees LIMIT 5;


/* Part Five
Write five queries on your project database, using the select-from-where construct of SQL. The
queries should be typical queries of the application domain. To receive full credit, all but perhaps one of
your queries must exhibit some interesting feature of SQL: queries over more than one relation, subqueries,
aggregations, grouping etc.
Turn in a description of all the relations that you use in your queries (e.g., the original create
statements or printouts from the SQL â€œdescribe table yournameâ€ function), a description of
what each of your queries is supposed to do, the SQL statement of each query, along with a
script illustrating their execution (for example the screenshot when you execute the query).
Your script should be sufficient to convince us that your commands run successfully. Please do
not, however, turn in query results that are more than 50 lines long.
*/

-- Grouping and aggregation
-- Find the number of products for each brand
SELECT Product.brand, COUNT(Product.brand)
FROM Product
GROUP BY Product.brand
ORDER BY COUNT(Product.brand) DESC;

-- Query over more than one relation:
-- Find the email of customers that have purchased both a phone from the store
SELECT Customer.email
FROM Customer, Basket, Product, Phone
WHERE Phone.barcode_no = Product.barcode_no
  AND Basket.order_num = Product.order_num
  AND Customer.email = Basket.email;

-- Query over more than one relation:
-- Select the brands available such that the store has both a phone and an accessory for that brand
SELECT Product.brand
FROM Phone, Product
WHERE Phone.barcode_no = Product.barcode_no
INTERSECT
SELECT Product.brand
FROM Accessories, Product
WHERE Accessories.barcode_no = Product.barcode_no;

-- Nested Query:
-- Find the id of employees whose shifts are on 02/22/2020
SELECT eid
FROM Employees
WHERE eid IN (SELECT eid
              FROM Shift
              WHERE date = '02/22/2020');

-- Trivial query
-- List the phone models that have a RAM over 8 GB
SELECT Phone.model, Phone.ram
FROM Phone
WHERE Phone.ram > 8;

/* Part Six
Write four data modification commands for your application. Most of these commands should
be â€œinteresting,â€ in the sense that they involve some complex feature, such as inserting the result of a query,
updating several tuples at once, or deleting a set of tuples that is more than one but less than all the tuples in
a relation.
Turn in a description of all the relations that you use in your modifications but are not described
so far. Provide a short description of what each of your statements is supposed to do, the
SQL statements themselves and a script or screenshot that shows your modification commands
running in a convincing fashion.
*/

--update several tuples at once
-- Update the Samsung and Apple brand phones/accessories price due to 20% and 10% discount respectively on them
UPDATE Product
SET unit_price=(case when brand='Samsung' then unit_price*0.8
                     when brand='Apple' then unit_price*0.9
    end)
where brand in ('Samsung', 'Apple');

--insert result of a query
-- Insert the manager of the warehouse using the employee id in employees relation
insert into warehouse(address, eid)
select '3475 Rue Durocher, Montreal, Canada', eid
from employees
where eid=2;

--Change the shift responsibility to cleanup for eid={1,2,3,4}
--update several tuples at once
update shift
set shift_responsibility='Cleanup'
where eid in (1,2,3,4);

--Update the phone storage of the maximum bar code value of phone
update phone
set storage=64
where barcode_no=(select max(barcode_no) from phone);

/* Part 7: Create two views on top of your database schema.
Turn in an informal description what data each of the views represents, show your CREATE
VIEW statements and the response of the system. Also, show a query involving each view and
the system response (but truncate the response if there are more than a few tuples produced).
Finally, show a script of what happens when you try run an SQL UPDATE statement on each of
your views. Are either of your views updatable (that is, the database system will automatically
translate the update into an update on the base table(s). Explain why or why not. Summarize
the conditions that must hold so that DB2/PostgreSQL allows updating a view.*/

--Products that are demanded by the customers currently
CREATE VIEW ProductsDemanded (barcode_no, brand, color, unit_price, order_num)
AS SELECT * FROM Product
   WHERE order_num IS NOT NULL;


SELECT * FROM ProductsDemanded;

--List of employees who are on the cleanup duty for a particular shift
CREATE VIEW CleanupDutyStaff (date, start_time, end_time, shift_responsibility, eid)
AS SELECT * from Shift
   WHERE shift_responsibility='Cleanup';

SELECT * FROM CleanupDutyStaff;

UPDATE ProductsDemanded SET order_num=1 where ProductsDemanded.barcode_no='03243234543';
update CleanupDutyStaff set eid=1  where CleanupDutyStaff.start_time='2020-02-22 19:00:00.000000' and CleanupDutyStaff.end_time='2020-02-22 21:00:00.000000';

drop VIEW ProductsDemanded;
drop VIEW CleanupDutyStaff;

/* Part 8
 Add two CHECK constraints to relations of your database schema.
Turn in the revised schema, its successful declaration, and the response of database
 to modifications (insert/update) that violate the constraints.
--  */

-- Inserting in-correct values
INSERT INTO Employees(eid, salary, home_address)
VALUES
(4, -1500, '320 rue Sherbrooke O., Montreal, Canada ');

INSERT INTO Shift(date, start_time, end_time, shift_responsibility, eid)
VALUES
('02/22/2020', '2020-02-22 13:00:00-07', '2020-02-22 10:00:00-07', 'Customer assistance', 4);

-- Revising the schema
ALTER TABLE employees
    ADD CONSTRAINT valid_salary_check CHECK (salary >= 0);

ALTER TABLE shift
    ADD CONSTRAINT valid_time_check CHECK (end_time > start_time);

-- DROP TABLE Stock;
-- DROP table Warehouse;
-- DROP TABLE Shift;
-- DROP TABLE Employees;
-- DROP TABLE PhoneAccessories;
-- DROP TABLE Phone;
-- DROP TABLE Accessories;
-- DROP TABLE Product;
-- DROP table Basket;
-- DROP table Customer;
