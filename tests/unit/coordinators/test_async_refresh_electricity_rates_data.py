from datetime import datetime, timedelta
import pytest
import mock

from unit import (create_rate_data)

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.coordinators.electricity_rates import async_refresh_electricity_rates_data

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_from = datetime.strptime("2023-07-14T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
period_to = datetime.strptime("2023-07-15T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

tariff_code = "E-1R-SUPER-GREEN-24M-21-07-30-A"
mpan = "1234567890"
serial_number = "abcdefgh"

def get_account_info(is_active_agreement = True):
  return {
    "electricity_meter_points": [
      {
        "mpan": mpan,
        "meters": [
          {
            "serial_number": serial_number,
            "is_export": False,
            "is_smart_meter": True,
            "device_id": "",
            "manufacturer": "",
            "model": "",
            "firmware": ""
          }
        ],
        "agreements": [
          {
            "valid_from": "2023-07-01T00:00:00+01:00" if is_active_agreement else "2023-08-01T00:00:00+01:00",
            "valid_to": "2023-08-01T00:00:00+01:00" if is_active_agreement else "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

@pytest.mark.asyncio
async def test_when_account_info_is_none_then_existing_rates_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  account_info = None
  existing_rates = {
    mpan: create_rate_data(period_from, period_to, [2, 4])
  }
  dispatches = { "planned": [], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert retrieved_rates == existing_rates
    assert rates_returned == False

@pytest.mark.asyncio
async def test_when_no_active_rates_then_empty_rates_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  account_info = get_account_info(False)
  existing_rates = {
    mpan: create_rate_data(period_from, period_to, [2, 4])
  }
  dispatches = { "planned": [], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert retrieved_rates == {}
    assert rates_returned == False

@pytest.mark.asyncio
async def test_when_current_is_not_thirty_minutes_then_existing_rates_returned():
  for minute in range(60):
    if minute == 0 or minute == 30:
      continue

    current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z").replace(minute=minute)
    expected_rates = create_rate_data(period_from, period_to, [1, 2])
    rates_returned = False
    async def async_mocked_get_electricity_rates(*args, **kwargs):
      nonlocal rates_returned
      rates_returned = True
      return expected_rates
    
    account_info = get_account_info()
    existing_rates = {
      mpan: create_rate_data(period_from, period_to, [2, 4])
    }
    dispatches = { "planned": [], "completed": [] }

    with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
      client = OctopusEnergyApiClient("NOT_REAL")
      retrieved_rates = await async_refresh_electricity_rates_data(
        current,
        client,
        account_info,
        existing_rates,
        dispatches
      )

      assert retrieved_rates == existing_rates
      assert rates_returned == False

@pytest.mark.asyncio
async def test_when_existing_rates_is_none_then_rates_retrieved():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  requested_period_from = None
  requested_period_to = None
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal requested_period_from, requested_period_to, rates_returned

    requested_client, requested_tariff_code, is_smart_meter, requested_period_from, requested_period_to = args
    rates_returned = True
    return expected_rates
  
  account_info = get_account_info()
  existing_rates = None
  expected_retrieved_rates = {
    mpan: expected_rates
  }
  dispatches = { "planned": [], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert retrieved_rates == expected_retrieved_rates
    assert rates_returned == True
    assert requested_period_from == (current - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    assert requested_period_to == (current + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
  
@pytest.mark.asyncio
async def test_when_key_not_in_existing_rates_is_none_then_rates_retrieved():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  account_info = get_account_info()
  existing_rates = {}
  expected_retrieved_rates = {
    mpan: expected_rates
  }
  dispatches = { "planned": [], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert retrieved_rates == expected_retrieved_rates
    assert rates_returned == True

@pytest.mark.asyncio
async def test_when_existing_rates_is_old_then_rates_retrieved():
  expected_rates = create_rate_data(period_from, period_to, [1, 2])
  rates_returned = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  account_info = get_account_info()
  existing_rates = {
    mpan: create_rate_data(period_from - timedelta(days=60), period_to - timedelta(days=60), [2, 4])
  }
  expected_retrieved_rates = {
    mpan: expected_rates
  }
  dispatches = { "planned": [], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert retrieved_rates == expected_retrieved_rates
    assert rates_returned == True

@pytest.mark.asyncio
async def test_when_dispatched_rates_provided_then_rates_are_adjusted():
  expected_rates = create_rate_data(period_from, period_to, [1, 2, 3, 4])
  rates_returned = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return expected_rates
  
  account_info = get_account_info()
  existing_rates = {}
  expected_retrieved_rates = {
    mpan: expected_rates
  }
  dispatches = { "planned": [{
    "start": datetime.strptime("2023-07-14T02:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    "end": datetime.strptime("2023-07-14T03:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z"),
    "source": "smart-charge"
  }], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert len(retrieved_rates) == len(expected_retrieved_rates)
    assert mpan in retrieved_rates
    assert len(retrieved_rates[mpan]) == len(expected_retrieved_rates[mpan])

    for index in range(len(retrieved_rates[mpan])):
      expected_rate = expected_retrieved_rates[mpan][index]
      actual_rate = retrieved_rates[mpan][index]

      if (index == 5 or index == 6):
        assert "is_intelligent_adjusted" in actual_rate
        assert actual_rate["is_intelligent_adjusted"] == True
        assert actual_rate["value_inc_vat"] == 1
      else:
        assert "is_intelligent_adjusted" not in actual_rate
        assert expected_rate == actual_rate

    assert rates_returned == True

@pytest.mark.asyncio
async def test_when_rates_not_retrieved_then_existing_rates_returned():
  expected_rates = create_rate_data(period_from, period_to, [1, 2, 3, 4])
  rates_returned = False
  async def async_mocked_get_electricity_rates(*args, **kwargs):
    nonlocal rates_returned
    rates_returned = True
    return None
  
  account_info = get_account_info()
  existing_rates = {
    mpan: expected_rates
  }
  dispatches = { "planned": [], "completed": [] }

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_electricity_rates=async_mocked_get_electricity_rates):
    client = OctopusEnergyApiClient("NOT_REAL")
    retrieved_rates = await async_refresh_electricity_rates_data(
      current,
      client,
      account_info,
      existing_rates,
      dispatches
    )

    assert retrieved_rates is not None
    assert mpan in retrieved_rates
    assert retrieved_rates[mpan] == expected_rates
    assert rates_returned == True