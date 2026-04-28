import psycopg2
import csv
import json
from config import load_config


# ──────────────────────────────────────────────
# P7 functions (unchanged)
# ──────────────────────────────────────────────

# Helper: resolve a group name to its id, creating the group if missing.
# Returns None if name is empty.
def _resolve_group_id(cur, group_name):
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups(name) VALUES(%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def _clean_phone_type(phone_type):
    if phone_type in ('home', 'work', 'mobile'):
        return phone_type
    return 'mobile'


# Insert a single contact. Email, birthday, group are optional.
def insert_contact(first_name, phone, email=None, birthday=None, group=None, phone_type='mobile'):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                group_id = _resolve_group_id(cur, group)
                cur.execute(
                    """INSERT INTO phonebook(first_name, phone, email, birthday, group_id)
                       VALUES(%s, %s, %s, %s, %s) RETURNING id""",
                    (first_name, phone, email or None, birthday or None, group_id)
                )
                contact_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                    (contact_id, phone, _clean_phone_type(phone_type))
                )
            conn.commit()
            print(f"Inserted contact with id {contact_id}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Insert contacts from a CSV file.
# Required: first_name, phone
# Optional: email, birthday, group, phone_type
def insert_from_csv(filename):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    inserted = 0
                    for row in reader:
                        group_id = _resolve_group_id(cur, row.get('group', '').strip())
                        cur.execute(
                            """INSERT INTO phonebook(first_name, phone, email, birthday, group_id)
                               VALUES(%s, %s, %s, %s, %s)
                               RETURNING id""",
                            (row['first_name'],
                             row['phone'],
                             row.get('email') or None,
                             row.get('birthday') or None,
                             group_id)
                        )
                        contact_id = cur.fetchone()[0]
                        cur.execute(
                            "INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                            (contact_id, row['phone'], _clean_phone_type(row.get('phone_type', 'mobile')))
                        )
                        inserted += 1
            conn.commit()
            print(f"Imported {inserted} contacts from {filename}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Query all contacts ordered by name
def query_all():
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, first_name, phone FROM phonebook ORDER BY first_name")
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Query contacts whose name contains the given string
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
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Query contacts whose phone starts with the given prefix
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
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Update a contact's name by id
def update_name(contact_id, new_name):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE phonebook SET first_name = %s WHERE id = %s", (new_name, contact_id))
                updated = cur.rowcount
            conn.commit()
            print(f"Updated {updated} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Update a contact's phone by id
def update_phone(contact_id, new_phone):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE phonebook SET phone = %s WHERE id = %s", (new_phone, contact_id))
                updated = cur.rowcount
            conn.commit()
            print(f"Updated {updated} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Delete a contact by exact name
def delete_by_name(name):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM phonebook WHERE first_name = %s", (name,))
                deleted = cur.rowcount
            conn.commit()
            print(f"Deleted {deleted} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Delete a contact by exact phone number
def delete_by_phone(phone):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
                deleted = cur.rowcount
            conn.commit()
            print(f"Deleted {deleted} row(s)")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# ──────────────────────────────────────────────
# New functions (TSIS-1)
# ──────────────────────────────────────────────

# Return all contacts that belong to the given group
def filter_by_group(group_name):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT p.id, p.first_name, p.email, p.birthday
                       FROM phonebook p
                       JOIN groups g ON p.group_id = g.id
                       WHERE g.name ILIKE %s""",
                    ('%' + group_name + '%',)
                )
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                if not rows:
                    print("No contacts in that group.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Search contacts whose email contains the given substring
def search_by_email(email_part):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, first_name, email FROM phonebook WHERE email ILIKE %s",
                    ('%' + email_part + '%',)
                )
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                if not rows:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# List all contacts sorted by name, birthday, or creation date
def sort_contacts(sort_by='name'):
    order_map = {
        'name':     'first_name',
        'birthday': 'birthday',
        'date':     'created_at',
    }
    column = order_map.get(sort_by, 'first_name')
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, first_name, phone, email, birthday FROM phonebook ORDER BY {column}"
                )
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Browse contacts page by page using get_contacts_paginated()
def paginated_nav():
    page_size = 5
    offset = 0
    config = load_config()
    while True:
        try:
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (page_size, offset))
                    rows = cur.fetchall()
            if not rows:
                print("No more contacts.")
            else:
                print(f"\n--- Page {offset // page_size + 1} ---")
                for row in rows:
                    print(row)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            break

        action = input("next / prev / quit: ").strip().lower()
        if action == 'next':
            offset += page_size
        elif action == 'prev':
            offset = max(0, offset - page_size)
        elif action == 'quit':
            break


# Export all contacts (main phone + extra phones + group) to a JSON file
def export_json(filename='contacts.json'):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Fetch all contacts including the main phone column
                cur.execute(
                    """SELECT p.id, p.first_name, p.phone, p.email,
                              p.birthday::TEXT, g.name AS group_name
                       FROM phonebook p
                       LEFT JOIN groups g ON p.group_id = g.id
                       ORDER BY p.first_name"""
                )
                contacts = cur.fetchall()

                result = []
                for cid, name, main_phone, email, birthday, group in contacts:
                    # Fetch extra phones from the phones table
                    cur.execute(
                        "SELECT phone, type FROM phones WHERE contact_id = %s",
                        (cid,)
                    )
                    extras = [{'phone': ph, 'type': tp} for ph, tp in cur.fetchall()]

                    # Include the main phone as the first item if it isn't
                    # already in the extras list (avoids duplicates)
                    phones = []
                    extra_numbers = [p['phone'] for p in extras]
                    if main_phone and main_phone not in extra_numbers:
                        phones.append({'phone': main_phone, 'type': 'mobile'})
                    phones.extend(extras)

                    result.append({
                        'name':     name,
                        'email':    email,
                        'birthday': birthday,
                        'group':    group,
                        'phones':   phones,
                    })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(result)} contacts to {filename}")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Import contacts from a JSON file, asking user about duplicates
def import_json(filename='contacts.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            contacts = json.load(f)
    except (Exception,) as error:
        print(error)
        return

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for contact in contacts:
                    name     = contact.get('name', '')
                    email    = contact.get('email')
                    birthday = contact.get('birthday')
                    group    = contact.get('group')
                    phones   = contact.get('phones', [])
                    main_phone = phones[0]['phone'] if phones else contact.get('phone', '')
                    if main_phone and not phones:
                        phones = [{'phone': main_phone, 'type': 'mobile'}]

                    # Resolve group id (creates it if missing)
                    group_id = _resolve_group_id(cur, group)

                    # Check if contact already exists
                    cur.execute("SELECT id FROM phonebook WHERE first_name = %s", (name,))
                    existing = cur.fetchone()

                    if existing:
                        action = input(f"'{name}' already exists. skip or overwrite? ").strip().lower()
                        if action == 'overwrite':
                            cur.execute(
                                """UPDATE phonebook
                                   SET phone=%s, email=%s, birthday=%s, group_id=%s
                                   WHERE id=%s""",
                                (main_phone, email, birthday, group_id, existing[0])
                            )
                            # Replace existing extra phones with the new ones
                            cur.execute("DELETE FROM phones WHERE contact_id = %s", (existing[0],))
                            for ph in phones:
                                cur.execute(
                                    "INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                                    (existing[0], ph['phone'], _clean_phone_type(ph.get('type', 'mobile')))
                                )
                            print(f"Overwritten {name}")
                        else:
                            print(f"Skipped {name}")
                    else:
                        cur.execute(
                            """INSERT INTO phonebook(first_name, phone, email, birthday, group_id)
                               VALUES(%s, %s, %s, %s, %s)
                               RETURNING id""",
                            (name, main_phone, email, birthday, group_id)
                        )
                        contact_id = cur.fetchone()[0]
                        for ph in phones:
                            cur.execute(
                                "INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                                (contact_id, ph['phone'], _clean_phone_type(ph.get('type', 'mobile')))
                            )
                        print(f"Inserted {name}")

            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Ask user for contact details and add an extra phone number via procedure
def add_phone_menu():
    name  = input("Contact name: ")
    phone = input("Phone number: ")
    ptype = input("Type (home/work/mobile): ").strip().lower()
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
            conn.commit()
            print("Phone added.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Ask user for contact name and group, then call the move_to_group procedure.
# Procedure moves all contacts matching the given name (per TSIS-1 spec).
def move_group_menu():
    name = input("Contact name: ")
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Show which contacts will be affected (case-insensitive exact match)
                cur.execute(
                    "SELECT id, first_name, phone FROM phonebook WHERE first_name ILIKE %s",
                    (name,)
                )
                matches = cur.fetchall()

            if not matches:
                print("No contacts with that name.")
                return

            # Warn if multiple contacts share the name (procedure will move all of them)
            if len(matches) > 1:
                print(f"Warning: {len(matches)} contacts share this name. All will be moved:")
                for row in matches:
                    print(f"  id={row[0]}  name={row[1]}  phone={row[2]}")
                if input("Continue? (yes/no): ").strip().lower() != 'yes':
                    print("Cancelled.")
                    return

            group = input("Group name: ")
            with psycopg2.connect(**config) as conn:
                with conn.cursor() as cur:
                    cur.execute("CALL move_to_group(%s, %s)", (name, group))
                conn.commit()
            print(f"Moved {len(matches)} contact(s) to group '{group}'.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# Search contacts using the search_contacts() DB function
def search_contacts(query):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM search_contacts(%s)", (query,))
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                if not rows:
                    print("No contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# ──────────────────────────────────────────────
# Console menu
# ──────────────────────────────────────────────

def print_menu():
    print("\n=== PhoneBook Menu (TSIS-1) ===")
    print("")
    print("--- Basic ---")
    print("1.  Insert contact       2.  Import from CSV")
    print("3.  Update name          4.  Update phone")
    print("5.  Show all             6.  Search by name")
    print("7.  Search by phone      8.  Delete by name")
    print("9.  Delete by phone")
    print("")
    print("--- Extended ---")
    print("10. Filter by group      11. Search by email")
    print("12. Sort contacts        13. Browse (paginated)")
    print("14. Export to JSON       15. Import from JSON")
    print("16. Add extra phone      17. Move to group")
    print("18. Full-text search")
    print("")
    print("--- Other ---")
    print("0.  Exit                 ?.  Show this menu")


def main():
    print_menu()
    while True:
        choice = input("\nEnter choice: ").strip()

        if choice == '1':
            name     = input("Name: ")
            phone    = input("Phone: ")
            ptype    = input("Phone type home/work/mobile [mobile]: ").strip().lower() or 'mobile'
            email    = input("Email (optional): ").strip() or None
            birthday = input("Birthday YYYY-MM-DD (optional): ").strip() or None
            group    = input("Group (optional): ").strip() or None
            insert_contact(name, phone, email, birthday, group, ptype)
        elif choice == '2':
            filename = input("CSV filename: ")
            insert_from_csv(filename)
        elif choice == '3':
            cid      = int(input("Contact id: "))
            new_name = input("New name: ")
            update_name(cid, new_name)
        elif choice == '4':
            cid       = int(input("Contact id: "))
            new_phone = input("New phone: ")
            update_phone(cid, new_phone)
        elif choice == '5':
            query_all()
        elif choice == '6':
            query_by_name(input("Name to search: "))
        elif choice == '7':
            query_by_phone(input("Phone prefix: "))
        elif choice == '8':
            delete_by_name(input("Name to delete: "))
        elif choice == '9':
            delete_by_phone(input("Phone to delete: "))
        elif choice == '10':
            filter_by_group(input("Group name: "))
        elif choice == '11':
            search_by_email(input("Email part: "))
        elif choice == '12':
            sort_by = input("Sort by (name/birthday/date): ").strip().lower()
            sort_contacts(sort_by)
        elif choice == '13':
            paginated_nav()
        elif choice == '14':
            filename = input("Output filename [contacts.json]: ").strip() or 'contacts.json'
            export_json(filename)
        elif choice == '15':
            filename = input("Input filename [contacts.json]: ").strip() or 'contacts.json'
            import_json(filename)
        elif choice == '16':
            add_phone_menu()
        elif choice == '17':
            move_group_menu()
        elif choice == '18':
            search_contacts(input("Search query: "))
        elif choice == '0':
            print("Goodbye!")
            break
        elif choice == '?':
            print_menu()
            continue
        else:
            print("Invalid choice, try again.")
            continue

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    main()
