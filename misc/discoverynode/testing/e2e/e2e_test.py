from collections.abc import Callable
import contextlib
import copy
import datetime
import glob
import json
import json
import os
from pathlib import Path
import random
import re
import shutil
import shutil
import signal
import ssl
import subprocess
import sys
import time
import time
from typing import Any
from typing import Any
from typing import Iterator
import textwrap
import shlex
from logging import info, warning, error

import pytest

ROOT_DIR = os.path.dirname(__file__)
UDMI_DIR = str(Path(__file__).parents[4])

# Assume the UDMI Directory is the UDMI directory and has not moved
assert UDMI_DIR.rsplit("/", 1)[1] == "udmi"

"""
devices_list = [
    x.parent.stem
    for x in Path(SITE_PATH).glob(
        os.path.join("udmi/devices/*/rsa_private.pem")
    )
]
"""


def until_true(func: Callable, message: str, **kwargs):
  """Blocks until given func returns True

  Raises:
    Exception if timeout has elapsed
  """
  timeout = kwargs.get("timeout", 0)
  interval = kwargs.get("interval", 0.1)

  expiry_time = time.time() + timeout
  while time.time() < expiry_time or timeout == 0:
    if func():
      return True
    if "do" in kwargs:
      kwargs["do"]()
    time.sleep(interval)
  raise Exception(f"Timed out waiting {timeout}s for {message}")


def dict_paths(thing: dict[str:Any], stem: str = "") -> Iterator[str]:
  """Returns json paths (in dot notation) from a given dictionary."""
  for k, v in thing.items():
    path = f"{stem}.{k}" if stem else k
    if isinstance(v, dict):
      yield from dict_paths(v, path)
    else:
      yield path


def normalize_keys(target: dict[Any:Any], replacement, *args):
  """Replaces value of given keys in a nested dictionary with given replacement."""
  for k, v in target.items():
    if k in args:
      target[k] = replacement
    elif isinstance(v, dict):
      normalize_keys(v, replacement, *args)
  return target




def localnet_block_from_id(id: int):
  """Generates localnet block f"""
  if id > 250:
    # because IP allocation and mac address assignment
    raise RuntimeError("more than 250 devices not supported")

  return {
      "ipv4": {"addr": f"123.123.123.{id}"},
      "ethmac": {"addr": f"00:00:aa:bb:cc:{id:02x}"},
      "bacnet": {"addr": str(3000 + id)},
  }



def run(cmd: str) -> subprocess.CompletedProcess:
  """Runs the given command inside the UDMI directory and wait for it to complete"""
  # stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
  info(cmd)
  result = subprocess.run(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr, cwd=UDMI_DIR)
  return result

def is_registrar_done() -> bool:
  run("git pull")
  history_files = list(Path(SITE_PATH).glob("udmi/history/*.json"))

  # we've deleted the history so there will only be one file
  assert len(history_files) <= 1

  if history_files:
    # currently file is empty at start, and only written to at the end
    return history_files[0].stat().st_size > 0

@pytest.fixture
def docker_devices():
  def _docker_devices(*, devices):
    for i in devices:
      localnet = localnet_block_from_id(i)
      run(shlex.join([
          "docker", "run", "--rm", "-d", 
          f"--name=discoverynode-test-device{i}",
          f"--network=discoverynode-network",
          "-e", f"BACNET_ID={localnet['bacnet']['addr']}",
          "test-bacnet-device"
      ]))

  yield _docker_devices

  run("docker ps -a | grep 'discoverynode-test-device' | awk '{print $1}' | xargs docker stop")

@pytest.fixture
def discovery_node():
  
  def _discovery_node(*, device_id, project_id, registry_id, key_file, algorithm):
    config = {
      "mqtt": {
        "device_id": device_id,
        "host": "mqtt.bos.goog",
        "port": 8883,
        "registry_id": registry_id,
        "region": "us-central1",
        "project_id": project_id,
        "key_file": key_file,
        "algorithm": algorithm
      },
      "nmap":{
        "targets": ["127.0.0.1"],
        "interface": "eth0"
      },
      "bacnet": {}
    }

    with open(
        os.path.join(ROOT_DIR, "discovery_node_config.json"), mode="w", encoding="utf-8"
    ) as f:
        json.dump(config, f, indent=2) 

    run(shlex.join([
        "docker", "run", "--rm", "-d", 
        f"--name=discoverynode-test-node",
        f"--network=discoverynode-network",
        "--mount", f"type=bind,source={ROOT_DIR}/discovery_node_config.json,target=/usr/src/app/config.json",
        "--mount", f"type=bind,source={ROOT_DIR}/rsa_private.pem,target=/usr/src/app/rsa_private.pem",
        "test-discovery_node", "python3",  "main.py", "--config_file=config.json"
    ]))


  yield _discovery_node
  info("logs::::")
  run("docker logs discoverynode-test-node")
  run("docker ps -a | grep 'discoverynode-test-node' | awk '{print $1}' | xargs docker stop")


def test_e2e(new_site_model, docker_devices, discovery_node):
  site_path = os.path.join(UDMI_DIR, "sites", "e2e")

  new_site_model(
      path=site_path,
      delete=True,
      name="ZZ-TRI-FECTA",
      number_of_devices=5,
      devices_with_localnet_block=range(1, 50),
      discovery_node_id="GAT-1",
      discovery_node_is_gateway=True,
      discovery_node_key_path=".",
      discovery_node_families=["bacnet"],
  )

  docker_devices(devices=range(1, 10))

  info("deleting existing site model")

  run("bin/registrar sites/e2e //gbos/bos-platform-dev -d")

  run("bin/registrar sites/e2e //gbos/bos-platform-dev ")

  # Note: After running registrar
  discovery_node(
    device_id="GAT-1",
    project_id="bos-platform-dev",
    registry_id="ZZ-TRI-FECTA",
    key_file="/usr/src/app/rsa_private.pem",
    algorithm="RS256"
  )

  run("bin/mapper GAT-1 provision")

  time.sleep(5)

  run("bin/mapper GAT-1 discover")

  time.sleep(30)

  run("bin/registrar sites/e2e //gbos/bos-platform-dev")

@pytest.fixture
def new_site_model():

  def _new_site_model(
      *,
      delete,
      path,
      name,
      number_of_devices,
      devices_with_localnet_block,
      discovery_node_id,
      discovery_node_is_gateway,
      discovery_node_key_path,
      discovery_node_families,
  ):

    device_prefix = "DDC"
    
    if delete:
      with contextlib.suppress(FileNotFoundError):
        shutil.rmtree(path)
    
    os.mkdir(path)

    #############

    # Copy reflector from udmi_site_model
    shutil.copytree(os.path.join(UDMI_DIR, "sites/udmi_site_model/reflector"), os.path.join(path, "reflector"))
    
    
    #############3

    cloud_iot_config = {
      "cloud_region": "us-central1",
      "site_name": name,
      "registry_id": name
    }

    with open(
        os.path.join(path, "cloud_iot_config.json"), mode="w", encoding="utf-8"
    ) as f:
        json.dump(cloud_iot_config, f, indent=2)

    os.mkdir(os.path.join(path, "devices"))

    ##########################

    # Create gateway
    os.mkdir(os.path.join(path, "devices", discovery_node_id))
    gateway_metadata = {
      "system": {
        "location": {
          "section": "2-3N8C"
        },
        "physical_tag": {
          "asset": {
            "guid": "drw://TBB",
            "site": "ZZ-TRI-FECTA",
            "name": discovery_node_id
          }
        }
      },
      "discovery": {
        "families": { }
      },
      "cloud": {
        "auth_type": "RS256"
      },
      "version": "1.5.1",
      "timestamp": "2020-05-01T13:39:07Z"
    }

    for family in discovery_node_families:
      gateway_metadata["discovery"]["families"][family] = {}
    
    if discovery_node_is_gateway:
      gateway_metadata["gateway"] = {"proxy_ids": []}
    
    gateway_path = os.path.join(path, "devices", discovery_node_id)
    
    with open(
        os.path.join(gateway_path, "metadata.json"), mode="w", encoding="utf-8"
    ) as f:
        json.dump(gateway_metadata, f, indent=2)

    shutil.copyfile(os.path.join(discovery_node_key_path, "rsa_public.pem"), os.path.join(gateway_path, "rsa_public.pem"))
    shutil.copyfile(os.path.join(discovery_node_key_path, "rsa_private.pem"), os.path.join(gateway_path, "rsa_private.pem"))
    ##############################

    base_device_public_key = textwrap.dedent("""
          -----BEGIN PUBLIC KEY-----
          MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvpaY1jwJWa3yQy5DKomL
          qYjuTeUekS1OSZxVFr5RclgsWJBTph+7Myfp9dCVpYCR6am4ycRWayp9DqmhSP6q
          9B4VIUDjV/PBuLvqrfL5XhVZUyMNcg1WlehfdsZWLzG5X5gGfGri7LqvmYIz3eHz
          yxkUV5t0sRhuZFk5wT2PrD7MWtjAIfEJmA6dZ5o/Jix3bF4wMsvFBK9XDRHibcS7
          o/3hw/1FABL+Bgw4L41CtrzRLYKmmRTvsIT8jXuUuptsf+58b9A1kWWsV0AIKjaJ
          73fh+iR8TBe5FDc8MwSgjgophYXBVCgzlIOkX7gwIiAYQWbWOFU9ltzIMgp7JsdR
          vwIDAQAB
          -----END PUBLIC KEY-----
    """).strip()

    for i in range(1, number_of_devices):
      device_id = f"{device_prefix}-{i}"
      device_path = os.path.join(path, "devices", device_id)
      os.mkdir(device_path)
      
      device_metadata =  {
        "system": {
          "location": {
            "section": "2-3N8C",
            "site": name
          },
          "physical_tag": {
            "asset": {
              "guid": "drw://TBB",
              "site": name,
              "name": device_id
            }
          }
        },
        "cloud": {
          "auth_type": "RS256"
        },
        "version": "1.5.1",
        "timestamp": "2020-05-01T13:39:07Z"
    }

      if i in devices_with_localnet_block:
        device_metadata["localnet"] = {}
        device_metadata["localnet"]["families"] = localnet_block_from_id(i)


      with open(
          os.path.join(device_path, "metadata.json"), mode="w", encoding="utf-8"
      ) as f:
        json.dump(device_metadata, f, indent=2)

      with open(
          os.path.join(device_path, "rsa_public.pem"), mode="w", encoding="utf-8"
      ) as f:
        f.write(base_device_public_key)
      

  yield _new_site_model

def proxy_id(x: int) -> str:
  return "".join([chr[int(x)] for x in str(x)]).rjust(4, "A")


def gateway_site_model():
  # generate random gateway site model
  gateways = {
      f"GAT-{i}": [f"{proxy_id(i)}-{x}" for x in range(1, random.randint(2, 5))]
      for i in range(1, random.randint(2, 5))
  }
