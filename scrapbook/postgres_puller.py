import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection

load_dotenv()


def connect() -> connection:
    """Connect to the PostgreSQL database using environment variables."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )


def query_all_members(conn) -> None:
    """Query all members and their direct commissions."""
    with conn.cursor() as cur:
        cur.execute("SELECT uuid, name, direct_commission, kickback_rate FROM members")
        members = cur.fetchall()
        print("Members:")
        for member in members:
            uuid, name, direct_commission, kickback_rate = member
            print(
                f"UUID: {uuid}, Name: {name}, Direct Commission: {direct_commission}, Kickback Rate: {kickback_rate}"
            )


def query_all_relationships(conn) -> None:
    """Query all parent-child relationships."""
    with conn.cursor() as cur:
        cur.execute("SELECT parent_uuid, child_uuid FROM children")
        relationships = cur.fetchall()
        print("\nParent-Child Relationships:")
        for relationship in relationships:
            parent_uuid, child_uuid = relationship
            print(f"Parent UUID: {parent_uuid}, Child UUID: {child_uuid}")


if __name__ == "__main__":
    conn = connect()
    try:
        query_all_members(conn)
        query_all_relationships(conn)
    finally:
        conn.close()
