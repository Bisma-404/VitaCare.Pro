import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'python_frontend'))
import requests
s = requests.Session()
print('GET login page')
r = s.get('http://127.0.0.1:5000/auth/login')
print('GET login status', r.status_code)
print('POST login')
r2 = s.post('http://127.0.0.1:5000/auth/login', data={'username':'admin','password':'admin123','user_type':'staff'}, allow_redirects=True)
print('POST login status', r2.status_code)
print('History length', len(r2.history))
for h in r2.history:
    print('  h:', h.status_code, h.headers.get('Location'))
print('Final URL after login:', r2.url[:200])

print('\nGET admin predict form (diabetes)')
g = s.get('http://127.0.0.1:5000/admin/predict/diabetes')
print('GET form status', g.status_code)
print(g.text[:600])

print('\nPOST prediction')
p = s.post('http://127.0.0.1:5000/admin/predict/diabetes', data={'pregnancies':'0','glucose':'180','blood_pressure':'85','skin_thickness':'20','insulin':'0','bmi':'33','dpf':'0.5','age':'45'}, allow_redirects=True)
print('POST predict status', p.status_code)
print('Final URL', p.url)
print(p.text[:800])
