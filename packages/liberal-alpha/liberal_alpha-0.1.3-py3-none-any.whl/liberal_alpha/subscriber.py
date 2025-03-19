# liberal_alpha/subscriber.py
import asyncio
import json
import websockets
import logging
import time
from pathlib import Path
from .crypto import decrypt_alpha_message, get_wallet_address
from .utils import fetch_subscribed_records, get_user_wallet_address

logger = logging.getLogger(__name__)

async def subscribe_to_websocket(url: str, wallet_address: str, record_id: int, record_name: str, 
                                 private_key: str = None, max_reconnect_attempts: int = 5):
    reconnect_attempts = 0
    output_dir = Path(f"decrypted_data/record_{record_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    while reconnect_attempts < max_reconnect_attempts:
        try:
            logger.info(f"Connecting to WebSocket for record {record_id} ({record_name}) at {url}")
            async with websockets.connect(url) as websocket:
                connection_request = {"wallet_address": wallet_address, "record_id": record_id}
                logger.info(f"Sending connection request for record {record_id}: {json.dumps(connection_request)}")
                await websocket.send(json.dumps(connection_request))
                
                while True:
                    message = await websocket.recv()
                    try:
                        parsed_message = json.loads(message)
                        logger.info(f"Record {record_id} ({record_name}) received: {json.dumps(parsed_message, indent=2)}")
                        
                        # 可根据需要修改判断条件，例如处理 "data" 和 "broadcast"
                        if parsed_message.get("status") in ["data"]:
                            logger.info(f"Record {record_id} ({record_name}): Received encrypted data!")
                            if private_key and "data" in parsed_message:
                                encrypted_data = parsed_message["data"]
                                logger.info("Attempting to decrypt data with private key...")
                                decrypted_data = decrypt_alpha_message(private_key, encrypted_data)
                                if decrypted_data:
                                    logger.info("Successfully decrypted data:")
                                    entry_id = encrypted_data.get("entry_id", "unknown")
                                    if isinstance(decrypted_data, dict):
                                        print("\n" + "="*50)
                                        print(f"DECRYPTED DATA (Entry ID: {entry_id}):")
                                        print(json.dumps(decrypted_data, indent=2))
                                        print("="*50)
                                    else:
                                        # 如果需要写入文件，可以在这里打开文件写入
                                        print("\n" + "="*50)
                                        print(f"DECRYPTED DATA (Entry ID: {entry_id}):")
                                        print(decrypted_data)
                                        print("="*50)
                                else:
                                    logger.warning("Failed to decrypt data - either not encrypted for this wallet or invalid encryption")
                            elif "data" in parsed_message:
                                logger.info(f"Data content (encrypted): {json.dumps(parsed_message['data'], indent=2)}")
                                logger.info("No private key provided for decryption")
                    except json.JSONDecodeError:
                        logger.warning(f"Record {record_id}: Received non-JSON message: {message}")
                        
        except websockets.exceptions.ConnectionClosed as e:
            reconnect_attempts += 1
            wait_time = reconnect_attempts * 2
            logger.error(f"WebSocket connection for record {record_id} closed: {e}. Reconnecting in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except Exception as e:
            reconnect_attempts += 1
            wait_time = reconnect_attempts * 2
            logger.error(f"Error in WebSocket connection for record {record_id}: {e}. Reconnecting in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    
    logger.error(f"Failed to maintain WebSocket connection for record {record_id} after {max_reconnect_attempts} attempts.")
    
async def main_async(api_key: str, base_url: str, wallet_address: str = None, private_key: str = None, record_id: int = None, max_reconnect: int = 5):
    if private_key:
        logger.info("Private key provided, will attempt to decrypt messages")
        wallet_address = get_wallet_address(private_key)
        logger.info(f"Decryption wallet address: {wallet_address}")
    if record_id:
        logger.info(f"Monitoring only record ID: {record_id}")
        records = [{"id": record_id, "name": f"Record {record_id}"}]
    else:
        records = fetch_subscribed_records(base_url, api_key)
        if not records:
            logger.error("No records found to monitor. Exiting.")
            return
    if not wallet_address:
        wallet_address = get_user_wallet_address(base_url, api_key)
        logger.info(f"Using wallet address: {wallet_address}")
        
    ws_base_url = base_url.replace("http://", "ws://").replace("https://", "wss://")
    ws_url = f"{ws_base_url}/ws/data"
    
    tasks = []
    for record in records:
        rid = record.get("id")
        rname = record.get("name", "Unknown")
        if rid:
            logger.info(f"Setting up monitoring for record {rid} ({rname})")
            task = asyncio.create_task(subscribe_to_websocket(ws_url, wallet_address, rid, rname, private_key, max_reconnect))
            tasks.append(task)
    if tasks:
        logger.info(f"Monitoring {len(tasks)} records...")
        await asyncio.gather(*tasks)
    else:
        logger.error("No valid records found to monitor. Exiting.")
