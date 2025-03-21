import os
import random
import string
from datetime import datetime
import json
import pytz
from groclake.datalake import Datalake
from dotenv import load_dotenv

rcalake_mapping = {
    "properties": {
        "rca_id": {"type": "keyword"},
        "ai_rca_name": {"type": "text"},
        "rca_name": {"type": "text"},
        "rca_issue_description": {"type": "text"},
        "rca_created_time": {"type": "date"},
        "rca_updated_time": {"type": "date"},
        "issue_source_monitor": {
            "type": "nested",
            "properties": {
                "issue_source_monitor_id": {"type": "keyword"},
                "issue_source_monitor_name": {"type": "text"},
                "issue_data": {
                    "type": "nested",
                    "properties": {
                        "issue_data_type": {"type": "keyword"},
                        "issue_data_source": {"type": "keyword"},
                        "issue_data_url": {"type": "text"},
                        "issue_data_payload": {"type": "object"}
                    }
                }
            }
        },
        "rca_steps": {
            "type": "nested",
            "properties": {
                "step_name": {"type": "text"},
                "step_entities": {
                    "type": "nested",
                    "properties": {
                        "code": {"type": "text"},
                        "payload_schema": {"type": "object"},
                        "payload_schema_type": {"type": "keyword"}
                    }
                },
                "step_status": {"type": "keyword"},
                "rca_attribution": {"type": "keyword"},
                "step_comment": {"type": "text"}
            }
        },
        "issue_ticket": {
            "type": "nested",
            "properties": {
                "issue_ticket_id": {"type": "keyword"},
                "issue_ticket_tool": {"type": "keyword"}
            }
        }
    }
}

load_dotenv()


class Config:
    # ES Configuration

    ES_CONFIG = {
        "host": os.getenv("ES_HOST"),
        "port": int(os.getenv("ES_PORT")),
        "api_key": os.getenv("ES_API_KEY"),
        "schema": os.getenv("ES_SCHEMA")
    }

    MYSQL_CONFIG = {
        'user': os.getenv('MYSQL_USER'),
        'passwd': os.getenv('MYSQL_PASSWORD'),
        'host': os.getenv('MYSQL_HOST'),
        'port': int(os.getenv('MYSQL_PORT')),
        'db': os.getenv('MYSQL_DATABASE'),
        'charset': 'utf8'
    }


class DatalakeConnection(Datalake):
    def __init__(self):
        super().__init__()

        ES_CONFIG = Config.ES_CONFIG
        ES_CONFIG['connection_type'] = 'es'

        MYSQL_CONFIG = Config.MYSQL_CONFIG
        MYSQL_CONFIG['connection_type'] = 'sql'

        self.plotch_pipeline = self.create_pipeline(name="groclake_pipeline")
        self.plotch_pipeline.add_connection(name="es_connection", config=ES_CONFIG)
        self.plotch_pipeline.add_connection(name="sql_connection", config=MYSQL_CONFIG)

        self.execute_all()

        self.connections = {
            "es_connection": self.get_connection("es_connection"),
            "sql_connection": self.get_connection("sql_connection")
        }

    def get_connection(self, connection_name):
        """
        Returns a connection by name from the pipeline.
        """
        return self.plotch_pipeline.get_connection_by_name(connection_name)


datalake_connection = DatalakeConnection()
es_connection = datalake_connection.connections["es_connection"]
mysql_connection = datalake_connection.connections["sql_connection"]


class RCALake:
    def __init__(self, index_uuid=None):
        if not index_uuid:
            raise ValueError(
                'Missing required index_uuid. Ensure you pass a valid index UUID when initializing the class.')
        self.index_uuid = index_uuid

    def generate_unique_id(self, length=16):
        characters = string.ascii_lowercase + string.digits
        unique_id = ''.join(random.choices(characters, k=length))
        return unique_id

    def get_current_datetime(self) -> str:
        return datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")

    def get_existing_index_uuid(self, index_uuid, entity_type):
        condition_clause = "entity_id = %s AND entity_type= %s"
        query = f"SELECT * FROM groclake_entity_master WHERE {condition_clause}"
        params = (index_uuid, entity_type)
        result = mysql_connection.read(query, params, multiple=False)
        return result

    def save_rcalake_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return mysql_connection.write(query, tuple(db_params.values()))
        else:
            return mysql_connection.write(query, tuple(db_params.values()))

    def create(self, rcalake_name=None):
        if not rcalake_name:
            return {"message": "RCALake name is required. Please provide a valid name"}
        if not rcalake_name.lower().strip().isidentifier():
            return {'error': f'Invalid RCALake name. Only alphanumeric characters and underscores are allowed.'}

        index_uuid = f"rc_{self.index_uuid}"
        if not index_uuid:
            index_uuid = self.generate_unique_id()

        existing_data = self.get_existing_index_uuid(index_uuid, 'rcalake')
        if existing_data and existing_data.get('entity_id', ''):
            self.index_uuid = existing_data.get('entity_id', '')
            print("existing index", self.index_uuid)
            return {
                "message": "An entry with the same index_uuid already exists.",
                "index_uuid": existing_data.get('entity_id', ''),
                "rcalake_name": existing_data.get('name', '')
            }

        db_params = {
            "entity_id": index_uuid,
            "entity_type": 'rcalake',
            "created_at": self.get_current_datetime(),
            "groc_account_id": '',
            "name": rcalake_name
        }

        try:
            response = es_connection.create_index(index_uuid, settings=None, mappings=rcalake_mapping)
            self.index_uuid = index_uuid
            try:
                self.save_rcalake_data_in_db(db_params, 'groclake_entity_master')
            except Exception as db_error:
                return {"message": "Database error occurred while saving rcalake.", "error": str(db_error)}
            print("index in create", self.index_uuid)
            return {
                    "message": "RCALake created successfully",
                    "index_uuid": index_uuid,
                    "rcalake_name": rcalake_name
            }
        except Exception as e:
            return {"message": "Error creating index", "error": str(e)}

    def push(self, rca_data):
        try:
            if not isinstance(rca_data, dict):
                return {"error": "Invalid RCA data format. Expected dictionary."}

            if not self.index_uuid:
                raise ValueError("Invalid index: rcalake_id is missing.")

            # Validate and format dates
            if "rca_created_time" in rca_data:
                rca_data["rca_created_time"] = datetime.strptime(
                    rca_data["rca_created_time"],
                    "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%dT%H:%M:%S")

            if "rca_updated_time" in rca_data:
                rca_data["rca_updated_time"] = datetime.strptime(
                    rca_data["rca_updated_time"],
                    "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%dT%H:%M:%S")

            try:
                write_response = es_connection.write(query={'index': self.index_uuid, 'body': rca_data})
                return {"message": "RCA data pushed successfully", "response": write_response}
            except Exception as e:
                return {"error": "Failed to push data to Elasticsearch", "details": str(e)}

        except Exception as e:
            return {"error": "An unexpected error occurred", "details": str(e)}

    def fetch(self, payload):
        try:
            read_response = es_connection.search(index=self.index_uuid, body=payload)
            return read_response
        except Exception as e:
            return {"error": "Failed to retrieve search results", "details": str(e)}

    def delete(self, index):
        try:
            if not self.index_uuid:
                raise ValueError("Invalid index: rcalake_id is missing.")

            # Delete the index from Elasticsearch
            es_response = es_connection.delete_index(index=index)

            # Soft delete in database
            status = 2 # Status code for soft delete
            query = "UPDATE groclake_entity_master SET status = %s WHERE entity_id = %s AND entity_type = %s"
            params = (status, index, 'rcalake')
            db_response = mysql_connection.write(query, params)

            return {
                "message": "RCALake deleted successfully"
            }

        except Exception as e:
            return {"error": "Failed to delete RCALake", "details": str(e)}