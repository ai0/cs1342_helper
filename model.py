from dataclasses import dataclass


@dataclass
class Student:
    first_name: str
    last_name: str
    smu_id: str
    smu_email: str
    github_username: str

    @property
    def full_name(self):
        return ' '.join((self.first_name, self.last_name))
