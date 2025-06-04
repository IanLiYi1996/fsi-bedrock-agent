import boto3
import os
from boto3.session import Session
import yaml
import argparse


def read_yaml_file(file_path):
    with open(file_path, "r") as file:
        try:
            return yaml.safe_load(file)
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None


class AmazonDynamoDB:
    """
    Support class that allows for:
        - Creation of DynamoDB tables and parameters in parameter store with the tables' names
        - Deletion of the tables and their parameters
    """

    def __init__(self):
        """
        Class initializer
        """
        self._boto_session = Session()
        self._region = self._boto_session.region_name
        self._dynamodb_client = boto3.client("dynamodb", region_name=self._region)
        self._dynamodb_resource = boto3.resource("dynamodb", region_name=self._region)
        self._smm_client = boto3.client("ssm")
        print(self._dynamodb_client, self._dynamodb_resource)

    def create_dynamodb(
        self, kb_name: str, table_name: str, pk_item: str, sk_item: str
    ):
        """
        Create a dynamoDB table for handling the fund info and stores table name
        in parameter store
        Args:
            kb_name: knowledge base table name for creating the SSM parameter
            table_name: table name
            pk_item: table primary key
            sk_item: table secondary key
        """
        try:
            table = self._dynamodb_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {"AttributeName": pk_item, "KeyType": "HASH"},
                    {"AttributeName": sk_item, "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": pk_item, "AttributeType": "S"},
                    {"AttributeName": sk_item, "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",  # Use on-demand capacity mode
            )

            # Wait for the table to be created
            print(f"Creating table {table_name}...")
            table.wait_until_exists()
            print(f"Table {table_name} created successfully!")
            self._smm_client.put_parameter(
                Name=f"{kb_name}-{table_name}-table-name",
                Description=f"{kb_name} {table_name} table name",
                Value=table_name,
                Type="String",
                Overwrite=True,
            )
        except self._dynamodb_client.exceptions.ResourceInUseException:
            print(f"Table {table_name} already exists, skipping table creation step")
            self._smm_client.put_parameter(
                Name=f"{kb_name}-{table_name}-table-name",
                Description=f"{kb_name} {table_name} table name",
                Value=table_name,
                Type="String",
                Overwrite=True,
            )

    def create_multiple_tables(self, kb_name: str, tables_config: list):
        """
        Create multiple DynamoDB tables based on configuration
        Args:
            kb_name: knowledge base name for creating the SSM parameters
            tables_config: list of table configurations, each containing table_name, pk_item, and sk_item
        """
        for table_config in tables_config:
            table_name = table_config["table_name"]
            pk_item = table_config["pk_item"]
            sk_item = table_config["sk_item"]
            
            self.create_dynamodb(kb_name, table_name, pk_item, sk_item)

    def delete_dynamodb_table(self, kb_name, table_name):
        """
        Delete the dynamoDB table and its parameter in parameter store
            kb_name: Knowledge base name for getting parameter name
            table_name: table name
        """
        # Delete DynamoDB table
        try:
            self._dynamodb_client.delete_table(TableName=table_name)
            print(f"Table {table_name} is being deleted...")
            waiter = self._dynamodb_client.get_waiter("table_not_exists")
            waiter.wait(TableName=table_name)
            print(f"Table {table_name} has been deleted.")
            self._smm_client.delete_parameter(Name=f"{kb_name}-{table_name}-table-name")

        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")

    def delete_multiple_tables(self, kb_name: str, tables_config: list):
        """
        Delete multiple DynamoDB tables based on configuration
        Args:
            kb_name: knowledge base name for deleting the SSM parameters
            tables_config: list of table configurations, each containing table_name
        """
        for table_config in tables_config:
            table_name = table_config["table_name"]
            self.delete_dynamodb_table(kb_name, table_name)


if __name__ == "__main__":
    dynamodb = AmazonDynamoDB()
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Example usage:
    config_path = f"{current_dir}/prereqs_config.yaml"
    data = read_yaml_file(config_path)

    parser = argparse.ArgumentParser(description="DynamoDB handler")
    parser.add_argument(
        "--mode",
        required=True,
        help="DynamoDB helper model. One for: create or delete.",
    )

    args = parser.parse_args()

    print(data)
    if args.mode == "create":
        if "tables" in data:
            # 创建多个表
            dynamodb.create_multiple_tables(
                data["knowledge_base_name"],
                data["tables"]
            )
            for table in data["tables"]:
                print(f"Table Name: {table['table_name']}")
        else:
            # 兼容旧配置，创建单个表
            dynamodb.create_dynamodb(
                data["knowledge_base_name"],
                data["table_name"],
                data["pk_item"],
                data["sk_item"],
            )
            print(f"Table Name: {data['table_name']}")
    if args.mode == "delete":
        if "tables" in data:
            # 删除多个表
            dynamodb.delete_multiple_tables(
                data["knowledge_base_name"],
                data["tables"]
            )
        else:
            # 兼容旧配置，删除单个表
            dynamodb.delete_dynamodb_table(data["knowledge_base_name"], data["table_name"])
