PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        stock INTEGER,
        price REAL,
        sizes TEXT,
        colors TEXT
    );
INSERT INTO products VALUES(12332,'Nike Track',95,1700.0,'L,S,M','Blue, Black, Green');
INSERT INTO products VALUES(12333,'Nike rack',100,1700.0,'L,S,M','Blue, Black, Green');
INSERT INTO products VALUES(20650,'Nike Track',100,1700.0,'L,S,M','Blue, Black, Green');
INSERT INTO products VALUES(88039,'Adidas Pant',NULL,1500.0,'L,S,M','Blue, Black, Green');
CREATE TABLE orders (
        order_number INTEGER PRIMARY KEY,
        order_date TEXT ,
        order_time TEXT,
        phone_number TEXT,
        status TEXT
    );
INSERT INTO orders VALUES(2776,'2024-03-01','19:05','9841626287','Initiated');
INSERT INTO orders VALUES(3245,'2024-02-13','23:10','7878787878','Initiated');
INSERT INTO orders VALUES(3709,'2024-02-28','21:56','9876543212','Initiated');
INSERT INTO orders VALUES(3816,'2024-02-13','23:23','9786878687','Initiated');
INSERT INTO orders VALUES(4385,'2024-02-13','23:07','22039','Initiated');
INSERT INTO orders VALUES(5211,'2024-03-01','18:38','9898989898','Initiated');
INSERT INTO orders VALUES(5544,'2024-02-16','20:35','88039','Initiated');
INSERT INTO orders VALUES(6431,'2024-02-16','20:37','9876543212','Initiated');
INSERT INTO orders VALUES(7502,'2024-02-28','22:01','87677565656','Initiated');
INSERT INTO orders VALUES(8096,'2024-02-14','00:40','28383','Initiated');
INSERT INTO orders VALUES(8903,'2024-02-13','23:14','9870604050','Initiated');
INSERT INTO orders VALUES(9243,'2024-02-28','21:34','9898989898','Initiated');
CREATE TABLE order_products (
        order_number INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        color REAL,
        size REAL,
        PRIMARY KEY (order_number, product_id),
        FOREIGN KEY (order_number) REFERENCES orders(order_number),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
INSERT INTO order_products VALUES(4385,NULL,NULL,NULL,NULL);
INSERT INTO order_products VALUES(3245,NULL,2,'black','L');
INSERT INTO order_products VALUES(8903,NULL,2,'black','L');
INSERT INTO order_products VALUES(3816,88039,2,'black','L');
INSERT INTO order_products VALUES(8096,NULL,NULL,NULL,NULL);
INSERT INTO order_products VALUES(5544,NULL,NULL,NULL,NULL);
INSERT INTO order_products VALUES(6431,88039,2,'black','L');
INSERT INTO order_products VALUES(9243,12332,2,'black','L');
INSERT INTO order_products VALUES(3709,12332,1,'black','L');
INSERT INTO order_products VALUES(7502,12332,1,'black','L');
INSERT INTO order_products VALUES(5211,88039,1,'black','L');
INSERT INTO order_products VALUES(2776,88039,NULL,NULL,NULL);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('products',88039);
COMMIT;
