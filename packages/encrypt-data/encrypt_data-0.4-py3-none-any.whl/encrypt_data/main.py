from cryptography.fernet import Fernet
import rsa
import json

class Encrypt:
    def __init__(self, public_key=''):
        self.__symmetric_key = Fernet.generate_key() # Generation of random symmetric key
        self.__cypher = Fernet(self.__symmetric_key) # Used to encrypt the text
        self.__public_key = rsa.PublicKey.load_pkcs1(public_key)
        self.__symmetric_key_encryption = rsa.encrypt(self.__symmetric_key, self.__public_key) # Encrypting the symmetric key
        self.hashing = Hashing()

    def encrypt_data(self, data_to_be_encrypted: dict = {}):
        """
        Provide the dictionary to be encrypted. This function will encrypt the dictionary and return a dictionary with the values as status, detail, encrypted_key, encrypted_data.
        Further more you can use the encrypted_key & Encrypted_data for your processing.

        dict = {'payload': {'name': 'john'}} -> The data would be encrypted is {'name': 'john'}

        If data provided is a Dict then also the hash value is encrypted else if Str is given then it is converted to a dict and then the hash value is given in it.
        """
        response = {}
        try:
            if data_to_be_encrypted:
                # print('Encryption of the data to be done over here.')

                if not isinstance(data_to_be_encrypted, dict):
                    data_to_be_encrypted = {'payload': {'data': data_to_be_encrypted}}
                else:
                    if 'payload' in data_to_be_encrypted.keys() and not isinstance(data_to_be_encrypted['payload'], dict):
                        data_to_be_encrypted['payload'] = {'data': data_to_be_encrypted['payload']}

                print(f"Data before hashing is: {data_to_be_encrypted}")
                hashed_data = self.hashing.hash_data(json.dumps(data_to_be_encrypted['payload']).encode('utf-8'))
                if hashed_data['status']:
                    print()
                    print(f"Hash data is: {hashed_data['detail']}")
                    print()
                    data_to_be_encrypted['payload']['hash_value'] = str(hashed_data['detail'])
                    data_to_be_encrypted['payload'] = self.__cypher.encrypt(json.dumps(data_to_be_encrypted['payload']).encode('utf-8'))
                    data_to_be_encrypted['encrypted_key'] = self.__symmetric_key_encryption
                    response['status'] = True
                    response['detail'] = 'Encryption Successfull'
                    response['encrypted_data'] = data_to_be_encrypted
                else:
                    response['status'] = False
                    response['detail'] = hashed_data['detail']
            else:
                response['status'] = False
                response['detail'] = 'Data not provided for Encryption.'
        except Exception as e:
            print(f"Exception caused in {self.encrypt_data.__name__} function: {e}")
            response['status'] = False
            response['detail'] = f"Exception caused in {self.encrypt_data.__name__} function: {e}"
        finally:
            return response
        
class Decrypt:
    def __init__(self, private_key='', data_to_be_decrypted: dict = {}):
        self.__private_key = rsa.PrivateKey.load_pkcs1(private_key)
        self.__data_to_be_decrypted = data_to_be_decrypted
        self.__symmetric_key_decryption = rsa.decrypt(self.__data_to_be_decrypted['encrypted_key'], self.__private_key) # Decrypting the symmetric key
        del self.__data_to_be_decrypted['encrypted_key']
        self.__cypher = Fernet(self.__symmetric_key_decryption)
        self.hashing = Hashing()

    def decrypt_data(self):
        response = {}
        try:
            self.__data_to_be_decrypted['payload'] = eval(self.__cypher.decrypt(self.__data_to_be_decrypted['payload']).decode('utf-8'))
            hash_data = eval(self.__data_to_be_decrypted['payload']['hash_value'])
            del self.__data_to_be_decrypted['payload']['hash_value']
            print()
            print(f"Hash data is: {hash_data}")
            print()

            hashed_data = self.hashing.hash_data(json.dumps(self.__data_to_be_decrypted['payload']).encode('utf-8'))
            print(type(hash_data), type(hashed_data['detail']))

            if hashed_data['status']:
                if hashed_data['detail'] == hash_data:
                    response['status'] = True
                    response['detail'] = 'Decryption Successfull'
                    response['decrypted_data'] = self.__data_to_be_decrypted
                else:
                    response['status'] = False
                    response['detail'] = "Hash value not matched. The data has been manipulated while travelling via network."
            else:
                response['status'] = False
                response['detail'] = hashed_data['detail']

        except Exception as e:
            print(f"Exception caused in {self.decrypt_data.__name__} function: {e}")
            response['status'] = False
            response['detail'] = f"Exception caused in {self.decrypt_data.__name__} function: {e}"
        finally:
            return response
    
class Hashing:
    def __init__(self):
        self.__hashing_algo = 'SHA-512'

    def hash_data(self, data_to_hash):
        response = {}
        try:
            response['detail'] = rsa.compute_hash(data_to_hash, self.__hashing_algo)
            response['status'] = True
        except Exception as e:
            print(f"Exception caused in {self.hash_data.__name__} function: {e}")
            response['status'] = False
            response['detail'] = f"Exception caused in {self.hash_data.__name__} function: {e}"
        finally:
            return response
