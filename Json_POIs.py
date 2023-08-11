import os
import json
import os
import sqlite3
from pprint import pprint

wDir = os.getcwd()
# Get Images if they exist
dbx = 'C:/Database/SC_Places.db'
con = sqlite3.connect(dbx, detect_types=sqlite3.PARSE_DECLTYPES |
                                        sqlite3.PARSE_COLNAMES)
cur = con.cursor()
query = "SELECT Data FROM POI_Directions WHERE Place = 'Darlington County' "
rows = cur.execute(query).fetchall()
directions = str(rows[0])
directions = directions[2:]
directions = directions[:-3]
filename = 'C:/Database/test.json'
json_file = open(filename, 'w')
n = json_file.write(directions)
json_file.close()