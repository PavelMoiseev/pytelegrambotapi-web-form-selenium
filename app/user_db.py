from dataclasses import dataclass
from typing import Optional
from collections import defaultdict


@dataclass
class User:
    name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    birth: Optional[str]

    name = None
    last_name = None
    email = None
    phone = None
    birth = None


user_db: dict = defaultdict(User)
