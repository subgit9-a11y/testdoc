"""
Predictive Analytics for Medicine Adherence (Supabase Powered)
Uses Supabase to predict patient behavior and optimize reminders.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.database import db_manager

logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    """AI-powered predictive analytics for medicine adherence using Supabase"""
    
    def __init__(self):
        self.models_initialized = db_manager.is_connected()
        
    async def analyze_patient_adherence(self, patient_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Analyze patient's adherence patterns and predict future behavior via Supabase"""
        if not db_manager.is_connected() or not db_manager.client:
            return {'error': 'Database not connected'}
            
        try:
            # 1. Get patient's reminder history from Supabase
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Use inner join for schedules
            res = db_manager.client.table("medicine_reminders")\
                .select("*, medicine_schedules!inner(*)")\
                .eq("patient_id", patient_id)\
                .gte("reminder_datetime", start_date.isoformat())\
                .lte("reminder_datetime", end_date.isoformat())\
                .execute()
            
            reminders = res.data or []
            if not reminders:
                return {'error': 'No reminder data found for patient'}
            
            # 2. Calculate metrics
            total = len(reminders)
            taken = len([r for r in reminders if r.get('status') == 'taken'])
            skipped = len([r for r in reminders if r.get('status') == 'skipped'])
            missed = len([r for r in reminders if r.get('status') == 'missed'])
            
            adherence_rate = (taken / total) * 100 if total > 0 else 0
            
            # Analyze patterns
            patterns = self._analyze_adherence_patterns(reminders)
            
            # Predict
            prediction = self._predict_adherence_risk(patterns, adherence_rate)
            
            return {
                'patient_id': patient_id,
                'analysis_period_days': days_back,
                'total_reminders': total,
                'taken_reminders': taken,
                'skipped_reminders': skipped,
                'missed_reminders': missed,
                'adherence_rate': round(adherence_rate, 2),
                'patterns': patterns,
                'prediction': prediction,
                'recommendations': self._generate_recommendations(patterns, adherence_rate)
            }
                
        except Exception as e:
            logger.error(f"Error analyzing adherence: {e}")
            return {'error': str(e)}
    
    def _analyze_adherence_patterns(self, reminders: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in patient behavior"""
        patterns = {'time_patterns': {}, 'day_patterns': {}, 'medicine_patterns': {}}
        
        try:
            for rem in reminders:
                dt_str = rem.get('reminder_datetime') or rem.get('dose_datetime')
                if not dt_str: continue
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                
                # Time slot
                slot = self._get_time_slot(dt.hour)
                if slot not in patterns['time_patterns']: patterns['time_patterns'][slot] = {'total': 0, 'taken': 0}
                patterns['time_patterns'][slot]['total'] += 1
                if rem.get('status') == 'taken': patterns['time_patterns'][slot]['taken'] += 1
                
                # Day of week
                day = dt.strftime('%A')
                if day not in patterns['day_patterns']: patterns['day_patterns'][day] = {'total': 0, 'taken': 0}
                patterns['day_patterns'][day]['total'] += 1
                if rem.get('status') == 'taken': patterns['day_patterns'][day]['taken'] += 1
                
                # Medicine
                med_name = rem.get('medicine_schedules', {}).get('medicine_name', 'Unknown')
                if med_name not in patterns['medicine_patterns']: patterns['medicine_patterns'][med_name] = {'total': 0, 'taken': 0}
                patterns['medicine_patterns'][med_name]['total'] += 1
                if rem.get('status') == 'taken': patterns['medicine_patterns'][med_name]['taken'] += 1

            # Ratios
            for cat in ['time_patterns', 'day_patterns', 'medicine_patterns']:
                for k in patterns[cat]:
                    tot = patterns[cat][k]['total']
                    patterns[cat][k]['adherence_rate'] = (patterns[cat][k]['taken'] / tot * 100) if tot > 0 else 0
            
            return patterns
        except Exception as e:
            logger.error(f"Pattern error: {e}")
            return patterns

    def _get_time_slot(self, hour: int) -> str:
        if 6 <= hour < 12: return 'morning'
        elif 12 <= hour < 17: return 'afternoon'
        elif 17 <= hour < 21: return 'evening'
        return 'night'

    def _predict_adherence_risk(self, patterns: Dict, current_adherence: float) -> Dict[str, Any]:
        risk_score = 0
        factors = []
        
        if current_adherence < 70:
            factors.append("Low overall adherence")
            risk_score += 30
        
        for slot, data in patterns['time_patterns'].items():
            if data['adherence_rate'] < 60:
                factors.append(f"Poor {slot} adherence")
                risk_score += 10
        
        return {
            'risk_level': 'high' if risk_score >= 40 else 'medium' if risk_score >= 20 else 'low',
            'risk_score': min(risk_score, 100),
            'risk_factors': factors,
            'confidence': 0.75
        }

    def _generate_recommendations(self, patterns: Dict, rate: float) -> List[str]:
        recs = []
        if rate < 70: recs.append("🚨 Schedule urgent consultation")
        elif rate < 85: recs.append("⚠️ Monitor closely")
        if not recs: recs.append("✅ Excellent work!")
        return recs

    async def get_population_insights(self, medicine_type: Optional[str] = None) -> Dict[str, Any]:
        """Population insights via Supabase"""
        if not db_manager.is_connected() or not db_manager.client: return {'error': 'No DB'}
        try:
            query = db_manager.client.table("medicine_schedules").select("medicine_name")
            if medicine_type: query = query.ilike("medicine_name", f"%{medicine_type}%")
            res = query.execute()
            
            meds = [r['medicine_name'] for r in res.data]
            return {
                'total_schedules': len(meds),
                'top_medicines': sorted(set(meds), key=meds.count, reverse=True)[:5]
            }
        except Exception as e: return {'error': str(e)}

# Global instance
predictive_analytics = PredictiveAnalytics()

# Global analytics instance
predictive_analytics = PredictiveAnalytics()