import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'python_frontend'))
from database.models import UserDAO
print('Checking for admin user...')
admin = UserDAO.get_user_by_username('admin')
print('Found admin:', bool(admin))
if not admin:
    print('Creating admin user...')
    uid = UserDAO.create_user('admin','admin123','ADMIN','Administrator', phone=None, email='admin@example.com', status='ACTIVE')
    print('Created admin id:', uid)
else:
    print('Admin user id:', admin.get('id'))

# Now perform login and prediction
import requests
s = requests.Session()
print('Logging in...')
r = s.post('http://127.0.0.1:5000/auth/login', data={'username':'admin','password':'admin123','user_type':'staff'})
print('Login status', r.status_code)
# Check redirect
print('Login final url', r.url)
print('Now POST prediction...')
p = s.post('http://127.0.0.1:5000/admin/predict/diabetes', data={'pregnancies':'0','glucose':'180','blood_pressure':'85','skin_thickness':'20','insulin':'0','bmi':'33','dpf':'0.5','age':'45'})
print('Predict status', p.status_code)
open('tmp_admin_predict_result.html','w', encoding='utf-8').write(p.text)
print('Saved tmp_admin_predict_result.html')
