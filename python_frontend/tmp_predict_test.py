from predictions.prediction_engine import PredictionEngine

pe = PredictionEngine()
# Feature keys use lowercase names expected by the prediction configs
features = {
    'pregnancies': 2,
    'glucose': 120,
    'bloodpressure': 70,
    'skinthickness': 20,
    'insulin': 79,
    'bmi': 28.0,
    'diabetespedigreefunction': 0.5,
    'age': 33
}
# No symptom strings for this test
symptoms = []
res = pe.predict(features, symptoms, 'diabetes')
print('PREDICTION:', res)
