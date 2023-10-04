import os,logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
from cassandra.cluster import Cluster
from smartContractInteraction import SmartContract
from typing import Tuple
from utils.kzg_utils.KZG10 import *
smart_contract = SmartContract(f"http://{os.environ['GANACHE_HOST']}:8545")
router = APIRouter()

class Commitment(BaseModel):
    leg: str
    commit: Tuple[int, int]
    coefficients: list[int]

class ProofAttributes(BaseModel):
    leg: str #has device_id format <device_id>#<increasing_number>
    range: tuple[datetime, datetime]

cluster = Cluster([os.environ['DB_HOST']])

@router.post('/insertCommitment')
def insert_commitment(commitment: Commitment):
    try:
        receipt = smart_contract.add_commitment(commitment.leg, commitment.commit)
        session = cluster.connect('mkeyspace')
        query = '''INSERT INTO coefficients
                (device_id, leg_number, coefficients)
                VALUES (%s, %s, %s)'''
        values = (int(commitment.leg.split("#")[0]), int(commitment.leg.split("#")[1]), [str(coeff) for coeff in commitment.coefficients])
        session.execute(query=query, parameters=values)
        #logging.error(f"Receipt: {receipt['transactionHash'].hex()}, {receipt['status']}")
        return {"transactionHash": receipt['transactionHash'].hex(), "code": receipt['status']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    
@router.post('/generateProof')
def generate_commitment(proof_attr: ProofAttributes, request: Request):
    try:
        newton = request.app.state.kzg.choose_method(KZG10.NEWTON)
        commitment = smart_contract.receive_commitment(proof_attr.leg)
        commitment = (commitment[0], commitment[1])
        parts = proof_attr.leg.split("#")
        device_id = int(parts[0])
        leg_number = int(parts[1])
        session = cluster.connect('mkeyspace')
        query = '''SELECT * FROM measurements WHERE
                device_id = %s AND leg_number = %s ALLOW FILTERING'''
        total_measurements = session.execute(query, (device_id, leg_number, )).all()
        total_measurements.sort(key=lambda x: x.measurement_time)
        values = []
        indices = []
        guard = False
        logging.error(f"Measurements: {[row.measurement_time for row in total_measurements]}")
        for index, row in enumerate(total_measurements):
            if row.measurement_time == proof_attr.range[0]:
                guard = True
            if row.measurement_time == proof_attr.range[1]:
                values.append(int(row.measurement_value))
                indices.append(index)
                break
            if guard:
                values.append(int(row.measurement_value))  
                indices.append(index)    
        #logging.error(f"Indices: {indices}")
        #logging.error(f"Values: {values}")
        query = '''SELECT * FROM coefficients WHERE
                device_id = %s AND leg_number = %s ALLOW FILTERING'''
        coefficients = session.execute(query, (device_id, leg_number, )).one().coefficients
        coefficients = [newton.F(int(coeff)) for coeff in coefficients]
        #logging.error(f"coefficients: {coefficients}")
        multiproof, icoeff, zpoly = newton.generate_multi_proof(coefficients, indices, values)
        #logging.error(f"Multiproof: {multiproof}")
        return {"proof_attributes": {"proof": format_proof(multiproof), "icoeff": [int(i) for i in icoeff], "zpoly": [int(i) for i in zpoly]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)