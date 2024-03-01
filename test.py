# import sqlite3
# import random
#
# # Create a connection to the SQLite database
# conn = sqlite3.connect('orders.db')
# cursor = conn.cursor()
#
#
#
#
# cursor.execute('''
#                 INSERT INTO products (product_id, type, stock, price, sizes ,colors)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             ''', (12333, 'Nike rack', 100, 1700, 'L,S,M','Blue, Black, Green'))
#
# conn.commit()
# conn.close()
import mysql.connector

# Connect to the MySQL server
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='BIZZBOT123',
    database='Enterprise_Database'
)
cursor = conn.cursor()

order_id = 5211
cursor.execute('''
    SELECT o.order_number, o.order_date, p.product_id, o.phone_number, o.status,
           op.quantity, p.type, p.stock, p.price, op.size, op.color
    FROM orders o
    JOIN order_products op ON o.order_number = op.order_number
    JOIN products p ON op.product_id = p.product_id
    WHERE o.order_number = %(order_id)s
''', {'order_id': int(order_id)})


# Fetch the result
result = cursor.fetchall()
print(result)
# Commit the changes and close the connection
conn.commit()
conn.close()

