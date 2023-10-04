import json, logging
from web3 import Web3
class SmartContract(object):
    def __init__(self, net_url):
            self.web3 = Web3(Web3.HTTPProvider(net_url, request_kwargs={'timeout':600}))

            self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
            self.accounts = self.web3.eth.accounts

            with open("./Storage.json", 'r') as f:
                info_json = json.load(f)

            abi = info_json["abi"]
            self.address = self.web3.to_checksum_address("0x2109C235c6482B6De93bFB72FB10D2788688838b")

            self.contract = self.web3.eth.contract(address=self.address, abi=abi)

    def add_commitment(self, date: str, commitment: tuple[int, int]):
        #logging.error(f"Adding commitment: {date}, {commitment}")
        txhash = self.contract.functions.store(date, commitment).transact({'from': self.accounts[0]})
        #logging.error(f"Transaction hash: {txhash}")
        receipt = self.web3.eth.wait_for_transaction_receipt(txhash)
        #logging.error(f"Receipt: {receipt}")
        return receipt
    
    def receive_commitment(self, date: str):
        return self.contract.functions.getCommitment(date).call()
    
def main():
    smart_contract = SmartContract("http://127.0.0.1:8545")
    receipt = smart_contract.add_commitment("2021-01-01", (1, 2))
    print(receipt)

if __name__ == "__main__":
    main()
