import os, sys
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from cassandra.cluster import Cluster
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from datetime import datetime
import base64
import requests
import logging
parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_folder_path)
from Orbitdbapi import OrbitdbAPI
from utils.abe_api import ABEAPI
from aiocache import SimpleMemoryCache
import asyncio

cluster = Cluster([os.environ['DB_HOST']])
orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
db = orbitdb.load(dbname='shared.measurements')
cache = SimpleMemoryCache()
router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

class Measurement(BaseModel):
    order_id: str #Must be known from the caller
    device_id: int
    leg_number: int
    measurement_id: int
    measurement_value: int
    measurement_timestamp: datetime
    measurement_location: tuple[float, float]

flags = {}

@router.post('/insertMeasurement')
async def insert_measurement(measurement: Measurement, request: Request):
    try:
        session = cluster.connect('mkeyspace')
        prep = session.prepare('''INSERT INTO measurements
        (measurement_id, measurement_location, measurement_time, measurement_value, device_id, leg_number)
        VALUES (?, ?, ?, ?, ?, ?)''')
        values = [measurement.measurement_id,
                    measurement.measurement_location,
                    measurement.measurement_timestamp,
                    measurement.measurement_value,
                    measurement.device_id,
                    measurement.leg_number]

        session.execute(prep, values)
        session.shutdown()
        device_id = measurement.device_id
        
        # if device_id not in request.app.state.gate_keys: 
        #     request.app.state.gate_keys[device_id] = base64.b64encode(get_random_bytes(32)).decode('utf-8')
        #     request.app.state.encrypted_symmetric_keys[device_id] = abe_api.cp_encrypt(request.app.state.gate_stops[device_id],
        #                                                                                     request.app.state.gate_keys[device_id])
        #logging.error(request.app.state.gate_keys)
        key = request.app.state.gate_keys[device_id]

        enc_measurement_value = encrypt(key, str(measurement.measurement_value))
        enc_measurement_time = encrypt(key, str(measurement.measurement_timestamp))
        enc_measurement_location = encrypt(key, f"{str(measurement.measurement_location[0])}, {str(measurement.measurement_location[1])}")
        #logging.error(f"Users: {request.app.state.gate_stops[device_id]}")
        #enc_abe_key = abe_api.cp_encrypt(request.app.state.gate_stops[device_id], key)
        enc_abe_key = request.app.state.encrypted_symmetric_keys[device_id]
        #logging.error(f"Encrypted key: {enc_abe_key}")
        data = {
            "order_id": measurement.order_id,
            "device_id": measurement.device_id,
            "measurement_id": measurement.measurement_id,
            "enc_measurement_value": enc_measurement_value,
            "enc_measurement_time": enc_measurement_time,
            "enc_measurement_location": enc_measurement_location,
            "abe_enc_key": enc_abe_key
        }
        asyncio.create_task(db.insertMeasurementsAsync(data))
        return {"info": "Measurement has been imported successfully", "code": 1}
    except Exception as e:
        logging.debug(e) 
        raise HTTPException(status_code=500, detail=e)


def encrypt(key, value):
    key = key.encode('utf-8')
    key = base64.b64decode(key)
    cipher = AES.new(key, AES.MODE_CBC)
    #logging.debug("Encrypting data")
    return base64.b64encode(cipher.encrypt(pad(bytes(value, 'utf-8'), AES.block_size))).decode('utf-8')

# async def send_data_to_orbit(data: dict):
#     async with aiohttp.ClientSession() as session:
#         async with session.post(f"{os.environ['ORBIT_HOST']}:3000/insertMeasurements", json=data) as response:
#             return await response.json()
