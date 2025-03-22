import secrets
import string
import typing

from terminusgps.wialon import flags, items
from terminusgps.wialon.items.base import WialonBase
from terminusgps.wialon.session import WialonSession


def get_hw_type_id(name: str, session: WialonSession) -> int | None:
    """
    Takes a Wialon hardware type name and returns its id, if it exists.

    :param name: The name of a Wialon hardware type.
    :type name: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :raises WialonError: If something goes wrong during a Wialon API call.
    :returns: A Wialon hardware type id, if it was found.
    :rtype: :py:obj:`int` | :py:obj:`None`

    """
    response = session.wialon_api.core_get_hw_types(
        **{
            "filterType": "id",
            "filterValue": "name,id",
            "includeType": "true",
            "ignoreRename": "true",
        }
    )
    hw_types = {item.get("name"): item.get("id") for item in response}
    return int(hw_types.get(name)) if name in hw_types.keys() else None


def get_id_from_imei(imei: str, session: WialonSession) -> str | None:
    """
    Takes a Wialon unit's IMEI # and returns its unit id.

    :param imei: A Wialon unit's IMEI #.
    :type imei: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :raises ValueError: If ``imei`` contains non-digit characters.
    :raises WialonError: If something goes wrong during a Wialon API call.
    :returns: A Wialon object id, if it was found.
    :rtype: :py:obj:`str` | :py:obj:`None`

    """
    if not imei.isdigit():
        raise ValueError(f"'imei' must be a digit, got '{imei}'.")

    results = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": f"*{imei}*",
                "sortType": "sys_unique_id",
                "propType": "property",
                "or_logic": 0,
            },
            "force": 0,
            "flags": flags.DATAFLAG_UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )

    if results.get("totalItemsCount", 0) == 1:
        return results["items"][0].get("id")


def get_id_from_iccid(iccid: str, session: WialonSession) -> str | None:
    """
    DEPRECATED: Use :py:func:`~terminusgps.wialon.utils.get_id_from_imei`.

    Takes a Wialon unit's IMEI # and returns its unit id, if it exists.

    :param iccid: A unique id.
    :type iccid: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :raises WialonError: If something goes wrong during a Wialon API call.
    :returns: A Wialon object id, if it was found.
    :rtype: :py:obj:`str` | :py:obj:`None`

    """
    return get_id_from_imei(imei=iccid, session=session)


def get_wialon_cls(items_type: str) -> typing.Type[WialonBase]:
    """
    Returns a Wialon object class based on items_type.

    :param items_type: A Wialon object type.
    :type items_type: :py:obj:`str`
    :returns: A subclass of :py:obj:`~terminusgps.wialon.items.base.WialonBase`.
    :rtype: :py:obj:`~terminusgps.wialon.items.base.WialonBase`

    """
    match items_type:
        case "user":
            return items.WialonUser
        case "avl_unit":
            return items.WialonUnit
        case "avl_unit_group":
            return items.WialonUnitGroup
        case "avl_resource":
            return items.WialonResource
        case _:
            raise ValueError(f"Invalid items_type, got '{items_type}'.")


def get_vin_info(vin_number: str, session: WialonSession) -> dict:
    """
    Retrieves vehicle data from a VIN number.

    :param value: A vehicle's VIN number.
    :type value: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A dictionary of vehicle information, if any was found.
    :rtype: :py:obj:`dict`

    """
    response = session.wialon_api.unit_get_vin_info(**{"vin": vin_number}).get(
        "vin_lookup_result"
    )
    return (
        {field.get("n"): field.get("v") for field in response.get("pflds")}
        if "error" not in response.keys()
        else {}
    )


def is_unique(value: str, session: WialonSession, items_type: str = "avl_unit") -> bool:
    """
    Determines if the value is unique among Wialon objects of type 'items_type'.

    :param value: A Wialon object name.
    :type value: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :param items_type: Type of Wialon objects to validate the value against. Default is ``"avl_unit"``.
    :type items_type: :py:obj:`str`
    :raises WialonError: If something goes wrong during a Wialon API call.
    :returns: Whether or not the value is unique among 'items_type'.
    :rtype: :py:obj:`bool`

    """
    return not bool(
        session.wialon_api.core_check_unique(
            **{"type": items_type, "value": value.strip()}
        ).get("result")
    )


def generate_wialon_password(length: int = 32) -> str:
    """
    Generates a Wialon compliant password between ``8`` and ``64`` characters.

    The generated password will contain:

        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one special symbol.
        - At least three digits.

    :param length: Length of the generated password. Default is ``32``.
    :type length: :py:obj:`int`
    :raises ValueError: If :py:length is less than ``8`` or greater than ``64``.
    :returns: A Wialon compliant password.
    :rtype: :py:obj:`str`

    """
    min_length, max_length = 8, 64
    if length > max_length:
        raise ValueError(
            f"Password cannot be greater than {max_length} characters in length. Got {length}."
        )
    elif length < min_length:
        raise ValueError(
            f"Password cannot be less than {min_length} characters in length. Got {length}."
        )

    s0 = list(string.ascii_uppercase)
    s1 = list(string.ascii_lowercase)
    s2 = list(string.digits)
    s3 = list("!@#$%^*()[]-_+")

    while True:
        password = "".join([secrets.choice(s0 + s1 + s2 + s3) for _ in range(length)])
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
            and any(c in s3 for c in password)
        ):
            break
    return password
