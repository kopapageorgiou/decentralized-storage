import os,logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from cassandra.cluster import Cluster
from smartContractInteraction import SmartContract
from typing import Tuple

smart_contract = SmartContract(f"http://{os.environ['GANACHE_HOST']}:8545")
router = APIRouter()

class Commitment(BaseModel):
    date: str
    commit: Tuple[int, int]

@router.post('/insertCommitment')
def insert_commitment(commitment: Commitment):
    try:
        receipt = smart_contract.add_commitment(commitment.date, commitment.commit)
        #logging.error(f"Receipt: {receipt['transactionHash'].hex()}, {receipt['status']}")
        return {"transactionHash": receipt['transactionHash'].hex(), "code": receipt['status']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
    
@router.get('/getCommitment/{date}')
def get_commitment(date: str):
    try:
        commitment = smart_contract.receive_commitment(date)
        return {"x": commitment[0], "y": commitment[1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)