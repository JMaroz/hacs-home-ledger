"""Base entity class for ha_integration_domain."""

from typing import TYPE_CHECKING

from custom_components.ha_integration_domain.const import ATTRIBUTION, DOMAIN
from custom_components.ha_integration_domain.coordinator import IntegrationBlueprintDataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class IntegrationBlueprintEntity(CoordinatorEntity[IntegrationBlueprintDataUpdateCoordinator]):
    """
    Base entity providing device info, unique ID and attribution.

    The unique ID is `{entry_id}_{key}`, the documented identifier of last resort.
    A real integration switches to the device's serial, MAC or account ID before its
    first release, because changing it afterwards needs a registry migration.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IntegrationBlueprintDataUpdateCoordinator,
        entity_description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name="Home Ledger",
            manufacturer="Home Ledger",
            model="Home Ledger",
        )
