from pysatl import Utils
from hdrbg import *
import re


def check_against_nist_cavp():
    print("check against test vectors from NIST CAVP")

    from pathlib import Path

    resource_path = Path(__file__).parent
    tests_done = {}
    impl_to_test = [DRBG_SHA2_256, DRBG_SHA2_224, DRBG_SHA2_384, DRBG_SHA2_512]
    for dut in impl_to_test:
        tests_done[dut.HASH] = 0

    for tv_file in ['Hash_DRBG.rsp']:
        tv_path = resource_path.joinpath(tv_file)
        all_test_vectors = open(tv_path).read()

        pattern = r'\[(.*)\]\n\[PredictionResistance = (.*)\]\n\[EntropyInputLen = (\d+)\]\n\[NonceLen = (\d+)\]\n\[PersonalizationStringLen = (\d+)\]\n\[AdditionalInputLen = (\d+)\]\n\[ReturnedBitsLen = (\d+)]\n'
        iterator = re.finditer(pattern, all_test_vectors)
        tv = []
        for m in iterator:
            if len(tv) > 0:
                tv[-1]['end'] = m.start() - 1
            tv.append({'name': m.group(1), 'start': m.end() + 1, 'end': len(all_test_vectors)})

        all_tests = []
        for dut in impl_to_test:
            for t in tv:
                if t['name'] == dut.HASH:
                    test_vectors = all_test_vectors[t['start'] : t['end']]
                    all_tests.append({'test_vectors': test_vectors, 'dut': dut})

        pattern = r'COUNT.=.(\d+)\nEntropyInput = ([0-9a-fA-F]+)\nNonce = ([0-9a-fA-F]+)\nPersonalizationString = ([0-9a-fA-F]*)\nAdditionalInput = ([0-9a-fA-F]*)\nAdditionalInput = ([0-9a-fA-F]*)\nReturnedBits = ([0-9a-fA-F]+)\n'

        for params in all_tests:
            matches = re.findall(pattern, params['test_vectors'])
            for m in matches:
                count, entropy, nonce, perso_str, addin0, addin1, expected = m
                print(
                    f'count={count}\n\tentropy={entropy}\n\tnonce={nonce}\n\tperso_str={perso_str}\n\taddin0={addin0}\n\taddin1={addin1}'
                )

                drbg = params['dut'](entropy=Utils.ba(entropy), nonce=Utils.ba(nonce), perso_str=Utils.ba(perso_str))
                expected = Utils.ba(expected)
                print(f'\trequest {len(expected)} bytes')
                result0 = drbg.get_bytes(len(expected), additional_input=Utils.ba(addin0))
                result1 = drbg.get_bytes(len(expected), additional_input=Utils.ba(addin1))
                if expected != result1:
                    raise RuntimeError(
                        f'Result mismatch:\nResult:   {Utils.hexstr(result1)}\nExpected: {Utils.hexstr(expected)}'
                    )
                tests_done[drbg.HASH] += 1

    print(f'test done: {tests_done}')


if __name__ == '__main__':

    logformat = '%(asctime)s.%(msecs)03d %(levelname)s:\t%(message)s'
    logdatefmt = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(level='INFO', format=logformat, datefmt=logdatefmt)

    check_against_nist_cavp()
    print('All test PASS')
