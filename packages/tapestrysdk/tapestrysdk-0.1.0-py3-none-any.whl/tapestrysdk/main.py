import requests

def hello():
    print("Hello from Tapestry!")

def fetch_library_data(token, folder_name):
    url = "https://tapestry.familygpt.app/admin/library"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = {
        "limit": 10,
        "page": 1,
        "active": "grid",
        "group_id": [],
        "organisation_id": 1,
        "parent": f"{folder_name}",
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}
