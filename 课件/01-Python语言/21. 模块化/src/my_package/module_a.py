print("module_a", __name__)

__all__: list[str] = ["member1"]


def member1() -> None:
    print("module_a.member1")


member2: str = "module_a.member2"

_private_member1: str = "module_a._private_member1"
