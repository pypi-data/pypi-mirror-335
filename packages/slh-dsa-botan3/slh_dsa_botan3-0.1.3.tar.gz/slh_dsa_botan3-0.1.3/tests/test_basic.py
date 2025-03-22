import base64
import json
import sys
import unittest

from slh_dsa_botan3 import slh_params, slh_private, slh_public

# show more progress in unittest output
_dot_progress = 0


def _show_progress():
    global _dot_progress

    _dot_progress += 1
    print("|\\+/"[_dot_progress % 4], end="\b", flush=True, file=sys.stderr)


# faster tests against PBKDF export
_original_export = slh_private.export_private_to_encrypted_pem
slh_private.export_private_to_encrypted_pem = lambda *kargs, **kwargs: _original_export(
    *kargs, **kwargs, pbkdf_msec=1
)


class TestBasicUsage(unittest.TestCase):

    def test_basic(self):

        slh_sha2_128f = slh_params(
            base_hash="SHA2", target_size=128, target_flavor="fast"
        )

        private_key = slh_sha2_128f.generate_keypair()
        public_key = private_key.get_public_key()

        message = "hello world"
        signature = private_key.sign(message)
        self.assertTrue(public_key.verify(message, signature))

    def test_export(self):

        slh_shake_128s = slh_params()
        privkey = slh_shake_128s.generate_keypair()

        passphrase = "this is a weak passphrase!"
        exported_private, exported_variant = privkey.export_private_to_encrypted_pem(
            passphrase=passphrase
        )

        exported_public, exported_pubvariant = privkey.public_key.export_to_plain_pem()
        self.assertEqual(exported_variant, exported_pubvariant)

        _show_progress()

        exported_variant = slh_shake_128s.variant_name

        imported_private = slh_private.import_from_encrypted_pem(
            exported_private, exported_variant, passphrase=passphrase
        )
        imported_public = slh_public.import_from_plain_pem(
            exported_public, exported_variant
        )

        _show_progress()

        message = b"this is an example of speech"
        signature = imported_private.sign(message)
        self.assertTrue(imported_public.verify(message, signature))

        self.assertEqual(privkey.get_public_bytes(), imported_public.get_public_bytes())

        _show_progress()

        imported_other = slh_private.import_from_encrypted_pem(
            exported_private, exported_variant, passphrase=passphrase, force_botan3=True
        )

        self.assertEqual(imported_private._private_bytes, imported_other._private_bytes)

    def test_vectors(self):

        # test vectors taken from ACPV-Server FIPS 205 validation
        with open("tests/vectors.jsonl", "r") as f:
            for line in f.readlines():
                vector = json.loads(line)

                _show_progress()

                variant = vector["variant"]
                message = base64.b64decode(vector["message"])
                privkey = base64.b64decode(vector["privkey"])
                signature = base64.b64decode(vector["signature"])

                private = slh_private(private_bytes=privkey, params=variant)
                output = private.sign(message, deterministic=True)

                self.assertEqual(output, signature)
                self.assertTrue(private.public_key.verify(message, output))
