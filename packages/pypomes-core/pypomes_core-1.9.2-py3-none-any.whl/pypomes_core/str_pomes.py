import random
import string
from contextlib import suppress
from datetime import date
from pathlib import Path
from typing import Any


def str_to_hex(source: str) -> str:
    """
    Obtain and return the hex representation of *source*.

    This is an encapsulation of the built-in methods *<str>.encode()* and *<bytes>.hex()*.

    :param source: the input string
    :return: the hex representation of the input string
    :raises AttributeError: *source* is not a string
    :raises UnicodeEncodeError:  a UTF-8 encoding error occurred
    """
    return source.encode().hex()


def str_from_hex(source: str) -> str:
    """
    Obtain and return the original string from its hex representation in *source*.

    This is an encapsulation of the built-in methods *bytes.fromhex()* and *<bytes>.decode()*

    :param source: the hex representation of a string
    :return: the original string
    :raises ValueError: *source* is not a valid hexadecimal string
    :raises TypeError: *source* is not a string
    :raises UnicodeDecodeError: a UTF-8 decoding error occurred
    """
    return bytes.fromhex(source).decode()


def str_as_list(source: str | Any,
                separator: str = ",") -> list | Any:
    """
    Return *source* as a *list*, by splitting its contents separated by *separator*.

    The returned substrings are fully whitespace-trimmed.
    If *source* is not a non-empty *str*, then it is itself returned.

    :param source: the string value to be worked on
    :param separator: the separator (defaults to ",")
    :return: a list built from the contents of *source*, or *source* itself, if is not a string
    """
    # declare the return variable
    result: list | Any

    if source and isinstance(source, str):
        result = [s.strip() for s in source.split(sep=separator)]
    else:
        result = source

    return result


def str_sanitize(target_str: str) -> str:
    """
    Clean the given *target_str* string.

    The sanitization is carried out by:
        - removing backslashes
        - replacing double quotes with single quotes
        - replacing newlines and tabs with whitespace
        - replacing multiple consecutive spaces with a single space

    :param target_str: the string to be cleaned
    :return: the cleaned string
    """
    cleaned: str = target_str.replace("\\", "") \
                             .replace('"', "'") \
                             .replace("\n", " ") \
                             .replace("\t", " ")
    return " ".join(cleaned.split())


def str_split_on_mark(source: str,
                      mark: str) -> list[str]:
    """
    Extract from *source* the text segments separated by *mark*, and return them in a *list*.

    The separator itself will not be in the returned list.

    :param source: the string to be inspected
    :param mark: the separator
    :return: the list of text segments extracted
    """
    # inicializa a variável de retorno
    result: list[str] = []

    pos: int = 0
    skip: int = len(mark)
    after: int = source.find(mark)
    while after >= 0:
        result.append(source[pos:after])
        pos = after + skip
        after = source.find(mark, pos)
    if pos < len(source):
        result.append(source[pos:])
    else:
        result.append("")

    return result


def str_find_char(source: str,
                  chars: str) -> int:
    """
    Locate and return the position of the first occurence, in *source*, of a character in *chars*.

    :param source: the string to be inspected
    :param chars: the reference characters
    :return: the position of the first character in *chars*, or -1 if none was found
    """
    # initialize the return variable
    result: int = -1

    # search for whitespace
    for inx, char in enumerate(source):
        if char in chars:
            result = inx
            break

    return result


def str_find_whitespace(source: str) -> int:
    """
    Locate and return the position of the first occurence of a *whitespace* character in *source*.

    :param source: the string to be inspected
    :return: the position of the first whitespace character, or -1 if none was found
    """
    # initialize the return variable
    result: int = -1

    # search for whitespace
    for inx, char in enumerate(source):
        if char.isspace():
            result = inx
            break

    return result


def str_between(source: str,
                from_str: str,
                to_str: str) -> str:
    """
    Extract and return the *substring* in *source* located between the delimiters *from_str* and *to_str*.

    :param source: the string to be inspected
    :param from_str: the initial delimiter
    :param to_str: the final delimiter
    :return: the extracted substring, or None if no substring was obtained
    """
    # initialize the return variable
    result: str | None = None

    pos1: int = source.find(from_str)
    if pos1 >= 0:
        pos1 += len(from_str)
        pos2: int = source.find(to_str, pos1)
        if pos2 >= pos1:
            result = source[pos1:pos2]

    return result


def str_positional(source: str,
                   list_origin: list[str],
                   list_dest: list) -> Any:
    """
    Locate the position of *source* within *list_origin*, and return the element in the same position in *list_dest*.

    :param source: the source string
    :param list_origin: the list to be inspected
    :param list_dest: the list containing the positionally corresponding values
    :return: the value positionally corresponding to the source string, or None if not found
    """
    # declare the return variable
    result: Any | None

    try:
        pos: int = list_origin.index(source)
        result = list_dest[pos]
    except (TypeError, ValueError, IndexError):
        result = None

    return result


def str_random(size: int,
               chars: str | list[str] = None) -> str:
    """
    Generate and return a random string containing *len* characters.

    If *chars* is  provided, either as a string or as a list of characters, the characters
    therein will be used in the construction of the random string. Otherwise, a concatenation of
    *string.ascii_letters*, *string.digits*, and *string.puctuation* will provide the base characters.

    :param size: the length of the target random string
    :param chars: optional characters to build the random string from (a string or a list of characteres)
    :return: the random string
    """
    # establish the base characters
    if not chars:
        chars: str = string.ascii_letters + string.digits + string.punctuation
    elif isinstance(chars, list):
        chars: str = "".join(chars)

    # generate and return the random string
    # ruff: noqa: S311
    return "".join(random.choice(seq=chars) for _ in range(size))


def str_rreplace(source: str,
                 old: str,
                 new: str,
                 count: int = 1) -> str:
    """
    Replace at most *count* occurrences of substring *old* with string *new* in *source*, in reverse order.

    :param source: the string to have a substring replaced
    :param old: the substring to replace
    :param new: the string replacement
    :param count: the maximum number of replacements (defaults to 1)
    :return: the modified string
    """
    return source[::-1].replace(old[::-1], new[::-1], count)[::-1]


def str_to_lower(source: Any) -> str:
    """
    Safely convert *source* to lower-case.

    If *source* is not a *str*, then it is itself returned.

    :param source: the string to convert to lower-case
    :return: *source* in lower-case, or *source* itself, if is not a string
    """
    return source.lower() if isinstance(source, str) else source


def str_to_upper(source: Any) -> str:
    """
    Safely convert *source* to upper-case.

    If *source* is not a *str*, then it is itself returned.

    :param source: the string to convert to upper-case
    :return: *source* in upper-case, or *source* itself, if it is not a string
    """
    return source.upper() if isinstance(source, str) else source


def str_from_any(source: Any) -> str:
    """
    Convert *source* to its string representation.

    These are the string representations returned:
        - *None*: the string 'None'
        - *bool*: the string 'True' of 'Talse'
        - *str* : the source string itself
        - *bytes*: its hex representation
        - *date*: the date in ISO format (*datetime* is a *date* subtype)
        - *Path*: its POSIX form
        - all other types: their *str()* representation

    :param source: the data to be converted to string.
    :return: the string representation of the source data
    """
    # declare the return variable
    result: str

    # obtain the string representation
    if isinstance(source, bytes):
        result = source.hex()
    elif isinstance(source, date):
        result = source.isoformat()
    elif isinstance(source, Path):
        result = source.as_posix()
    else:
        result = str(source)

    return result


def str_to_bool(source: str) -> bool:
    """
    Obtain and return the *bool* value encoded in *source*.

    These are the criteria:
        - case is disregarded
        - the string values accepted to stand for *True* are *1*, *t*, or *true*
        - the string values accepted to stand for *False* are *0*, *f*, or *false*
        - all other values causes *None* to be returned

    :param source: the encoded bool value
    :return: the decoded bool value
    """
    # noinspection PyUnusedLocal
    result: bool | None = None
    if source in ["1", "t", "true"]:
        result = True
    elif source in ["0", "f", "false"]:
        result = False

    return result


def str_to_int(source: str,
               values: list[float] = None) -> int:
    """
    Obtain and return the *int* value encoded in *source*.

    If *values* is specified, the value obtained is checked for occurrence therein.
    If no valid value was obtained, *None* is returned.

    :param source: the encoded int value
    :param values: optional list of valid values
    :return: the decoded int value
    """
    # noinspection PyUnusedLocal
    result: int | None = None
    with suppress(Exception):
        result = int(source)
    if values and result not in values:
        result = None

    return result


def str_to_float(source: str,
                 values: list[float] = None) -> float:
    """
    Obtain and return the *float* value encoded in *source*.

    If *values* is specified, the value obtained is checked for occurrence therein.
    If no valid value was obtained, *None* is returned.

    :param source: the encoded float value
    :param values: optional list of valid values
    :return: the decoded float value
    """
    # noinspection PyUnusedLocal
    result: float | None = None
    with suppress(Exception):
        result = float(source)
    if values and result not in values:
        result = None

    return result
