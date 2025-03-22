# cao/engine.py

import os
from .registry import ConverterRegistry

def convert(input_path, output_path):
    input_ext = os.path.splitext(input_path)[1][1:]
    output_ext = os.path.splitext(output_path)[1][1:]

    SourceClass = ConverterRegistry.get_source(input_ext)
    TargetClass = ConverterRegistry.get_target(output_ext)

    if not SourceClass:
        raise ValueError(f"No source registered for: {input_ext}")
    if not TargetClass:
        raise ValueError(f"No target registered for: {output_ext}")

    data = SourceClass().extract(input_path)

    if not TargetClass.accepts_type(data["type"]):
        raise ValueError(f"{output_ext} target does not support data type: {data['type']}")

    TargetClass.write(data, output_path)
