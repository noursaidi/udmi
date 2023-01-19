"""Generated class for site.json"""
from .site_location import SiteLocation
from .site_origin import SiteLocation


class Site:
  """Generated schema class"""

  def __init__(self):
    self.timestamp = None
    self.version = None
    self.id = None
    self.name = None
    self.location = None
    self.origin = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = Site()
    result.timestamp = source.get('timestamp')
    result.version = source.get('version')
    result.id = source.get('id')
    result.name = source.get('name')
    result.location = SiteLocation.from_dict(source.get('location'))
    result.origin = SiteLocation.from_dict(source.get('origin'))
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = Site.from_dict(source[key])
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
    if self.id:
      result['id'] = self.id # 5
    if self.name:
      result['name'] = self.name # 5
    if self.location:
      result['location'] = self.location.to_dict() # 4
    if self.origin:
      result['origin'] = self.origin.to_dict() # 4
    return result
