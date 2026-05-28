# STEP 0

# SQL Library and Pandas Library
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('data.sqlite')

pd.read_sql("""SELECT * FROM sqlite_master""", conn)

# STEP 1
# Employees working in the Boston office (firstName, city)
df_boston = pd.read_sql("""
    SELECT e.firstName, o.city
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE o.city = 'Boston'
""", conn)

# STEP 2
# Offices with zero employees (empty result if all offices have staff)
df_zero_emp = pd.read_sql("""
    SELECT o.officeCode, o.city
    FROM offices o
    LEFT JOIN employees e ON o.officeCode = e.officeCode
    WHERE e.employeeNumber IS NULL
""", conn)

# STEP 3
# All employees with their office city and state, ordered by firstName then lastName
df_employee = pd.read_sql("""
    SELECT e.firstName, e.lastName, o.city, o.state
    FROM employees e
    LEFT JOIN offices o ON e.officeCode = o.officeCode
    ORDER BY e.firstName, e.lastName
""", conn)

# STEP 4
# Customers who have never placed an order, sorted by contactLastName
df_contacts = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, c.phone, c.salesRepEmployeeNumber
    FROM customers c
    LEFT JOIN orders o ON c.customerNumber = o.customerNumber
    WHERE o.orderNumber IS NULL
    ORDER BY c.contactLastName
""", conn)

# STEP 5
# All customer payments with contact info, sorted by amount descending
df_payment = pd.read_sql("""
    SELECT c.contactFirstName, c.contactLastName, p.amount, p.paymentDate
    FROM customers c
    JOIN payments p ON c.customerNumber = p.customerNumber
    ORDER BY CAST(p.amount AS FLOAT) DESC
""", conn)

# STEP 6
# Employees whose customers have average credit limit > 90k, sorted by customer count desc
df_credit = pd.read_sql("""
    SELECT e.employeeNumber, e.firstName, e.lastName, COUNT(c.customerNumber) AS numcustomers
    FROM employees e
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY e.employeeNumber, e.firstName, e.lastName
    HAVING AVG(c.creditLimit) > 90000
    ORDER BY numcustomers DESC
""", conn)

# STEP 7
# Products with total orders and total units sold, sorted by totalunits desc
df_product_sold = pd.read_sql("""
    SELECT p.productName, COUNT(od.orderNumber) AS numorders, SUM(od.quantityOrdered) AS totalunits
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    GROUP BY p.productName
    ORDER BY totalunits DESC
""", conn)

# STEP 8
# Products with count of unique customers who purchased them, sorted by numpurchasers desc
df_total_customers = pd.read_sql("""
    SELECT p.productName, p.productCode, COUNT(DISTINCT o.customerNumber) AS numpurchasers
    FROM products p
    JOIN orderdetails od ON p.productCode = od.productCode
    JOIN orders o ON od.orderNumber = o.orderNumber
    GROUP BY p.productName, p.productCode
    ORDER BY numpurchasers DESC
""", conn)

# STEP 9
# Number of customers per office
df_customers = pd.read_sql("""
    SELECT COUNT(c.customerNumber) AS n_customers, o.officeCode, o.city
    FROM offices o
    JOIN employees e ON o.officeCode = e.officeCode
    JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
    GROUP BY o.officeCode, o.city
""", conn)

# STEP 10
# Employees who sold products ordered by fewer than 20 distinct customers
df_under_20 = pd.read_sql("""
    SELECT DISTINCT e.employeeNumber, e.firstName, e.lastName, o.city, o.officeCode
    FROM employees e
    JOIN offices o ON e.officeCode = o.officeCode
    WHERE e.employeeNumber IN (
        SELECT DISTINCT c.salesRepEmployeeNumber
        FROM customers c
        JOIN orders ord ON c.customerNumber = ord.customerNumber
        JOIN orderdetails od ON ord.orderNumber = od.orderNumber
        WHERE od.productCode IN (
            SELECT od2.productCode
            FROM orderdetails od2
            JOIN orders ord2 ON od2.orderNumber = ord2.orderNumber
            GROUP BY od2.productCode
            HAVING COUNT(DISTINCT ord2.customerNumber) < 20
        )
    )
    ORDER BY e.lastName
""", conn)

conn.close()
