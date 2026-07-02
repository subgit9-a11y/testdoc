import os
import json
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CashfreePayouts:
    def __init__(self):
        self.client_id = os.getenv("CASHFREE_CLIENT_ID")
        self.client_secret = os.getenv("CASHFREE_CLIENT_SECRET")
        self.env = os.getenv("CASHFREE_ENV", "TEST") # 'TEST' or 'PROD'
        
        if self.env == "PROD":
            self.base_url = "https://payout-api.cashfree.com/payout/v1"
        else:
            self.base_url = "https://payout-gamma.cashfree.com/payout/v1"

    def _get_token(self):
        url = f"{self.base_url}/authorize"
        headers = {
            "X-Client-Id": self.client_id,
            "X-Client-Secret": self.client_secret
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("data", {}).get("token")
        else:
            logger.error(f"Cashfree Auth Error: {response.text}")
            return None

    def add_beneficiary(self, bene_id, name, email, phone, bank_account=None, ifsc=None, vpa=None, address="India"):
        token = self._get_token()
        if not token: return False

        url = f"{self.base_url}/addBeneficiary"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "beneId": bene_id,
            "name": name,
            "email": email,
            "phone": phone,
            "address1": address,
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001"
        }
        if bank_account and ifsc:
            payload["bankAccount"] = bank_account
            payload["ifsc"] = ifsc
        if vpa:
            payload["vpa"] = vpa
        
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        if res_data.get("subCode") == "200" or res_data.get("subCode") == "409": # 409 is already exists
            return True
        logger.error(f"Cashfree addBeneficiary failed: {res_data}")
        return False

    def request_transfer(self, transfer_id, bene_id, amount, transfer_mode="banktransfer", remarks="Doctor Payout"):
        token = self._get_token()
        if not token: return None

        url = f"{self.base_url}/requestTransfer"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "beneId": bene_id,
            "amount": str(amount),
            "transferId": transfer_id,
            "transferMode": transfer_mode,
            "remarks": remarks
        }
        
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        if res_data.get("subCode") == "200":
            return res_data.get("data", {}).get("referenceId")
        
        logger.error(f"Cashfree requestTransfer failed: {res_data}")
        return None

cashfree_payouts = CashfreePayouts()
