from database.models import DiseaseThresholdDAO

thresholds = DiseaseThresholdDAO.get_all_thresholds()
print('Found', len(thresholds), 'threshold entries')
for t in thresholds:
    print(f"Disease: {t.get('disease_name')} | Param: {t.get('parameter_name')} | min={t.get('min_value')} max={t.get('max_value')} unit={t.get('unit')}")
