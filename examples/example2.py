from typing import Annotated, NotRequired, Required, TypedDict

from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
    JSONProperty
)


class OptInExample(TypedDict, total=False):
    first_arg: Annotated[int, JSONProperty("firstArg")]
    second_arg: NotRequired[Annotated[str, JSONProperty("secondArg")]]
    third_arg: Required[Annotated[float, JSONProperty("thirdArg")]]


class OptOutExample(TypedDict, total=True):
    first_arg: Annotated[int, JSONProperty("firstArg")]
    second_arg: NotRequired[Annotated[str, JSONProperty("secondArg")]]
    third_arg: Required[Annotated[float, JSONProperty("thirdArg")]]


def main() -> None:
    opt_in_obj: OptInExample = {'first_arg': 1, 'third_arg': 2.0}
    opn_in_text = serialize_typed(opt_in_obj, OptInExample)
    opt_in_roundtrip = deserialize_typed(opn_in_text, OptInExample)
    assert opt_in_obj == opt_in_roundtrip

    opt_out_obj: OptOutExample = {'first_arg': 1, 'third_arg': 2.0}
    opn_out_text = serialize_typed(opt_out_obj, OptOutExample)
    opt_out_roundtrip = deserialize_typed(opn_out_text, OptOutExample)
    assert opt_out_obj == opt_out_roundtrip

    print("here")


if __name__ == "__main__":
    main()
