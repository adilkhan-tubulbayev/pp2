import psycopg2
import csv
from config import load_config


# Insert a single contact from console input
def insert_contact(first_name, phone):
    sql = """INSERT INTO phonebook(first_name, phone)
            VALUES(%s, %s) RETURNING id;"""
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (first_name, phone))
                contact_id = cur.fetchone()[0]
            conn.commit()
            print(f"Inserted contact with id {contact_id}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Insert contacts from a CSV file
def insert_from_csv(filename):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cur.execute(
                            "INSERT INTO phonebook(first_name, phone) VALUES(%s, %s)",
                            (row['first_name'], row['phone'])
                        )
            conn.commit()
            print(f"Contacts imported from {filename}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Query all contacts
def query_all():
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, first_name, phone FROM phonebook ORDER BY first_name")
                rows = cur.fetchall()
                for row in rows:
                    print(row)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Query contacts by name filter
def query_by_name(name):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, first_name, phone FROM phonebook WHERE first_name ILIKE %s",
                    ('%' + name + '%',)
                )
                rows = cur.fetchall()
                for row in rows:
                    print(row)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Query contacts by phone prefix
def query_by_phone(phone_prefix):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, first_name, phone FROM phonebook WHERE phone LIKE %s",
                    (phone_prefix + '%',)
                )
                rows = cur.fetchall()
                for row in rows:
                    print(row)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Update contact's name
def update_name(contact_id, new_name):
    sql = "UPDATE phonebook SET first_name = %s WHERE id = %s"
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (new_name, contact_id))
                updated = cur.rowcount
            conn.commit()
            print(f"Updated {updated} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Update contact's phone
def update_phone(contact_id, new_phone):
    sql = "UPDATE phonebook SET phone = %s WHERE id = %s"
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (new_phone, contact_id))
                updated = cur.rowcount
            conn.commit()
            print(f"Updated {updated} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Delete contact by name
def delete_by_name(name):
    sql = "DELETE FROM phonebook WHERE first_name = %s"
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (name,))
                deleted = cur.rowcount
            conn.commit()
            print(f"Deleted {deleted} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Delete contact by phone
def delete_by_phone(phone):
    sql = "DELETE FROM phonebook WHERE phone = %s"
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (phone,))
                deleted = cur.rowcount
            conn.commit()
            print(f"Deleted {deleted} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Console menu
def main():
    while True:
        print("\n--- PhoneBook Menu ---")
        print("1. Insert contact (console)")
        print("2. Insert from CSV")
        print("3. Update contact name")
        print("4. Update contact phone")
        print("5. Query all contacts")
        print("6. Search by name")
        print("7. Search by phone")
        print("8. Delete by name")
        print("9. Delete by phone")
        print("0. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            insert_contact(name, phone)
        elif choice == '2':
            filename = input("Enter CSV filename: ")
            insert_from_csv(filename)
        elif choice == '3':
            cid = int(input("Enter contact id: "))
            new_name = input("Enter new name: ")
            update_name(cid, new_name)
        elif choice == '4':
            cid = int(input("Enter contact id: "))
            new_phone = input("Enter new phone: ")
            update_phone(cid, new_phone)
        elif choice == '5':
            query_all()
        elif choice == '6':
            name = input("Enter name to search: ")
            query_by_name(name)
        elif choice == '7':
            phone = input("Enter phone prefix: ")
            query_by_phone(phone)
        elif choice == '8':
            name = input("Enter name to delete: ")
            delete_by_name(name)
        elif choice == '9':
            phone = input("Enter phone to delete: ")
            delete_by_phone(phone)
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == '__main__':
    main()
