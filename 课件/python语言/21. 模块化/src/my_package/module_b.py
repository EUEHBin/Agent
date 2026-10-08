print("module_b")

__all__: list[str] = ["member1"]


def member1() -> None:
    print("module_b.member1")


member2: str = "module_b.member2"

_private_member1: str = "module_b._private_member1"
