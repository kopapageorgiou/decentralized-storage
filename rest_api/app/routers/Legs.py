import os
from fastapi import APIRouter, Request
from pydantic import BaseModel
import logging

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)

class Leg(BaseModel):
    device_id: int
    leg: list[str]

@router.post('/insertLeg')
def insert_leg(leg: Leg, request: Request):
    try:
        request.app.state.gate_stops[leg.device_id] = leg.leg
        return {"info": "Leg has been imported successfully", "code": 1}
    except Exception as e:
        return {"info": e, "code": 0}