import pymssql

# Connection details
server = "127.0.0.1"
database = "db1"
username = "admin"
password = "5cDN8pCIUxq4"

# Connect to the database
conn = pymssql.connect(server, username, password, database)
cursor = conn.cursor()


# SQL script with multiple SELECT statements
script = """
-- First SELECT statement
SELECT
    @@VERSION AS 'SQL Server Version';

-- Second SELECT statement
SELECT
    CURRENT_TIMESTAMP AS 'Current Timestamp';

-- Third SELECT statement
SELECT
    name, create_date, state, is_read_only
FROM
    sys.databases;
"""

# Execute the script
cursor.execute(script)


# Fetch results from each result set
while True:
    try:
        # Fetch the next result set
        # Print the column names
        print("=============")
        print([column for column in cursor.description])
        results = cursor.fetchall()
        # Print the rows
        for row in results:
            print(row)
        if not cursor.nextset():
            break
    except pymssql.ProgrammingError:
        break

cursor.close()
conn.close()
