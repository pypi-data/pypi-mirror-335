import json
import logging
from datetime import datetime
from itertools import islice
from tqdm import tqdm

from bson import ObjectId
from jinja2 import Template
from sqlalchemy import text
from concurrent.futures import ThreadPoolExecutor

from .codec import get_codec_options

class Commands():
    def from_table(self, table: str, step: int = None) -> dict:
        item = {
            "type": "table",
            "object": table,
            "step": step if step else self.config["meta"]["nesting_level"]
        }

        return item

    def from_query(self, query: str, data: dict = {}) -> dict:
        item = {
            "type": "query",
            "object": query,
            "step": self.config["meta"]["nesting_level"]
        }
        if data:
            item["data"] = data

        return item
    
    def add_pruning(self, foreign_key: str, foreign_collection: str, foreign_primary_key: str,
                    relationship: str = "one-to-many", pruning_type: str = "link") -> None:
        item = {
            "relationship": relationship,
            "foreign_key": foreign_key,
            "foreign_collection": foreign_collection,
            "foreign_primary_key": foreign_primary_key,
            "pruning_type": pruning_type,
            "type": "pruning"
        }
        return item
    
    def remove(self, collection_name: str) -> None:
        self.config["mapping"].pop(collection_name, None)
        self.config["pruning"].pop(collection_name, None)
    
    def rename(self, old_collection_name: str, new_collection_name: str) -> None:
        self.config["mapping"][new_collection_name] = self.config["mapping"].pop(old_collection_name, None)
        self.config["pruning"][new_collection_name] = self.config["pruning"].pop(old_collection_name, None)

        for coll, rules in self.config["pruning"].items():
            for idx, rule in enumerate(rules):
                if rule["foreign_collection"] == old_collection_name:
                    self.config["pruning"][coll][idx]["foreign_collection"] = new_collection_name

    def backup(self, *args, auto: bool = False) -> None:
        try:
            collections_to_backup = list(args)
            all_collections = self.mongo_database.list_collection_names()

            if auto:
                collections_to_backup += [coll for coll in list(self.config["mapping"].keys())]

            collections_to_backup = set(collections_to_backup)
            
            for coll in collections_to_backup:
                if coll in all_collections:
                    collection = self.mongo_database[coll]
                    backup_name = f"{coll}_backup_{datetime.now().strftime('%Y%m%d%H%M')}"
                    pipeline = [
                        {'$match': {}},
                        {'$out': backup_name}
                    ]
                    collection.aggregate(pipeline)
                    self.logger.logger.log(logging.INFO, "BACKUP %s FOR COLLECTION %s WAS CREATED SUCCESSFULLY", backup_name, coll)
        except Exception as err:
            self.logger.logger.log(logging.ERROR, "BACKUP %s FOR COLLECTION %s WAS CREATED WITH AN ERROR: %s", backup_name, coll, err)

    def rollback(self, report_path: str = None) -> None:
        try:
            if report_path:
                with open(report_path, 'r') as report_file:
                    rollback_data = json.load(report_file)["collections"]
            else:
                rollback_data = self.logger.report["collections"]
            
            for collection_name, inserted_ids in rollback_data.items():
                collection = self.mongo_database[collection_name].with_options(codec_options=get_codec_options())
                collection.delete_many({"_id": {"$in": [ObjectId(id) for id in inserted_ids]}})
                self.logger.logger.log(logging.INFO, "MIGRATION %s WAS ROLLED BACK SUCCESSFULLY", self.config["title"])
        except Exception as err:
            self.logger.logger.log(logging.ERROR, "MIGRATION %s WAS ROLLED BACK WITH AN ERROR: %s", self.config["title"], err)

    def __chunks(self, dictionary: dict, n_items: int):
        it = iter(dictionary.items())
        while True:
            chunk = list(islice(it, n_items))
            if not chunk:
                break
            yield chunk

    def execute(self, name: str, item: dict, batch_size: int = None, dump: bool = False) -> None:
        """
        DOC-STRING
        Слишком маленький размер батча влечёт за собой ... (хуже работать будет)
        """
        self.logger.logger.log(logging.INFO, "PROCESSING COLLECTION %s FROM %s %s WAS STARTED", name, item['type'], item['object'][:40])
        try:
            with self.session_factory() as session:
                if item["type"] == "table":
                    sql_result = session.execute(text(f"SELECT * FROM {item['object']}"))
                elif item["type"] == "query":
                    query_template = Template(item["object"])
                    query = query_template.render(item.get("data", {}))
                    sql_result = session.execute(text(query))

            while True:
                documents = sql_result.mappings().fetchmany(batch_size) if batch_size else sql_result.mappings().all()
                
                if not(documents):
                    break
                
                documents = [dict(doc) for doc in documents]
                collection = self.mongo_database[name].with_options(codec_options=get_codec_options())
            
                if dump:
                    with open(f"{name}-{datetime.now()}.json", "w") as json_file:
                        json.dump(documents, json_file, indent=4)

                if not(self.config["meta"]["debug_mode"]) and not(dump):
                    inserts = collection.insert_many(documents, ordered=False)          
                    self.logger.report["collections"][name] = [str(id) for id in inserts.inserted_ids]

                if not(batch_size):
                    break
                
            self.logger.logger.log(logging.INFO, "PROCESSING COLLECTION %s HAS FINISHED SUCCESSFULLY", name)
        except Exception as err:
            self.logger.logger.log(logging.ERROR, "PROCESSING COLLECTION %s HAS FINISHED WITH AN ERROR: %s", name, err)

    def migrate(self, batch_size: int = None, dump: bool = False) -> None:
        """
        DOC-STRING
        """
        try:
            self.logger.logger.log(logging.INFO, "MIGRATION %s HAS STARTED WITH PARAMS: %s", self.config["title"], self.config["meta"])
            nesting_level = self.config["meta"]["nesting_level"]
            max_workers = self.config["meta"]["max_workers"]

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                with tqdm(total=nesting_level+1, desc="") as pbar:
                    for step in range(nesting_level, -1, -1):
                        current_step_migrations = {}
                        for collection_name in self.config["mapping"]:
                            if self.config["mapping"][collection_name]["step"] == step:
                                current_step_migrations[collection_name] = self.config["mapping"][collection_name]
                        for pool in self.__chunks(current_step_migrations, max_workers):
                            pbar.set_description_str(f"STEP {step}")
                            pbar.set_postfix_str(str(list(current_step_migrations.keys())))
                            [executor.submit(self.execute, name, item, batch_size, dump) for name, item in pool]
                    pbar.set_description_str("Finished")
            
            self.config["meta"]["last_update"] = datetime.now()
            self.logger.logger.log(logging.INFO, "MIGRATION %s HAS FINISHED SUCCESSFULLY", self.config["title"])
        except Exception as err:
            self.logger.logger.log(logging.ERROR, "MIGRATION %s HAS FAILED WITH AN ERROR %s", self.config["title"], err)
        finally:
            self.logger.save_report()

    def dump(self, batch_size: int = None):
        """
        DOC-STRING
        """
        self.migrate(batch_size=batch_size, dump=True)

    def prune(self) -> None:
        """
        DOC-STRING
        """
        pruning_level = self.config["meta"]["pruning_level"]
        try:
            self.logger.logger.log(logging.INFO, "PRUNING %s HAS STARTED", self.config["title"])
            for step in range(pruning_level, -1, -1):
                for collection_name in self.config["pruning"]:
                    if self.config["mapping"][collection_name]["step"] == step:
                        self.logger.logger.log(logging.INFO, "PRUNING COLLECTION %s WAS STARTED", collection)
                        prunings = self.config["pruning"][collection_name]
                        collection = self.mongo_database[collection_name].with_options(codec_options=get_codec_options())
                        for item in prunings:
                            foreign_collection = self.mongo_database[item["foreign_collection"]].with_options(codec_options=get_codec_options())
                            relationship = item["relationship"]
                            pruning_type = item["pruning_type"]

                            if not(self.config["meta"]["debug_mode"]):
                                if relationship in ("one-to-one", "many-to-one"):
                                    pipeline = [
                                        {"$lookup": {
                                            "from": item["foreign_collection"],
                                            "let": {"fk_val": f"${item['foreign_key']}"},
                                            "pipeline": [
                                                {"$match": {"$expr": {"$eq": [f"${item['foreign_primary_key']}", "$$fk_val"]}}},
                                                {"$limit": 1}
                                            ],
                                            "as": "_temp_match"
                                        }},
                                        {"$unwind": {"path": "$_temp_match", "preserveNullAndEmptyArrays": False}}
                                    ]

                                    if pruning_type == "link":
                                        pipeline.extend([
                                            {"$set": {item["foreign_collection"]: "$_temp_match._id"}},
                                            {"$unset": "_temp_match"}
                                        ])
                                    elif pruning_type == "object":
                                        pipeline.extend([
                                            {"$replaceRoot": {"newRoot": {"$mergeObjects": ["$_temp_match", "$$ROOT"]}}},
                                            {"$unset": ["_temp_match"]}
                                        ])
                                    else:
                                        self.logger.logger.log(logging.ERROR, "Incorrect 'pruning_type' was received: %s for %s. Allowed values: 'link', 'object'", pruning_type, collection_name)
                                    
                                    pipeline.append({"$merge": {
                                        "into": collection_name,
                                        "on": "_id",
                                        "whenMatched": "replace",
                                        "whenNotMatched": "discard"
                                    }})

                                    collection.aggregate(pipeline)

                                    if pruning_type == "object":
                                        migrated_ids = collection.distinct(f"{item['foreign_key']}")
                                        foreign_collection.delete_many({item["foreign_primary_key"]: {"$in": migrated_ids}})

                                elif relationship == "one-to-many":
                                    pipeline = [
                                        {"$lookup": {
                                            "from": item["foreign_collection"],
                                            "localField": item["foreign_key"],
                                            "foreignField": item["foreign_primary_key"],
                                            "as": item["foreign_collection"]
                                        }}
                                    ]

                                    if pruning_type == "link":
                                        pipeline.append({"$set": {
                                            item["foreign_collection"]: {
                                                "$map": {
                                                    "input": f"${item['foreign_collection']}",
                                                    "in": "$$this._id"
                                                }
                                            }
                                        }})

                                    pipeline.append({"$merge": {
                                        "into": collection_name,
                                        "on": "_id",
                                        "whenMatched": "replace",
                                        "whenNotMatched": "discard"
                                    }})

                                    collection.aggregate(pipeline)

                                    if pruning_type == "object":
                                        migrated_ids = list(collection.aggregate([
                                            {"$unwind": f"${item['foreign_collection']}"},
                                            {"$group": {"_id": f"${item['foreign_collection']}.{item['foreign_primary_key']}"}}
                                        ]))
                                        foreign_collection.delete_many({item['foreign_primary_key']: {"$in": [x["_id"] for x in migrated_ids]}})

                                elif relationship == "many-to-many":
                                    if pruning_type != "link":
                                        self.logger.logger.log(logging.ERROR, "Many-to-Many supports only 'link' pruning type for %s.", collection_name)
                                    collection.aggregate([
                                        {"$lookup": {
                                            "from": item["foreign_collection"],
                                            "localField": item["foreign_key"],
                                            "foreignField": item["foreign_primary_key"],
                                            "as": item["foreign_collection"]
                                        }},
                                        {"$set": {
                                            item["foreign_collection"]: {
                                                "$map": {
                                                    "input": f"${item['foreign_collection']}",
                                                    "in": "$$this._id"
                                                }
                                            }
                                        }},
                                        {"$merge": {
                                            "into": collection_name,
                                            "on": "_id",
                                            "whenMatched": "replace"
                                        }}
                                    ])

                                    foreign_collection.aggregate([
                                        {"$lookup": {
                                            "from": collection_name,
                                            "localField": item["foreign_primary_key"],
                                            "foreignField": item["foreign_key"],
                                            "as": collection_name
                                        }},
                                        {"$set": {
                                            collection_name: {
                                                "$map": {
                                                    "input": f"${collection_name}",
                                                    "in": "$$this._id"
                                                }
                                            }
                                        }},
                                        {"$merge": {
                                            "into": item["foreign_collection"],
                                            "on": "_id",
                                            "whenMatched": "replace"
                                        }}
                                    ])
                                else:
                                    self.logger.logger.log(logging.ERROR, "Incorrect relationship type was received: %s for %s. Allowed values: '<one/many>-to-<one/many>'.", relationship, collection_name)
                        self.logger.logger.log(logging.INFO, "PRUNING COLLECTION %s HAS FINISHED SUCCESSFULLY", collection_name)
                        self.logger.report["pruned"].append(collection_name)
            self.logger.logger.log(logging.INFO, "PRUNING %s HAS FINISHED SUCCESSFULLY", self.config["title"])
        except Exception as err:
            self.logger.logger.log(logging.ERROR, "PRUNING %s HAS FAILED WITH AN ERROR %s", self.config["title"], err)
        finally:
            self.logger.save_report()