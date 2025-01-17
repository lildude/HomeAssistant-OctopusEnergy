from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..utils import get_off_peak_cost
from ..utils.rate_information import get_current_rate_information

from .base import OctopusEnergyElectricitySensor

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityOffPeak(CoordinatorEntity, OctopusEnergyElectricitySensor, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if the current rate is off peak."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""

    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)
  
    self._state = None
    self._attributes = {}
    self._last_updated = None

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_off_peak"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Off Peak"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    """Determine if current rate is off peak."""
    current = now()
    rates = self.coordinator.data[self._mpan] if self.coordinator is not None and self._mpan in self.coordinator.data else None
    if (rates is not None and (self._last_updated is None or self._last_updated < (current - timedelta(minutes=30)) or (current.minute % 30) == 0)):
      _LOGGER.debug(f"Updating OctopusEnergyElectricityOffPeak for '{self._mpan}/{self._serial_number}'")
      off_peak_value = get_off_peak_cost(rates)

      rate_information = get_current_rate_information(rates, current)

      self._state = off_peak_value is not None and rate_information is not None and off_peak_value == rate_information["current_rate"]["value_inc_vat"]

      self._last_updated = current
    
    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = state.state
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyElectricityOffPeak state: {self._state}')
