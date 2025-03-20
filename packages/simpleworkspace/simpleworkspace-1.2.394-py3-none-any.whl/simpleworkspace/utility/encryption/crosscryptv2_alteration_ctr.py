from base64 import b64decode as _b64decode, b64encode as _b64encode
from cryptography.hazmat.primitives import hashes as _hashes
from cryptography.hazmat.primitives.ciphers import CipherContext as _CipherContext, Cipher as _Cipher, algorithms as _algorithms, modes as _modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from io import BufferedIOBase as _BufferedIOBase
from simpleworkspace.types.byte import ByteEnum as _ByteEnum
import abc as _abc, os as _os


class _CipherStream_Base(_abc.ABC):
    def __init__(self, headers:'CrossCryptV2_Alteration_CTR.Headers', encryption_key:bytes):
        if not isinstance(encryption_key, bytes):
            raise TypeError("Bad key: wrong datatype")
        self.headers = headers
        self._internalCipherStream = self._Factory_CipherStream(encryption_key)
        self.Update = self._internalCipherStream.update
        self.Finalize = self._internalCipherStream.finalize

    @_abc.abstractmethod
    def _Factory_CipherStream(self, encryption_key:bytes) -> _CipherContext: ...
        
    
class _CipherStream_Encryptor(_CipherStream_Base):
    def _Factory_CipherStream(self, encryption_key:bytes):
        return _Cipher(_algorithms.AES(encryption_key), _modes.CTR(self.headers.nonce), backend=default_backend()).encryptor()

class _CipherStream_Decryptor(_CipherStream_Base):
    def _Factory_CipherStream(self, encryption_key:bytes):
        return _Cipher(_algorithms.AES(encryption_key), _modes.CTR(self.headers.nonce), backend=default_backend()).encryptor()


class CrossCryptV2_Alteration_CTR:
    # Format: schema[16] + CipherNonce[16] + Cipher...
    #   -schema: reserved space

    DEF_AES_KEY_LENGTH = 32
    DEF_PASSWORD_HASH_ITER = 100000

    class Headers:
        class _Schema:
            '''reserved usage for future'''
            DEF_LENGTH = 16
            def ParseBytes(self, schema:bytes):
                return
            def ToBytes(self):
                return bytes([0]*self.DEF_LENGTH)

        DEF_NONCE_LENGTH = 16
        DEF_LENGTH = _Schema.DEF_LENGTH + DEF_NONCE_LENGTH

        def __init__(self):
            self.schema = self._Schema()
            self.nonce:bytes = None

        def ParseBytes(self, headers:bytes):
            self.schema.ParseBytes(headers[0 : self._Schema.DEF_LENGTH])
            self.nonce = headers[self._Schema.DEF_LENGTH : self.DEF_LENGTH]

        def ToBytes(self):
            if(self.nonce is None):
                raise Exception("Headers cannot be constructed, missing nonce...")
            return self.schema.ToBytes() + self.nonce

    def __init__(self, password:str) -> None:
        self._password = password
    
    def GetEncryptor(self):
        headers = self.Headers()
        headers.nonce = self._GenerateNonce()
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
        return encryptor.headers.ToBytes() + encryptor.Update(plainBytes) + encryptor.Finalize()
    
    def DecryptBytes(self, cipherBytes:bytes):
        headers = self.Headers()
        headers.ParseBytes(cipherBytes[:self.Headers.DEF_LENGTH])
        cipherBytes = cipherBytes[self.Headers.DEF_LENGTH:]
        decryptor = self.GetDecryptor(headers)

        return decryptor.Update(cipherBytes) + decryptor.Finalize()
    
    def EncryptStream(self, inputStream:_BufferedIOBase, outputStream:_BufferedIOBase):
        readSize = 1 * _ByteEnum.MegaByte.value
        encryptor = self.GetEncryptor()
        outputStream.write(encryptor.headers.ToBytes())
        while(True):
            data = inputStream.read(readSize)
            if not data:
                break
            outputStream.write(encryptor.Update(data))
        
        outputStream.write(encryptor.Finalize())
        outputStream.flush()

    def DecryptStream(self, inputStream:_BufferedIOBase, outputStream:_BufferedIOBase):
        readSize = 1 * _ByteEnum.MegaByte.value

        headers = self.Headers()
        headers.ParseBytes(inputStream.read(self.Headers.DEF_LENGTH))
        decryptor = self.GetDecryptor(headers)

        while(True):
            data = inputStream.read(readSize)
            if not data:
                break
            outputStream.write(decryptor.Update(data))
        
        outputStream.write(decryptor.Finalize())
        outputStream.flush()
        
    def _GetDerivedKey_ForEncryption(self):
        '''used for aes-ctr'''
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

    def _GenerateNonce(self):
        '''
        We have a dedicated Nonce generator, with reasoning that its crucial that nonce's
        needs to be random. In the case of a bad PRNG implementation, we want to throw an error
        to not allow proceding with encryption
        '''
        nonce = _os.urandom(CrossCryptV2_Alteration_CTR.Headers.DEF_NONCE_LENGTH)
        if not isinstance(nonce, bytes):
            raise TypeError("Bad Nonce: wrong datatype")
        if len(nonce) != CrossCryptV2_Alteration_CTR.Headers.DEF_NONCE_LENGTH:
            raise ValueError("Bad Nonce: wrong length")
        if all(x == nonce[0] for x in nonce):
            raise ValueError("Bad Nonce: bad PRNG implementation, all bytes are same")
        return nonce
    