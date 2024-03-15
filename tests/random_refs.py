import uuid
import random
import string


def random_username(name=""):
    return f"user-{name}-{uuid.uuid4()}"


def random_valid_password(length=12):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation
    all_characters = lowercase_letters + uppercase_letters + digits + special_characters

    password = "".join(random.choice(all_characters) for _ in range(length - 4))
    password += random.choice(lowercase_letters)
    password += random.choice(uppercase_letters)
    password += random.choice(digits)
    password += random.choice(special_characters)

    return password


def random_invalid_password():
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase
    digits = string.digits
    special_characters = string.punctuation
    all_characters = lowercase_letters + uppercase_letters + digits + special_characters

    # Empty password
    invalid_empty_password = ""

    # Password less than 8 characters
    invalid_short_password = "".join(
        random.choice(all_characters) for _ in range(random.randint(2, 7))
    )

    # Password without digits or special characters
    invalid_no_digit_or_special = "".join(
        random.choice(lowercase_letters + uppercase_letters) for _ in range(8)
    )

    invalid_password_with_spaces = "".join(
        random.choice(all_characters) for _ in range(7)
    )
    invalid_password_with_spaces += " "

    invalid_passwords = [
        invalid_empty_password,
        invalid_short_password,
        invalid_no_digit_or_special,
        invalid_password_with_spaces,
    ]

    return random.choice(invalid_passwords)


def random_email():
    return f"email-{uuid.uuid4()}@gmail.com"
