
# 🚀 Production Server Data Cloning to Staging Server with Sensitive Data Filtering 🛡️

This repository contains a Python script that facilitates the process of cloning data from a production MongoDB server to a staging MongoDB server. The script exports data from the production server, anonymizes sensitive data, and then imports the anonymized data into the staging server.

## Objective 🎯

The main objective of this script is to provide a streamlined approach to clone data from a production MongoDB server to a staging MongoDB server while ensuring that sensitive data is properly anonymized during the process.

## How It Works 🛠️

1. The script connects to the production MongoDB server and lists all available databases.

2. For each database on the production server:
   - The script exports data from each collection to a JSON file.
   - Sensitive data fields are anonymized in the exported JSON files.

3. The anonymized JSON files are imported into the corresponding collections on the staging MongoDB server.

## Prerequisites 📋

- Python 3.x
- The `pymongo` library (install using `pip install pymongo`)

## Usage 🚀

1. Clone this repository to your local machine:

    ```sh
    git clone https://github.com/your-username/production-to-staging.git
    cd production-to-staging
    ```

2. Modify the script's configuration:
   - Open the `main.py` file.
   - Replace `source_uri` with the URI of your production MongoDB server.
   - Replace `destination_uri` with the URI of your staging MongoDB server.
   - Customize `sensitive_fields` list according to your data structure.

3. Run the script:

    ```sh
    python main.py
    ```

## Python Code Snippet 🐍

```python
import subprocess
import json
from pymongo import MongoClient
import os

def mask_sensitive_data(record, sensitive_fields):
    masked_record = record.copy()
    for field in sensitive_fields:
        if field in masked_record:
            masked_record[field] = '*********' 
    return masked_record

def anonymize_data(input_filename, output_filename, sensitive_fields):
    data = []
    with open(input_filename, 'r') as file:
        for line in file:
            record = json.loads(line)
            masked_record = mask_sensitive_data(record, sensitive_fields)
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
    
    # Get a list of databases
    source_databases = source_client.list_database_names()
    
    # Export data from all databases and collections
    for database_name in source_databases:
        source_database = source_client[database_name]
        destination_database = destination_client[database_name]
        
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
            
            # Anonymize data
            anonymize_data(output_file, output_file, sensitive_fields)
    
    # Import all anonymized JSON files into the destination MongoDB
    anonymized_files = [f for f in os.listdir(output_folder) if f.endswith("_anonymized.json")]
    for file in anonymized_files:
        database_name, collection_name = file.replace("_anonymized.json", "").split("_", 1)
        import_command = [
            "mongoimport",
            "--uri", destination_uri,
            "--collection", collection_name,
            "--db", database_name,
            "--file", f"{output_folder}/{file}",
            "--jsonArray",
            "--quiet"
        ]
        subprocess.run(" ".join(import_command), shell=True)

if __name__ == '__main__':
    main()
```

## Important Notes 📝

- The script assumes that both the production and staging MongoDB servers are accessible and properly configured.
- Make sure to carefully review and adjust the code to fit your specific environment and requirements.
- This script does not handle complex data structures or data transformations. It's recommended to adapt the code to your specific data schema.

## Disclaimer ⚠️

This script is provided as-is and without any warranties. Use it responsibly and ensure that you comply with all legal and security requirements when handling sensitive data.

