import json
from app import app

client = app.test_client()

sample = {
    'test_data': {
        'pregnancies': 0,
        'glucose': 110,
        'blood_pressure': 75,
        'skin_thickness': 18,
        'insulin': 80,
        'bmi': 26.5,
        'dpf': 0.4,
        'age': 28
    },
    'symptoms': []
}

resp = client.post('/api/predict/diabetes', data=json.dumps(sample), content_type='application/json')
print('Status:', resp.status_code)
try:
    j = resp.get_json()
    print(json.dumps(j, indent=2))
except Exception:
    print('Response not JSON; raw length:', len(resp.data))
