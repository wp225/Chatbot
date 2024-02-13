import sqlite3
import random

# Create a connection to the SQLite database
conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

# Delete existing data
cursor.execute('DELETE FROM products')
cursor.execute('DELETE FROM orders')
cursor.execute('DELETE FROM order_products')

# Commit the deletion changes
conn.commit()


cursor.execute('''
                INSERT INTO products (product_id, type, stock, price, sizes ,colors)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (88039, 'Adidas Pant', 100, 1500, 'L,S,M','Blue, Black, Green'))

conn.commit()
