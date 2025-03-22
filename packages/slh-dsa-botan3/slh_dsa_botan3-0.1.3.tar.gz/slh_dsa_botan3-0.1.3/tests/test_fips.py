import json
import os
import random
import unittest

from slh_dsa_botan3 import SLHUnsupported, slh_params, slh_private, slh_public
from tests.test_basic import _show_progress

# FIPS 205 vectors
fips_path = "./tests/ACVP-Server/gen-val/json-files/"


class TestFIPS205Vectors(unittest.TestCase):

    def test_keygen(self):
        """test only private key signatures and public key generation"""

        try:
            with open(
                os.path.join(fips_path, "SLH-DSA-keyGen-FIPS205", "prompt.json"), "r"
            ) as f:
                all_prompts = json.load(f)
            with open(
                os.path.join(
                    fips_path, "SLH-DSA-keyGen-FIPS205", "expectedResults.json"
                ),
                "r",
            ) as f:
                all_results = json.load(f)
        except FileNotFoundError:
            self.skipTest("SLH-DSA-keyGen-FIPS205 unavailable")

        # for all parameters set
        for prompts, results in zip(
            all_prompts["testGroups"], all_results["testGroups"]
        ):
            assert prompts["tgId"] == results["tgId"]
            variant_name = prompts["parameterSet"]

            # take only 3 from each group
            skpk_pairs = list(results["tests"])
            random.shuffle(skpk_pairs)
            skpk_pairs = skpk_pairs[:5]

            for idx, skpk in enumerate(skpk_pairs):
                first = bool(idx == 0)
                sk = bytes.fromhex(skpk["sk"])
                pk = bytes.fromhex(skpk["pk"])

                _show_progress()

                # check_key (with signature) only for first candidate
                privkey = slh_private(
                    private_bytes=sk, params=variant_name, check_key=first
                )
                self.assertEqual(privkey.get_public_bytes(), pk)

    def test_siggen(self):

        try:
            with open(
                os.path.join(fips_path, "SLH-DSA-sigGen-FIPS205", "prompt.json"), "r"
            ) as f:
                all_prompts = json.load(f)
            with open(
                os.path.join(
                    fips_path, "SLH-DSA-sigGen-FIPS205", "expectedResults.json"
                ),
                "r",
            ) as f:
                all_results = json.load(f)
        except FileNotFoundError:
            self.skipTest("SLH-DSA-sigGen-FIPS205 unavailable")

        # for all parameters set
        for prompts, results in zip(
            all_prompts["testGroups"], all_results["testGroups"]
        ):
            assert prompts["tgId"] == results["tgId"]

            variant_name = prompts["parameterSet"]

            # test only for deterministic (easier)
            deterministic = prompts.get("deterministic", False)
            if deterministic is not True:
                continue

            # don't test for internal (botan don't expose that)
            if prompts.get("signatureInterface", "external") == "internal":
                continue

            for prompt, result in zip(prompts["tests"], results["tests"]):
                assert prompt["tcId"] == result["tcId"]

                _show_progress()

                # skip if context provided (no support)
                if prompt.get("context", ""):
                    continue

                params = slh_params.from_string(variant_name)
                prehash = prompt.get("hashAlg", None)

                # sadly no botan prehash yet :/
                try:
                    params = params.with_prehash(prehash)
                except SLHUnsupported as e:
                    continue

                message = bytes.fromhex(prompt.get("message"))

                sk = bytes.fromhex(prompt.get("sk", ""))
                privkey = slh_private(private_bytes=sk, params=params, check_key=False)
                signature = privkey.sign(message, deterministic=True)

                reference = bytes.fromhex(result.get("signature", ""))
                self.assertEqual(reference, signature)

    def test_sigver(self):

        try:
            with open(
                os.path.join(fips_path, "SLH-DSA-sigVer-FIPS205", "prompt.json"), "r"
            ) as f:
                all_prompts = json.load(f)
            with open(
                os.path.join(
                    fips_path, "SLH-DSA-sigVer-FIPS205", "expectedResults.json"
                ),
                "r",
            ) as f:
                all_results = json.load(f)
        except FileNotFoundError:
            self.skipTest("SLH-DSA-sigVer-FIPS205 unavailable")

        # for all parameters set
        for prompts, results in zip(
            all_prompts["testGroups"], all_results["testGroups"]
        ):
            assert prompts["tgId"] == results["tgId"]

            variant_name = prompts["parameterSet"]

            # don't test for internal (botan don't expose that)
            if prompts.get("signatureInterface", "external") == "internal":
                continue

            for prompt, result in zip(prompts["tests"], results["tests"]):
                assert prompt["tcId"] == result["tcId"]

                _show_progress()

                # skip if context provided (no support)
                if prompt.get("context", ""):
                    continue

                params = slh_params.from_string(variant_name)
                prehash = prompt.get("hashAlg", None)

                # sadly no botan prehash yet :/
                try:
                    params = params.with_prehash(prehash)
                except SLHUnsupported as e:
                    continue

                message = bytes.fromhex(prompt.get("message"))
                pk = bytes.fromhex(prompt.get("pk", ""))
                signature = bytes.fromhex(prompt.get("signature", ""))

                pubkey = slh_public(public_bytes=pk, params=params)
                verify = pubkey.verify(message, signature, throw=False)
                passed = result.get("testPassed", False)

                self.assertEqual(verify, passed)
