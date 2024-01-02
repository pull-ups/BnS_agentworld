import requests
import json

# The URL of the endpoint

url = 'http://10.1.1.43:10002/make_decision'

# Sample data to be sent in the POST request
data = {
    "agent_ids": [1, 2, 3]  # List of agent IDs. Replace with actual IDs as needed.
}

# Make the POST request and get the response
response = requests.post(url, json=data)

# Print the status code and response data
print("Status Code:", response.status_code)
print("Response:", response.json())