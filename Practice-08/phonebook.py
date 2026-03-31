import psycopg2
from config import load_config


# 1. Search contacts by pattern using function
def search_by_pattern(pattern):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                if not rows:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# 2. Upsert contact using procedure
def upsert_contact(name, phone):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
            conn.commit()
            print(f"Upserted contact: {name}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# 3. Insert many contacts with validation using procedure
def insert_many(names, phones):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "CALL insert_many_contacts(%s, %s)",
                    (names, phones)
                )
                # Check for invalid contacts in temp table
                cur.execute("SELECT * FROM invalid_contacts")
                invalid = cur.fetchall()
                if invalid:
                    print("Invalid contacts:")
                    for row in invalid:
                        print(f"  {row[0]}, {row[1]} - {row[2]}")
                else:
                    print("All contacts inserted successfully.")
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# 4. Get contacts with pagination using function
def get_paginated(limit, offset):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                if not rows:
                    print("No more contacts.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# 5. Delete contact by name or phone using procedure
def delete_contact(value):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_contact(%s)", (value,))
            conn.commit()
            print(f"Deleted contact: {value}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Console menu
def main():
    while True:
        print("\n--- PhoneBook Menu (Practice 8) ---")
        print("1. Search by pattern")
        print("2. Upsert contact (insert or update)")
        print("3. Insert many contacts")
        print("4. View contacts (paginated)")
        print("5. Delete contact by name or phone")
        print("0. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            pattern = input("Enter search pattern: ")
            search_by_pattern(pattern)
        elif choice == '2':
            name = input("Enter name: ")
            phone = input("Enter phone: ")
            upsert_contact(name, phone)
        elif choice == '3':
            names = []
            phones = []
            print("Enter contacts (empty name to stop):")
            while True:
                name = input("  Name: ")
                if not name:
                    break
                phone = input("  Phone: ")
                names.append(name)
                phones.append(phone)
            if names:
                insert_many(names, phones)
        elif choice == '4':
            limit = int(input("Page size: "))
            offset = int(input("Offset: "))
            get_paginated(limit, offset)
        elif choice == '5':
            value = input("Enter name or phone to delete: ")
            delete_contact(value)
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


if __name__ == '__main__':
    main()
