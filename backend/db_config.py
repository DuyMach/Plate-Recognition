import mysql.connector

db_config = {
    'host': '127.0.0.1', # Port forwarding
    'user': 'dmach1',
    'password': 'Athena99!',
    'database': 'spr23_cis422_dmach1'
}

def get_database_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def validate_license_plate(license_plate):
    connection = get_database_connection()

    if connection:
        try:
            cursor = connection.cursor()

            query = "SELECT COUNT(*) FROM license_plate_table WHERE plate_number = %s"
            cursor.execute(query, (license_plate,))
            
            result = cursor.fetchone()[0]

            return result > 0

        except Exception as e:
            print(f"Error executing database query: {e}")
            return False

        finally:
            cursor.close()
            connection.close()

    return False

def insert_license_plate(license_plate):
    connection = get_database_connection()

    if connection:
        try:
            cursor = connection.cursor()

            query = "INSERT INTO license_plate_table (plate_number) VALUES (%s)"
            cursor.execute(query, (license_plate,))
            
            connection.commit()

            return True

        except Exception as e:
            print(f"Error executing database query: {e}")
            return False

        finally:
            cursor.close()
            connection.close()

    return False