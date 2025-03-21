def get_tables_query(dialect: str = "postgresql"):
    if dialect in ("postgresql"):
        return """
                SELECT 
                  n.nspname AS table_schema, 
                  c.relname AS table_name, 
                  n2.nspname AS parent_schema, 
                  c2.relname AS parent_table 
                FROM 
                  pg_constraint r 
                  JOIN pg_class c ON r.conrelid = c.oid 
                  JOIN pg_namespace n ON c.relnamespace = n.oid 
                  JOIN pg_class c2 ON r.confrelid = c2.oid 
                  JOIN pg_namespace n2 ON c2.relnamespace = n2.oid 
                WHERE 
                  r.contype = 'f'
            """

def get_relations_query(dialect: str = "postgresql"):
    if dialect in ("postgresql"):
        return """
                SELECT
                    ns1.nspname AS schema,
                    cl1.relname AS table,
                    fk_att.attname AS foreign_key,
                    ns2.nspname AS foreign_schema,
                    cl2.relname AS foreign_table,
                    pk_att.attname AS foreign_primary_key
                FROM
                    pg_constraint con
                    JOIN pg_class cl1 ON con.conrelid = cl1.oid
                    JOIN pg_namespace ns1 ON cl1.relnamespace = ns1.oid
                    JOIN pg_class cl2 ON con.confrelid = cl2.oid
                    JOIN pg_namespace ns2 ON cl2.relnamespace = ns2.oid
                    CROSS JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS fk(attnum, ord)
                    CROSS JOIN LATERAL unnest(con.confkey) WITH ORDINALITY AS pk(attnum, ord)
                    JOIN pg_attribute fk_att 
                        ON fk_att.attrelid = con.conrelid 
                        AND fk_att.attnum = fk.attnum
                    JOIN pg_attribute pk_att 
                        ON pk_att.attrelid = con.confrelid 
                        AND pk_att.attnum = pk.attnum
                WHERE
                    con.contype = 'f'
                    AND fk.ord = pk.ord
                    AND CONCAT(ns1.nspname, '.', cl1.relname) IN :schema_tables;
            """