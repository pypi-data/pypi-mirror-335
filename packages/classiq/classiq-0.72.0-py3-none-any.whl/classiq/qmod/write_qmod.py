import json
from pathlib import Path
from typing import Optional, Union

from classiq.interface.model.model import Model, SerializedModel

from classiq.qmod.native.pretty_printer import DSLPrettyPrinter
from classiq.qmod.quantum_function import GenerativeQFunc, QFunc
from classiq.qmod.utilities import DEFAULT_DECIMAL_PRECISION

_QMOD_SUFFIX = "qmod"
_SYNTHESIS_OPTIONS_SUFFIX = "synthesis_options.json"


def write_qmod(
    model: Union[SerializedModel, QFunc, GenerativeQFunc],
    name: str,
    directory: Optional[Path] = None,
    decimal_precision: int = DEFAULT_DECIMAL_PRECISION,
) -> None:
    """
    Creates a native Qmod file from a serialized model and outputs the synthesis options (Preferences and Constraints) to a file.
    The native Qmod file may be uploaded to the Classiq IDE.

    Args:
        model: The entry point of the Qmod model - a qfunc named 'main' (or alternatively the output of 'create_model').
        name: The name to save the file by.
        directory: The directory to save the files in. If None, the current working directory is used.
        decimal_precision: The number of decimal places to use for numbers, set to 4 by default.

    Returns:
        None
    """
    if isinstance(model, (QFunc, GenerativeQFunc)):
        model_obj = model.create_model()
    else:
        model_obj = Model.model_validate_json(model)
    pretty_printed_model = DSLPrettyPrinter(decimal_precision=decimal_precision).visit(
        model_obj
    )

    synthesis_options = model_obj.model_dump(
        include={"constraints", "preferences"}, exclude_none=True
    )

    synthesis_options_path = Path(f"{name}.{_SYNTHESIS_OPTIONS_SUFFIX}")
    if directory is not None:
        synthesis_options_path = directory / synthesis_options_path

    synthesis_options_path.write_text(json.dumps(synthesis_options, indent=2))

    native_qmod_path = Path(f"{name}.{_QMOD_SUFFIX}")
    if directory is not None:
        native_qmod_path = directory / native_qmod_path

    native_qmod_path.write_text(pretty_printed_model)
