import pandas as pd
from typing import List
from app.models.schemas import AnomalyResult
from app.config import settings
from app.data.loader import load_csv_to_dataframe

class AnomalyService:
    def __init__(self):
        self.df = load_csv_to_dataframe()

    def detect_anomalies(self) -> List[AnomalyResult]:
        if self.df is None or self.df.empty:
            return []

        anomalies = []
        
        for _, row in self.df.iterrows():
            # 1. Critical unresolved
            if row.get('priority') == 'Critical' and row.get('status') != 'Resolved':
                # assuming response_time_hrs or missing resolution implies it's unresolved
                # checking ticket age is hard without current time vs created_at, but we can check resolution_time_hrs
                # If it's unresolved, we might just flag all critical open tickets, or use a threshold if age is trackable.
                # Here we simplify: if Critical and Open, flag it.
                anomalies.append(AnomalyResult(
                    ticket_id=row['ticket_id'],
                    severity="high",
                    anomaly_type="critical_unresolved",
                    reason="Critical ticket is open/unresolved.",
                ))
            
            # 2. Very slow resolution
            res_time = row.get('resolution_time_hrs')
            if pd.notna(res_time) and res_time > settings.ANOMALY_RESOLUTION_THRESHOLD_HOURS:
                anomalies.append(AnomalyResult(
                    ticket_id=row['ticket_id'],
                    severity="medium",
                    anomaly_type="slow_resolution",
                    reason=f"Resolution time {res_time} hrs exceeds threshold {settings.ANOMALY_RESOLUTION_THRESHOLD_HOURS} hrs.",
                    detected_value=res_time,
                    threshold=settings.ANOMALY_RESOLUTION_THRESHOLD_HOURS
                ))

            # 3. Very slow first response
            resp_time = row.get('response_time_hrs')
            if pd.notna(resp_time) and resp_time > settings.ANOMALY_RESPONSE_THRESHOLD_HOURS:
                anomalies.append(AnomalyResult(
                    ticket_id=row['ticket_id'],
                    severity="medium",
                    anomaly_type="slow_response",
                    reason=f"Response time {resp_time} hrs exceeds threshold {settings.ANOMALY_RESPONSE_THRESHOLD_HOURS} hrs.",
                    detected_value=resp_time,
                    threshold=settings.ANOMALY_RESPONSE_THRESHOLD_HOURS
                ))

            # 4. Low customer rating
            rating = row.get('customer_rating')
            if pd.notna(rating) and rating <= settings.LOW_RATING_THRESHOLD:
                severity = "high" if row.get('priority') == 'Critical' else "medium"
                anomalies.append(AnomalyResult(
                    ticket_id=row['ticket_id'],
                    severity=severity,
                    anomaly_type="low_rating",
                    reason=f"Customer rating is {rating}, which is low.",
                    detected_value=rating,
                    threshold=settings.LOW_RATING_THRESHOLD
                ))

        # Statistical anomalies (e.g. resolution time > mean + 2*std)
        if 'resolution_time_hrs' in self.df.columns:
            mean = self.df['resolution_time_hrs'].mean()
            std = self.df['resolution_time_hrs'].std()
            thresh = mean + settings.STATISTICAL_Z_THRESHOLD * std
            
            stat_anomalies = self.df[self.df['resolution_time_hrs'] > thresh]
            for _, row in stat_anomalies.iterrows():
                # Avoid duplicates if already flagged by business rules
                if not any(a.ticket_id == row['ticket_id'] and a.anomaly_type == "slow_resolution" for a in anomalies):
                    anomalies.append(AnomalyResult(
                        ticket_id=row['ticket_id'],
                        severity="low",
                        anomaly_type="statistical_slow_resolution",
                        reason=f"Resolution time {row['resolution_time_hrs']} hrs is statistically anomalous (mean={mean:.2f}, std={std:.2f}).",
                        detected_value=row['resolution_time_hrs'],
                        threshold=thresh
                    ))

        return anomalies
