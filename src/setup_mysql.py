import MySQLdb

conn = MySQLdb.connect(host='localhost', user='root', password='')
cursor = conn.cursor()

try:
    cursor.execute("DROP USER IF EXISTS 'cioa_user'@'localhost'")
    print("Dropped existing user")
except Exception as e:
    print(f"Drop user error: {e}")

try:
    cursor.execute("CREATE USER 'cioa_user'@'localhost' IDENTIFIED BY 'cioa_pass'")
    print("Created user")
except Exception as e:
    print(f"Create user error: {e}")

try:
    cursor.execute("GRANT ALL PRIVILEGES ON cioa_portal.* TO 'cioa_user'@'localhost'")
    print("Granted privileges")
except Exception as e:
    print(f"Grant error: {e}")

try:
    cursor.execute("FLUSH PRIVILEGES")
    print("Flushed privileges")
except Exception as e:
    print(f"Flush error: {e}")

cursor.close()
conn.close()
print("Done")
