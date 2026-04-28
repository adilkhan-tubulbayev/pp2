-- Drop old versions of functions that changed their return type
DROP FUNCTION IF EXISTS get_contacts_paginated(integer, integer);
DROP FUNCTION IF EXISTS search_contacts(text);

-- Practice 8 procedure: insert new contact or update phone if name exists
CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_name) THEN
        UPDATE phonebook SET phone = p_phone WHERE first_name = p_name;
    ELSE
        INSERT INTO phonebook(first_name, phone) VALUES(p_name, p_phone);
    END IF;
END;
$$;

-- Practice 8 procedure: insert many contacts with simple phone validation
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names  TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] !~ '^\+\d{10,15}$' THEN
            RAISE NOTICE 'Skipping invalid phone for %: %', p_names[i], p_phones[i];
        ELSIF EXISTS (SELECT 1 FROM phonebook WHERE first_name = p_names[i]) THEN
            UPDATE phonebook SET phone = p_phones[i] WHERE first_name = p_names[i];
        ELSE
            INSERT INTO phonebook(first_name, phone) VALUES(p_names[i], p_phones[i]);
        END IF;
    END LOOP;
END;
$$;

-- Practice 8 procedure: delete contact by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook
    WHERE first_name = p_value OR phone = p_value;
END;
$$;

-- Paginated query used by the console next / prev loop
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(
    id         INT,
    first_name VARCHAR,
    phone      VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT
            p.id,
            p.first_name,
            p.phone,
            p.email,
            p.birthday,
            g.name AS group_name
        FROM phonebook p
        LEFT JOIN groups g ON p.group_id = g.id
        ORDER BY p.first_name
        LIMIT p_limit OFFSET p_offset;
END;
$$;

-- TSIS-1 procedure: add another phone number to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id
    FROM phonebook
    WHERE first_name ILIKE p_contact_name
    LIMIT 1;

    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'Contact "%" not found.', p_contact_name;
    ELSE
        INSERT INTO phones(contact_id, phone, type)
        VALUES(v_contact_id, p_phone, p_type);
    END IF;
END;
$$;

DROP PROCEDURE IF EXISTS move_to_group(integer, varchar);

-- TSIS-1 procedure: move contact to a group, creating the group if needed
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INT;
BEGIN
    SELECT id INTO v_group_id
    FROM groups
    WHERE name ILIKE p_group_name
    LIMIT 1;

    IF v_group_id IS NULL THEN
        INSERT INTO groups(name) VALUES(p_group_name) RETURNING id INTO v_group_id;
    END IF;

    UPDATE phonebook
    SET group_id = v_group_id
    WHERE first_name ILIKE p_contact_name;
END;
$$;

-- TSIS-1 function: search name, email, main phone, and all extra phones
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id         INT,
    first_name VARCHAR,
    phone      VARCHAR,
    email      VARCHAR
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT DISTINCT
            p.id,
            p.first_name,
            p.phone,
            p.email
        FROM phonebook p
        LEFT JOIN phones ph ON ph.contact_id = p.id
        WHERE p.first_name ILIKE '%' || p_query || '%'
           OR p.phone      ILIKE '%' || p_query || '%'
           OR p.email      ILIKE '%' || p_query || '%'
           OR ph.phone     ILIKE '%' || p_query || '%'
        ORDER BY p.first_name;
END;
$$;
