print("sub_package.module_b")

__all__: list[str] = ["member1"]


def member1() -> None:
    print("sub_package.module_b.member1")


member2: str = "sub_package.module_b.member2"

_private_member1: str = "sub_package.module_b._private_member1"
