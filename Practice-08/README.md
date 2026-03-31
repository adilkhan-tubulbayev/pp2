# Practice 8: PostgreSQL Functions & Stored Procedures, PhoneBook

Extends Practice 7 PhoneBook with PostgreSQL functions and stored procedures.

## Repository Structure

```
Practice-08/
├── phonebook.py       # Python app calling functions/procedures
├── functions.sql      # search_contacts(), get_contacts_paginated()
├── procedures.sql     # upsert_contact(), insert_many_contacts(), delete_contact()
├── config.py          # Database config loader
├── connect.py         # Connection + table + SQL setup
├── database.ini       # PostgreSQL credentials
└── README.md
```

## Setup

1. Make sure `phonebook` database exists from Practice 7
2. Run `python connect.py` to create functions and procedures
3. Run `python phonebook.py` to start the app

## Features

- **search_contacts(pattern)** — function, returns contacts matching name or phone
- **upsert_contact(name, phone)** — procedure, inserts or updates if exists
- **insert_many_contacts(names[], phones[])** — procedure, bulk insert with phone validation
- **get_contacts_paginated(limit, offset)** — function, paginated query
- **delete_contact(value)** — procedure, deletes by name or phone

## Resources

- [PostgreSQL PL/pgSQL Tutorial](https://neon.com/postgresql/postgresql-plpgsql)
- [PostgreSQL CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html)
- [PostgreSQL CREATE PROCEDURE](https://www.postgresql.org/docs/current/sql-createprocedure.html)
