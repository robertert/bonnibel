"""Weryfikacja podpisów webhooków (Git/Jira) — strategia + fabryka."""
from __future__ import annotations

import hashlib
import hmac
from abc import ABC, abstractmethod


class SignatureVerifier(ABC):
    @abstractmethod
    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        ...

    @staticmethod
    def _hmac_sha256(payload: bytes, secret: str) -> str:
        return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


class GitSignatureVerifier(SignatureVerifier):
    """GitHub: nagłówek X-Hub-Signature-256 w formacie 'sha256=<hex>'."""

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        if not signature:
            return False
        expected = "sha256=" + self._hmac_sha256(payload, secret)
        return hmac.compare_digest(expected, signature)


class JiraSignatureVerifier(SignatureVerifier):
    """Jira: HMAC-SHA256 jako czysty hex (bez prefiksu)."""

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        if not signature:
            return False
        expected = self._hmac_sha256(payload, secret)
        candidate = signature.split("=", 1)[-1]  # toleruj ewentualny prefiks
        return hmac.compare_digest(expected, candidate)


class SignatureVerifierFactory:
    """Dobiera weryfikator na podstawie dostawcy webhooka."""

    _verifiers = {
        "GITHUB": GitSignatureVerifier,
        "JIRA": JiraSignatureVerifier,
    }

    @classmethod
    def for_provider(cls, provider: str) -> SignatureVerifier:
        verifier_cls = cls._verifiers.get(provider.upper())
        if verifier_cls is None:
            raise ValueError(f"Unsupported webhook provider: {provider}")
        return verifier_cls()
