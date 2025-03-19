# liberal_alpha/utils.py
import logging
import requests
import json

logger = logging.getLogger(__name__)

def fetch_subscribed_records(base_url: str, api_key: str) -> list:
    try:
        headers = {"X-API-Key": api_key}
        response = requests.get(f"{base_url}/api/subscriptions", headers=headers)
        if response.status_code == 401:
            logger.info("API key header auth failed, trying query parameter...")
            response = requests.get(f"{base_url}/api/subscriptions?key={api_key}")
        if response.status_code == 200:
            data = response.json()
            subscriptions = []
            if "data" in data:
                if isinstance(data["data"], list):
                    subscriptions = data["data"]
                elif isinstance(data["data"], dict) and "subscriptions" in data["data"]:
                    subscriptions = data["data"]["subscriptions"]
            records = []
            for sub in subscriptions:
                if "record" in sub:
                    records.append(sub["record"])
                elif "subscription" in sub and "record" in sub:
                    records.append(sub["record"])
            own_records_response = requests.get(f"{base_url}/api/records", headers=headers)
            if own_records_response.status_code == 200:
                own_data = own_records_response.json()
                if "data" in own_data:
                    if "data_records" in own_data["data"] and isinstance(own_data["data"]["data_records"], list):
                        records.extend(own_data["data"]["data_records"])
                    if "alpha_records" in own_data["data"] and isinstance(own_data["data"]["alpha_records"], list):
                        records.extend(own_data["data"]["alpha_records"])
            logger.info(f"Found {len(records)} records to monitor")
            return records
        else:
            logger.error(f"Failed to fetch subscriptions: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error fetching subscribed records: {e}")
        return []

def get_user_wallet_address(base_url: str, api_key: str) -> str:
    try:
        headers = {"X-API-Key": api_key}
        response = requests.get(f"{base_url}/api/users/me", headers=headers)
        if response.status_code != 200:
            response = requests.get(f"{base_url}/api/protected-api-key", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and "user" in data["data"] and "wallet_address" in data["data"]["user"]:
                return data["data"]["user"]["wallet_address"]
            elif "wallet_address" in data:
                return data["wallet_address"]
            elif "data" in data and "wallet_address" in data["data"]:
                return data["data"]["wallet_address"]
        logger.warning("Could not retrieve wallet address, using default")
        return "0x" + api_key[:40]
    except Exception as e:
        logger.error(f"Error getting wallet address: {e}")
        return "0x" + api_key[:40]
