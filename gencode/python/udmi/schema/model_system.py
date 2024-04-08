"""Generated class for model_system.json"""


class Object11D8FD30:
  """Generated schema class"""

  def __init__(self):
    self.x = None
    self.y = None
    self.z = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = Object11D8FD30()
    result.x = source.get('x')
    result.y = source.get('y')
    result.z = source.get('z')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = Object11D8FD30.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.x:
      result['x'] = self.x # 5
    if self.y:
      result['y'] = self.y # 5
    if self.z:
      result['z'] = self.z # 5
    return result


class Object5437D086:
  """Generated schema class"""

  def __init__(self):
    self.lat = None
    self.long = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = Object5437D086()
    result.lat = source.get('lat')
    result.long = source.get('long')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = Object5437D086.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.lat:
      result['lat'] = self.lat # 5
    if self.long:
      result['long'] = self.long # 5
    return result


class Object1F163D1E:
  """Generated schema class"""

  def __init__(self):
    self.site = None
    self.section = None
    self.room = None
    self.floor = None
    self.position = None
    self.coordinates = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = ObjectD01F3C0D()
    result.site = source.get('site')
    result.section = source.get('section')
    result.room = source.get('room')
    result.floor = source.get('floor')
    result.position = Object11D8FD30.from_dict(source.get('position'))
    result.coordinates = Object5437D086.from_dict(source.get('coordinates'))
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = ObjectD01F3C0D.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.site:
      result['site'] = self.site # 5
    if self.section:
      result['section'] = self.section # 5
    if self.room:
      result['room'] = self.room # 5
    if self.floor:
      result['floor'] = self.floor # 5
    if self.position:
      result['position'] = self.position.to_dict() # 4
    if self.coordinates:
      result['coordinates'] = self.coordinates.to_dict() # 4
    return result
from .model_system_connection import SystemConnection
from .model_system_hardware import SystemHardware


class Object30C7601F:
  """Generated schema class"""

  def __init__(self):
    self.guid = None
    self.site = None
    self.name = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = Object30C7601F()
    result.guid = source.get('guid')
    result.site = source.get('site')
    result.name = source.get('name')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = Object30C7601F.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.guid:
      result['guid'] = self.guid # 5
    if self.site:
      result['site'] = self.site # 5
    if self.name:
      result['name'] = self.name # 5
    return result


class Object898FDF44:
  """Generated schema class"""

  def __init__(self):
    self.asset = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = ObjectB03D37EB()
    result.asset = Object30C7601F.from_dict(source.get('asset'))
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = ObjectB03D37EB.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.asset:
      result['asset'] = self.asset.to_dict() # 4
    return result


class Object734A44BA:
  """Generated schema class"""

  def __init__(self):
    self.suffix = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = Object734A44BA()
    result.suffix = source.get('suffix')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = Object734A44BA.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.suffix:
      result['suffix'] = self.suffix # 5
    return result


class SystemModel:
  """Generated schema class"""

  def __init__(self):
    self.location = None
    self.connection = None
    self.hardware = None
    self.software = None
    self.physical_tag = None
    self.adjunct = None
    self.min_loglevel = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = SystemModel()
    result.location = ObjectD01F3C0D.from_dict(source.get('location'))
    result.connection = SystemConnection.from_dict(source.get('connection'))
    result.hardware = SystemHardware.from_dict(source.get('hardware'))
    result.software = source.get('software')
    result.physical_tag = ObjectB03D37EB.from_dict(source.get('physical_tag'))
    result.adjunct = Object734A44BA.from_dict(source.get('adjunct'))
    result.min_loglevel = source.get('min_loglevel')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = SystemModel.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.location:
      result['location'] = self.location.to_dict() # 4
    if self.connection:
      result['connection'] = self.connection.to_dict() # 4
    if self.hardware:
      result['hardware'] = self.hardware.to_dict() # 4
    if self.software:
      result['software'] = self.software # 1
    if self.physical_tag:
      result['physical_tag'] = self.physical_tag.to_dict() # 4
    if self.adjunct:
      result['adjunct'] = self.adjunct.to_dict() # 4
    if self.min_loglevel:
      result['min_loglevel'] = self.min_loglevel # 5
    return result
