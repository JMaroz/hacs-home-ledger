"""Config flow schemas for the user step."""

import voluptuous as vol


def get_user_schema() -> vol.Schema:
    """
    Build the schema for the user step.

    Returns:
        The voluptuous schema for the setup confirmation form.

    """
    return vol.Schema({})


__all__ = ["get_user_schema"]
