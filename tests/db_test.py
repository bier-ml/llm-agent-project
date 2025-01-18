import psycopg2
import json
from datetime import datetime


def test_database_connection():
    try:
        # Connect to the database
        conn = psycopg2.connect(dbname="ivan_db", user="ivan", password="ivan", host="localhost", port="5432")

        # Create a cursor
        cur = conn.cursor()

        # Test 1: Insert a user
        cur.execute(
            """
            INSERT INTO users (telegram_id, username, preferences)
            VALUES (%s, %s, %s)
            RETURNING user_id;
        """,
            (123456789, "test_user", json.dumps({"favorite_coins": ["BTC", "ETH"]})),
        )
        user_id = cur.fetchone()[0]

        # Test 2: Insert a crypto token
        cur.execute(
            """
            INSERT INTO crypto_tokens (token_name, symbol, price)
            VALUES (%s, %s, %s)
            RETURNING token_id;
        """,
            ("Bitcoin", "BTC", 50000.0),
        )
        token_id = cur.fetchone()[0]

        # Test 3: Retrieve the inserted data
        cur.execute("SELECT * FROM users WHERE telegram_id = %s;", (123456789,))
        user = cur.fetchone()
        print("Retrieved user:", user)

        cur.execute("SELECT * FROM crypto_tokens WHERE symbol = %s;", ("BTC",))
        token = cur.fetchone()
        print("Retrieved token:", token)

        # Commit the transaction
        conn.commit()

        print("All database tests passed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the cursor and connection
        if "cur" in locals():
            cur.close()
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    test_database_connection()
