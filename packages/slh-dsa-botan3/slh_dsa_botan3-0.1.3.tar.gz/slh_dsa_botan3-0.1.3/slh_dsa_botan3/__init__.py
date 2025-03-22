"""This wraps `botan <https://botan.randombit.net/>`_'s implementation of
`SLH-DSA <https://csrc.nist.gov/pubs/fips/205/final>`_
leveraging the ``botan3``
`python bindings <https://botan.randombit.net/handbook/api_ref/python.html>`_.

For example:

.. code-block:: python

    from slh_dsa_botan3 import slh_params

    slh_dsa = slh_params.from_string('SLH-DSA-SHAKE-128s')

    private_key = slh_dsa.generate_keypair()
    public_key = private_key.get_public_key()

    message = "hello world"
    signature = private_key.sign(message)

    assert public_key.verify(message, signature)

This showcase the three classes provided by this module:

 - the :any:`slh_params` parameter set factory
 - the :any:`slh_private` private key wrapper
 - the :any:`slh_public` public key wrapper

This module also provide export / import functions, for example:

.. code-block:: python

    from slh_dsa_botan3 import slh_params, slh_private, slh_public

    slh_shake_128s = slh_params()
    privkey = slh_shake_128s.generate_keypair()

    passphrase = "this is a weak passphrase!"
    exported_private, exported_variant = privkey.export_private_to_encrypted_pem(
        passphrase=passphrase
    )
    imported_private = slh_private.import_from_encrypted_pem(
        exported_private, exported_variant, passphrase=passphrase
    )

    exported_public, exported_variant = privkey.public_key.export_to_plain_pem()
    imported_public = slh_public.import_from_plain_pem(
        exported_public, exported_variant
    )

    message = "this is an example of speech"
    signature = imported_private.sign(message)
    assert imported_public.verify(message, signature)

Note
----
This module patches the following ``botan3`` internals:

 - ``botan3._ctype_str()``

This may affect other modules using ``botan3`` but should be compatible with most.

Warning
-------
This module is experimental and may expose users to vulnerabilities.
"""

import hashlib
import os
import subprocess
import sys
import warnings

try:
    import Crypto.IO.PEM
    import Crypto.IO.PKCS8

    _cryptodome_enabled = True
except ImportError:
    _cryptodome_enabled = False


def _resolve_botan3_against_virtualenv():
    """:meta private: import botan3 directly from venv, if not, warn & try from system"""

    virtual_env = os.getenv("VIRTUAL_ENV")
    if not virtual_env:
        import botan3  # botan3 needs to be installed

        return botan3

    try:
        import botan3  # look for botan3 in virtualenv

        return botan3
    except ModuleNotFoundError:
        pass

    warnings.warn(  # recommended setup: python3 -m venv --system-site-packages botan3 venv
        "botan3.py missing from virtualenv, is it installed locally?"
    )

    new_path = None
    for path in sys.path:
        if virtual_env in path:
            new_path = os.path.join("/usr/", path.replace(virtual_env, ""))
            break

    if not new_path or not os.path.isdir(new_path):
        import botan3  # botan3 not found in virtualenv :(

        return botan3

    try:
        old_syspath = list(sys.path)
        sys.path.append(new_path)

        import botan3  # botan3.py not found in /usr/lib/python*/site-packages?

        return botan3
    finally:
        sys.path = old_syspath


try:
    import botan3
except ModuleNotFoundError:
    botan3 = _resolve_botan3_against_virtualenv()


def _relaxed_ctype_str(s):
    """Monkeypatch botan3._ctype_str to allow for bytes strings"""
    if s is None:
        return None
    if isinstance(s, bytes):
        return s
    assert isinstance(s, str)
    return s.encode("utf-8")


botan3._ctype_str = _relaxed_ctype_str


class SLHError(BaseException):
    """Top-level generic error for SLH-DSA botan3 module"""

    pass


class SLHUnsupported(SLHError):
    """Invalid parameters for SLH-DSA botan3 module, see :any:`slh_dsa_whitelist`"""

    pass


class SLHImportError(SLHError):
    """Unable to import input public or private key formatted as PEM"""

    pass


class SLHVerifyError(SLHError):
    """Signature could not be verified against message and public key"""

    pass


class SLHInvalidKeyError(SLHError):
    """Invalid key material, unable to properly sign payloads"""

    pass


#: All SLH-DSA parameter sets, see `botan3 source code <https://botan.randombit.net/doxygen/sp__parameters_8cpp_source.html>`_ for details.
slh_dsa_whitelist = [
    "SLH-DSA-SHA2-128s",
    "SLH-DSA-SHA2-128f",
    "SLH-DSA-SHA2-192s",
    "SLH-DSA-SHA2-192f",
    "SLH-DSA-SHA2-256s",
    "SLH-DSA-SHA2-256f",
    "SLH-DSA-SHAKE-128s",
    "SLH-DSA-SHAKE-128f",
    "SLH-DSA-SHAKE-192s",
    "SLH-DSA-SHAKE-192f",
    "SLH-DSA-SHAKE-256s",
    "SLH-DSA-SHAKE-256f",
    "Hash-SLH-DSA-SHA2-128s-with-SHA256",
    "Hash-SLH-DSA-SHA2-128f-with-SHA256",
    "Hash-SLH-DSA-SHA2-192s-with-SHA512",
    "Hash-SLH-DSA-SHA2-192f-with-SHA512",
    "Hash-SLH-DSA-SHA2-256s-with-SHA512",
    "Hash-SLH-DSA-SHA2-256f-with-SHA512",
    "Hash-SLH-DSA-SHAKE-128s-with-SHAKE128",
    "Hash-SLH-DSA-SHAKE-128f-with-SHAKE128",
    "Hash-SLH-DSA-SHAKE-192s-with-SHAKE256",
    "Hash-SLH-DSA-SHAKE-192f-with-SHAKE256",
    "Hash-SLH-DSA-SHAKE-256s-with-SHAKE256",
    "Hash-SLH-DSA-SHAKE-256f-with-SHAKE256",
]

#: All SLH-DSA OIDs, see `FIPS 205 <https://csrc.nist.gov/pubs/fips/205/final>`_ for details.
slh_dsa_oids = {
    "2.16.840.1.101.3.4.3.20": "SLH-DSA-SHA2-128s",
    "2.16.840.1.101.3.4.3.21": "SLH-DSA-SHA2-128f",
    "2.16.840.1.101.3.4.3.22": "SLH-DSA-SHA2-192s",
    "2.16.840.1.101.3.4.3.23": "SLH-DSA-SHA2-192f",
    "2.16.840.1.101.3.4.3.24": "SLH-DSA-SHA2-256s",
    "2.16.840.1.101.3.4.3.25": "SLH-DSA-SHA2-256f",
    "2.16.840.1.101.3.4.3.26": "SLH-DSA-SHAKE-128s",
    "2.16.840.1.101.3.4.3.27": "SLH-DSA-SHAKE-128f",
    "2.16.840.1.101.3.4.3.28": "SLH-DSA-SHAKE-192s",
    "2.16.840.1.101.3.4.3.29": "SLH-DSA-SHAKE-192f",
    "2.16.840.1.101.3.4.3.30": "SLH-DSA-SHAKE-256s",
    "2.16.840.1.101.3.4.3.31": "SLH-DSA-SHAKE-256f",
}


class slh_params:
    """SLH-DSA parameter set, works as :any:`slh_private` key factory.

    The expected sizes are for different configurations:

    .. code-block:: console

        target_size     target_flavor   pk size     sig size
        128             s (small)       32           7856
                        f (fast)        32          17088
        192             s (small)       48          16224
                        f (fast)        48          35664
        256             s (small)       64          29792
                        f (fast)        64          49856

    The default is ``SLH-DSA-SHAKE-128s`` FIPS-205 parameter set.


    Parameters
    ----------
    base_hash
        either "SHA2" or "SHAKE"
    target_size
        either 128, 192 or 256
    target_flavor
        either "small" (s) or "fast" (f)
    target_prehash
        either None, "SHA256", "SHA512", "SHAKE128" or "SHAKE256"

    Warning
    -------
    Support for ``target_prehash`` other than None is disabled!
    """

    algo_name = "SLH-DSA"
    supported_hash = ["SHA2", "SHAKE"]
    supported_sizes = [128, 192, 256]
    supported_flavors = dict(small="s", fast="f", s="s", f="f")
    supported_prehash = ["SHA256", "SHA512", "SHAKE128", "SHAKE256", None]
    variant_format = "{algo_name}-{base_hash}-{target_size}{target_flavor}"
    variant_prehash_format = "Hash-{variant_name}-with-{target_prehash}"

    def __init__(
        self,
        *,
        base_hash="SHAKE",
        target_size=128,
        target_flavor="small",
        target_prehash=None,
    ):

        if not isinstance(target_size, int):
            target_size = int(target_size)

        if base_hash not in self.supported_hash:
            raise SLHUnsupported(
                f"Unsupported base hash: {base_hash} not in {self.supported_hash}"
            )
        if target_size not in self.supported_sizes:
            raise SLHUnsupported(
                f"Unsupported hash size: {target_size} not in {self.supported_sizes}"
            )
        if target_flavor not in self.supported_flavors:
            raise SLHUnsupported(
                f"Unsupported s/f flavor: {target_flavor} not in {self.supported_flavors}"
            )
        if target_prehash not in self.supported_prehash:
            raise SLHUnsupported(
                f"Unsupported prehash: {target_prehash} not in {self.supported_prehash}"
            )

        self.base_hash = base_hash
        self.target_size = target_size
        self.target_flavor = self.supported_flavors[target_flavor]
        self.target_prehash = target_prehash

        #: Parameter set, formatted as ``botan3`` / FIPS-205 expects it
        self.variant_name = self.variant_format.format(
            algo_name=self.algo_name,
            base_hash=self.base_hash,
            target_size=self.target_size,
            target_flavor=self.target_flavor,
        )

        if self.target_prehash:
            self.variant_name = self.variant_prehash_format.format(
                variant_name=self.variant_name, target_prehash=self.target_prehash
            )

        if self.variant_name not in slh_dsa_whitelist:
            raise SLHUnsupported(
                f"Variant {self.variant_name} not in whitelist:\n\n"
                + "Supported variants:\n    "
                + "\n    ".join(slh_dsa_whitelist)
                + "\n"
            )

        # botan3 "Hash-<variant>-with-<prehash>" seems to be no-op
        if self.target_prehash is not None:
            raise SLHUnsupported(
                "Support for prehash has been disabled!\n\n"
                "It seems that botan3 support for SLH-DSA prehash is partial."
            )

    @classmethod
    def from_string(cls, params_string):
        """Given parameters as string, return :any:`slh_params` instance

        As formatted in FIPS-205 e.g. ``"SLH-DSA-SHA2-128s"``

        Notes
        -----
        See :any:`slh_dsa_whitelist` for full whitelist of parameters
        """
        if params_string not in slh_dsa_whitelist:
            raise SLHUnsupported(
                f"SLH-DSA string {params_string} not in whitelist:\n\n"
                + "Supported variants:\n    "
                + "\n    ".join(slh_dsa_whitelist)
                + "\n"
            )

        target_prehash = None
        if not params_string.startswith(cls.algo_name):
            assert params_string.startswith("Hash-")

            params_string = params_string[len("Hash-") :]
            algo, name, base, sizeflv, _, target_prehash = params_string.split("-")
            params_string = "-".join((algo, name, base, sizeflv))

        assert params_string.startswith(cls.algo_name)

        target_flavor = None
        if params_string.endswith("s"):
            target_flavor = "small"
        if params_string.endswith("f"):
            target_flavor = "fast"

        assert target_flavor is not None
        params_string = params_string[:-1]

        algo, name, base_hash, target_size = params_string.split("-")
        assert "-".join((algo, name)) == cls.algo_name

        return cls(
            base_hash=base_hash,
            target_size=target_size,
            target_flavor=target_flavor,
            target_prehash=target_prehash,
        )

    def with_prehash(self, target_prehash):
        """Return another :any:`slh_params` instance with ``target_prehash`` overridden

        Some canonization is done:

            - ``SHAKE-{128,256}`` becomes ``SHAKE{128,256}``
            - ``SHA2-{256,512}`` becomes ``SHA{256,512}``

        """

        if target_prehash:
            target_prehash = target_prehash.replace("SHAKE-128", "SHAKE128")
            target_prehash = target_prehash.replace("SHAKE-256", "SHAKE256")
            target_prehash = target_prehash.replace("SHA2-256", "SHA256")
            target_prehash = target_prehash.replace("SHA2-512", "SHA512")

        return slh_params(
            base_hash=self.base_hash,
            target_size=self.target_size,
            target_flavor=self.target_flavor,
            target_prehash=target_prehash,
        )

    def generate_keypair(self, *, use_passphrase=True):
        """Generate a new private key, internally using ``botan keygen`` command line.

        For now ``botan3.PrivateKey.create`` does not support SLH-DSA, we thus
        use ``botan keygen --algo=SLH-DSA --params={self.variant_name}`` with
        a ``subprocess.check_output()`` call to generate a new keypair.

        If ``use_passphrase`` is True, attempt to encrypt the child process
        output.

        Warning
        -------
        This function is only to be run in a trusted environment!
        """

        cmd_line = ["botan", "keygen"]
        cmd_line += [f"--algo={self.algo_name}"]
        cmd_line += [f"--params={self.variant_name}"]

        if use_passphrase:
            passphrase = os.urandom(16).hex()
            cmd_line += [f"--passphrase={passphrase}"]

        # seems that botan3 FFI do not accept PrivateKey.create for SLH-DSA :/
        exported = subprocess.check_output(cmd_line)
        imported = None

        try:
            imported = botan3.PrivateKey.load(exported, passphrase=passphrase)
            return slh_private(private_bytes=imported, params=self)
        finally:
            if imported:
                del imported

        return None

    def __repr__(self):
        return (
            f'<{type(self).__module__}.{type(self).__name__} for "{self.variant_name}">'
        )


class slh_private:
    """SLH-DSA private key, unsafe to use on an untrusted environments.

    Parameters
    ----------
    private_bytes
        Private key as raw bytes, or ``None`` if a new private key is to be
        generated.
    params
        A :any:`slh_params` instance or equivalent string.
    check_key
        If True, will attempt to validate that given ``private_bytes`` can
        generate a valid signature, using the given ``params`` parameter set.
    """

    def __init__(self, *, private_bytes: bytes, params: slh_params, check_key=None):
        if isinstance(params, str):
            params = slh_params.from_string(params)
        assert isinstance(params, slh_params)

        if private_bytes is None:
            check_key = check_key or False
            private_bytes = params.generate_keypair()._private_bytes

        if isinstance(private_bytes, botan3.PrivateKey):
            if private_bytes.algo_name() != params.algo_name:
                raise SLHUnsupported("botan3.PrivateKey object is not SLH-DSA?")
            private_bytes = private_bytes.to_raw()
        assert isinstance(private_bytes, bytes)

        self._params = params
        self._public_bytes = None

        self._private_bytes = private_bytes
        self._public_key = slh_public(
            public_bytes=self.get_public_bytes(), params=self._params
        )

        if check_key is None or check_key is True:
            self.check_key()

    @classmethod
    def generate_from_params(cls, *, params, check_key=False):
        """Alias for ``slh_public(private_bytes=None, params=params)``"""
        return cls(private_bytes=None, params=params, check_key=False)

    @property
    def params(self):
        """SLH-DSA parameter set used by private key"""
        return self._params

    @property
    def variant_name(self):
        """SLH-DSA parameter set string used by private key"""
        return self._params.variant_name

    def get_public_bytes(self):
        """Return public key bytes associated with this private key"""
        if self._public_bytes:
            return self._public_bytes

        private_key = botan3.PrivateKey.load_slh_dsa(
            self.variant_name, self._private_bytes
        )
        public_key = None

        try:
            public_key = private_key.get_public_key()
            self._public_bytes = public_key.to_raw()
        finally:
            del private_key
            if public_key is not None:
                del public_key

        return self._public_bytes

    def get_public_fingerprint(self, hash_name="sha256", hexdigest=True):
        hash_obj = hashlib.new(hash_name)
        hash_obj.update(self._public_bytes)
        return hash_obj.hexdigest() if hexdigest else hash_obj.digest()

    @property
    def public_key(self):
        """Alias for :any:`slh_private.get_public_key()`"""
        return self._public_key

    def get_public_key(self):
        """Return public key as a :any:`slh_public` instance"""
        return self._public_key

    def check_key(self, strong=True, check_with_signature=True, throw=True):
        """Check that key is valid and working

        This calls underlying ``botan3.PrivateKey.check_key(strong=strong)``
        function, and then if ``check_with_signature`` is True, it attempts
        to validate that private key can sign a random message successfully.

        Parameters
        ----------
        strong
            boolean forwarded to ``botan3.PrivateKey.check_key``
        check_with_signature
            if True, sign a random message, then verify it
        throw
            if False, return False instead of throwing :any:`SLHInvalidKeyError`

        Raises
        ------
        SLHInvalidKeyError
            If ``throw`` is True and one check had failed.
        """

        rng = botan3.RandomNumberGenerator()
        private_key = botan3.PrivateKey.load_slh_dsa(
            self.variant_name, self._private_bytes
        )

        try:
            if not private_key.check_key(rng):
                if not throw:
                    return False

                raise SLHInvalidKeyError(
                    "Invalid key: botan3.PrivateKey.check_key() returned False"
                )

            if check_with_signature:
                message = os.urandom(16).hex()
                signed = self.sign(message, deterministic=True)
                status = self.public_key.verify(message, signed, throw=False)
                if status:
                    return True

                if not throw:
                    return status

                raise SLHInvalidKeyError(
                    "Invalid private key: unable to sign random message"
                )

        finally:
            del rng
            del private_key

        return True

    def sign(self, message: bytes, deterministic=False):
        """Sign ``message`` using private key, use of ``deterministic=False`` recommended

        Parameters
        ----------
        message
            string message to sign, as unicode string or bytes
        deterministic
            if False, randomize signature (recommended)
        """
        flavor = "Deterministic" if deterministic else "Randomized"

        rng = botan3.RandomNumberGenerator()
        private_key = botan3.PrivateKey.load_slh_dsa(
            self.variant_name, self._private_bytes
        )
        signer = botan3.PKSign(private_key, flavor)

        try:
            signer.update(message)
            signed = signer.finish(rng)
        finally:
            del rng
            del private_key
            del signer

        return signed

    def export_private_to_encrypted_pem(self, *, passphrase: str, pbkdf_msec=1000):
        """Export private key to encrypted PEM using passphrase.

        The output PEM-encoded is a standard PKCS#8 encrypted private key,
        using PBES2 as defined in PKCS#5 v2.0 on the input passphrase.

        The algorithms used are ``PBKDF2`` with ``AES-256/CBC`` and
        ``SHA-256``.

        Parameters
        ----------
        passphrase
            the string used to protect output encrypted PEM
        pbkdf_msec
            milliseconds of PBKDF2 applied to passphrase

        Returns
        -------
        A tuple of exported PEM output string and parameter set used as string.
        """

        rng = botan3.RandomNumberGenerator()
        private_key = botan3.PrivateKey.load_slh_dsa(
            self.variant_name, self._private_bytes
        )

        try:
            exported = private_key.export_encrypted(
                passphrase,
                rng,
                pem=True,
                msec=pbkdf_msec,
                cipher="AES-256/CBC",
                pbkdf="SHA-256",
            )
        finally:
            del rng
            del private_key

        return (exported, self.variant_name)

    @classmethod
    def import_from_encrypted_pem(
        cls,
        input_pem: str,
        variant_name: str,
        *,
        passphrase: str,
        check_key=True,
        force_botan3=False,
    ):
        """From an encrypted PEM output and its variant name, obtain a :any:`slh_private` instance

        This function is compatible with
        :any:`slh_private.export_private_to_encrypted_pem()`
        and implements the same behavior.

        If ``variant_name`` is ``None`` attempt to deduce which variant has
        been used.

        Note
        ----

        Parameter ``variant_name`` is ignored if ``force_botan3`` is True.

        Parameters
        ----------
        input_pem
            PEM string as returned by the export function
        variant_name
            variant name as returned by the export function
        passphrase
            passphrase as provided to export function
        check_key
            if True, attempt to sign a random string to verify that import was
            successful, if False, do not perform extra computation
        force_botan3
            if True, use botan3 to import and decrypt key, and do not attempt
            to use ``pycryptodome`` PEM & PKCS8 ``Crypto.IO`` module.

        Raises
        ------
        SLHImportError
            raised if import was not successful
        """

        # import with pure botan
        if force_botan3:
            private_key = None

            try:
                private_key = botan3.PrivateKey.load(input_pem, passphrase=passphrase)
                return cls(
                    private_bytes=private_key, params=variant_name, check_key=check_key
                )
            except BaseException as e:
                raise SLHImportError(
                    "Unable to import key from PEM, see above for reason"
                ) from e
            finally:
                if private_key:
                    del private_key

            return None

        if not _cryptodome_enabled:
            raise SLHImportError(
                'PyCryptodome unavailable ("import Crypto" failed) and force_botan3=False'
            )

        # import with pycryptodome
        try:

            # decode PEM
            private_der, marker_string, pem_decrypted = Crypto.IO.PEM.decode(input_pem)
            if marker_string != "ENCRYPTED PRIVATE KEY":
                raise SLHImportError(
                    'Expected "ENCRYPTED PRIVATE KEY" as PEM marker string'
                )
            assert not pem_decrypted

            # decrypt key
            private_oid, private_bytes, params = Crypto.IO.PKCS8.unwrap(
                private_der, passphrase=passphrase
            )
            if params is not None:
                raise SLHImportError(
                    "Expected no extra DER-encoded parameters to private key!"
                )

            # validate OID
            if private_oid not in slh_dsa_oids:
                raise SLHImportError(f"Unknown OID for SLH-DSA: {private_oid}")

            variant_name = variant_name or slh_dsa_oids[private_oid]
            if slh_dsa_oids[private_oid] != variant_name:
                raise SLHImportError(
                    f"Expected {variant_name} variant, got {slh_dsa_oids[private_oid]} instead?"
                )

            # construct slh_private
            return cls(
                private_bytes=private_bytes, params=variant_name, check_key=check_key
            )
        except SLHImportError as e:
            raise e
        except BaseException as e:
            raise SLHImportError(f"Unable to import key from PEM: {e}") from e

        return None

    def __repr__(self):
        public_bytes = self.get_public_bytes().hex()
        public_bytes = public_bytes[:4] + ".." + public_bytes[-4:]
        return f'<{type(self).__module__}.{type(self).__name__} privkey=(hidden) pubkey=({public_bytes}) params="{self.variant_name}">'


class slh_public:
    """SLH-DSA public key, safe to manipulate in an untrusted environment

    Parameters
    ----------
    public_bytes
        Public key as raw bytes
    params
        A :any:`slh_params` instance or equivalent string.
    """

    def __init__(self, *, public_bytes, params):
        if isinstance(params, str):
            params = slh_params.from_string(params)
        assert isinstance(params, slh_params)

        if isinstance(public_bytes, botan3.PublicKey):
            if public_bytes.algo_name() != params.algo_name:
                raise SLHUnsupported("botan3.PublicKey object is not SLH-DSA?")
            public_bytes = public_bytes.to_raw()
        assert isinstance(public_bytes, bytes)

        self._public_bytes = public_bytes
        self._params = params

    @property
    def params(self):
        """SLH-DSA parameter set used by public key"""
        return self._params

    @property
    def variant_name(self):
        """SLH-DSA parameter set string used by public key"""
        return self._params.variant_name

    def get_public_bytes(self):
        """Return public as raw bytes"""
        return self._public_bytes

    def get_public_fingerprint(self, hash_name="sha256", hexdigest=True):
        """:meta private: Return public key additionally hashed with provided ``hash_name``

        Warning
        -------

        This fingerprint can not be used to verify signatures!
        """
        hash_obj = hashlib.new(hash_name)
        hash_obj.update(self._public_bytes)
        return hash_obj.hexdigest() if hexdigest else hash_obj.digest()

    def export_to_plain_pem(self):
        """Export public key as plain PEM string

        Returns
        -------
        A tuple of exported PEM output string and parameter set used as string.
        """

        public_key = botan3.PublicKey.load_slh_dsa(
            self.variant_name, self._public_bytes
        )

        try:
            pem_export = public_key.to_pem()
            return pem_export, self.variant_name
        finally:
            del public_key

    @classmethod
    def import_from_plain_pem(cls, input_pem: str, variant_name: str):
        """Import public key from plain PEM string

        Parameters
        ----------
        input_pem
            input PEM string as returned by public export function
        variant_name
            variant name as returned by public export function
        """

        public_key = botan3.PublicKey.load(input_pem)

        try:
            return cls(public_bytes=public_key.to_raw(), params=variant_name)
        finally:
            del public_key

    def verify(self, message: bytes, signature: bytes, throw=True):
        """Verify ``message`` string with public key and ``signature`` bytes.

        If ``throw`` is False, return False on errors, or else True.

        Raises
        ------
        SLHVerifyError
            If ``throw`` is True and verification failed.
        """

        public_key = botan3.PublicKey.load_slh_dsa(
            self.variant_name, self._public_bytes
        )
        verifier = botan3.PKVerify(public_key, "")

        try:
            verifier.update(message)
            status = verifier.check_signature(signature)
        except BaseException as e:
            raise SLHVerifyError("Verification failed, see above for reason") from e
        finally:
            del public_key
            del verifier

        if throw and not status:
            raise SLHVerifyError("Invalid signature")
        return status

    def __repr__(self):
        public_bytes = self.get_public_bytes().hex()
        public_bytes = public_bytes[:4] + ".." + public_bytes[-4:]
        return f'<{type(self).__module__}.{type(self).__name__} pubkey=({public_bytes}) params="{self.variant_name}">'
