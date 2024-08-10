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
except Exception as e:
    print(f"Caught generic {type(e)} '{e}'.")
    members = []
    member_id_to_children_id = {}
finally:
    conn.close()

member_id_to_member = {member.id: member for member in members}

for member in members:
    children_ids = member_id_to_children_id.get(member.id, [])
    member.children = [member_id_to_member[children_id] for children_id in children_ids]


# Create Dash App
app = Dash(__name__)


# Create Cytoscape Elements
def generate_elements(members):
    elements = []
    for member in members:
        elements.append(
            {"data": {"id": member.id, "label": member.name}, "classes": ""}
        )
        for child in member.children:
            elements.append({"data": {"source": member.id, "target": child.id}})
    return elements


elements = generate_elements(members)

app.layout = html.Div(
    children=[
        cyto.Cytoscape(
            id="cytoscape",
            layout={"name": "breadthfirst"},
            style={
                "width": "100%",
                "height": "80vh",  # 80% of the browser window height
                "border": "2px solid black",  # Add a border around the graph
                "box-sizing": "border-box",  # Ensures border is included in the element's dimensions
            },
            elements=elements,
            minZoom=0.5,
            maxZoom=3.0,
            stylesheet=[
                {
                    "selector": "node",
                    "style": {
                        "label": "data(label)",
                        "background-color": "#0074D9",
                        "color": "#fff",
                        "text-halign": "center",
                        "text-valign": "center",
                        "font-size": "14px",
                    },
                },
                {
                    "selector": "edge",
                    "style": {
                        "line-color": "#888",
                        "width": 2,
                    },
                },
                {
                    "selector": ".highlighted",
                    "style": {
                        "background-color": "red",
                    },
                },
            ],
        ),
        html.Div(id="member-info", style={"marginTop": 20}),
        html.Div(id="children-table", style={"marginTop": 20}),
    ],
)


# Callback for updating node color and displaying information
@app.callback(
    [
        Output("cytoscape", "stylesheet"),
        Output("member-info", "children"),
        Output("children-table", "children"),
    ],
    [Input("cytoscape", "tapNodeData")],
)
def display_tap_node_data(node_data):
    if not node_data:
        return no_update, no_update, no_update

    member_id = node_data["id"]
    member = next(m for m in members if m.id == member_id)

    # Highlight selected node
    stylesheet = [
        {
            "selector": "node",
            "style": {
                "label": "data(label)",
                "background-color": "#0074D9",
                "color": "#fff",
                "text-halign": "center",
                "text-valign": "center",
                "font-size": "14px",
            },
        },
        {
            "selector": "edge",
            "style": {
                "line-color": "#888",
                "width": 2,
            },
        },
        {
            "selector": f'[id = "{member_id}"]',
            "style": {
                "background-color": "red",
            },
        },
    ]

    # Display Member Info
    member_info = html.Div(
        [
            html.H4(f"Member: {member.name}"),
            html.P(f"ID: {member.id}"),
            html.P(f"Direct Commission: ${member.direct_commission}"),
            html.P(f"Kickback Rate: {member.kickback_rate*100}%"),
        ]
    )

    # Display Children's Table
    if member.children:
        children_data = [
            {
                "ID": child.id,
                "Name": child.name,
                "Direct Commission": child.direct_commission,
            }
            for child in member.children
        ]
        children_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in ["ID", "Name", "Direct Commission"]],
            data=children_data,
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "backgroundColor": "#2f2f2f",  # Dark gray for cell background
                "color": "#ffffff",  # White text color
                "border": "1px solid #555",  # Light gray border color
            },
            style_header={
                "backgroundColor": "#2f2f2f",  # Dark gray for header background
                "color": "#ffffff",  # White text color for header
                "border": "1px solid #555",  # Light gray border color for header
            },
        )
    else:
        children_table = html.P("No children available.")

    return stylesheet, member_info, children_table


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
