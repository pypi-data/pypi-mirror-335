class SSH_key_not_set(Exception):
    def __init__(self, *args: object) -> None:
        self.message="SSH Key file not set"
        super().__init__(self.message)

class Permission_Denied_SSH(Exception):
    def __init__(self, *args: object) -> None:
        self.message="Permission Denied Check if the set SSH  jey is correct"
        super().__init__(self.message)
