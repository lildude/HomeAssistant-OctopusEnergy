import pytest
from datetime import datetime

from custom_components.octopus_energy.utils import get_active_tariff_code

@pytest.mark.asyncio
async def test_when_active_tariff_available_then_get_active_tariff_code_returns_expected_code():
  # Arrange
  now = datetime.strptime("2022-03-23T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  agreements = [
    {
      'tariff_code': 'G-1R-FIX-12M-18-02-14-G',
      'valid_from': '2018-04-02T00:00:00+01:00',
      'valid_to': '2019-04-02T00:00:00+01:00'
    }, 
    {
      'tariff_code': 'G-1R-FIX-12M-18-12-21-G',
      'valid_from': '2019-04-02T00:00:00+01:00',
      'valid_to': '2020-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-SUPER-GREEN-12M-20-02-12-G',
      'valid_from': '2020-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-VAR-20-10-01-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-FIX-12M-21-02-16-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2022-04-02T00:00:00+01:00'
    }
  ]

  # Act
  result = get_active_tariff_code(now, agreements)

  # Assert
  assert result is not None
  assert result == 'G-1R-FIX-12M-21-02-16-G'

@pytest.mark.asyncio
async def test_when_agreements_ended_then_get_active_tariff_code_returns_none():
  # Arrange
  now = datetime.strptime("2022-04-03T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  agreements = [
    {
      'tariff_code': 'G-1R-FIX-12M-18-02-14-G',
      'valid_from': '2018-04-02T00:00:00+01:00',
      'valid_to': '2019-04-02T00:00:00+01:00'
    }, 
    {
      'tariff_code': 'G-1R-FIX-12M-18-12-21-G',
      'valid_from': '2019-04-02T00:00:00+01:00',
      'valid_to': '2020-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-SUPER-GREEN-12M-20-02-12-G',
      'valid_from': '2020-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-VAR-20-10-01-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-FIX-12M-21-02-16-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2022-04-02T00:00:00+01:00'
    }
  ]

  # Act
  result = get_active_tariff_code(now, agreements)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_agreements_not_started_then_get_active_tariff_code_returns_none():
  # Arrange
  now = datetime.strptime("2018-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  agreements = [
    {
      'tariff_code': 'G-1R-FIX-12M-18-02-14-G',
      'valid_from': '2018-04-02T00:00:00+01:00',
      'valid_to': '2019-04-02T00:00:00+01:00'
    }, 
    {
      'tariff_code': 'G-1R-FIX-12M-18-12-21-G',
      'valid_from': '2019-04-02T00:00:00+01:00',
      'valid_to': '2020-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-SUPER-GREEN-12M-20-02-12-G',
      'valid_from': '2020-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-VAR-20-10-01-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-FIX-12M-21-02-16-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2022-04-02T00:00:00+01:00'
    }
  ]

  # Act
  result = get_active_tariff_code(now, agreements)

  # Assert
  assert result is None

@pytest.mark.asyncio
async def test_when_agreement_has_no_end_date_then_get_active_tariff_code_returns_code():
  # Arrange
  now = datetime.strptime("2022-04-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  agreements = [
    {
      'tariff_code': 'G-1R-FIX-12M-18-02-14-G',
      'valid_from': '2018-04-02T00:00:00+01:00',
      'valid_to': '2019-04-02T00:00:00+01:00'
    }, 
    {
      'tariff_code': 'G-1R-FIX-12M-18-12-21-G',
      'valid_from': '2019-04-02T00:00:00+01:00',
      'valid_to': '2020-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-SUPER-GREEN-12M-20-02-12-G',
      'valid_from': '2020-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-VAR-20-10-01-G',
      'valid_from': '2021-04-02T00:00:00+01:00',
      'valid_to': '2021-04-02T00:00:00+01:00'
    },
    {
      'tariff_code': 'G-1R-FIX-12M-21-02-16-G',
      'valid_from': '2021-04-02T00:00:00+01:00'
    }
  ]

  # Act
  result = get_active_tariff_code(now, agreements)

  # Assert
  assert result is not None
  assert result == 'G-1R-FIX-12M-21-02-16-G'