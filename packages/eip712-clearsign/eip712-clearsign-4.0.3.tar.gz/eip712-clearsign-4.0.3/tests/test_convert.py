from pathlib import Path

import pytest

from eip712.convert.input_to_resolved import EIP712InputToResolvedConverter
from eip712.convert.resolved_to_instructions import EIP712ResolvedToInstructionsConverter
from eip712.model.input.descriptor import InputEIP712DAppDescriptor
from eip712.model.instruction import EIP712MessageInstruction
from eip712.model.resolved.descriptor import ResolvedEIP712DAppDescriptor

DATA_DIRECTORY = Path(__file__).parent / "data"


@pytest.mark.parametrize("file", ["paraswap_eip712"])
def test_convert(file: str) -> None:
    input_model = InputEIP712DAppDescriptor.load(DATA_DIRECTORY / f"{file}.json")
    resolved_model = EIP712InputToResolvedConverter().convert(input_model)

    resolved_expected_model = ResolvedEIP712DAppDescriptor.load(DATA_DIRECTORY / f"{file}.resolved.json")

    assert resolved_model == resolved_expected_model

    instructions = EIP712ResolvedToInstructionsConverter().convert(resolved_model)

    assert len(instructions) == 1
    assert "0xf3cd476c3c4d3ac5ca2724767f269070ca09a043" in instructions
    dict_for_address = instructions["0xf3cd476c3c4d3ac5ca2724767f269070ca09a043"]
    assert len(dict_for_address) == 1
    assert "16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3" in dict_for_address
    instructions_list = dict_for_address["16c6594547c8c6af18ca0d8b500976bfb7f38764060cec3792c2aad3"]
    assert len(instructions_list) == 10

    message = instructions_list[0]
    assert isinstance(message, EIP712MessageInstruction)

    assert message.display_name == "AugustusRFQ ERC20 order"
    assert message.field_mappers_count == 9
