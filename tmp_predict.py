import requests
s = requests.Session()
# Login
r = s.post('http://127.0.0.1:5000/auth/login', data={'username':'admin','password':'admin123','user_type':'staff'})
print('LOGIN_STATUS', r.status_code)
# Prediction post
p = s.post('http://127.0.0.1:5000/admin/predict/diabetes', data={'pregnancies':'0','glucose':'180','blood_pressure':'85','skin_thickness':'20','insulin':'0','bmi':'33','dpf':'0.5','age':'45'})
print('PREDICT_STATUS', p.status_code)
open('tmp_admin_predict_result.html','w',encoding='utf-8').write(p.text)
print('SAVED tmp_admin_predict_result.html')
