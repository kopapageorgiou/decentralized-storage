import os
from fastapi import APIRouter
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Device(BaseModel):
    device_id: int
    description: str
    customer_id: int

@router.post('/insertDevice')
def insert_client(device: Device):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO devices
        (device_id, description, customer_id)
        VALUES (%s, %s, %s)'''
        values = (device.device_id,
                  device.description,
                  device.customer_id, )
        session.execute(query=query, parameters=values)
        session.shutdown()
        return {"info": "Device has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}