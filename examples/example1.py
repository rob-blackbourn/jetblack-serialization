from typing import NotRequired, Required, TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class OptInExample(TypedDict, total=False):
    a: int
    b: NotRequired[str]
    c: Required[float]


class OptOutExample(TypedDict, total=True):
    a: int
    b: NotRequired[str]
    c: Required[float]


def main() -> None:
    opt_in_obj: OptInExample = {'a': 1, 'c': 2.0}
    opn_in_text = serialize_typed(opt_in_obj, OptInExample)
    opt_in_roundtrip = deserialize_typed(opn_in_text, OptInExample)
    assert opt_in_obj == opt_in_roundtrip

    opt_out_obj: OptOutExample = {'a': 1, 'c': 2.0}
    opn_out_text = serialize_typed(opt_out_obj, OptOutExample)
    opt_out_roundtrip = deserialize_typed(opn_out_text, OptOutExample)
    assert opt_out_obj == opt_out_roundtrip

    print("here")


if __name__ == "__main__":
    main()
