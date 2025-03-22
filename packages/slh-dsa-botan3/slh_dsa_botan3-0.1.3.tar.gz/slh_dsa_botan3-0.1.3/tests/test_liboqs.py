import os
import unittest

from slh_dsa_botan3 import slh_params, slh_private, slh_public

#
# import our stuff
#


slh_shake_128s = slh_params(base_hash="SHAKE", target_size=128, target_flavor="small")

#
# import oqs stuff if available
#

if os.getenv("OQS_INSTALL_PATH") is not None:  # install oqs first!
    try:
        import oqs
    except ImportError:
        pass

oqs_sig_alg = "SPHINCS+-SHAKE-128s-simple"
try:
    oqs_sig = oqs.Signature(oqs_sig_alg)
except BaseException:
    oqs_sig = None

#
# emulate external SLH NIST API as liboqs only exposes internal stuff rn
#


def _external_slh(message):
    # no prehash (0x00) | context length (0x00) | ctx == b'' | msg
    return b"\x00\x00" + message


#
# test it :)
#


class TestOQSCompat(unittest.TestCase):

    def setUp(self):
        if oqs_sig is None:
            self.skipTest("liboqs-python not installed")

    def test_genkey_compat(self):
        public_bytes = oqs_sig.generate_keypair()
        private_bytes = oqs_sig.export_secret_key()

        private_key = slh_private(private_bytes=private_bytes, params=slh_shake_128s)
        self.assertEqual(private_key.get_public_bytes(), public_bytes)

        public_key = slh_public(public_bytes=public_bytes, params=slh_shake_128s)

        message = "hello world"
        signature = private_key.sign(message)
        self.assertTrue(public_key.verify(message, signature))

    def test_sign_compat(self):

        private_key = slh_shake_128s.generate_keypair()
        private_bytes = private_key._private_bytes

        oqs_sig = oqs.Signature(oqs_sig_alg, secret_key=private_bytes)

        message = b"hello world"
        signature = oqs_sig.sign(_external_slh(message))

        public_key = private_key.get_public_key()
        self.assertTrue(public_key.verify(message, signature))

        # -- no way to get public bytes from oqs.Signature object? :o
        # public_bytes = private_key.get_public_bytes()

    def test_verify_compat(self):

        private_key = slh_shake_128s.generate_keypair()
        public_key = private_key.get_public_key()

        message = b"hello world"
        signature = private_key.sign(message)

        public_bytes = public_key.get_public_bytes()
        self.assertTrue(oqs_sig.verify(_external_slh(message), signature, public_bytes))
