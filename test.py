import subprocess
import json
import random
from pymongo import MongoClient
import os

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
            
            # Remove fields with null values
            masked_record = {key: value for key, value in masked_record.items() if value is not None}
            
            if masked_record:  # Check if the record is not empty after removing null fields
                data.append(masked_record)
    
    if data:  # Check if any records are left to save
        with open(output_filename, 'w') as file:
            json.dump(data, file, indent=4)

def main():
    source_uri = "mongodb+srv://admin:mypassword@cluster0.0sqlfya.mongodb.net"  
    destination_uri = "mongodb://127.0.0.1:4002"  
    sensitive_fields = ['gst_id','name','address', 'birthdate', 'email','account_id']
    output_folder = "exported_data" 
    
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Connect to the source MongoDB
    source_client = MongoClient(source_uri)
    
    # Connect to the destination MongoDB
    destination_client = MongoClient(destination_uri)
    
    # Get a list of databases and collection names from the source MongoDB
    source_databases = source_client.list_database_names()
    
    # Export data from all databases and collections
    for database_name in source_databases:
        source_database = source_client[database_name]
        
        # Get collection names from the source database
        collection_names = source_database.list_collection_names()
        for collection_name in collection_names:
            output_file = f"{output_folder}/{database_name}_{collection_name}_anonymized.json"
            
            # Skip exporting if the anonymized file already exists
            if os.path.exists(output_file):
                continue
            
            export_command = [
                "mongoexport",
                "--uri", source_uri,
                "--collection", collection_name,
                "--db", database_name,
                "--out", output_file
            ]
            subprocess.run(" ".join(export_command), shell=True)
            
            anonymize_data(output_file, output_file, sensitive_fields)
            
            # Import data into the destination MongoDB using the same names
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

if __name__ == '__main__':
    main()
