import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', password='')
cursor = conn.cursor()

try:
    cursor.execute("GRANT ALL PRIVILEGES ON cioa_portal.* TO 'cioa_user'@'localhost'")
    print("Grant executed")
except Exception as e:
    print(f"Grant error: {e}")

try:
    cursor.execute("SHOW GRANTS FOR 'cioa_user'@'localhost'")
    grants = cursor.fetchall()
    for g in grants:
        print("Current grants:", g[0])
except Exception as e:
    print(f"Show grants error: {e}")

cursor.close()
conn.close()
