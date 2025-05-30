import pymysql

def connect_to_mysql():
    try:
        # Establish a connection to the MySQL server
        connection = pymysql.connect(
            # host="localhost",
            # database="somultas",
            # user="root",  # Assuming the username is root, change it if needed
            # password="207754"
            host="18.217.50.145",
            database="somultas_producao",
            user="root",  # Assuming the username is root, change it if needed
            password="kAwiVrwDeC6R05kzxw7fwCUP26"
            # host="database-1.c4f1g6nwchzu.us-east-2.rds.amazonaws.com",
            # database="somultas_producao",
            # user="root",  # Assuming the username is root, change it if needed
            # password="kAwiVrwDeC6R05kzxw7fwCUP26"
        )

        if connection.open:
            return connection
        else:
            return None

    except pymysql.Error as error:
        print("Error:", error)
        return None

def connect_to_mysql_bolsa():
    try:
        # Establish a connection to the MySQL server
        connection = pymysql.connect(
            # host="localhost",
            # database="bolsa",
            # user="root",  # Assuming the username is root, change it if needed
            # password="207754"
            # host="3.20.123.221",
            # database="teste",
            # user="root2",  # Assuming the username is root, change it if needed
            # password="0truqUF42Yn0vqIJSHFXShkVwJ3tvjFjghdz8LaBCnnbdHILxa-"
            host="bolsadeleads.c4f1g6nwchzu.us-east-2.rds.amazonaws.com",
            database="bolsa",
            user="root",  # Assuming the username is root, change it if needed
            password="q_Zs]!dat.-(hdp"
        )

        if connection.open:
            return connection
        else:
            return None

    except pymysql.Error as error:
        print("Error:", error)
        return None

def write_data_to_mysql(table, columns, values, db):
    # Connect to MySQL database
    if db == 'sissm':
        connection = connect_to_mysql()
    else:
        connection = connect_to_mysql_bolsa()

    if connection:
        try:
            # Create a cursor object using the cursor() method
            cursor = connection.cursor()

            # Generate the SQL query dynamically based on input parameters
            # Prepare placeholders for column names and values in the query
            column_placeholders = ', '.join(columns)
            value_placeholders = ', '.join(['%s'] * len(values))

            # SQL query to insert data into the specified table
            insert_query = f"INSERT INTO {table} ({column_placeholders}) VALUES ({value_placeholders})"

            # Execute the SQL query with the provided values
            cursor.execute(insert_query, values)

            # Commit your changes to the database
            connection.commit()

            # print("Data inserted successfully")

        except pymysql.Error as error:
            # Handle any errors that occurred during the process
            print("Error:", error)

        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()

def execute_mysql_query_with_params(query, db):
    if db == 'sissm':
        connection = connect_to_mysql()
    else:
        connection = connect_to_mysql_bolsa()

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()  # Fetch the result after executing the query
            connection.commit()
            # print("Query executed successfully.")
            if result:
                return result  # Assuming the ID is the first column in the result
            else:
                return None
        except pymysql.Error as error:
            print("Error:", error)
            return None
        finally:
            cursor.close()
            connection.close()
    else:
        print("Failed to connect to MySQL.")
        return None
