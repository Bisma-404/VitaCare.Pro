from app import app
from database.models import UserDAO
from utils.mapping import DISEASE_CONFIG

app.testing = True
client = app.test_client()

# Ensure admin exists
admin_user = UserDAO.get_user_by_username('admin')
if not admin_user:
    print('Creating admin user `admin` with password `adminpass`')
    uid = UserDAO.create_user('admin', 'adminpass', 'ADMIN', 'Administrator', phone='0000000000', email='admin@example.com')
    print('Created user id:', uid)
else:
    print('Admin user exists')

# Login via POST
login_resp = client.post('/auth/login', data={'username':'admin','password':'adminpass','user_type':'staff'}, follow_redirects=True)
print('Login status:', login_resp.status_code)

# Build form data for diabetes
cfg = DISEASE_CONFIG.get('diabetes')
form_data = {}
if cfg and 'fields' in cfg:
    for f in cfg['fields']:
        name = f['name']
        form_data[name] = str(f.get('example', f.get('default', 1)))

# Post with AJAX header
resp = client.post('/admin/predict/diabetes', data=form_data, headers={'X-Requested-With':'XMLHttpRequest'})
print('AJAX POST status:', resp.status_code)
try:
    print('Response JSON keys:', resp.get_json().keys())
    html = resp.get_json().get('html', '')
    print('HTML fragment length:', len(html))
    # Save fragment for inspection
    with open('tmp_admin_ajax_result.html','w',encoding='utf-8') as fh:
        fh.write(html)
    print('Saved fragment to tmp_admin_ajax_result.html')
except Exception as e:
    print('Failed to parse JSON response:', e)
    print('Raw data length:', len(resp.data))
    with open('tmp_admin_ajax_raw.bin','wb') as fh:
        fh.write(resp.data)
    print('Saved raw response to tmp_admin_ajax_raw.bin')
