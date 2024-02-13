import sqlite3
import random

# Create a connection to the SQLite database
conn = sqlite3.connect('orders.db')
cursor = conn.cursor()




cursor.execute('''
                INSERT INTO products (product_id, type, stock, price, sizes ,colors)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (88039, 'Adidas Pant', 100, 1500, 'L,S,M','Blue, Black, Green'))

conn.commit()
