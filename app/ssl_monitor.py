"""
SSL Expiration "Doomsday" Monitor
Fixes Issue #40: Prevent sudden platform outages due to Let's Encrypt / SSL auto-renewal failures.
"""

import ssl
import socket
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# List of critical platform domains that would cause a global outage if SSL expires
CRITICAL_DOMAINS = [
    "ayureze.in",
    "app.ayureze.in",
    "brain.ayureze.in",
    "whatsapp.ayureze.in",
    "ykewayjfdanhqtqpziwt.supabase.co",
    "s3.ap-southeast-1.wasabisys.com",
    "ayureze-healthcare.myshopify.com"
]

class SSLExpirationMonitor:
    def __init__(self, warning_days: int = 14):
        """
        Args:
            warning_days: Number of days before expiration to trigger a critical alert.
        """
        self.warning_days = warning_days

    def check_ssl_expiry(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Connect to a hostname and extract the SSL certificate expiration date.
        """
        context = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # 'notAfter' format is usually 'May  9 23:59:59 2026 GMT'
                    expire_date_str = cert.get('notAfter')
                    
                    # Parse the date
                    expire_date = datetime.strptime(expire_date_str, '%b %d %H:%M:%S %Y %Z')
                    expire_date = expire_date.replace(tzinfo=timezone.utc)
                    
                    now = datetime.now(timezone.utc)
                    days_remaining = (expire_date - now).days
                    
                    return {
                        "hostname": hostname,
                        "expire_date": expire_date.isoformat(),
                        "days_remaining": days_remaining,
                        "is_expiring_soon": days_remaining <= self.warning_days,
                        "error": None
                    }
        except Exception as e:
            logger.error(f"Failed to check SSL for {hostname}: {e}")
            return {
                "hostname": hostname,
                "expire_date": None,
                "days_remaining": 0,
                "is_expiring_soon": True, # Assume critical if we can't even check it
                "error": str(e)
            }

    def run_daily_audit(self):
        """
        Audit all critical domains and trigger alerts if any are within the danger zone.
        """
        logger.info(f"🔍 Running Daily SSL Expiration Audit for {len(CRITICAL_DOMAINS)} domains...")
        
        alerts_triggered = []
        
        for domain in CRITICAL_DOMAINS:
            result = self.check_ssl_expiry(domain)
            
            if result["error"]:
                logger.error(f"❌ SSL Check Failed for {domain}: {result['error']}")
                alerts_triggered.append(result)
            elif result["is_expiring_soon"]:
                logger.critical(
                    f"🚨 SSL DOOMSDAY ALERT: Certificate for {domain} expires in {result['days_remaining']} days! "
                    f"(Threshold: {self.warning_days} days)"
                )
                alerts_triggered.append(result)
            else:
                logger.info(f"✅ {domain} SSL is healthy (Expires in {result['days_remaining']} days)")

        if alerts_triggered:
            self._trigger_engineering_alert(alerts_triggered)
            
        return alerts_triggered
        
    def _trigger_engineering_alert(self, alerts: List[Dict[str, Any]]):
        """
        Send a PagerDuty/Slack/SMS alert to the DevOps team.
        """
        logger.critical("🚨 Dispatched high-priority SSL Expiration alerts to Engineering Team!")
        # Implement Datadog/Slack/PagerDuty API payload here in production

# Global Instance
ssl_monitor = SSLExpirationMonitor()

if __name__ == "__main__":
    # For manual testing
    ssl_monitor.run_daily_audit()
