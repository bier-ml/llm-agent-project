import psycopg2


def verify_database():
    try:
        # Connect to the database
        conn = psycopg2.connect(dbname="ivan_db", user="ivan", password="ivan", host="localhost", port="5432")

        # Create a cursor
        cur = conn.cursor()

        # Get list of all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cur.fetchall()

        print("Found tables:")
        for table in tables:
            print(f"- {table[0]}")
            # Get column information for each table
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table[0]}'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            for column in columns:
                print(f"  - {column[0]}: {column[1]}")
            print()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    verify_database()
