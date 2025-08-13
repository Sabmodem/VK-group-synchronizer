from dataclasses import dataclass
from enum import Enum

class Role(Enum):
    moderator = 'moderator'
    editor = 'editor'
    administrator = 'administrator'
    advertiser = 'advertiser'
    without_permisions = None

@dataclass(frozen=True)
class SetGroupAdminDto:
    group_id: int
    user_id: int
    role: Role

    def to_json(self) -> dict:
        return {
            'group_id': self.group_id,
            'user_id': self.user_id,
            'role': self.role.value,
            'is_contact': False
        }