import requests

# Test the staff prediction endpoint
url = "http://127.0.0.1:5000/staff/reports/3/predict"
data = {
    'prediction_type': 'diabetes',
    'glucose': '150',
    'bmi': '30',
    'age': '45',
    'symptoms': 'fatigue,frequent_urination'
}

try:
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
except Exception as e:
    print(f"Error: {e}")