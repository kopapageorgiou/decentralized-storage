import os, sys, logging, base64
from fastapi import APIRouter, Request
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad
from utils.abe_api import ABEAPI
abe_api = ABEAPI(f"http://{os.environ['ABE_HOST']}:12345")

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

class Device(BaseModel):
    device_id: int
    poi_id: str


@router.post('/generateKey')
def generate_key(device: Device, request: Request):
    try:
        request.app.state.gate_stops[device.device_id].remove(device.poi_id)
        #logging.debug("Stations: "+str(request.app.state.gate_stops[device.device_id]))
        request.app.state.gate_keys[device.device_id] = base64.b64encode(get_random_bytes(32)).decode('utf-8')
        request.app.state.encrypted_symmetric_keys[device.device_id] = abe_api.cp_encrypt(request.app.state.gate_stops[device.device_id],
                                                                                            request.app.state.gate_keys[device.device_id])
        #logging.debug(request.app.state.gate_keys)
        return {"info": "Key changed", "code": 1}
    except Exception as e:
        logging.debug(e)
        return {"info": e, "code": 0}