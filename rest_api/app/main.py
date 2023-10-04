from fastapi import FastAPI
from cassandra.cluster import Cluster
from routers import Devices, Measurements, GenerateKey, Customers, Legs, Commitment
from utils.kzg_utils.KZG10 import *
from fastapi_cprofile.profiler import CProfileMiddleware
import os, sys
import logging
from Orbitdbapi import OrbitdbAPI

for handler, logger in logging.Logger.manager.loggerDict.items():
    if handler.startswith("cassandra") and not isinstance(logger, logging.PlaceHolder):
        logger.setLevel(logging.ERROR)  # or CRITICAL
        logger.propagate = False
logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

app = FastAPI() 

app.state.gate_stops = {}
app.state.gate_keys = {}
app.state.encrypted_symmetric_keys = {}
app.state.kzg = KZG10()
app.include_router(Customers.router)
app.include_router(Devices.router)
app.include_router(Measurements.router)
app.include_router(GenerateKey.router)
app.include_router(Legs.router)
app.include_router(Commitment.router)