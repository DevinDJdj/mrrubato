#Load the sql IPython extension
#pip install ipython-sql
#not working...
#pip install jupyterlab
#pip install notebook
#http://localhost:8888/tree

#chmod 0700  /run/user/1000/
#ipython
#%load_ext sql
#%sql sqlite:///sample.db
#jupyter notebook
#http://localhost:8888/notebooks/Untitled.ipynb
#this is set up to use jupyter notebook.  
#import config.py
#hmmm...
#interesting, list functions to call.  
#lets write this all up in one script.  

#automate function calls to DB...
#lot of possibilities here.  

import sys

import datetime
# adding Folder_2/subfolder to the system path
#not great mechanism for config.  Maybe just make absolute path?
sys.path.insert(0, 'c:/devinpiano/')
sys.path.insert(1, 'c:/devinpiano/music')
#sys.path.append('../')
import config  

import os
import pandas as pd
import requests
import json
from oauth2client.tools import argparser, run_flow
import google.generativeai as genai

from IPython.display import HTML, Markdown, display
import time
from chromadb import Documents, EmbeddingFunction, Embeddings
from google.api_core import retry

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from google.api_core import retry

import sqlite3
import textwrap


db_file = "sample.db"
db_conn = sqlite3.connect(db_file)


def list_tables() -> list[str]:
    """Retrieve the names of all tables in the database."""
    # Include print logging statements so you can see when functions are being called.
    print(' - DB CALL: list_tables')

    cursor = db_conn.cursor()

    # Fetch the table names.
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    tables = cursor.fetchall()
    return [t[0] for t in tables]



def describe_table(table_name: str) -> list[tuple[str, str]]:
    """Look up the table schema.

    Returns:
      List of columns, where each entry is a tuple of (column, type).
    """
    print(' - DB CALL: describe_table')

    cursor = db_conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")

    schema = cursor.fetchall()
    # [column index, column name, column type, ...]
    return [(col[1], col[2]) for col in schema]



def execute_query(sql: str) -> list[list[str]]:
    """Execute a SELECT statement, returning the results."""
    print(' - DB CALL: execute_query')

    cursor = db_conn.cursor()

    cursor.execute(sql)
    return cursor.fetchall()



def print_chat_turns(chat):
    """Prints out each turn in the chat history, including function calls and responses."""
    for event in chat.history:
        print(f"{event.role.capitalize()}:")

        for part in event.parts:
            if txt := part.text:
                print(f'  "{txt}"')
            elif fn := part.function_call:
                args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
                print(f"  Function call: {fn.name}({args})")
            elif resp := part.function_response:
                print("  Function response:")
                print(textwrap.indent(str(resp), "    "))

        print()

def init_data():
    execute_query("""
                  -- Create the 'products' table
CREATE TABLE IF NOT EXISTS products (
  	product_id INTEGER PRIMARY KEY AUTOINCREMENT,
  	product_name VARCHAR(255) NOT NULL,
  	price DECIMAL(10, 2) NOT NULL
  );""")

    execute_query("""
-- Create the 'staff' table
CREATE TABLE IF NOT EXISTS staff (
  	staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
  	first_name VARCHAR(255) NOT NULL,
  	last_name VARCHAR(255) NOT NULL
  );
    """)

    execute_query("""
-- Create the 'orders' table
CREATE TABLE IF NOT EXISTS orders (
  	order_id INTEGER PRIMARY KEY AUTOINCREMENT,
  	customer_name VARCHAR(255) NOT NULL,
  	staff_id INTEGER NOT NULL,
  	product_id INTEGER NOT NULL,
  	FOREIGN KEY (staff_id) REFERENCES staff (staff_id),
  	FOREIGN KEY (product_id) REFERENCES products (product_id)
  );

""")

    execute_query("""
                  -- Insert data into the 'products' table
INSERT INTO products (product_name, price) VALUES
  	('Laptop', 799.99),
  	('Keyboard', 129.99),
  	('Mouse', 29.99);
    """)
    execute_query("""
-- Insert data into the 'staff' table
INSERT INTO staff (first_name, last_name) VALUES
  	('Alice', 'Smith'),
  	('Bob', 'Johnson'),
  	('Charlie', 'Williams');
    """)

    execute_query("""
-- Insert data into the 'orders' table
INSERT INTO orders (customer_name, staff_id, product_id) VALUES
  	('David Lee', 1, 1),
  	('Emily Chen', 2, 2),
  	('Frank Brown', 1, 3);
    """)


if __name__ == '__main__':
    argparser.add_argument("--title", help="Video title", default="What a Wonderful World")
    argparser.add_argument("--video", help="Video ID", default="4flRJWtfY9c")

    args = argparser.parse_args()


    genai.configure(api_key=config.cfg['google']['AISTUDIO'])

#    init_data()
    list_tables()
    describe_table("products")
    execute_query("select * from products")


    db_tools = [list_tables, describe_table, execute_query]

    instruction = """You are a helpful chatbot that can interact with an SQL database for a computer
    store. You will take the users questions and turn them into SQL queries using the tools
    available. Once you have the information you need, you will answer the user's question using
    the data returned. Use list_tables to see what tables are present, describe_table to understand
    the schema, and execute_query to issue an SQL SELECT query."""

    model = genai.GenerativeModel(
        "models/gemini-1.5-flash-latest", tools=db_tools, system_instruction=instruction
    )

    # Define a retry policy. The model might make multiple consecutive calls automatically
    # for a complex query, this ensures the client retries if it hits quota limits.
    from google.api_core import retry

    retry_policy = {"retry": retry.Retry(predicate=retry.if_transient_error)}

    # Start a chat with automatic function calling enabled.
    chat = model.start_chat(enable_automatic_function_calling=True)


    resp = chat.send_message("What is the cheapest product?", request_options=retry_policy)
    print(resp.text)

    resp = chat.send_message("and how much is it?", request_options=retry_policy)
    print(resp.text)

    model = genai.GenerativeModel(
        "models/gemini-1.5-pro-latest", tools=db_tools, system_instruction=instruction
    )

    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message('Which salesperson sold the cheapest product?', request_options=retry_policy)
    print(response.text)

    print_chat_turns(chat)

