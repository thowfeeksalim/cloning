import subprocess
import json
import random
from pymongo import MongoClient
import os

def generate_fake_data(field):
    if field == "name":
        return f"User{random.randint(1000, 9999)}"
    elif field == "email":
        return f"user{random.randint(1000, 9999)}@example.com"
    elif field == "gst_id":
        return f"{random.randint(100000, 999999)}"
    elif field == "address":
        return f"Address{random.randint(1000, 9999)}"
    elif field == "birthdate":
        return f"01-01-2000"  
    elif field == "accounts":
        return [{"account_id": str(random.randint(1000, 9999))} for _ in range(2)]
    elif field == "tier_and_details":
        return {"tier": f"Tier{random.randint(1, 3)}", "details": f"Details{random.randint(1000, 9999)}"}
    elif field == "active":
        return random.choice([True, False])

def anonymize_data(input_filename, output_filename, sensitive_fields):
    data = []
    with open(input_filename, 'r') as file:
        for line in file:
            record = json.loads(line)
            masked_record = record.copy()
            for field in sensitive_fields:
                if field in masked_record:
                    masked_record[field] = generate_fake_data(field)
            data.append(masked_record)
    
    with open(output_filename, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    source_uri = "mongodb://127.0.0.1:4001"  
    destination_uri = "mongodb://127.0.0.1:4002"  
    sensitive_fields = ['gst_id','name','address', 'birthdate', 'email', 'accounts', 'tier_and_details', 'active']
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