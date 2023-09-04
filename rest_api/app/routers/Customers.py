import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from cassandra.cluster import Cluster


cluster = Cluster([os.environ['DB_HOST']])
router = APIRouter()

class Customer(BaseModel):
    customer_id: int
    description: str

@router.post('/insertCustomer')
def insert_customer(customer: Customer):
    try:
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO customers (customer_id, description) VALUES (%s, %s)'''
        session.execute(query=query, parameters=(customer.customer_id, customer.description))
        session.shutdown()
        return {"info": "Customer has been imported successfully", "code": 1}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)