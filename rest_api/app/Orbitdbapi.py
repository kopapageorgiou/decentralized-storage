import requests
import sys
import logging
import aiohttp
import logging
class OrbitdbAPI():
    def __init__(self, orbithost: str, port: int=3000) -> None:
        self.BASE_URL = f"http://{orbithost}:{str(port)}"
        #self.operators = ['eq', 'ne', 'gt', 'gte', 'lt', 'lte']
    
    def load(self, dbname: str) -> dict:
        response = requests.post(self.BASE_URL+'/loadDB', json={"name": dbname}).json()
        if response['info'] == 'Query fetched successfully' and dbname == 'shared.measurements':
            #logging.debug("here")
            return _measurementsdb(response['data'], self.BASE_URL)
        elif response['info'] == 'Query fetched successfully':
            return _dataBase(response['data'], self.BASE_URL)
        else:
            return None
    
    
    # def closeDB(self, dbname: str) -> dict:
    #     self.key = None
# ! DEPRICATED. Probably will be removed or modified
class _dataBase():
    def __init__(self, info: dict, baseURL: str) -> None:
        self.BASE_URL = baseURL
        self.info = info
        self.dbname = self.info['dbname']
        self.key = self.info['options']['indexBy']
        self.operators = ['eq', 'ne', 'gt', 'gte', 'lt', 'lte']

        #return requests.post(self.BASE_URL+'/insertMeasurements', json=attr).json()
    
    def query(self, query: dict) -> dict:
        #assert 'key' in query, "Query must contain a key attribute"
        assert 'operator' in query.keys(), "Query must contain an attribute named operator"
        assert query['operator'] in self.operators, "Operator must be one of the following: " + str(self.operators)
        assert 'attribute' in query.keys(), "Query must contain an attribute named attribute"
        assert 'value' in query.keys(), "Query must contain an attribute named value"

        return requests.post(self.BASE_URL+'/queryData', json={
            "name": self.dbname,
            "attribute": query['attribute'],
            "operator": query['operator'],
            "value": query['value']}).json()
    
    def getAll(self) -> dict:
        return requests.post(self.BASE_URL+'/getData', json={"name": self.dbname}).json()

class _measurementsdb(_dataBase):

    def insertMeasurements(self, data: dict) -> dict:
        assert 'measurement_id' in data.keys(), "Data must contain an attribute named measurement_id"
        # attr = {}
        # for key in data.keys():
        #     attr[key] = data[key]
        response = requests.post(self.BASE_URL+'/insertMeasurements', json=data)
        return response.json(), response.elapsed.total_seconds()
    
    async def insertMeasurementsAsync(self, data: dict):
        assert 'measurement_id' in data.keys(), "Data must contain an attribute named measurement_id"
        async with aiohttp.ClientSession() as session:
            async with session.post(self.BASE_URL+'/insertMeasurements', json=data) as response:
                res = await response.json()
                logging.error("SAVED SUCCESFULLY IN ORBIT")
                logging.error("Response: " + str(res))
                return res