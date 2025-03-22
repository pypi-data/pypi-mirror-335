Authorizenet API Authentication
===============================

To authorize with the Authorizenet API, use these utility functions to provide data to each API call.

.. currentmodule:: terminusgps.authorizenet.auth

.. py:function:: get_merchant_auth() -> merchantAuthenticationType

    Generates and returns a :py:obj:`~authorizenet.apicontractsv1.merchantAuthenticationType` object.

    This object is generated using :confval:`MERCHANT_AUTH_LOGIN_ID` and :confval:`MERCHANT_AUTH_TRANSACTION_KEY`.

    :returns: A merchant authentication object.
    :rtype: :py:obj:`~authorizenet.apicontractsv1.merchantAuthenticationType`

.. py:function:: get_environment() -> str

    Gets the current application environment for Authorizenet API calls.    

    This string is generated using :confval:`DEBUG`.

    :returns: The current Authorizenet API environment.
    :rtype: :py:obj:`str`

.. py:function:: get_validation_mode() -> str

    Gets the current application validation mode for Authorizenet API calls.    

    This string is generated using :confval:`DEBUG`.

    :returns: The current Authorizenet API validation mode.
    :rtype: :py:obj:`str`
