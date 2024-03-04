"""Generated class for event_discovery.json"""
from .entry import Entry
from .discovery_family import FamilyDiscovery
from .discovery_registry import RegistryDiscovery
from .discovery_device import DeviceDiscovery
from .discovery_point import PointDiscovery
from .discovery_feature import FeatureDiscovery
from .ancillary_properties import AncillaryProperties
from .state_system_hardware import StateSystemHardware


class SystemDiscoveryEvent:
  """Generated schema class"""

  def __init__(self):
    self.serial_no = None
    self.ancillary = None
    self.hardware = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = SystemDiscoveryEvent()
    result.serial_no = source.get('serial_no')
    result.ancillary = AncillaryProperties.from_dict(source.get('ancillary'))
    result.hardware = StateSystemHardware.from_dict(source.get('hardware'))
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = SystemDiscoveryEvent.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.serial_no:
      result['serial_no'] = self.serial_no # 5
    if self.ancillary:
      result['ancillary'] = self.ancillary.to_dict() # 4
    if self.hardware:
      result['hardware'] = self.hardware.to_dict() # 4
    return result


class DiscoveryEvent:
  """Generated schema class"""

  def __init__(self):
    self.timestamp = None
    self.version = None
    self.generation = None
    self.status = None
    self.scan_family = None
    self.scan_addr = None
    self.families = None
    self.registries = None
    self.devices = None
    self.points = None
    self.features = None
    self.system = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = DiscoveryEvent()
    result.timestamp = source.get('timestamp')
    result.version = source.get('version')
    result.generation = source.get('generation')
    result.status = Entry.from_dict(source.get('status'))
    result.scan_family = source.get('scan_family')
    result.scan_addr = source.get('scan_addr')
    result.families = FamilyDiscovery.map_from(source.get('families'))
    result.registries = RegistryDiscovery.map_from(source.get('registries'))
    result.devices = DeviceDiscovery.map_from(source.get('devices'))
    result.points = PointDiscovery.map_from(source.get('points'))
    result.features = FeatureDiscovery.map_from(source.get('features'))
    result.system = SystemDiscoveryEvent.from_dict(source.get('system'))
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = DiscoveryEvent.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.timestamp:
      result['timestamp'] = self.timestamp # 5
    if self.version:
      result['version'] = self.version # 5
    if self.generation:
      result['generation'] = self.generation # 5
    if self.status:
      result['status'] = self.status.to_dict() # 4
    if self.scan_family:
      result['scan_family'] = self.scan_family # 5
    if self.scan_addr:
      result['scan_addr'] = self.scan_addr # 5
    if self.families:
      result['families'] = FamilyDiscovery.expand_dict(self.families) # 2
    if self.registries:
      result['registries'] = RegistryDiscovery.expand_dict(self.registries) # 2
    if self.devices:
      result['devices'] = DeviceDiscovery.expand_dict(self.devices) # 2
    if self.points:
      result['points'] = PointDiscovery.expand_dict(self.points) # 2
    if self.features:
      result['features'] = FeatureDiscovery.expand_dict(self.features) # 2
    if self.system:
      result['system'] = self.system.to_dict() # 4
    return result
