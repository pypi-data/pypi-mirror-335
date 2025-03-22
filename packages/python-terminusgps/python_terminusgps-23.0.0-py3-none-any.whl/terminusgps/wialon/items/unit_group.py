from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonBase


class WialonUnitGroup(WialonBase):
    def create(self, creator_id: str | int, name: str) -> int | None:
        """
        Creates a new Wialon unit group.

        :param creator_id: A Wialon user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: A name for the group.
        :type name: :py:obj:`str`
        :raises ValueError: If ``creator_id`` is not a digit.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: The Wialon id for the new group, if it was created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """

        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_unit_group(
            **{
                "creatorId": creator_id,
                "name": name,
                "dataFlags": flags.DATAFLAG_UNIT_BASE,
            }
        )
        return int(response.get("item", {}).get("id")) if response.get("item") else None

    def set_items(self, new_items: list[str]) -> None:
        """
        Sets this group's members to a list of Wialon unit ids.

        :param new_items: A list of Wialon unit ids.
        :type new_items: :py:obj:`list`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.unit_group_update_units(
            **{"itemId": self.id, "units": new_items}
        )

    def is_member(self, item: WialonBase) -> bool:
        """
        Determines whether or not ``item`` is a member of the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: :py:obj:`True` if ``item`` is a member of the group, else :py:obj:`False`.
        :rtype: :py:obj:`bool`

        """
        return True if item.id in self.items else False

    def add_item(self, item: WialonBase) -> None:
        """
        Adds a Wialon item to the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        new_items: list[str] = self.items.copy() + [str(item.id)]
        self.set_items(new_items)

    def rm_item(self, item: WialonBase) -> None:
        """
        Removes a Wialon unit from the group, if it's a member of the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises AssertionError: If the item wasn't in the group.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.is_member(item), f"Cannot remove {item}, it's not in the group"
        new_items: list[str] = self.items.copy()
        new_items.remove(str(item.id))
        self.set_items(new_items)

    @property
    def items(self) -> list[str]:
        """
        Returns a list of the group's Wialon unit ids.

        :type: :py:obj:`list`

        """
        response = self.session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit_group",
                    "propName": "sys_id",
                    "propValueMask": str(self.id),
                    "sortType": "sys_id",
                    "propType": "property",
                    "or_logic": 0,
                },
                "force": 1,
                "flags": flags.DATAFLAG_UNIT_BASE,
                "from": 0,
                "to": 0,
            }
        )
        return [unit_id for unit_id in response.get("items")[0].get("u", [])]


def main() -> None:
    import logging

    from django.utils import timezone
    from django.conf import settings
    from terminusgps.wialon.session import WialonSession
    from terminusgps.wialon.items import WialonUnit
    from terminusgps.wialon.utils import get_hw_type_id

    timestamp = f"{timezone.now():%Y_%m_%d_%H:%M:%S}"
    with WialonSession(log_level=logging.DEBUG) as session:
        unit = WialonUnit(
            id=None,
            session=session,
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"test_unit_{timestamp}",
            hw_type_id=get_hw_type_id("Test HW", session=session),
        )
        group = WialonUnitGroup(
            id=None,
            session=session,
            creator_id=settings.WIALON_ADMIN_ID,
            name=f"test_group_{timestamp}",
        )
        group.add_item(unit)
        print(f"{group.items = }")
        unit.delete()
        group.delete()
    return


if __name__ == "__main__":
    main()
