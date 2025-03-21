import os
import json
import uuid
from jsonschema import validate
from collections import defaultdict
from sqlalchemy import text

from .adapters import get_tables_query, get_relations_query

current_dir = os.path.dirname(__file__)
schema_path = os.path.join(current_dir, 'schema.json')

class Config():
    """
    DOC-STRING
    """
    with open(schema_path, 'r') as file:
        __json_schema = json.load(file)

    __default_config = {
        "title": "Sample",
        "id": str(uuid.uuid4()),
        "description": "...",
        "meta": {
            "nesting_level": 0,
            "pruning_level": 0,
            "pruning_type": "link",
            "max_workers": None,
            "debug_mode": True,
            "log": True,
            "analyze": True,
            "last_update": "1970-01-01 00:00:00"
        },
        "target_schemes": [],
        "excluded": [],
        "mapping": {},
        "pruning": {}
        }

    def __init__(self, sql_connection, sql_dialect, mongo_connection, config: dict = None):
        self.sql_connection = sql_connection
        self.sql_dialect = sql_dialect
        self.mongo_connection = mongo_connection
        if config:
            self.set_config(config)
        else:
            self.reset_config()

    def set_config(self, config: dict = None) -> None:
        if config and not(validate(config, self.__json_schema)):
            self.config = self.__default_config.copy()
            self.config.update(config)
        else:
            raise Exception("Configuration setting failed")

    def reset_config(self) -> None:
        self.config = self.__default_config

    def validate_config(self, config: dict = {}) -> bool:
        return config and not(validate(config, self.__json_schema))
    
    def save_config(self, path: str = "config.json") -> None:
        with open(path, 'w') as json_file:
            json.dump(self.config, json_file, indent=4)

    def auto_config(self, schemes: list = [], tables: list = [], excluded: list = []) -> None:
        """
        DOC-STRING
        """
        tree = self.__get_dependencies_tree(schemes, tables, excluded)
        for table in tree:
            item = tree[table]
            if table not in excluded:
                self.config["mapping"][f"{item['schema']}_{item['table']}"] = {
                    "type": "table",
                    "object": f"{item['schema']}.{item['table']}",
                    "step": item["step"]
                }
                self.config["pruning"][f"{item['schema']}_{item['table']}"] = item["pruning"]
        self.config["target_schemes"] = schemes
        self.config["excluded"] = excluded
        return self.config

    def __calculate_step(self, table, child_relations, visited=None) -> int:
        if visited is None:
            visited = set()

        if table in visited:
            return 0
        
        visited.add(table)

        if not child_relations.get(table, []):
            return 0

        step = 1 + max(self.__calculate_step(child, child_relations, visited) for child in child_relations[table])
        self.config["meta"]["nesting_level"] = max(step, self.config["meta"]["nesting_level"])

        return step

    def __get_dependencies_tree(self, schemes, tables, excluded) -> dict:
        tree = {}
        schema_tables = {}
        parent_relations = defaultdict(list)
        child_relations = defaultdict(list)

        for table_schema in schemes:
            for table_name in tables:
                schema_tables[f"{table_schema}.{table_name}"] = {
                    "table_schema": table_schema,
                    "table_name": table_name
                }

        query = get_tables_query(self.sql_dialect)
        query += "  AND CONCAT(n.nspname, '.', c.relname) NOT IN :excluded" if excluded else ""
        query += "  AND n.nspname IN :schemes" if schemes else ""
        query += "  AND c.relname IN :tables" if tables else ""
        tables_for_config = self.sql_connection.execute(text(query),
            {"schemes": tuple(schemes), "tables": tuple(tables), "excluded": tuple(excluded)}).fetchall()
        
        for row in tables_for_config:
            table_schema, table_name, parent_schema, parent_table = row
            full_table_name = f"{table_schema}.{table_name}"
            full_parent_table_name = f"{parent_schema}.{parent_table}"

            parent_relations[full_table_name].append(full_parent_table_name)
            child_relations[full_parent_table_name].append(full_table_name)

            schema_tables[full_table_name] = {
                "table_schema": table_schema,
                "table_name": table_name
            }
            schema_tables[full_parent_table_name] = {
                "table_schema": parent_schema,
                "table_name": parent_table
            }
    
        query = get_relations_query(self.sql_dialect)
        table_relations = self.sql_connection.execute(text(query),
            {"schema_tables": tuple(schema_tables.keys())}).fetchall()

        for table in schema_tables:
            tree[table] = {
                "schema": schema_tables[table]["table_schema"],
                "table": schema_tables[table]["table_name"],
                "parent_tables": parent_relations.get(table, []),
                "child_tables": child_relations.get(table, []),
                "step": self.__calculate_step(table, child_relations),
                "pruning": []
            }

        for row in table_relations:
            schema, table, foreign_key, foreign_schema, foreign_table, foreign_pkey = row
            tree[f"{schema}.{table}"]['pruning'].append(
                {
                    "relationship": "one-to-many",
                    "pruning_type": self.config["meta"]["pruning_type"],
                    "foreign_key": foreign_key,
                    "foreign_collection": f"{foreign_schema}_{foreign_table}",
                    "foreign_primary_key": foreign_pkey
                }
            )
        self.config["meta"]["pruning_level"] = self.config["meta"]["nesting_level"] - 1

        return tree