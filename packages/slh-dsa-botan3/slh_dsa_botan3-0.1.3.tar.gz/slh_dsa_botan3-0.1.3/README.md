
# FIPS-205 SLH-DSA bindings for botan3

The [botan](https://botan.randombit.net/) library
implements NIST's
[FIP-205](https://csrc.nist.gov/pubs/fips/205/final)
[SLH-DSA](https://botan.randombit.net/doxygen/group__sphincsplus__common.html)
signature and exposes `botan3`
[python bindings](https://botan.randombit.net/handbook/api_ref/python.html).

This module wraps these bindings to help usage of SLH-DSA in python:

```py
from slh_dsa_botan3 import slh_params

slh_dsa = slh_params.from_string('SLH-DSA-SHAKE-128s')

private_key = slh_dsa.generate_keypair()
public_key = private_key.get_public_key()

message = "hello world"
signature = private_key.sign(message)

assert public_key.verify(message, signature)
```

See [documentation](https://archive-rip.gitlab.io/slh_dsa_botan3/) for more
examples.

## Quick setup

You need a working `botan3` installation:

```sh
% botan --version
3.7.1
```

You may need to install `python3-botan` depending on your distribution:

```sh
% python -c 'import botan3; print(botan3.version_string())'
Botan 3.7.1 (release, dated 20250205, revision git:09cc7f97ceb828c19461b2a63f820d3226bb921b, distribution unspecified)
```

It is recommended to work in a virtual environment as follows:

```sh
% python3 -m venv --system-site-packages botan3 venv
% source venv/bin/activate
```

You can then install `slh_dsa_botan3` using the following:

```sh
% pip install slh_dsa_botan3
```

Note that this is experimental and may include mistakes, use with care!

## Tests & Validation

This module has optional dependencies required for testing and development:

```sh
% pip install -r requirements-dev.txt
```

You can use the following recipe to run all tests:

```sh
make tests
```

This will in sequence:
 - run `./tests/sync-ACVP-Server.sh` to populate `./tests/ACVP-Server`
   with [ACVP test vectors](https://pages.nist.gov/ACVP/)
 - run `./tests/liboqs/liboqs-python.sh` to build and install
   [liboqs](https://openquantumsafe.org/liboqs/) in `./venv/share/liboqs`
 - run all tests, including:
    - basic unit tests
    - few fixed test vectors
    - all external ACVP test vectors (without prehash)
    - basic interoperability with `liboqs` Sphincs3.1+ implementation

Note that this module offer no support for SLH-DSA *pre-hashing* nor
context binding.
