from app.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher


def test_hash_and_verify_roundtrip() -> None:
    hasher = Argon2PasswordHasher()

    hashed = hasher.hash("S3cret-turismo!")

    assert hashed != "S3cret-turismo!"
    assert hasher.verify("S3cret-turismo!", hashed)


def test_verify_rejects_wrong_password() -> None:
    hasher = Argon2PasswordHasher()

    hashed = hasher.hash("S3cret-turismo!")

    assert not hasher.verify("otra-clave", hashed)


def test_hash_uses_argon2id() -> None:
    assert Argon2PasswordHasher().hash("S3cret-turismo!").startswith("$argon2id$")
