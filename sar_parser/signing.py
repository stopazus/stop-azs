"""Minimal cryptographic helpers for Suspicious Activity Report workflows.

The goal of this module is to offer a compact API for computing and verifying
signatures without depending on optional third party libraries.  While the
module is intentionally lightweight, it still performs the most common tasks
required when exchanging SAR payloads with counterparties:

* normalising payload input (``str`` or ``bytes``) before hashing,
* computing a keyed-hash (HMAC) signature using well known algorithms, and
* verifying signatures in a timing safe manner.

The helpers operate on bytes and use base64 to expose signatures as ASCII
strings so that they can be embedded into JSON/XML metadata without further
encoding.  Only algorithms backed by Python's :mod:`hashlib` are supported so
that the module remains completely dependency free.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import hmac
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Mapping, MutableMapping, Optional, Sequence, Union

__all__ = [
    "DEFAULT_ALGORITHM",
    "SUPPORTED_ALGORITHMS",
    "Signature",
    "SignatureError",
    "sign_payload",
    "sign_file_with_gpg",
    "verify_signature",
]

# Mapping between algorithm names and the constructors from :mod:`hashlib`.
_HASH_CONSTRUCTORS: Mapping[str, Callable[[], "hashlib._Hash"]] = {
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}

SUPPORTED_ALGORITHMS: Iterable[str] = tuple(_HASH_CONSTRUCTORS.keys())
"""List the names of algorithms understood by :func:`sign_payload`."""

DEFAULT_ALGORITHM = "sha256"
"""Default digest algorithm used when the caller does not specify one."""


class SignatureError(ValueError):
    """Exception raised when signature data cannot be processed."""


def _normalise_bytes(value: Union[str, bytes], *, name: str) -> bytes:
    """Return ``value`` as UTF-8 encoded bytes.

    Parameters
    ----------
    value:
        The incoming payload (``str`` or ``bytes``).
    name:
        Name of the argument being normalised.  Used in error messages.
    """

    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return value.encode("utf-8")
    raise TypeError(f"{name} must be str or bytes, got {type(value)!r}")


def _normalise_algorithm(algorithm: Optional[str]) -> str:
    if algorithm is None:
        algorithm = DEFAULT_ALGORITHM
    if not isinstance(algorithm, str):
        raise TypeError("algorithm must be a string")
    key = algorithm.lower()
    if key not in _HASH_CONSTRUCTORS:
        supported = ", ".join(sorted(_HASH_CONSTRUCTORS))
        raise SignatureError(
            f"Unsupported algorithm '{algorithm}'. Supported algorithms: {supported}."
        )
    return key


def _validate_signature_value(signature: str) -> str:
    if not isinstance(signature, str):
        raise TypeError("signature must be a string")
    try:
        # ``validate=True`` makes sure the string is real base64 data.
        base64.b64decode(signature.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:  # pragma: no cover - sanity guard
        raise SignatureError("signature value must be base64 encoded ASCII") from exc
    return signature


@dataclass(frozen=True)
class Signature:
    """Container object returned by :func:`sign_payload`.

    Parameters
    ----------
    algorithm:
        Name of the hashing algorithm that was used (normalised to lowercase).
    value:
        Base64 encoded digest.
    key_id:
        Optional identifier of the secret that was used to compute the
        signature.  This can help clients pick the correct secret when multiple
        keys are in rotation.
    """

    algorithm: str
    value: str
    key_id: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "algorithm", _normalise_algorithm(self.algorithm))
        object.__setattr__(self, "value", _validate_signature_value(self.value))
        if self.key_id is not None and not isinstance(self.key_id, str):
            raise TypeError("key_id must be a string if provided")

    def as_dict(self) -> Dict[str, str]:
        """Return a JSON serialisable representation of the signature."""

        data: MutableMapping[str, str] = {"algorithm": self.algorithm, "value": self.value}
        if self.key_id is not None:
            data["key_id"] = self.key_id
        return dict(data)

    @classmethod
    def from_dict(cls, payload: Mapping[str, str]) -> "Signature":
        """Build :class:`Signature` from a dictionary structure."""

        if "algorithm" not in payload or "value" not in payload:
            missing = {key for key in ("algorithm", "value") if key not in payload}
            raise SignatureError(f"signature payload missing required keys: {sorted(missing)}")
        return cls(
            algorithm=payload["algorithm"],
            value=payload["value"],
            key_id=payload.get("key_id"),
        )

    def __str__(self) -> str:  # pragma: no cover - trivial representation
        return self.value


def sign_payload(
    payload: Union[str, bytes],
    secret: Union[str, bytes],
    *,
    algorithm: Optional[str] = None,
    key_id: Optional[str] = None,
) -> Signature:
    """Return a :class:`Signature` for ``payload`` using ``secret``.

    ``secret`` should be the shared key agreed upon by both parties.  The
    function uses HMAC under the hood to protect against length extension
    attacks and to provide integrity.
    """

    algo = _normalise_algorithm(algorithm)
    message = _normalise_bytes(payload, name="payload")
    secret_bytes = _normalise_bytes(secret, name="secret")
    digest = hmac.new(secret_bytes, message, _HASH_CONSTRUCTORS[algo]).digest()
    value = base64.b64encode(digest).decode("ascii")
    return Signature(algorithm=algo, value=value, key_id=key_id)


def verify_signature(
    payload: Union[str, bytes],
    secret: Union[str, bytes],
    signature: Union[Signature, str],
    *,
    algorithm: Optional[str] = None,
) -> bool:
    """Return ``True`` if ``signature`` matches ``payload``.

    When ``signature`` is a string the caller must provide ``algorithm`` since
    the signature string alone does not contain this information.  This helper
    relies on :func:`hmac.compare_digest` to avoid timing attacks.
    """

    if isinstance(signature, Signature):
        expected_algorithm = signature.algorithm
        expected_value = signature.value
    else:
        expected_algorithm = _normalise_algorithm(algorithm)
        expected_value = _validate_signature_value(signature)

    candidate = sign_payload(
        payload,
        secret,
        algorithm=expected_algorithm,
    )
    return hmac.compare_digest(candidate.value, expected_value)


def _path(value: Union[str, Path]) -> Path:
    if isinstance(value, Path):
        return value.expanduser()
    return Path(value).expanduser()


def sign_file_with_gpg(
    report_path: Union[Path, str],
    *,
    key_id: Optional[str] = None,
    output: Optional[Union[Path, str]] = None,
    armor: bool = True,
) -> Path:
    """Create a detached GPG signature for ``report_path`` and return its path."""

    gpg_binary = shutil.which("gpg")
    if gpg_binary is None:
        raise RuntimeError("gpg executable not found on PATH")

    report_path = _path(report_path)
    if not report_path.exists():
        raise FileNotFoundError(f"Report file not found: {report_path}")
    if not report_path.is_file():
        raise ValueError(f"Report path must be a file, got: {report_path}")

    if output is None:
        suffix = ".sig"
        signature_path = report_path.with_suffix(report_path.suffix + suffix)
    else:
        signature_candidate = _path(output)
        if signature_candidate.exists() and signature_candidate.is_dir():
            signature_path = signature_candidate / (report_path.name + ".sig")
        else:
            signature_path = signature_candidate
    signature_path.parent.mkdir(parents=True, exist_ok=True)

    command = [gpg_binary, "--batch", "--yes", "--output", str(signature_path)]
    if key_id:
        command.extend(["--local-user", key_id])
    if armor:
        command.append("--armor")
    command.extend(["--detach-sign", str(report_path)])

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - subprocess failure guard
        raise RuntimeError(f"gpg signing failed with exit code {exc.returncode}") from exc

    return signature_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sar-parser-signing",
        description="Cryptographic helpers for Suspicious Activity Report tooling.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sign_gpg = sub.add_parser("sign-gpg", help="Create a detached signature using gpg")
    sign_gpg.add_argument("file", type=_path, help="Report file to sign")
    sign_gpg.add_argument("--key-id", dest="key_id", help="Optional GPG key identifier")
    sign_gpg.add_argument("--output", type=_path, help="Override signature output path")
    sign_gpg.add_argument(
        "--no-armor",
        dest="armor",
        action="store_false",
        default=True,
        help="Produce a binary signature instead of ASCII-armored output",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "sign-gpg":
        signature_path = sign_file_with_gpg(
            args.file,
            key_id=args.key_id,
            output=args.output,
            armor=args.armor,
        )
        print(f"[INFO] Signature written to: {signature_path}")
        return 0

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
