from app import app
from database.models import UserDAO
from utils.mapping import DISEASE_CONFIG

app.testing = True
client = app.test_client()

# Ensure admin exists
admin = UserDAO.get_user_by_username('admin')
if not admin:
    print('Creating admin user `admin`')
    uid = UserDAO.create_user('admin', 'adminpass', 'ADMIN', 'Administrator', phone='0000000000', email='admin@example.com')
    admin = UserDAO.get_user_by_username('admin')

print('Using admin id:', admin['id'])

# Set session as logged-in admin
with client.session_transaction() as sess:
    sess['user_id'] = admin['id']
    sess['username'] = admin['username']
    sess['role'] = admin['role']
    sess['name'] = admin.get('name', 'Administrator')
    sess['user_type'] = 'staff'

# Build form data for diabetes using defaults
cfg = DISEASE_CONFIG.get('diabetes')
form_data = {}
if cfg and 'fields' in cfg:
    for f in cfg['fields']:
        name = f['name']
        form_data[name] = str(f.get('default', 1))

# Include patient_id so the handler will create a report and attach prediction
form_data['patient_id'] = str(admin['id'])

resp = client.post('/admin/predict/diabetes', data=form_data, follow_redirects=True)
print('POST status:', resp.status_code)
print('Response length:', len(resp.data))
try:
    txt = resp.get_data(as_text=True)
    if 'Prediction failed' in txt:
        print('Prediction failed in response')
    else:
        print('Prediction likely succeeded; response contains:', txt[:200])
except Exception as e:
    print('Error reading response:', e)
