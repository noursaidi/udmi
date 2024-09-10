import datetime
import enum
import schema.util
import dataclasses
import json
import collections

@dataclasses.dataclass
class DiscoverySystemSoftware:
  firmware: str = None


@dataclasses.dataclass
class DiscoverySystemHardware:
  make: str = None
  model: str = None

@dataclasses.dataclass
class DiscoverySystem:
  hardware: DiscoverySystemHardware = dataclasses.field(default_factory=DiscoverySystemHardware)
  software: DiscoverySystemSoftware = dataclasses.field(default_factory=DiscoverySystemSoftware)

@dataclasses.dataclass
class DiscoveryFamily:
  addr: str 

@dataclasses.dataclass
class DiscoveryEvent:
  generation: str
  scan_family: str
  scan_addr: str
  timestamp = None

  version: str = "1.5.1"
  timestamp: datetime.datetime = dataclasses.field(default_factory=schema.util.current_time_utc)
  families: dict[str, DiscoveryFamily] = dataclasses.field(default_factory=dict)
  system: DiscoverySystem = dataclasses.field(default_factory=DiscoverySystem)

  def to_json(self) -> str:
    as_dict = dataclasses.asdict(self)
    as_dict["timestamp"] = datetime.datetime.now()
    return json.dumps(as_dict, default=schema.util.json_serializer, indent=4)
  

