-- 2. Procedure: upsert contact - insert new or update phone if name exists
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


-- 3. Procedure: insert many users with phone validation
-- Phone must start with '+' and contain only digits after that, length 10-15
-- Returns invalid entries via a temp table
CREATE OR REPLACE PROCEDURE insert_many_contacts(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
    current_name TEXT;
    current_phone TEXT;
BEGIN
    -- Create temp table for invalid data
    CREATE TEMP TABLE IF NOT EXISTS invalid_contacts(
        name TEXT,
        phone TEXT,
        reason TEXT
    ) ON COMMIT DROP;

    FOR i IN 1..array_length(p_names, 1) LOOP
        current_name := p_names[i];
        current_phone := p_phones[i];

        -- Validate phone: must start with '+' and be 10-15 chars
        IF current_phone !~ '^\+\d{10,15}$' THEN
            INSERT INTO invalid_contacts(name, phone, reason)
            VALUES(current_name, current_phone, 'Invalid phone format');
        ELSE
            -- Upsert: update if exists, insert if not
            IF EXISTS (SELECT 1 FROM phonebook WHERE first_name = current_name) THEN
                UPDATE phonebook SET phone = current_phone WHERE first_name = current_name;
            ELSE
                INSERT INTO phonebook(first_name, phone) VALUES(current_name, current_phone);
            END IF;
        END IF;
    END LOOP;
END;
$$;


-- 5. Procedure: delete contact by name or phone
CREATE OR REPLACE PROCEDURE delete_contact(p_value VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM phonebook
    WHERE first_name = p_value OR phone = p_value;
END;
$$;
