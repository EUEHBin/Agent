print("sub_package.module_a")

__all__: list[str] = ["member1"]
from .. import module_a


def member1() -> None:
    print("sub_package.module_a.member1")


member2: str = "sub_package.module_a.member2"

_private_member1: str = "sub_package.module_a._private_member1"
