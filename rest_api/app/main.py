from fastapi import FastAPI
from cassandra.cluster import Cluster
from routers import Devices, Measurements, GenerateKey, Customers, Legs, Commitment
from fastapi_cprofile.profiler import CProfileMiddleware
import os, sys
import logging
from Orbitdbapi import OrbitdbAPI
#import pip_system_certs.wrapt_requests
#import ipfshttpclient as ipfs
from utils.vault_abe import Vault
cluster = Cluster([os.environ['DB_HOST']])

app = FastAPI()
#app.add_middleware(CProfileMiddleware, enable=True, print_each_request=True, strip_dirs=True, sort_by='cumulative', server_app=app, filename='/tmp/profiler/output.pstats')
app.state.gate_stops = {}
#app.state.gate_stops[14999] = ["user1", "user2", "user3", "user4", "user5"]
#logging.debug(f"Init stations: {app.state.gate_stops[14999]}")
#app.state.vault = Vault(f"https://{os.environ['VAULT_HOST']}:8200")
app.include_router(Customers.router)
# app.include_router(Gateways.router)
app.include_router(Devices.router)
app.include_router(Measurements.router)
app.include_router(GenerateKey.router)
app.include_router(Legs.router)
app.include_router(Commitment.router)
app.state.gate_keys = {}
# @app.post('/test')
# def hello():
#     try:
#         session = cluster.connect('mkeyspace')
#         query= '''SELECT * FROM clients'''
#         rows = session.execute(query=query)
#         return{"values from clients table": [row for row in rows]}
#     except Exception as e:
#         return {"exception": e}


# @app.post('/testOrbitdb')
# def hello():
#     try:
#         print(os.environ['ORBIT_HOST'], file=sys.stderr)
#         orbitdb = OrbitdbAPI(orbithost=os.environ['ORBIT_HOST'], port=3000)
#         db = orbitdb.load(dbname='test-base1')
#         print(db, file=sys.stderr)
#         res = db.insert(data={"key": 1, "name": "testName"})
#         print(res, file=sys.stderr)
#         res = db.query(query={"attribute": "name", "operator": "eq", "value": "testName"})
#         print(res, file=sys.stderr)
#         res = db.getAll()
#         print(res, file=sys.stderr)
#         #client = OrbitDbAPI(base_url=f"https://{os.environ['ORBIT_HOST']}:3000",timeout=60)
#         #print(res.json(), file=sys.stderr)
        
#         # with open('/etc/ssl/certs/X509Certificate.pem', 'rb') as infile:
#         #     customca = infile.read()
#         # with open(cafile, 'ab') as outfile:
#         #     outfile.write(b'\n')
#         #     outfile.write(customca)
#          #print(db, file=sys.stderr)
#         return{"Database": db}
#     except Exception as e:
#         print(e.args, file=sys.stderr)
#         return {"exception": e}