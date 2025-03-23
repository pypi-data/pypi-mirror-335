****************
Python3 examples
****************

One liner
=========

.. testcode::

	from hdrbg import DRBG_SHA2_224
	print(DRBG_SHA2_224(entropy=bytes(224),nonce=bytes(112)).get_bytes(16).hex())

.. testoutput::

    8e171068da6c33b029ef73ec76085250



Dumping intermediate values
============================
This is useful to people working on their own implemention of Hash DRBG.
The verbosity is controlled by the logging level. 

- Use 'DEBUG' to dump all intermediate values

.. testsetup:: ['dump']

    import logging    
    class PrintHandler(logging.StreamHandler):
        def emit(self, record):
            msg = self.format(record)
            print(msg)
            self.flush()
    print_handler = PrintHandler()
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) 
    logger.addHandler(print_handler)
    

.. testcode:: ['dump']

    import logging  
    from hdrbg import DRBG_SHA2_224
    logging.basicConfig(format='%(message)s', level='DEBUG')
    print(DRBG_SHA2_224(entropy=bytes(224),nonce=bytes(112)).get_bytes(16).hex())

.. testoutput:: ['dump']

    out_size = 55, cls.HASH_DIGEST_SIZE = 28, nloops = 2
    temp = F6 5C DB CB 34 CC 86 02 50 8D 34 B9 48 3D B6 FC E2 D2 91 F7 D4 AF 5F 26 C6 A1 04 AB
    temp = F6 5C DB CB 34 CC 86 02 50 8D 34 B9 48 3D B6 FC E2 D2 91 F7 D4 AF 5F 26 C6 A1 04 AB A5 32 19 C2 CD 29 0D FE 58 4F F9 8D E5 59 33 05 5C 98 75 DC 9C 12 6F FB 6E A1 CB 8D
    out_size = 55, cls.HASH_DIGEST_SIZE = 28, nloops = 2
    temp = 79 15 1E 55 02 FA A7 FE E4 87 DB 06 AD 3C AA 6C BC 2A 32 C7 15 EB 33 31 13 9B D8 61
    temp = 79 15 1E 55 02 FA A7 FE E4 87 DB 06 AD 3C AA 6C BC 2A 32 C7 15 EB 33 31 13 9B D8 61 DF 73 10 3D 70 A9 DB 9D 1D C2 EB B5 0F EC D3 33 F8 2E 14 12 86 08 D1 21 6C C4 17 C2
    C = 79 15 1E 55 02 FA A7 FE E4 87 DB 06 AD 3C AA 6C BC 2A 32 C7 15 EB 33 31 13 9B D8 61 DF 73 10 3D 70 A9 DB 9D 1D C2 EB B5 0F EC D3 33 F8 2E 14 12 86 08 D1 21 6C C4 17
    V = F6 5C DB CB 34 CC 86 02 50 8D 34 B9 48 3D B6 FC E2 D2 91 F7 D4 AF 5F 26 C6 A1 04 AB A5 32 19 C2 CD 29 0D FE 58 4F F9 8D E5 59 33 05 5C 98 75 DC 9C 12 6F FB 6E A1 CB
    reseed_counter = 1
    C = 79 15 1E 55 02 FA A7 FE E4 87 DB 06 AD 3C AA 6C BC 2A 32 C7 15 EB 33 31 13 9B D8 61 DF 73 10 3D 70 A9 DB 9D 1D C2 EB B5 0F EC D3 33 F8 2E 14 12 86 08 D1 21 6C C4 17
    V = 6F 71 FA 20 37 C7 2E 01 35 15 0F BF F5 7A 61 69 9E FC C4 BE EA 9A 92 57 DA 3C DD 48 D0 38 4B 05 B2 63 D6 C9 87 CF 90 7A 7B EF 5F 55 2B 91 F5 A3 CE 00 3C E3 C7 C0 52
    reseed_counter = 2
    8e171068da6c33b029ef73ec76085250



