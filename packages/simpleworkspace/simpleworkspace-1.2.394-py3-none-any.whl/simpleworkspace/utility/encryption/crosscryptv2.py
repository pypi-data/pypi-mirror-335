from base64 import b64decode as _b64decode, b64encode as _b64encode
from cryptography.hazmat.primitives import hashes as _hashes, padding as _padding
from cryptography.hazmat.primitives.ciphers import CipherContext as _CipherContext, Cipher as _Cipher, algorithms as _algorithms, modes as _modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from io import BufferedIOBase as _BufferedIOBase
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import abc as _abc, os as _os


class _CipherStream_Base(_abc.ABC):
    def __init__(self, headers:'CrossCryptV2.Headers', encryption_key:bytes):
        if not isinstance(encryption_key, bytes):
            raise TypeError("Bad key: wrong datatype")
        self.headers = headers
        self._internalCipherStream = self._Factory_CipherStream(encryption_key)
        self.Update = self._internalCipherStream.update
        self.Finalize = self._internalCipherStream.finalize

    @_abc.abstractmethod
    def _Factory_CipherStream(self, encryption_key:bytes) -> _CipherContext: ...
    
class _CipherStream_Encryptor(_CipherStream_Base):
    '''
    Stream encryptor, for AES CBC mode
    Plaintext data is automatically padded when finalize() is performed
    '''

    def _Factory_CipherStream(self, encryption_key:bytes):
        return _Cipher(_algorithms.AES(encryption_key), _modes.CBC(self.headers.iv), backend=default_backend()).encryptor()
    
 
class _CipherStream_Decryptor(_CipherStream_Base):
    '''
    Stream decryptor, for AES CBC mode
    Note: User needs to perform unpadding of last decrypted block, self.Padding.UnPad() can be used for this purpose
    '''

    def _Factory_CipherStream(self, encryption_key:bytes):
        return _Cipher(_algorithms.AES(encryption_key), _modes.CBC(self.headers.iv), backend=default_backend()).decryptor()
    


class CrossCryptV2:
    # Format: schema[16] + IV[16] + Cipher...Padding
    #   -schema: reserved space

    DEF_AES_KEY_LENGTH = 32
    DEF_AES_BLOCK_LENGTH = 16
    DEF_PASSWORD_HASH_ITER = 100000

    class Headers:
        class _Schema:
            '''reserved usage for future'''
            DEF_LENGTH = 16
            def ParseBytes(self, schema:bytes):
                return
            def ToBytes(self):
                return bytes([0]*self.DEF_LENGTH)

        DEF_IV_LENGTH = 16
        DEF_LENGTH = _Schema.DEF_LENGTH + DEF_IV_LENGTH

        def __init__(self):
            self.schema = self._Schema()
            self.iv:bytes = None

        def ParseBytes(self, headers:bytes):
            self.schema.ParseBytes(headers[0 : self._Schema.DEF_LENGTH])
            self.iv = headers[self._Schema.DEF_LENGTH : self.DEF_LENGTH]

        def ToBytes(self):
            if(self.iv is None):
                raise Exception("Headers cannot be constructed, missing IV...")
            return self.schema.ToBytes() + self.iv

    def __init__(self, password:str) -> None:
        self._password = password
    
    def GetEncryptor(self):
        headers = self.Headers()
        headers.iv = self._GenerateIV()
        return _CipherStream_Encryptor(
            headers=headers,
            encryption_key=self._GetDerivedKey_ForEncryption(),
        )
        
    def GetDecryptor(self, headers:Headers):
        return _CipherStream_Decryptor(
            headers=headers,
            encryption_key=self._GetDerivedKey_ForEncryption(),
        )

    def EncryptString(self, plainText:str):
        cipherBytes = self.EncryptBytes(plainText.encode())
        return _b64encode(cipherBytes).decode()
    
    def DecryptString(self, cipherText:str):
        plainBytes = self.DecryptBytes(_b64decode(cipherText))
        return plainBytes.decode()

    def EncryptBytes(self, plainBytes:bytes):
        encryptor = self.GetEncryptor()
        plainBytes = self.Padding.Pad(plainBytes)
        return encryptor.headers.ToBytes() + encryptor.Update(plainBytes) + encryptor.Finalize()
    
    def DecryptBytes(self, cipherBytes:bytes):
        headers = self.Headers()
        headers.ParseBytes(cipherBytes[:self.Headers.DEF_LENGTH])
        cipherBytes = cipherBytes[self.Headers.DEF_LENGTH:]
        decryptor = self.GetDecryptor(headers)

        decryptedBytes = decryptor.Update(cipherBytes) + decryptor.Finalize()
        return self.Padding.UnPad(decryptedBytes)
    
    def EncryptStream(self, inputStream:_BufferedIOBase, outputStream:_BufferedIOBase):
        readSize = 1 * _ByteEnum.MegaByte.value #must be multiple of blocklength (n%16==0)
        encryptor = self.GetEncryptor()
        outputStream.write(encryptor.headers.ToBytes())

        currentBlockFill = 0
        while(True):
            data = inputStream.read(readSize)
            if not data:
                if(currentBlockFill == 0): #incase last data was multiple of block length, add one full block of padding aswell
                    outputStream.write(encryptor.Update(self.Padding.Pad(b'')))
                break
            currentBlockFill = len(data) % self.DEF_AES_BLOCK_LENGTH 
            if(currentBlockFill != 0): # readsize is always multiple of block length, if not, then this is last block
                data = self.Padding.Pad(data)
            outputStream.write(encryptor.Update(data))
        
        outputStream.write(encryptor.Finalize())
        outputStream.flush()

    def DecryptStream(self, inputStream:_BufferedIOBase, outputStream:_BufferedIOBase):
        readSize = 1 * _ByteEnum.MegaByte.value

        headers = self.Headers()
        headers.ParseBytes(inputStream.read(self.Headers.DEF_LENGTH))
        decryptor = self.GetDecryptor(headers)

        lastDecryptedBlock = None
        while(True):
            data = inputStream.read(readSize)
            if not data:
                break
            decryptedBytes = decryptor.Update(data)
            outputStream.write(decryptedBytes)
            lastDecryptedBlock = decryptedBytes[-self.DEF_AES_BLOCK_LENGTH:] # for unpadding reference later
        
        #prepare unpadding of last block
        if(lastDecryptedBlock):
            outputStream.seek(-self.DEF_AES_BLOCK_LENGTH, _os.SEEK_END)
            outputStream.truncate()
            outputStream.write(self.Padding.UnPad(lastDecryptedBlock))
        
        outputStream.write(decryptor.Finalize())
        outputStream.flush()
        
    def _GetDerivedKey_ForEncryption(self):
        '''used for aes-cbc'''
        return self._generate_raw_PBKDF2()[0:32]

    def _GetDerivedKey_ForHMAC(self):
        '''if hmac is perfomed ontop of encryption, instead of rederiving, a prepared key is here ready for use'''
        return self._generate_raw_PBKDF2()[32:64]

    _cache_generate_raw_PBKDF2 = None
    def _generate_raw_PBKDF2(self):
        if self._cache_generate_raw_PBKDF2 is not None:
            return self._cache_generate_raw_PBKDF2

        kdf = PBKDF2HMAC(
            algorithm=_hashes.SHA512(),
            length=64,  # 64 bytes = 512 bits
            salt=bytes([0] * 16), #16 null bytes, salting password is not practical for encryption usage
            iterations=self.DEF_PASSWORD_HASH_ITER,
            backend=default_backend()
        )
        key = kdf.derive(self._password.encode())

        if(len(key) != 64):
            raise ValueError("PBKDF2 Bad output: Wrong length")
        if(all(x == key[0] for x in key)):
            raise ValueError("PBKDF2 Bad output: all bytes are same")

        self._cache_generate_raw_PBKDF2 = key
        return key

    def _GenerateIV(self):
        '''
        We have a dedicated IV/Nonce generator, with reasoning that its crucial that IV/Nonce
        needs to be random. In the case of a bad PRNG implementation, we want to throw an error
        to not allow proceding with encryption
        '''
        iv = _os.urandom(CrossCryptV2.Headers.DEF_IV_LENGTH)
        if not isinstance(iv, bytes):
            raise TypeError("Bad IV: wrong datatype")
        if len(iv) != CrossCryptV2.Headers.DEF_IV_LENGTH:
            raise ValueError("Bad IV: wrong length")
        if all(x == iv[0] for x in iv):
            raise ValueError("Bad IV: bad PRNG implementation, all bytes are same")
        return iv
    
    class Padding:
        @staticmethod
        def Pad(data:bytes):
            padder = _padding.PKCS7(CrossCryptV2.DEF_AES_BLOCK_LENGTH * 8).padder()
            return padder.update(data) + padder.finalize()
        @staticmethod
        def UnPad(data:bytes):
            padder = _padding.PKCS7(CrossCryptV2.DEF_AES_BLOCK_LENGTH * 8).unpadder()
            return padder.update(data) + padder.finalize()
        