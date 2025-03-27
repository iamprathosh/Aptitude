import os
import sqlite3
from pprint import pprint

# Connect to the database
conn = sqlite3.connect('instance/polls.db')
cursor = conn.cursor()

# Get the schema of the Vote table
cursor.execute("PRAGMA table_info(vote)")
columns = cursor.fetchall()
print("Vote table schema:")
for col in columns:
    print(f"  {col}")

# Count votes
cursor.execute("SELECT COUNT(*) FROM vote")
count = cursor.fetchone()[0]
print(f"\nTotal votes: {count}")

# Get all votes
cursor.execute("SELECT * FROM vote LIMIT 5")
votes = cursor.fetchall()
print("\nSample votes:")
for vote in votes:
    print(f"  {vote}")

# Check if session_id exists
try:
    cursor.execute("SELECT id, option_id, session_id FROM vote LIMIT 1")
    print("\nSession ID column exists!")
except sqlite3.OperationalError as e:
    print(f"\nError: {e}")

conn.close()