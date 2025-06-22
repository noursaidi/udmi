# pylint: disable=protected-access

"""Test discovery controller's logic"""
from unittest import mock
from typing import Callable
import pytest
import udmi.schema.state as state
import udmi.discovery.discovery as discovery
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



def test_nmap_bathometer_depth_1():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  nmap_scan = udmi.discovery.nmap.NmapBannerScan(
      mock_state, mock_publisher, target_ips=["127.0.0.1"]
  )

  with mock.patch("threading.Thread") as mock_thread:
    generation = make_timestamp()
    config = {
        "discovery": {
            "families": {"ether": {"generation": generation, "scan_depth": 1}}
        }
    }
    nmap_scan.controller(config)

    mock_thread.assert_called_once()
    call_args = mock_thread.call_args

    assert call_args.kwargs["target"] == nmap_scan.nmap_runner

    nmap_args = call_args.kwargs["args"][0]
    expected_nmap_args = ["-T4", "-F", "127.0.0.1"]
    assert nmap_args == expected_nmap_args


def test_nmap_bathometer_depth_2():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  nmap_scan = udmi.discovery.nmap.NmapBannerScan(
      mock_state, mock_publisher, target_ips=["127.0.0.1"]
  )

  with mock.patch("threading.Thread") as mock_thread:
    generation = make_timestamp()
    config = {
        "discovery": {
            "families": {"ether": {"generation": generation, "scan_depth": 2}}
        }
    }
    nmap_scan.controller(config)

    mock_thread.assert_called_once()
    call_args = mock_thread.call_args

    assert call_args.kwargs["target"] == nmap_scan.nmap_runner

    nmap_args = call_args.kwargs["args"][0]
    expected_nmap_args = ["--script", "banner", "-p-", "-T4", "-A", "127.0.0.1"]
    assert nmap_args == expected_nmap_args


def test_nmap_bathometer_default_depth():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  nmap_scan = udmi.discovery.nmap.NmapBannerScan(
      mock_state, mock_publisher, target_ips=["127.0.0.1"]
  )

  with mock.patch("threading.Thread") as mock_thread:
    generation = make_timestamp()
    config = {"discovery": {"families": {"ether": {"generation": generation}}}}
    nmap_scan.controller(config)

    mock_thread.assert_called_once()
    nmap_args = mock_thread.call_args.kwargs["args"][0]
    expected_nmap_args = ["-T4", "-F", "127.0.0.1"]  # default depth 1
    assert nmap_args == expected_nmap_args


def test_nmap_bathometer_unsupported_depth():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  nmap_scan = udmi.discovery.nmap.NmapBannerScan(
      mock_state, mock_publisher, target_ips=["127.0.0.1"]
  )

  with mock.patch("threading.Thread") as mock_thread:
    generation = make_timestamp()
    config = {
        "discovery": {
            "families": {"ether": {"generation": generation, "scan_depth": 99}}
        }
    }
    nmap_scan.controller(config)

    mock_thread.assert_not_called()


def test_nmap_bathometer_swap_depths():
  mock_state = udmi.schema.state.State()
  mock_publisher = mock.MagicMock()
  nmap_scan = udmi.discovery.nmap.NmapBannerScan(
      mock_state, mock_publisher, target_ips=["127.0.0.1"]
  )

  with mock.patch("threading.Thread") as mock_thread:
    mock_thread_instance = mock.MagicMock()
    mock_thread.return_value = mock_thread_instance

    # --- First config: depth 1 ---
    config1 = {
        "discovery": {
            "families": {"ether": {"generation": make_timestamp(), "scan_depth": 1}}
        }
    }
    nmap_scan.controller(config1)

    # --- Second config: depth 2 ---
    config2 = {
        "discovery": {
            "families": {
                "ether": {"generation": make_timestamp(seconds_from_now=1), "scan_depth": 2}
            }
        }
    }
    nmap_scan.controller(config2)

    mock_thread_instance.join.assert_called_once()
    assert mock_thread.call_count == 2
    nmap_args = mock_thread.call_args.kwargs["args"][0]
    expected_nmap_args = ["--script", "banner", "-p-", "-T4", "-A", "127.0.0.1"]
    assert nmap_args == expected_nmap_args
