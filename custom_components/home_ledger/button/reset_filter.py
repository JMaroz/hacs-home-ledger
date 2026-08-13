"""Reset filter button for home_ledger."""

from custom_components.home_ledger.api import HomeLedgerApiClientError
from custom_components.home_ledger.const import DOMAIN
from custom_components.home_ledger.entity import HomeLedgerEntity
from homeassistant.components.button import ButtonDeviceClass, ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

ENTITY_DESCRIPTIONS: tuple[ButtonEntityDescription, ...] = (
    ButtonEntityDescription(
        key="reset_filter",
        translation_key="reset_filter",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
)


class HomeLedgerButton(ButtonEntity, HomeLedgerEntity):
    """Button that resets the device's filter timer."""

    async def async_press(self) -> None:
        """Reset the filter timer on the device."""
        client = self.coordinator.config_entry.runtime_data.client
        try:
            await client.async_reset_filter()
        except HomeLedgerApiClientError as exception:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="reset_filter_failed",
            ) from exception

        await self.coordinator.async_request_refresh()
