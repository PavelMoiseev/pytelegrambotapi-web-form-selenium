import phonenumbers
from datetime import datetime
from email.utils import parseaddr


def validate_name(name: str) -> bool:
    return name.isalpha()


def validate_email(email: str) -> bool:
    try:
        email = parseaddr(email)[1]
        email_domain = email.split('.')[-1]
        return all([email and '@' in email, '.' in email, len(email_domain) > 1])
    except ValueError:
        return False


def validate_phone_number(phone: str) -> bool:
    try:
        phone_number = phonenumbers.parse(phone)
        return phonenumbers.is_possible_number(phone_number)
    except ValueError:
        return False


def validate_date_of_birth(birthday: str) -> bool:
    birthday_format = '%d.%m.%Y'
    try:
        res = datetime.strptime(birthday, birthday_format)
        return 1902 <= res.year <= 2002
    except ValueError:
        return False
