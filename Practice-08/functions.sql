-- 1. Function: search contacts by pattern (matches name or phone)
CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INT, first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    WHERE p.first_name ILIKE '%' || pattern || '%'
       OR p.phone LIKE '%' || pattern || '%';
END;
$$ LANGUAGE plpgsql;


-- 4. Function: get contacts with pagination (LIMIT and OFFSET)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, first_name VARCHAR, phone VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.first_name, p.phone
    FROM phonebook p
    ORDER BY p.first_name
    LIMIT p_limit OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;
