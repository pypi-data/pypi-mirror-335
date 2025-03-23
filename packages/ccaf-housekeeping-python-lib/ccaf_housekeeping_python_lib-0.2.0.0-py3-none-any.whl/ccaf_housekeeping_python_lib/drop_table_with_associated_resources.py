import time
from typing import Tuple, Dict
import re
import uuid
from cc_clients_python_lib.flink_client import FlinkClient, StatementPhase
from cc_clients_python_lib.kafka_client import KafkaClient
from cc_clients_python_lib.http_status import HttpStatus


__copyright__  = "Copyright (c) 2025 Jeffrey Jonathan Jennings"
__license__    = "MIT"
__credits__    = ["Jeffrey Jonathan Jennings (J3)"]
__maintainer__ = "Jeffrey Jonathan Jennings (J3)"
__email__      = "j3@thej3.com"
__status__     = "dev"


DROP_STAGES = {
    "statement_drop": "statement_drop",
    "kafka_key_schema_subject_drop": "kafka_key_schema_subject_drop",
    "kafka_value_schema_subject_drop": "kafka_value_schema_subject_drop",
    "kafka_topic_drop": "kafka_topic_drop",
    "table_drop": "table_drop"
}

MAX_RETRY = 3


class DropTableWithAssociatedResources():
    def __init__(self, flink_config: dict, kafka_config: dict):
        """Initialize the class.
        
        Args:
            flink_config (dict): The Flink configuration.
            kafka_config (dict): The Kafka configuration.
        """
        self.flink_client = FlinkClient(flink_config)
        self.kafka_client = KafkaClient(kafka_config)

    def drop_table(self, catalog_name: str, database_name: str, table_name: str) -> Tuple[bool, str, Dict]:
        """Drop the table and associated resources.
        
        Args:
            catalog_name (str): The catalog name.
            database_name (str): The database name.
            table_name (str): The table name.
            
        Returns:
            bool:   The success status.
            str:    The error message.
            dict:   The response.
        """
        # Regular expression search pattern to find the table name within a DROP, INSERT,
        # and SELECT statement.
        search_pattern = r'(?:drop|from|insert)\s+([-.`\w+\s]+?)\s*(?=\;|\)|\(|values)'

        # Initialize the variables.
        drop_stages = {}
        
        # Retrieve a list of all the statements in a Flink region.
        http_status_code, error_message, response = self.flink_client.get_statement_list()
        if http_status_code != HttpStatus.OK:
            return False, error_message, {}
        
        # Iterate through the list of statements.
        number_of_deleted_statements = 0
        for item in response:
            statement = item.get("spec").get("statement").lower()

            # Find the table name in the statement.
            candidate_find = re.search(search_pattern, statement)

            # If the table name is found in the statement, then delete the statement.
            if candidate_find:
                statement_phase = StatementPhase(item.get("status").get("phase"))
                statement_id = item.get("name")
                statement_catalog_name = item.get("spec").get("properties").get("sql.current-catalog")
                statement_database_name = item.get("spec").get("properties").get("sql.current-database")

                if statement_phase == StatementPhase.FAILED:
                    # If the statement has failed, then delete the statement.
                    if statement_catalog_name == catalog_name and table_name in candidate_find.group(1):
                        http_status_code, error_message = self.flink_client.delete_statement(statement_id)
                        if http_status_code != HttpStatus.ACCEPTED:
                            return False, error_message, {}
                        else:
                            number_of_deleted_statements += 1
                else:
                    # If the statement is not in a failed state, then delete the statement.
                    if statement_catalog_name == catalog_name and statement_database_name == database_name and table_name in candidate_find.group(1):
                        http_status_code, error_message = self.flink_client.delete_statement(statement_id)
                        if http_status_code != HttpStatus.ACCEPTED:
                            return False, error_message, {}
                        else:
                            number_of_deleted_statements += 1

        # Statement drop stage activity note.
        drop_stages[DROP_STAGES["statement_drop"]] = f"{number_of_deleted_statements} statement{'s' if number_of_deleted_statements > 0 else ''} deleted."

        # Drop the table.
        http_status_code, error_message, exist = self.kafka_client.kafka_topic_exist(table_name.replace("`", ""))
        if http_status_code not in [HttpStatus.OK, HttpStatus.NOT_FOUND]:
            return False, error_message, {}
        
        if exist:
            retry = 0
            max_retry = MAX_RETRY
            while retry <= max_retry:
                http_status_code, error_message, response = self.flink_client.submit_statement(f"drop-{table_name}-{str(uuid.uuid4())}",
                                                                                               f"DROP TABLE {table_name};",
                                                                                               {"sql.current-catalog": catalog_name, "sql.current-database": database_name})
                if http_status_code != HttpStatus.CREATED:
                    return False, error_message, {}
                elif http_status_code == HttpStatus.CREATED:
                    drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic dropped."
                    drop_stages[DROP_STAGES["table_drop"]] = "Table dropped."
                else:
                    time.sleep(15)
                    retry += 1
                    statement_phase = StatementPhase(item.get("status").get("phase"))
        else:
            drop_stages[DROP_STAGES["kafka_topic_drop"]] = "Kafka topic does not exist."
            drop_stages[DROP_STAGES["table_drop"]] = "No action was taken since backing Kafka topic does not exist."
        
        return True, "", drop_stages
    