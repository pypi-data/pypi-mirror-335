from hashlib import sha224, sha256, sha384, sha512, sha3_512
import logging
from pysatl import Utils


class DRBG_SHA2_512:
    """Hash DRBG with SHA2-512"""

    HASH = 'SHA-512'  # name of the hash as it is specified in NIST CAVP test 'rsp' files
    HASH_DIGEST_SIZE = 512 // 8
    SECURITY_STRENGTH = 512 // 2
    SEEDLEN = 888
    SEED_SIZE = SEEDLEN // 8
    RESEED_INTERVAL = 2**48
    MAX_REQUEST_SIZE = (2**19) // 8

    @classmethod
    def _hash(cls, data: bytes) -> bytes:
        return sha512(data).digest()

    @classmethod
    def add_mod_seedlen(cls, *args) -> bytes:
        argsi = [int.from_bytes(a, byteorder='big') for a in args]
        mask = (1 << cls.SEEDLEN) - 1
        out = sum(argsi) & mask
        return out.to_bytes(cls.SEED_SIZE, byteorder='big')

    @classmethod
    def _hash_df(cls, data, out_size) -> bytes:
        nloops = (out_size + cls.HASH_DIGEST_SIZE - 1) // cls.HASH_DIGEST_SIZE
        logging.debug(f'out_size = {out_size}, cls.HASH_DIGEST_SIZE = {cls.HASH_DIGEST_SIZE}, nloops = {nloops}')
        out_size_in_bits = (8 * out_size).to_bytes(4, byteorder='big')
        temp = bytearray()
        for i in range(1, nloops + 1):
            hin = bytearray()
            hin += i.to_bytes(1, byteorder='big')
            hin += out_size_in_bits
            hin += data
            temp += cls._hash(hin)
            logging.debug(f'temp = {Utils.hexstr(temp)}')
        return bytes(temp[:out_size])  # or [-out_size:]

    def __init__(self, *, entropy: bytes, nonce: bytes, perso_str: bytes = bytes(0)):
        """Initialize a DRBG instance."""

        if len(entropy) * 8 < self.SECURITY_STRENGTH:
            raise RuntimeError(f'entropy must have at least {self.SECURITY_STRENGTH} bits, got only {len(entropy) * 8}')
        if len(entropy) * 8 > 2**35:
            raise RuntimeError(f'entropy must be at most 2**35 bits, got {len(entropy) * 8}')
        if len(nonce) * 8 < self.SECURITY_STRENGTH // 2:
            raise RuntimeError(
                f'nonce must have at least {self.SECURITY_STRENGTH // 2} bits, got only {len(nonce) * 8}'
            )
        if len(perso_str) * 8 > 2**35:
            raise RuntimeError(f'perso_str must be at most 2**35 bits got {len(perso_str) * 8}')
        seed_material = bytearray()
        seed_material += entropy
        seed_material += nonce
        seed_material += perso_str
        self._V = self._hash_df(seed_material, self.SEED_SIZE)
        seedc = bytearray([0])
        seedc += self._V
        self._C = self._hash_df(seedc, self.SEED_SIZE)
        self._reseed_counter = 1
        logging.debug(f'C = {Utils.hexstr(self._C)}')
        logging.debug(f'V = {Utils.hexstr(self._V)}')
        logging.debug(f'reseed_counter = {self._reseed_counter}')

    def get_bytes(self, size: int, *, additional_input: bytes = bytes(0)):
        """Generate random bytes"""

        if size > self.MAX_REQUEST_SIZE:
            raise RuntimeError(f'Maximum size per request is {self.MAX_REQUEST_SIZE}, {size} bytes were requested')
        if self._reseed_counter > self.RESEED_INTERVAL:
            raise RuntimeError()
        if len(additional_input) > 0:
            win = bytearray([2])
            win += self._V
            win += additional_input
            w = self._hash(win)
            self._V = self.add_mod_seedlen(self._V, w)
            logging.debug(f'C = {Utils.hexstr(self._C)}')
            logging.debug(f'V = {Utils.hexstr(self._V)}')
            logging.debug(f'reseed_counter = {self._reseed_counter}')
        out = self._hash_gen(size)
        hin = bytearray([3])
        hin += self._V
        h = self._hash(hin)
        self._V = self.add_mod_seedlen(self._V, h, self._C, self._reseed_counter.to_bytes(32, byteorder='big'))
        self._reseed_counter += 1
        logging.debug(f'C = {Utils.hexstr(self._C)}')
        logging.debug(f'V = {Utils.hexstr(self._V)}')
        logging.debug(f'reseed_counter = {self._reseed_counter}')
        return out

    def _hash_gen(self, size) -> bytes:
        nloops = (size + self.HASH_DIGEST_SIZE - 1) // self.HASH_DIGEST_SIZE
        data = self._V
        w = bytearray()
        for _i in range(1, nloops + 1):
            w += self._hash(data)
            data = self.add_mod_seedlen(data, bytearray([1]))
        return bytes(w[:size])  # or [-size:]


class DRBG_SHA2_256(DRBG_SHA2_512):
    """Hash DRBG with SHA2-256"""

    HASH = 'SHA-256'  # name of the hash as it is specified in NIST CAVP test 'rsp' files
    HASH_DIGEST_SIZE = 256 // 8
    SECURITY_STRENGTH = 256 // 2
    SEEDLEN = 440
    SEED_SIZE = SEEDLEN // 8

    @classmethod
    def _hash(cls, data: bytes) -> bytes:
        return sha256(data).digest()


class DRBG_SHA2_224(DRBG_SHA2_512):
    """Hash DRBG with SHA2-224"""

    HASH = 'SHA-224'  # name of the hash as it is specified in NIST CAVP test 'rsp' files
    HASH_DIGEST_SIZE = 224 // 8
    SECURITY_STRENGTH = 224 // 2
    SEEDLEN = 440
    SEED_SIZE = SEEDLEN // 8

    @classmethod
    def _hash(cls, data: bytes) -> bytes:
        return sha224(data).digest()


class DRBG_SHA2_384(DRBG_SHA2_512):
    """Hash DRBG with SHA2-384"""

    HASH = 'SHA-384'  # name of the hash as it is specified in NIST CAVP test 'rsp' files
    HASH_DIGEST_SIZE = 384 // 8
    SECURITY_STRENGTH = 384 // 2
    SEEDLEN = 888
    SEED_SIZE = SEEDLEN // 8

    @classmethod
    def _hash(cls, data: bytes) -> bytes:
        return sha384(data).digest()


class DRBG_SHA3_512(DRBG_SHA2_512):
    """Hash DRBG with SHA3-512"""

    @classmethod
    def _hash(cls, data: bytes) -> bytes:
        return sha3_512(data).digest()
