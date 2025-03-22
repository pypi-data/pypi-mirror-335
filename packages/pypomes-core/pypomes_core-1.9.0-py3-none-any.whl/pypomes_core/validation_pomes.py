from datetime import date, datetime
from flask import jsonify, Response
from logging import Logger
from typing import Any, Final
from .datetime_pomes import TIMEZONE_LOCAL
from .env_pomes import APP_PREFIX, env_get_str
from .str_pomes import str_as_list, str_sanitize, str_find_whitespace

VALIDATION_MSG_LANGUAGE: Final[str] = env_get_str(key=f"{APP_PREFIX}_VALIDATION_MSG_LANGUAGE",
                                                  def_value="en")
VALIDATION_MSG_PREFIX: Final[str] = env_get_str(key=f"{APP_PREFIX}_VALIDATION_MSG_PREFIX",
                                                def_value=APP_PREFIX)


def validate_value(attr: str,
                   val: str | int | float,
                   min_val: int = None,
                   max_val: int = None,
                   values: list = None,
                   required: bool = False) -> str:
    """
    Validate *val* according to value, range, or membership in values list, as specified.

    :param attr: the name of the attribute
    :param val: the value to be validated
    :param min_val: if *val* is a string, specifies its minimum length; otherwise, specifies its minimum value
    :param max_val: if *val* is a string, specifies its maximum length; otherwise, specifies its maximum value
    :param values: if provided, requires *val* to be contained therein
    :param required:  requires *val* to be specified
    :return: *None* if *val* passes validation, or the corresponding error message otherwise
    """
    # initialize the return variable
    result: str | None = None

    if val is None or val == "":
        if isinstance(required, bool) and required:
            # 121: Required attribute
            result = validate_format_error(121, f"@{attr}")
    elif isinstance(values, list):
        if val not in values:
            length: int = len(values)
            if length == 1:
                # 149: Invalid value {}: must be {}
                result = validate_format_error(149, val, values[0], f"@{attr}")
            else:
                # 150: Invalid value {}: must be one of {}
                result = validate_format_error(150, val, values[:length], f"@{attr}")
    elif isinstance(val, str):
        length: int = len(val)
        if min_val is not None and max_val == min_val and length != min_val:
            # 146: Invalid value {}: length must be {}
            result = validate_format_error(156, val, min_val, f"@{attr}")
        elif max_val is not None and max_val < length:
            # 148: Invalid value {}: length longer than {}
            result = validate_format_error(148, val, max_val, f"@{attr}")
        elif min_val is not None and length < min_val:
            # 147: Invalid value {}: length shorter than {}
            result = validate_format_error(147, val, min_val, f"@{attr}")
    elif (min_val is not None and val < min_val) or \
         (max_val is not None and val > max_val):
        if min_val is not None and max_val is not None:
            # 151: Invalid value {}: must be in the range {}
            result = validate_format_error(151, val, [min_val, max_val], f"@{attr}")
        elif min_val is not None:
            # 144: Invalid value {}: must be greater than {}
            result = validate_format_error(144, val, min_val, f"@{attr}")
        else:
            # 143: Invalid value {}: must be less than {}
            result = validate_format_error(143, val, max_val, f"@{attr}")

    return result


def validate_bool(errors: list[str] | None,
                  scheme: dict[str, Any],
                  attr: str,
                  default: bool = None,
                  required: bool = False,
                  logger: Logger = None) -> bool:
    """
    Validate the boolean value associated with *attr* in *scheme*.

    If provided, this value must be on of:
        - a *bool*
        - the integer *1* or *0*
        - the string *1*, *t*, or *true*, case disregarded
        - the string *0*, *f*, or *false*, case disregarded

    :param errors: incidental error messages
    :param scheme: dictionary containing the value to be validated
    :param attr: the name of the attribute whose value is being validated
    :param default: default value, overrides *required*
    :param required: specifies whether a value must be provided
    :param logger: optional logger
    :return: the validated value, or *None* if validation failed
    """
    # initialize the return variable
    result: bool | None = None

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # retrieve the value
    value = scheme.get(suffix)

    # validate it
    if value is None or value == "":
        if default is not None:
            value = default
        elif required:
            # 121: Required attribute
            stat = validate_format_error(121, f"@{attr}")
    elif isinstance(value, str):
        if value.lower() in ["1", "t", "true"]:
            value = True
        elif value.lower() in ["0", "f", "false"]:
            value = False
        else:
            # 152: Invalid value {}: must be type {}
            stat = validate_format_error(152, value, "bool", f"@{attr}")
    # bool is subtype of int
    elif isinstance(value, int) and not isinstance(value, bool):
        if value == 1:
            value = True
        elif value == 0:
            value = False
        else:
            # 152: Invalid value {}: must be type {}
            stat = validate_format_error(152, value, "bool", f"@{attr}")
    elif not isinstance(value, bool):
        # 152: Invalid value {}: must be type {}
        stat = validate_format_error(152, value, "bool", f"@{attr}")

    if stat:
        __validate_log(errors, stat, logger)
    else:
        result = value

    return result


def validate_int(errors: list[str] | None,
                 scheme: dict[str, Any],
                 attr: str,
                 min_val: int = None,
                 max_val: int = None,
                 values: list[int] = None,
                 default: int = None,
                 required: bool = False,
                 logger: Logger = None) -> int:
    """
    Validate the *int* value associated with *attr* in *scheme*.

    If provided, this value must be a *int*, or a valid string representation of a *int*.

    :param errors: incidental error messages
    :param scheme: dictionary containing the value to be validated
    :param attr: the attribute associated with the value to be validated
    :param min_val: the minimum value accepted
    :param max_val:  the maximum value accepted
    :param values: optional list of allowed values
    :param default: optional default value, overrides *required*
    :param required: specifies whether a value must be provided
    :param logger: optional logger
    :return: the validated value, or *None* if validation failed
    """
    # initialize the return variable
    result: int | None = None

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # retrieve the value
    value: int = scheme.get(suffix)

    # validate it ('bool' is subtype of 'int')
    if value is None and isinstance(default, int) and not isinstance(default, bool):
        value = default
    elif isinstance(value, str) and value.isnumeric():
        value = int(value)
    elif value is not None and \
            (isinstance(value, bool) or not isinstance(value, int)):
        # 152: Invalid value {}: must be type {}
        stat = validate_format_error(152, value, "int", f"@{attr}")

    if not stat:
        stat = validate_value(attr=attr,
                              val=value,
                              min_val=min_val,
                              max_val=max_val,
                              values=values,
                              required=required)
    if stat:
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
    else:
        result = value

    return result


def validate_float(errors: list[str] | None,
                   scheme: dict[str, Any],
                   attr: str,
                   min_val: float = None,
                   max_val: float = None,
                   required: bool = False,
                   values: list[float | int] = None,
                   default: int | float = None,
                   logger: Logger = None) -> float:
    """
    Validate the *float* value associated with *attr* in *scheme*.

    If provided, this value must be a *float*, or a valid string representation of a *float*.

    :param errors: incidental error messages
    :param scheme: dictionary containing the value to be validated
    :param attr: the attribute associated with the value to be validated
    :param min_val: the minimum value accepted
    :param max_val:  the maximum value accepted
    :param values: optional list of allowed values
    :param default: optional default value, overrides *required*
    :param required: specifies whether a value must be provided
    :param logger: optional logger
    :return: the validated value, or *None* if validation failed
    """
    # initialize the return variable
    result: float | None = None

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # retrieve the value
    value: float = scheme.get(suffix)

    # validate it
    if value is None and isinstance(default, int | float):
        value = float(default)
    elif (isinstance(value, int) and not isinstance(value, bool)) or \
            (isinstance(value, str) and value.replace(".", "", 1).isnumeric()):
        value = float(value)
    elif isinstance(value, bool) or \
            (value is not None and not isinstance(value, int | float)):
        # 152: Invalid value {}: must be type {}
        stat = validate_format_error(152, value, "float", f"@{attr}")

    if not stat:
        stat = validate_value(attr=attr,
                              val=value,
                              min_val=min_val,
                              max_val=max_val,
                              values=values,
                              required=required)
    if stat:
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
    else:
        result = value

    return result


def validate_str(errors: list[str] | None,
                 scheme: dict[str, Any],
                 attr: str,
                 min_length: int = None,
                 max_length: int = None,
                 values: list[str] = None,
                 default: str = None,
                 required: bool = False,
                 logger: Logger = None) -> str:
    """
    Validate the *str* value associated with *attr* in *scheme*.

    If provided, this value must be a *str*.

    :param errors: incidental error messages
    :param scheme: dictionary containing the value to be validated
    :param attr: the attribute associated with the value to be validated
    :param min_length: optional minimum length accepted
    :param max_length:  optional maximum length accepted
    :param values: optional list of allowed values
    :param default: optional default value, overrides *required*
    :param required: specifies whether a value must be provided
    :param logger: optional logger
    :return: the validated value, or *None* if validation failed
    """
    # initialize the return variable
    result: str | None = None

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # obtain the value
    value: str | None = scheme.get(suffix)

    # validate it
    if value is None and isinstance(default, str):
        value = default
    elif value is not None and not isinstance(value, str):
        # 152: Invalid value {}: must be type {}
        stat = validate_format_error(152, value, "str", f"@{attr}")
    else:
        stat = validate_value(attr=attr,
                              val=value,
                              min_val=min_length,
                              max_val=max_length,
                              values=values,
                              required=required)
    if stat:
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
    else:
        result = value

    return result


def validate_date(errors: list[str] | None,
                  scheme: dict[str, Any],
                  attr: str,
                  day_first: bool = False,
                  default: date = None,
                  required: bool = False,
                  logger: Logger = None) -> date:
    """
    Validate the *date* value associated with *attr* in *scheme*.

    If provided, this value must be a *date*, or a valid string representation of a *date*.

    :param errors: incidental error messages
    :param scheme: dictionary containing the value to be validated
    :param attr: the attribute associated with the value to be validated
    :param day_first: indicates that the day precedes the month in the string representing the date
    :param default: optional default value, overrides *required*
    :param required: specifies whether a value must be provided
    :param logger: optional logger
    :return: the validated value, or *None* if validation failed
    """
    # import needed module
    from .datetime_pomes import date_parse

    # initialize the return variable
    result: date | None = None

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # obtain the value
    value: str = scheme.get(suffix)

    # validate it
    if value:
        result = date_parse(dt_str=value,
                            dayfirst=day_first)
        if not result:
            # 141: Invalid value {}
            stat = validate_format_error(141, value, f"@{attr}")
        elif result > datetime.now(tz=TIMEZONE_LOCAL).date():
            # 153: Invalid value {}: date is later than the current date
            stat = validate_format_error(153, value, f"@{attr}")
    elif isinstance(default, date):
        result = default
    elif isinstance(required, bool) and required:
        # 121: Required attribute
        stat = validate_format_error(121, f"@{attr}")

    if stat:
        result = None
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
    return result


def validate_datetime(errors: list[str] | None,
                      scheme: dict[str, Any],
                      attr: str,
                      day_first: bool = True,
                      default: datetime = None,
                      required: bool = False,
                      logger: Logger = None) -> datetime:
    """
    Validate the *datetime* value associated with *attr* in *scheme*.

    If provided, this value must be a *date*, or a valid string representation of a *date*.

    :param errors: incidental error messages
    :param scheme: dictionary containing the value to be validated
    :param attr: the attribute associated with the value to be validated
    :param day_first: indicates that the day precedes the month in the string representing the date
    :param default: optional default value, overrides *required*
    :param required: specifies whether a value must be provided
    :param logger: optional logger
    :return: the validated value, or *None* if validation failed
    """
    # import needed module
    from .datetime_pomes import datetime_parse

    # initialize the return variable
    result: datetime | None = None

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # obtain and validate the value
    value: str = scheme.get(suffix)
    if value:
        result = datetime_parse(dt_str=value,
                                dayfirst=day_first)
        if not result:
            # 141: Invalid value {}
            stat = validate_format_error(141, value, f"@{attr}")
        elif result > datetime.now(tz=TIMEZONE_LOCAL):
            # 153: Invalid value {}: date is later than the current date
            stat = validate_format_error(153, value, f"@{attr}")
    elif isinstance(default, datetime):
        result = default
    elif isinstance(required, bool) and required:
        # 121: Required attribute
        stat = validate_format_error(121, f"@{attr}")

    if stat:
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
    return result


def validate_ints(errors: list[str] | None,
                  scheme: dict[str, Any],
                  attr: str,
                  min_val: int = None,
                  max_val: int = None,
                  required: bool = False,
                  logger: Logger = None) -> list[int]:
    """
    Validate the list of *int* values associated with *attr* in *scheme*.

    If provided, this list must contain *int*s, or valid string representations of *int*s.

    :param errors: incidental error messages
    :param scheme: dictionary containing the list of values to be validated
    :param attr: the attribute associated with the list of values to be validated
    :param min_val: the minimum value accepted
    :param max_val:  the maximum value accepted
    :param required: whether the list of values must be provided
    :param logger: optional logger
    :return: the list of validated values, *[]* if not required and no values found, or *None* if validation failed
    """
    # initialize the return variable
    result: list | None = []

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # obtain the values
    values: list = scheme.get(suffix)
    if values:
        if isinstance(values, str):
            values = str_as_list(values)
        if isinstance(values, list):
            result = []
            if len(values) > 0:
                for inx, value in enumerate(values):
                    result.append(value)
                    if isinstance(value, int):
                        stat = validate_value(attr=f"@{attr}[{inx+1}]",
                                              val=value,
                                              min_val=min_val,
                                              max_val=max_val)
                    else:
                        # 152: Invalid value {}: must be type {}
                        stat = validate_format_error(152, value, "int", f"@{attr}[{inx+1}]")
            elif required:
                # 121: Required attribute
                stat = validate_format_error(121, f"@{attr}")
        else:
            # 152: Invalid value {}: must be type {}
            stat = validate_format_error(152, result, "list", f"@{attr}")
    elif required:
        # 121: Required attribute
        stat = validate_format_error(121, f"@{attr}")

    if stat:
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
        result = None

    return result


def validate_strs(errors: list[str] | None,
                  scheme: dict[str, Any],
                  attr: str,
                  min_length: int = None,
                  max_length: int = None,
                  required: bool = False,
                  logger: Logger = None) -> list[str]:
    """
    Validate the list of *str* values associated with *attr* in *scheme*.

    If provided, this list must contain *str*s.

    :param errors: incidental error messages
    :param scheme: dictionary containing the list of values to be validated
    :param attr: the attribute associated with the list of values to be validated
    :param min_length: optional minimum length accepted
    :param max_length:  optional maximum length accepted
    :param required: whether the list of values must be provided
    :param logger: optional logger
    :return: the list of validated values, *[]* if not required and no values found, or *None* if validation failed
    """
    # initialize the return variable
    result: list | None = []

    stat: str | None = None
    pos: int = attr.rfind(".") + 1
    suffix: str = attr[pos:]

    # obtain the values
    values: list = scheme.get(suffix)
    if values:
        if isinstance(values, str):
            values = str_as_list(values)
        if isinstance(values, list):
            result = []
            if len(values) > 0:
                for inx, value in enumerate(values):
                    result.append(value)
                    if isinstance(value, str):
                        stat = validate_value(attr=f"@{attr}[{inx+1}]",
                                              val=value,
                                              min_val=min_length,
                                              max_val=max_length)
                    else:
                        # 152: Invalid value {}: must be type {}
                        stat = validate_format_error(152, value, "str", f"@{attr}[{inx+1}]")
            elif required:
                # 121: Required attribute
                stat = validate_format_error(121, f"@{attr}")
        else:
            # 152: Invalid value {}: must be type {}
            stat = validate_format_error(152, result, "list", f"@{attr}")
    elif required:
        # 121: Required attribute
        stat = validate_format_error(121, f"@{attr}")

    if stat:
        __validate_log(errors=errors,
                       err_msg=stat,
                       logger=logger)
        result = None

    return result


def validate_build_response(errors: list[str],
                            reply: dict) -> Response:
    """
    Build a *Response* object based on the given *errors* list and the set of key/value pairs in *reply*.

    :param errors: the reference errors
    :param reply: the key/value pairs to add to the response as JSON string
    :return: the appropriate *Response* object
    """
    # declare the return variable
    result: Response

    if len(errors) == 0:
        # 'reply' might be 'None'
        result = jsonify(reply)
    else:
        reply_err: dict = {"errors": validate_format_errors(errors=errors)}
        if isinstance(reply, dict):
            reply_err.update(reply)
        result = jsonify(reply_err)
        result.status_code = 400

    return result


def validate_format_error(error_id: int,
                          *args: Any) -> str:
    """
    Format and return the error message identified by *err_id* in the standard messages list.

    The message is built from the message element in the standard messages list, identified by *err_id*.
    The occurrences of '{}' in the element are sequentially replaced by the given *args*.

    :param error_id: the identification of the message element
    :param args: optional arguments to format the error message with
    :return: the formatted error message
    """
    # retrieve the standard validation messages list
    match VALIDATION_MSG_LANGUAGE:
        case "en":
            from .validation_msgs import _ERR_MSGS_EN
            err_msgs = _ERR_MSGS_EN
        case "pt":
            from .validation_msgs import _ERR_MSGS_PT
            err_msgs = _ERR_MSGS_PT
        case _:
            err_msgs = {}

    # initialize the return variable
    result: str = ""
    if VALIDATION_MSG_PREFIX:
        result += VALIDATION_MSG_PREFIX + str(error_id) + ": "
    result += err_msgs.get(error_id) or ""

    # apply the provided arguments
    for arg in args:
        if arg is None:
            pos1: int = result.find(": {}")
            pos2: int = result.find(" {}")
            if pos1 < 0 or pos2 < pos1:
                result = result.replace(" {}", "", 1)
            else:
                result = result.replace(": {}", "", 1)
        elif not result or (isinstance(arg, str) and arg.startswith("@")):
            result += " " + arg
        elif isinstance(arg, str) and arg.find(" ") > 0:
            result = result.replace("{}", arg, 1)
        else:
            result = result.replace("{}", f"'{arg}'", 1)

    return result


def validate_format_errors(errors: list[str]) -> list[dict[str, str]]:
    """
    Build and return a list of dicts from the list of errors *errors*.

    Each element in *errors* is encoded as a *dict*.
    This list is tipically used in a returning *JSON* string.

    :param errors: the list of errors to build the list of dicts with
    :return: the built list
    """
    # initialize the return variable
    result: list[dict[str, str]] = []

    # extract error code, description, and attribute from text
    for error in errors:

        # locate the last indicator for the attribute
        pos = error.rfind("@")

        # is there a whitespace in the attribute's name ?
        if pos > 0 and str_find_whitespace(error[pos:]) > 0:
            # yes, disregard the attribute
            pos = -1

        # was the attribute's name found ?
        if pos == -1:
            # no
            out_error: dict[str, str] = {}
            desc: str = error
        else:
            # yes
            term: str = "attribute" if VALIDATION_MSG_LANGUAGE == "en" else "atributo"
            out_error: dict[str, str] = {term: error[pos + 1:]}
            desc: str = error[:pos - 1]

        # does the text contain an error code ?
        if VALIDATION_MSG_PREFIX and desc.startswith(VALIDATION_MSG_PREFIX):
            # yes
            term: str = "code" if VALIDATION_MSG_LANGUAGE == "en" else "codigo"
            pos: int = desc.find(":")
            out_error[term] = desc[0:pos]
            desc = desc[pos+2:]

        term: str = "description" if VALIDATION_MSG_LANGUAGE == "en" else "descricao"
        out_error[term] = desc
        result.append(out_error)

    return result


def validate_unformat_errors(errors: list[dict[str, str] | str]) -> list[str]:
    """
    Extract and return the list of errors used to build the list of dicts *errors*.

    :param errors: the list of dicts to extract the errors from
    :return: the built list
    """
    # initialize the return variable
    result: list[str] = []

    # define the dictionary keys
    name: str = "code" if VALIDATION_MSG_LANGUAGE == "en" else "codigo"
    desc: str = "description" if VALIDATION_MSG_LANGUAGE == "en" else "descricao"

    # traverse the list of dicts
    for error in errors:
        if isinstance(error, dict):
            desc: str = str_sanitize(error.get(desc) or "''")
            result.append(f"{error.get(name)}: {desc}")
        else:
            result.append(error)

    return result


def __validate_log(errors: list[str],
                   err_msg: str,
                   logger: Logger) -> None:
    """
    LOg *err_msg* using *logger*, and add it to the error messages list *errors*.

    :param errors: the error messages list
    :param err_msg: the message to log
    :param logger: the logger
    """
    if logger:
        logger.error(err_msg)
    if isinstance(errors, list):
        errors.append(err_msg)
