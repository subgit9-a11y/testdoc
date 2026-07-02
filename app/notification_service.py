"""Notification Service for Push Notifications"""

import os
import logging
from typing import Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class NotificationService:
    """Unified notification service for push, SMS, and in-app notifications"""
    
    def __init__(self):
        self.firebase_initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase for push notifications"""
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            
            if firebase_admin._apps:
                self.firebase_initialized = True
                logger.info("Firebase already initialized")
                return
            
            service_account_env = os.getenv("FIREBASE_SERVICE_ACCOUNT")
            if not service_account_env:
                logger.warning("Firebase credentials not configured")
                return

            service_account_info = None
            
            # Case 1: JSON Content
            if service_account_env.strip().startswith('{'):
                try:
                    import json
                    service_account_info = json.loads(service_account_env)
                except Exception as e:
                    logger.error(f"Invalid JSON content in FIREBASE_SERVICE_ACCOUNT: {e}")
                    return
            # Case 2: File Path
            else:
                try:
                    path = service_account_env.strip()
                    if not os.path.exists(path):
                        local_path = os.path.basename(path)
                        if os.path.exists(local_path):
                            path = local_path
                        else:
                            logger.error(f"Firebase service account file not found: {path}")
                            return
                            
                    with open(path, 'r') as f:
                        service_account_info = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to read Firebase service account file: {e}")
                    return

            if service_account_info:
                cred = credentials.Certificate(service_account_info)
                firebase_admin.initialize_app(cred)
                self.firebase_initialized = True
                logger.info("Firebase initialized for notifications")
            else:
                logger.warning("Firebase credentials not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.firebase_initialized = False
    
    async def send_push_notification(
        self,
        patient_id: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        fcm_token: Optional[str] = None
    ) -> bool:
        """Send push notification to user"""
        
        if not self.firebase_initialized:
            logger.warning("Firebase not initialized, cannot send push notification")
            return False
        
        try:
            from firebase_admin import messaging
            
            # Get FCM token for patient (you'd fetch this from database)
            if not fcm_token:
                # TODO: Fetch from database
                logger.warning(f"No FCM token for patient {patient_id}")
                return False
            
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=fcm_token
            )
            
            # Send
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    async def notify_buddy_match(
        self,
        patient_id: str,
        buddy_name: str,
        match_score: float
    ):
        """Notify user about new buddy match"""
        await self.send_push_notification(
            patient_id=patient_id,
            title="🤝 You have a new buddy match!",
            body=f"Meet {buddy_name}! You're {int(match_score * 100)}% compatible.",
            data={
                "type": "buddy_match",
                "buddy_name": buddy_name,
                "match_score": str(match_score)
            }
        )
    
    async def notify_check_in_reminder(
        self,
        patient_id: str,
        buddy_name: str
    ):
        """Remind user to do daily check-in"""
        await self.send_push_notification(
            patient_id=patient_id,
            title="⏰ Daily Check-in Time!",
            body=f"{buddy_name} is waiting for your check-in. Don't break the streak!",
            data={
                "type": "check_in_reminder"
            }
        )
    
    async def notify_both_checked_in(
        self,
        patient_id: str,
        points_earned: int,
        streak_days: int
    ):
        """Notify when both buddies complete check-in"""
        await self.send_push_notification(
            patient_id=patient_id,
            title="🎉 Both buddies checked in!",
            body=f"You earned {points_earned} points! Streak: {streak_days} days 🔥",
            data={
                "type": "check_in_complete",
                "points": str(points_earned),
                "streak": str(streak_days)
            }
        )
    
    async def notify_new_message(
        self,
        patient_id: str,
        buddy_name: str,
        message_preview: str
    ):
        """Notify about new buddy message"""
        await self.send_push_notification(
            patient_id=patient_id,
            title=f"💬 Message from {buddy_name}",
            body=message_preview[:50] + "..." if len(message_preview) > 50 else message_preview,
            data={
                "type": "new_message",
                "buddy_name": buddy_name
            }
        )

# Global instance
notification_service = NotificationService()
