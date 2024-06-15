import requests

url = "http://localhost:8000/api/generate_roster"
payload = {
  "employees": [
    {"id": 1, "name": "Alice", "preferences": ["day", "evening"]},
    {"id": 2, "name": "Bob", "preferences": ["night"]},
    {"id": 3, "name": "Charlie", "preferences": ["day", "night"]},
    {"id": 4, "name": "David", "preferences": ["evening", "night"]},
    {"id": 5, "name": "Eve", "preferences": ["day"]},
    {"id": 6, "name": "Frank", "preferences": ["evening"]},
    {"id": 7, "name": "Grace", "preferences": ["night", "evening"]}
  ],
  "start_date": "2024-06-17"
}

response = requests.post(url, json=payload)

# Check if the request was successful
if response.status_code == 200:
    roster = response.json()

    # Save the roster to a text file
    with open("roster.txt", "w") as file:
        for shift in roster:
            file.write(f"Employee ID: {shift['employee_id']}, Shift Type: {shift['shift_type']}, Date: {shift['date']}\n")
else:
    print(f"Failed to generate roster. Status code: {response.status_code}")
    print(response.json())
