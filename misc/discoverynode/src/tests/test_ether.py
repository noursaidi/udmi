# pylint: disable=protected-access

"""Test discovery controller's logic"""
from unittest import mock
from typing import Callable
import pytest
import udmi.schema.state as state
import udmi.discovery.ether
import time
import datetime
import udmi.schema.state
import udmi.schema.util 
import logging
import sys

stdout = logging.StreamHandler(sys.stdout)
stdout.addFilter(lambda log: log.levelno < logging.WARNING)
stdout.setLevel(logging.INFO)
stderr = logging.StreamHandler(sys.stderr)
stderr.setLevel(logging.WARNING)
logging.basicConfig(
    format="%(asctime)s|%(levelname)s|%(module)s:%(funcName)s %(message)s",
    handlers=[stderr, stdout],
    level=logging.INFO,
)
logging.root.setLevel(logging.DEBUG)


def make_timestamp(*,seconds_from_now = 0):
  return udmi.schema.util.datetime_serializer(udmi.schema.util.current_time_utc() + datetime.timedelta(seconds=seconds_from_now))


def test_chain():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  ether = udmi.discovery.ether.EtherDiscovery(
      mock_state, mock_publisher
  )

  with mock.patch.object(ether, 'nmap_start_discovery') as mock_namp_start_discovery, \
       mock.patch.object(ether, 'ping_start_discovery') as mock_ping_start_discovery, \
       mock.patch.object(ether, 'nmap_stop_discovery') as mock_nmap_stop_discovery, \
       mock.patch.object(ether, 'ping_stop_discovery') as mock_ping_stop_discovery:

    ether.controller({
        "discovery": {
            "families": {"ether": {"generation": make_timestamp(), "depth": 'ping'}}
        }
    })
    time.sleep(1)
    mock_namp_start_discovery.assert_not_called()
    mock_ping_start_discovery.assert_called_once()

    ether.controller({
        "discovery": {
            "families": {"ether": {"generation": make_timestamp(), "depth": 'ports'}}
        }
    })
    time.sleep(1)
    mock_nmap_stop_discovery.assert_not_called()
    mock_ping_stop_discovery.assert_called_once()
    mock_ping_start_discovery.assert_called_once()
    mock_ping_start_discovery.assert_called_once()

    ether.controller({
        "discovery": {
            "families": {"ether": {}}
        }
    })
    time.sleep(1)
    mock_nmap_stop_discovery.assert_called_once()
    
  
def test_start_nmap():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  ether = udmi.discovery.ether.EtherDiscovery(
      mock_state, mock_publisher
  )

  with mock.patch.object(ether, 'nmap_start_discovery') as mock_namp_start_discovery, \
      mock.patch.object(ether, 'ping_start_discovery') as mock_ping_start_discovery:
    generation = make_timestamp()
    config = {
        "discovery": {
            "families": {"ether": {"generation": generation, "depth": 'ports'}}
        }
    }
  
    ether.controller(config)
    time.sleep(1)
    mock_namp_start_discovery.assert_called_once()
    mock_ping_start_discovery.assert_not_called()
