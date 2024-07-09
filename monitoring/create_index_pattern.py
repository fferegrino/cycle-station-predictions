import json

import requests

kibana_url = "http://localhost:5601"

api_endpoint = f"{kibana_url}/api/index_patterns/index_pattern"

# Define the index pattern
index_pattern = {"index_pattern": {"title": "prediction_service-*", "timeFieldName": "@timestamp"}}

headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}

response = requests.post(api_endpoint, headers=headers, data=json.dumps(index_pattern))

if response.status_code == 200:
    print("Index pattern created successfully!")
    print(response.json())
else:
    print(f"Failed to create index pattern. Status code: {response.status_code}")
    print(response.text)
