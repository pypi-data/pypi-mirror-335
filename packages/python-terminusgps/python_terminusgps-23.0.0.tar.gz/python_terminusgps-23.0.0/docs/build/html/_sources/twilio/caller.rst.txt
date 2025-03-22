Caller object
=============


.. currentmodule:: terminusgps.twilio.caller

.. py:class:: TwilioCaller

    An asyncronous phone messager/caller.

    .. py:method:: create_notification(to_number, message, [method="sms"]) -> asyncio.Task

        Creates a task that must be awaited in an asyncronous event loop in order to be executed.

        :meta async:
        :param to_number: A phone number, starting with a '+' and country code.
        :type to_number: :py:obj:`str`
        :param message: A message to send to `to_number`.
        :type message: :py:obj:`str`
        :param method: Notification method to use. Default is ``"sms"``.
        :type method: :py:obj:`str`
        :returns: An awaitable notification task.
        :rtype: :py:obj:`asyncio.Task`

    .. py:method:: create_call(to_number, message) -> None

        Creates a phone call task.

        :meta async:
        :param to_number: A phone number, starting with a '+' and country code.
        :type to_number: :py:obj:`str`
        :param message: A message to send to `to_number`.
        :type message: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

    .. py:method:: create_sms(to_number, message) -> None

        Creates an sms message task.

        :meta async:
        :param to_number: A phone number, starting with a '+' and country code.
        :type to_number: :py:obj:`str`
        :param message: A message to send to `to_number`.
        :type message: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`
