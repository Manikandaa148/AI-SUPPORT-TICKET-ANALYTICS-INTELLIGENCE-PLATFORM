from app.services.anomaly_service import AnomalyService

def test_anomaly_detection():
    service = AnomalyService()
    anomalies = service.detect_anomalies()
    assert isinstance(anomalies, list)
    # Even if empty, it returns a list
