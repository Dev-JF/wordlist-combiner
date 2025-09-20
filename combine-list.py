import sqlite3
import os, fnmatch


# Loops over a windows folder looking for txt files
def findFiles (path, filter):
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, filter):
            yield os.path.join(root, file)

for textFile in findFiles(r"E:\Combine List\wordlists", '*.txt'):
    print(textFile)



db_path = "words.db"
text_file = textFile

# Connect to SQLite
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create table with UNIQUE constraint - to deduplicate the wordlist 
cur.execute("""
CREATE TABLE IF NOT EXISTS wordlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE
)
""")

batch_size = 100000
buffer = []

with open(text_file, "r", encoding="latin-1") as f:
    for i, line in enumerate(f, start=1):
        word = line.strip()
        if word:
            buffer.append((word,))
        
        # Insert batch
        if i % batch_size == 0:
            cur.executemany("INSERT OR IGNORE INTO wordlist (word) VALUES (?)", buffer)
            conn.commit()
            buffer.clear()
            print(f"Inserted {i:,} lines so far...")

# Insert remaining
if buffer:
    cur.executemany("INSERT OR IGNORE INTO wordlist (word) VALUES (?)", buffer)
    conn.commit()

conn.close()
print("✅ Import complete.")
