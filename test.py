import subprocess
import json
import os
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

def generate_fake_data(field, index):
    if field == "name":
        return f"User{index}"
    elif field == "email":
        return f"user{index}@example.com"
    elif field == "gst_id":
        return f"{100000 + index}"
    elif field == "address":
        return f"Address{index}"
    elif field == "birthdate":
        return f"01-01-2000"
    elif field == "accounts":
        return [{"account_id": str(index * 2 + i)} for i in range(2)]
    elif field == "tier_and_details":
        return {"tier": f"Tier{index % 3 + 1}", "details": f"Details{index}"}
    elif field == "active":
        return bool(index % 2)

def anonymize_data(input_filename, output_filename, sensitive_fields):
    data = []
    with open(input_filename, 'r', encoding='utf-8') as file:
        for index, line in enumerate(file):
            record = json.loads(line)
            masked_record = record.copy()
            for field in sensitive_fields:
                if field in masked_record:
                    masked_record[field] = generate_fake_data(field, index)
            
            masked_record = {key: value for key, value in masked_record.items() if value is not None}
            
            if masked_record:
                data.append(masked_record)
    
    if data:
        with open(output_filename, 'w') as file:
            json.dump(data, file, indent=4)

def process_collection(source_uri, destination_uri, collection_name, database_name, sensitive_fields, output_folder):
    output_file = f"{output_folder}/{database_name}_{collection_name}_anonymized.json"
    if not os.path.exists(output_file):
        export_command = [
            "mongoexport",
            "--uri", source_uri,
            "--collection", collection_name,
            "--db", database_name,
            "--out", output_file
        ]
        subprocess.run(" ".join(export_command), shell=True)

        anonymize_data(output_file, output_file, sensitive_fields)

        import_command = [
            "mongoimport",
            "--uri", destination_uri,
            "--collection", collection_name,
            "--db", database_name,
            "--file", output_file,
            "--jsonArray",
            "--quiet"
        ]
        subprocess.run(" ".join(import_command), shell=True)

def main():
    source_uri = "mongodb+srv://admin:mypassword@cluster0.0sqlfya.mongodb.net"
    destination_uri = "mongodb://127.0.0.1:4002"
    sensitive_fields = ['gst_id', 'name', 'address', 'birthdate', 'email', 'account_id']
    output_folder = "exported_data"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    source_client = MongoClient(source_uri)
    destination_client = MongoClient(destination_uri)
    source_databases = source_client.list_database_names()

    with ThreadPoolExecutor() as executor:
        tasks = []
        for database_name in source_databases:
            source_database = source_client[database_name]
            collection_names = source_database.list_collection_names()
            for collection_name in collection_names:
                tasks.append(
                    executor.submit(
                        process_collection,
                        source_uri, destination_uri, collection_name, database_name, sensitive_fields, output_folder
                    )
                )
        for task in tasks:
            task.result()

if __name__ == '__main__':
    main()
