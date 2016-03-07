import sqlite3
import sys
import os

target = sys.argv[1]

try:
    os.remove(target)
except Exception as e:
    print e

conn = sqlite3.connect(target)
with open('dictionary-seed.sql') as f:
    query = f.read()

conn.executescript(query)
conn.close()