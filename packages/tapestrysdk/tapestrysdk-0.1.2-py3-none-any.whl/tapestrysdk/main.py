import requests
import pandas as pd
import io

def hello():
    print("Hello from Tapestry!")

def fetch_library_data(token, parent):
    url = "http://localhost:8951/admin/get_folder_item"
    headers = { 
        "accept": "application/json, text/plain, */*",
        "authorization": f"{token}",
        "content-type": "application/json",
    }  
    params = {
        "parent": parent,
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}

def fetch_document_details(token, document_id):
    url = "http://localhost:8951/admin/get_file_details"
    headers = { 
        "accept": "application/json, text/plain, */*",
        "authorization": f"{token}",
        "content-type": "application/json",
    } 
    params = {
        "document_id": document_id,
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}


    url = "http://localhost:5173/admin/get_file_details"
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"{token}",
        "content-type": "application/json",
    }
    params = {"document_id": document_id}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            file_info = data.get("body", {})

            if not file_info:
                return {"error": "No file details found"}

            file_url = file_info.get("file_id", "")
            file_type = file_info.get("file_type", "").lower()

            if not file_url:
                return {"error": "No file URL found"}

            # Download the file from S3
            file_response = requests.get(file_url)

            if file_response.status_code != 200:
                return {"error": "Failed to download file", "details": file_response.text}

            # Read file content based on type
            if file_type in ["xlsx", "xls"]:
                df = pd.read_excel(io.BytesIO(file_response.content))  # Read Excel
            elif file_type == "csv":
                df = pd.read_csv(io.StringIO(file_response.text))  # Read CSV
            else:
                return {"error": "Unsupported file type", "file_type": file_type}

            return df.to_dict(orient="records")  # Return extracted data as a list of dictionaries

        except requests.exceptions.JSONDecodeError:
            return {"error": "Response is not valid JSON", "details": response.text}
    else:
        return {"error": f"Request failed with status code {response.status_code}", "details": response.text}