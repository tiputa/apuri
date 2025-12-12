from .settings import AUTH_PASSWORD_VALIDATORS

# python


def test_auth_password_validators_is_list():
    assert isinstance(
        AUTH_PASSWORD_VALIDATORS, list
    ), "AUTH_PASSWORD_VALIDATORS must be a list"


def test_each_validator_is_dict_with_name():
    assert (
        len(AUTH_PASSWORD_VALIDATORS) > 0
    ), "AUTH_PASSWORD_VALIDATORS should not be empty"
    for i, item in enumerate(AUTH_PASSWORD_VALIDATORS):
        assert isinstance(
            item, dict
        ), f"Item {i} in AUTH_PASSWORD_VALIDATORS must be a dict"
        assert "NAME" in item, f"Item {i} missing 'NAME' key"
        name = item["NAME"]
        assert isinstance(name, str), f"'NAME' in item {i} must be a string"
        assert name.strip() != "", f"'NAME' in item {i} must not be empty"


def test_validator_names_use_full_django_path():
    for i, item in enumerate(AUTH_PASSWORD_VALIDATORS):
        name = item["NAME"]
        assert name.startswith(
            "django.contrib.auth.password_validation."
        ), f"'NAME' in item {i} should start with 'django.contrib.auth.password_validation.'"


def test_contains_default_django_validators():
    expected = {
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    }
    actual = {
        name.rsplit(".", 1)[-1]
        for name in (item["NAME"] for item in AUTH_PASSWORD_VALIDATORS)
    }
    assert expected.issubset(actual), f"Missing default validators: {expected - actual}"


def test_no_duplicate_validator_names():
    names = [item["NAME"] for item in AUTH_PASSWORD_VALIDATORS]
    assert len(names) == len(
        set(names)
    ), "Duplicate validator 'NAME' entries found in AUTH_PASSWORD_VALIDATORS"
