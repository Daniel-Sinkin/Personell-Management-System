"""
Hardcoded PostgreSQL data entry for testing purposes.
"""

import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection

load_dotenv()


def connect() -> connection:
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )


def execute_sql(sql) -> None:
    conn = connect()
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    conn.close()


execute_sql("""
CREATE TABLE members (
    uuid VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    direct_commission FLOAT NOT NULL,
    kickback_rate FLOAT NOT NULL DEFAULT 0.2
);
CREATE TABLE children (
    parent_uuid VARCHAR REFERENCES members(uuid),
    child_uuid VARCHAR REFERENCES members(uuid),
    PRIMARY KEY (parent_uuid, child_uuid)
);
""")

execute_sql("""
INSERT INTO members (uuid, name, direct_commission, kickback_rate) VALUES
('1a2b3c', 'Alice', 100.00, 0.2),
('2b3c4d', 'Bob', 25.00, 0.2),
('3c4d5e', 'Carol', 10.00, 0.2),
('4d5e6f', 'Dave', 5.00, 0.2),
('5e6f7g', 'Frank', 2.00, 0.2),
('6f7g8h', 'Grace', 3.00, 0.2),
('7g8h9i', 'George', 30.00, 0.2),
('8h9i0j', 'Henry', 8.00, 0.2),
('9i0j1k', 'Isabel', 15.00, 0.2),
('0j1k2l', 'Judy', 20.00, 0.2),
('1k2l3m', 'Edward', 12.00, 0.2),
('2l3m4n', 'Ivy', 7.00, 0.2),
('3m4n5o', 'Jack', 9.00, 0.2),
('4n5o6p', 'Kate', 14.00, 0.2),
('5o6p7q', 'Linda', 40.00, 0.2),
('6p7q8r', 'Martin', 60.00, 0.2);

INSERT INTO children (parent_uuid, child_uuid) VALUES
('1a2b3c', '2b3c4d'), -- Alice -> Bob
('2b3c4d', '3c4d5e'), -- Bob -> Carol
('3c4d5e', '4d5e6f'), -- Carol -> Dave
('3c4d5e', '5e6f7g'), -- Carol -> Frank
('3c4d5e', '6f7g8h'), -- Carol -> Grace
('7g8h9i', '8h9i0j'), -- George -> Henry
('7g8h9i', '9i0j1k'), -- George -> Isabel
('4n5o6p', '2l3m4n'), -- Kate -> Ivy
('4n5o6p', '3m4n5o'), -- Kate -> Jack
('5o6p7q', '4n5o6p'), -- Linda -> Kate
('6p7q8r', '5o6p7q'); -- Martin -> Linda
""")
