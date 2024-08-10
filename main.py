import os
from dataclasses import dataclass, field

import dash_cytoscape as cyto
import psycopg2
import ujson as json
from dash import Dash, Input, Output, dash_table, dcc, html, no_update
from dotenv import load_dotenv
from psycopg2.extensions import connection

from src.member import Member

load_dotenv()


def connect() -> connection:
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )


def query_all_members(conn) -> list[Member]:
    """Query all members and their direct commissions."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT uuid, name, direct_commission, kickback_rate FROM members")
        members_data = cur.fetchall()
        members = []
        for member_data in members_data:
            id, name, direct_commision, kickback_rate = member_data
            new_member = Member(
                id=id,
                name=name,
                direct_commission=direct_commision,
                kickback_rate=kickback_rate,
            )
            members.append(new_member)
    return members


def query_all_relationships(conn) -> dict[str, list[str]]:
    """Query all parent-child relationships."""
    with conn.cursor() as cur:
        cur.execute("SELECT parent_uuid, child_uuid FROM children")
        relationships = cur.fetchall()
        relationship_map = {}
        for relationship in relationships:
            parent_uuid, child_uuid = tuple(map(str, relationship))
            if parent_uuid not in relationship_map:
                relationship_map[parent_uuid] = [child_uuid]
            elif child_uuid in relationship_map[parent_uuid]:
                raise RuntimeError(f"Duplicate row {parent_uuid}, {child_uuid}")
            else:
                relationship_map[parent_uuid].append(child_uuid)
        return relationship_map


conn = connect()
try:
    members = query_all_members(conn)
    member_id_to_children_id = query_all_relationships(conn)
except:
    members = None
    member_id_to_children_id = None
finally:
    conn.close()

member_id_to_member = {member.id: member for member in members}

for member in members:
    children_ids = member_id_to_children_id.get(member.id, [])
    member.children = [member_id_to_member[children_id] for children_id in children_ids]


