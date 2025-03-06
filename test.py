import requests

url = "https://urban-waffle-6pgqvpq6v4v396w-5181.app.github.dev/api/logs"
headers = {"Content-Type": "application/json"}
data = {
    "Timestamp": "2025-03-05T16:41:19Z",
    "Phone": "+1234567890",
    "Status": "success",
    "Platform": "application",
    "Text": "Test message",
    "SystemIp": "192.168.1.1",
    "ImageBase64": "iVBORw0KGgoAAAANSUhEUgAA..."
}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
print(response.json())
