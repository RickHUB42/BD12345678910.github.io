import requests
import json
def get_url(file_path: str) -> str:
    dataset_id = 'a5e7b52d-a7e3-4f29-9084-b8d405d2edd6'
    token = 'dataset-xiMuq1Ku1ZGzMWJmWvHZdvfJ'
    url = f"http://localhost/v1/datasets/{dataset_id}/document/create-by-file"
    files = { "file": (file_path, open(file_path, "rb")) }
    data_payload = {
    "indexing_technique": "high_quality",
    "process_rule": {
        "mode": "custom",
        "rules": {
            "pre_processing_rules": [
                {"id": "remove_extra_spaces", "enabled": True},
            ],
            "segmentation": {
                "separator": "###",
                "max_tokens": 500
            }
        }
    }
    }
    payload = {'data': json.dumps(data_payload)}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, data=payload, files=files, headers=headers)

    print(response.text)
dataset_id = 'a5e7b52d-a7e3-4f29-9084-b8d405d2edd6'
token = 'dataset-xiMuq1Ku1ZGzMWJmWvHZdvfJ'
url = f"http://localhost/v1/datasets/{dataset_id}"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(url, headers=headers)
print(response.text)



get_url("IAIndependent.pdf")