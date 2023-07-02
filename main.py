import asyncio
import re

from js import document
from tpmstream.__main__ import parse_all_types
from tpmstream.io.auto import Auto
from tpmstream.io.hex import Hex
from tpmstream.io.pretty import Pretty
from tpmstream.spec import all_types
from tpmstream.spec.commands import CommandResponseStream, Response
from tpmstream.spec.structures.constants import TPM_CC

input = Element("in").element
output = Element("out").element
tpm_types = Element("tpm-type").element


def type_to_str(tpm_type, command_code=None):
    if command_code is None:
        return tpm_type.__name__
    return f"{tpm_type.__name__} ({command_code})"


def str_to_type(s):
    types_without_response = {
        type_to_str(tpm_type): (tpm_type, None)
        for tpm_type in all_types
        if tpm_type is not Response
    }
    types_with_response = {
        type_to_str(Response, command_code): (Response, command_code)
        for command_code in TPM_CC
    }
    return (types_without_response | types_with_response)[s]


def on_input(*args):
    document.body.classList.add("wait")
    input.classList.add("wait")
    tpm_types.classList.add("wait")

    asyncio.create_task(on_input_catch_all(args))


async def on_input_catch_all(*args):
    input.classList.remove("invalid")

    if input.value:
        try:
            await on_input_unwrapped(*args)
        except Exception as e:
            input.classList.add("invalid")
            output.innerHTML = f'<span class="color-warning">{str(e)}</span>'
            output.innerHTML += f'{__import__("traceback").format_exc()}'

    document.body.classList.remove("wait")
    input.classList.remove("wait")
    tpm_types.classList.remove("wait")


async def on_input_unwrapped(*args):
    input_value = bytes.fromhex(input.value)
    canonical_objs = list(parse_all_types(Auto, input_value))

    tpm_types.innerHTML = ""

    for canonical_obj, command_code in canonical_objs:
        option = document.createElement("option")
        value = type_to_str(type(canonical_obj.object), command_code=command_code)
        option.text = value
        option.value = value
        tpm_types.add(option, None)

    # always have CommandResponseStream
    option = document.createElement("option")
    value = type_to_str(CommandResponseStream, command_code=None)
    option.text = value
    option.value = value
    tpm_types.add(option, None)

    tpm_types.selectedIndex = 0
    on_select()


def on_select():
    input_value = bytes.fromhex(input.value)
    tpm_type, command_code = str_to_type(tpm_types.value)

    events = Auto.marshal(
        tpm_type=tpm_type,
        buffer=input_value,
        command_code=command_code,
        abort_on_error=False,
    )

    output.innerHTML = ""
    for line in Pretty.unmarshal(events):
        if isinstance(line, bytes):
            output.innerHTML += " " + line.hex().decode()
        else:
            line = re.sub(r"\[92m([^]*)", r'<span class="color-name">\1</span>', line)
            line = re.sub(r"\[34m([^]*)", r'<span class="color-type">\1</span>', line)
            line = re.sub(
                r"\[33m([^]*)", r'<span class="color-value">\1</span>', line
            )
            line = re.sub(
                r"\[31m([^]*)", r'<span class="color-warning">\1</span>', line
            )
            line = re.sub(
                r"\[30m([^]*)", r'<span class="color-indent">\1</span>', line
            )
            line = re.sub(r"\[0m", "", line)
            output.innerHTML += line + "\n"
