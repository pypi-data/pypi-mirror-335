from abc import abstractmethod
from typing import Type

from terminusgps.wialon import flags
from terminusgps.wialon.session import WialonSession


class WialonBase:
    def __init__(
        self, id: str | int | None, session: WialonSession, *args, **kwargs
    ) -> None:
        if isinstance(id, str) and not id.isdigit():
            raise ValueError(f"'id' must be a digit. Got '{id}'.")

        self._session = session
        self._id = str(id if id else self.create(*args, **kwargs))
        self.populate()

    def __str__(self) -> str:
        return str(self.id)

    def populate(self) -> None:
        """Retrieves and saves the latest data for the item from Wialon."""
        response = self.session.wialon_api.core_search_item(
            **{"id": str(self.id), "flags": 0x1}
        ).get("item", {})
        self.name = response.get("nm")
        self.hw_type = response.get("cls")
        self.access_lvl = response.get("uacl")

    @property
    def session(self) -> WialonSession:
        """
        A valid Wialon API session.

        :type: :py:obj:`~terminusgps.wialon.session.WialonSession`

        """

        return self._session

    @property
    def id(self) -> int | None:
        """
        A unique Wialon ID.

        :type: :py:obj:`int` | :py:obj:`None`

        """

        return int(self._id) if self._id else None

    def has_access(self, other: Type["WialonBase"]) -> bool:
        """
        Checks if this Wialon object has access to ``other``.

        :type: :py:obj:`bool`

        """
        response = self.session.wialon_api.core_check_accessors(
            **{"items": [other.id], "flags": False}
        )
        return True if self.id in response.keys() else False

    @abstractmethod
    def create(self, *args, **kwargs) -> int | None:
        """Creates a Wialon object and returns its id."""
        raise NotImplementedError("Subclasses must implement this method.")

    def rename(self, new_name: str) -> None:
        """
        Renames the Wialon object to the new name.

        :param new_name: A new name.
        :type new_name: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_name(
            **{"itemId": self.id, "name": new_name}
        )

    def add_afield(self, field: tuple[str, str]) -> None:
        """
        Adds an admin field to the Wialon object.

        :param field: A tuple containing the name of the field and the value of the field.
        :type field: :py:obj:`tuple`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_admin_field(
            **{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": field[0],
                "v": field[1],
            }
        )

    def update_afield(self, field_id: int, field: tuple[str, str]) -> None:
        """
        Updates an admin field by id to the Wialon object.

        :param field_id: The admin field id.
        :type field_id: :py:obj:`int`
        :param field: A tuple containing the name of the field and the value of the field.
        :type field: :py:obj:`tuple`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_admin_field(
            **{
                "itemId": self.id,
                "id": field_id,
                "callMode": "update",
                "n": field[0],
                "v": field[1],
            }
        )

    def add_cfield(self, field: tuple[str, str]) -> None:
        """
        Adds a custom field to the Wialon object.

        :param field: A tuple containing the name of the field and the value of the field.
        :type field: :py:obj:`tuple`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_custom_field(
            **{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": field[0],
                "v": field[1],
            }
        )

    def update_cfield(self, field_id: int, field: tuple[str, str]) -> None:
        """
        Updates a custom field by id.

        :param field_id: The admin field id.
        :type field_id: :py:obj:`int`
        :param field: A tuple containing the name of the field and the value of the field.
        :type field: :py:obj:`tuple`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_custom_field(
            **{
                "itemId": self.id,
                "id": field_id,
                "callMode": "update",
                "n": field[0],
                "v": field[1],
            }
        )

    def add_cproperty(self, property: tuple[str, str]) -> None:
        """
        Adds a custom property to the Wialon object.

        :param property: A tuple containing the name of the property and the value of the property.
        :type property: :py:obj:`tuple`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_custom_property(
            **{"itemId": self.id, "name": property[0], "value": property[1]}
        )

    def add_profile_field(self, field: tuple[str, str]) -> None:
        """
        Adds a profile field to the Wialon object.

        :param field: A tuple containing the name of the field and the value of the field.
        :type field: :py:obj:`tuple`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_update_profile_field(
            **{"itemId": self.id, "n": field[0], "v": field[1]}
        )

    def delete(self) -> None:
        """
        Deletes the Wialon object.

        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """

        self.session.wialon_api.item_delete_item(**{"itemId": self.id})

    @property
    def cfields(self) -> dict:
        """Custom fields associated with the Wialon object."""
        fields = (
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DATAFLAG_UNIT_CUSTOM_FIELDS}
            )
            .get("item", {})
            .get("cfields")
        )

        return {field["n"]: field["v"] for _, field in fields.items()} if fields else {}

    @property
    def afields(self) -> dict:
        """Admin fields associated with the Wialon object."""
        fields = (
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DATAFLAG_UNIT_ADMIN_FIELDS}
            )
            .get("item", {})
            .get("afields")
        )
        return {field["n"]: field["v"] for _, field in fields.items()} if fields else {}
