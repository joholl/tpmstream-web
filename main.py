import asyncio
import re

from tpmstream.io.auto import Auto
from tpmstream.io.pretty import Pretty
from tpmstream.spec.commands import CommandResponseStream


input = Element('in').element
output = Element('out').element


def convert(*args):
    asyncio.create_task(convert_catch_all(args))


async def convert_catch_all(*args):
    input.classList.remove("invalid")

    if not input.value:
        return

    try:
        await convert_unwrapped(*args)
    except Exception as e:
        input.classList.add("invalid")
        output.innerHTML = f'<span class="color-warning">{str(e)}</span>'
        return


async def convert_unwrapped(*args):
    buffer = bytearray.fromhex(input.value)

    events = Auto.marshal(
        tpm_type=CommandResponseStream,
        buffer=buffer,
        command_code=None,
        abort_on_error=False,
    )

    output.innerHTML = ""
    for line in Pretty.unmarshal(events):
        if isinstance(line, bytes):
            output.innerHTML += " " + line.hex().decode()
        else:

            line = re.sub(r"\[92m([^]*)", r'<span class="color-name">\1</span>', line)
            line = re.sub(r"\[34m([^]*)", r'<span class="color-type">\1</span>', line)
            line = re.sub(r"\[33m([^]*)", r'<span class="color-value">\1</span>', line)
            line = re.sub(r"\[31m([^]*)", r'<span class="color-warning">\1</span>', line)
            line = re.sub(r"\[30m([^]*)", r'<span class="color-indent">\1</span>', line)
            line = re.sub(r"\[0m", '', line)
            output.innerHTML += line + "\n"
