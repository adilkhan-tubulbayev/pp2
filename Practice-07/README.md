# Practice 7: Python & PostgreSQL, PhoneBook

Console-based PhoneBook application backed by PostgreSQL.

## Repository Structure

```
Practice-07/
├── phonebook.py     # Main app - CRUD operations and console menu
├── config.py        # Database config loader from database.ini
├── connect.py       # Connection test and table creation
├── contacts.csv     # Sample contacts data
├── database.ini     # PostgreSQL connection settings
└── README.md
```

## Setup

1. Install PostgreSQL and create database: `createdb phonebook`
2. Install psycopg2: `pip install psycopg2-binary`
3. Edit `database.ini` with your credentials
4. Create table: `python connect.py`
5. Run app: `python phonebook.py`

## Features

- Insert contacts from console or CSV file
- Query all contacts or search by name/phone
- Update contact name or phone by id
- Delete contacts by name or phone

## Resources

- [PostgreSQL Python Tutorial](https://neon.com/postgresql/postgresql-python)
- [psycopg2 Docs](https://www.psycopg.org/docs/)
