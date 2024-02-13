import sqlite3

# Create a connection to the SQLite database
conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

# Create the products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        stock INTEGER,
        price REAL,
        sizes TEXT,
        colors TEXT
    )
''')

# Create the orders table with order_number as the primary key
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_number INTEGER PRIMARY KEY,
        order_date TEXT ,
        order_time TEXT,
        phone_number TEXT,
        status TEXT
    )
''')

# Create the order_products table to represent the many-to-many relationship
cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_products (
        order_number INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        color REAL,
        size REAL,
        PRIMARY KEY (order_number, product_id),
        FOREIGN KEY (order_number) REFERENCES orders(order_number),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
