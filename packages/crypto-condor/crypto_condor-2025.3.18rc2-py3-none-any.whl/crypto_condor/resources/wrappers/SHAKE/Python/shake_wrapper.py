"""Wrapper template for SHAKE implementations."""


def CC_SHAKE_128_digest(data: bytes, output_length: int) -> bytes:
    """Hashes with SHAKE128."""
    raise NotImplementedError()


def CC_SHAKE_256_digest(data: bytes, output_length: int) -> bytes:
    """Hashes with SHAKE256."""
    raise NotImplementedError()
