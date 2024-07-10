import json

import requests

kibana_url = "http://localhost:5601"

index_pattern_name = "prediction_service-*"

create_api_endpoint = f"{kibana_url}/api/index_patterns/index_pattern"
delete_api_endpoint = f"{kibana_url}/api/index_patterns/index_pattern/{index_pattern_name}"

headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}


def delete_index_pattern():
    response = requests.delete(delete_api_endpoint, headers=headers)
    if response.status_code == 200:
        print(f"Successfully deleted existing index pattern: {index_pattern_name}")
    elif response.status_code == 404:
        print(f"Index pattern {index_pattern_name} not found. Proceeding to create.")
    else:
        print(f"Failed to delete index pattern. Status code: {response.status_code}")
        print(response.text)


index_pattern = {"index_pattern": {"title": index_pattern_name, "timeFieldName": "request.timestamp", "fields": {}}}

delete_index_pattern()

response = requests.post(create_api_endpoint, headers=headers, data=json.dumps(index_pattern))

if response.status_code == 200:
    print("New index pattern created successfully!")
    print(response.json())
else:
    print(f"Failed to create new index pattern. Status code: {response.status_code}")
    print(response.text)
