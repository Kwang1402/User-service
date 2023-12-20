from user_service.domains.models import validate_password


def test_password_not_long_enough():
    password = "abc123@"
    assert validate_password(password) == False


def test_password_does_not_contain_digit():
    password = "abcde!@#"
    assert validate_password(password) == False


def test_password_does_not_contain_special_character():
    password = "abcde123"
    assert validate_password(password) == False


def test_password_contains_spaces():
    password = "abc 123 !@#"
    assert validate_password(password) == False


def test_password_is_valid():
    password = "abc123!@#"
    assert validate_password(password) == True
