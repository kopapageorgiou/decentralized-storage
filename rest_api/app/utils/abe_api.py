import requests, logging
from typing import List

# This concerns Cipher Policy ABE
class ABEAPI:
    def __init__(self, host: str) -> None:
        self.base_url = host

    def generate_cp_attribute_key(self, attributes: List[str]):
        assert len(attributes) > 0, "At least one attribute must be provided"
        attr = "|".join(attributes)
        key_gen_attribute = f"/gen_attribute_keys?scheme=cp&attribute={attr}"
        r = requests.get(self.base_url + key_gen_attribute)
        print(r.json())
        return r.json()["key"]

    def cp_encrypt(self, attributes: List[str], plaintext: str):
        assert len(attributes) > 0, "At least one attribute must be provided"
        assert len(plaintext) > 0, "Plaintext must be provided"
        policy = " or ".join(attributes)
        encrypt = f"/encrypt?scheme=cp&key={policy}&plaintext=" + plaintext
        #logging.error(self.base_url + encrypt)
        r = requests.get(self.base_url + encrypt)
        return r.json()["ciphertext"]

    def cp_decrypt(self, ciphertext: str, key_attr: str):
        decrypt = "/decrypt?scheme=cp&key=" + key_attr + "&ciphertext=" + ciphertext
        r = requests.get(self.base_url + decrypt)
        return r.json()["plaintext"]