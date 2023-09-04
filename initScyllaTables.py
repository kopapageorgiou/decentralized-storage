from cassandra.cluster import Cluster

cluster = Cluster(["127.0.0.1"])
try:
    session = cluster.connect()
    query = '''CREATE KEYSPACE mKeySpace WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': 1}
    AND durable_writes = true;'''
    session.execute(query=query)
except Exception as e:
    print(e)
    session = cluster.connect("mkeyspace")
    

query = '''
    CREATE TABLE IF NOT EXISTS customers (
    customer_id int PRIMARY KEY,
    description text,
    ) WITH comment='Clients information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE IF NOT EXISTS devices (
    device_id int PRIMARY KEY,
    description text,
    customer_id int,
    ) WITH comment='Gateways information'
''' #! STEP 2
session.execute(query=query)

query = '''
    CREATE TABLE measurements (
    measurement_id int PRIMARY KEY,
    measurement_value float,
    measurement_time text,
    measurement_location text,
    device_id int,
    ) WITH comment='Measurements information'
''' #! STEP 2
session.execute(query=query)
session.shutdown()
#query= '''SELECT * FROM monkeySpecies''' #! STEP 3
#rows = 
#print([row for row in rows])