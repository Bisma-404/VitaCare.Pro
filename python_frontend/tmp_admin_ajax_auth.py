from app import app
from database.models import UserDAO
from utils.mapping import DISEASE_CONFIG

app.testing = True
client = app.test_client()

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
    js = resp.get_json()
    print('Response JSON keys:', list(js.keys()))
    html = js.get('html','')
    print('HTML fragment length:', len(html))
    with open('tmp_admin_ajax_auth_result.html','w',encoding='utf-8') as fh:
        fh.write(html)
    print('Saved fragment to tmp_admin_ajax_auth_result.html')
except Exception as e:
    print('Failed to parse JSON:', e)
    print('Raw status:', resp.status)
    with open('tmp_admin_ajax_auth_raw.bin','wb') as fh:
        fh.write(resp.data)
    print('Saved raw response to tmp_admin_ajax_auth_raw.bin')
