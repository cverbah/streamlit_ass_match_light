import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import json
import re
import time
import mysql.connector

# env
load_dotenv()
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]  # need to be changed
MYSQL_HOST = os.environ["MYSQL_HOST"]


def get_retails_from_client(client_ids, host=MYSQL_HOST, database='winodds', user='cvergara', password=MYSQL_PASSWORD):
    """ query client retails competitors"""
    # formatting for the query
    if len(client_ids) == 1:
        client_ids = tuple(client_ids)[0]
        client_ids = f"'{client_ids}'"
        aux = '='
    elif len(client_ids) > 1:
        client_ids = tuple(client_ids)
        aux = 'IN'

    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

    mycursor = mydb.cursor()

    query = f"SELECT cr.client_id, cr.is_client, cr.retail_id \
              FROM clients_retails cr \
              WHERE cr.client_id {aux} {client_ids} "

    mycursor.execute(query)
    results = mycursor.fetchall()

    cols_name = [i[0] for i in mycursor.description]
    cols_and_rows = [dict(zip(cols_name, result)) for result in results]
    df = pd.DataFrame(cols_and_rows)
    return df

