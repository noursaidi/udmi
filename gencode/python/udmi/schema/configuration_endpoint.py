"""Generated class for configuration_endpoint.json"""


class ObjectA90DCC28:
  """Generated schema class"""

  def __init__(self):
    self.basic = None
    self.jwt = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = ObjectA90DCC28()
    result.basic = source.get('basic')
    result.jwt = source.get('jwt')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = ObjectA90DCC28.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.basic:
      result['basic'] = self.basic # 5
    if self.jwt:
      result['jwt'] = self.jwt # 5
    return result


class EndpointConfiguration:
  """Generated schema class"""

  def __init__(self):
    self.protocol = None
    self.transport = None
    self.hostname = None
    self.port = None
    self.config_sync_sec = None
    self.client_id = None
    self.auth_provider = None
    self.nonce = None

  @staticmethod
  def from_dict(source):
    if not source:
      return None
    result = EndpointConfiguration()
    result.protocol = source.get('protocol')
    result.transport = source.get('transport')
    result.hostname = source.get('hostname')
    result.port = source.get('port')
    result.config_sync_sec = source.get('config_sync_sec')
    result.client_id = source.get('client_id')
    result.auth_provider = ObjectA90DCC28.from_dict(source.get('auth_provider'))
    result.nonce = source.get('nonce')
    return result

  @staticmethod
  def map_from(source):
    if not source:
      return None
    result = {}
    for key in source:
      result[key] = EndpointConfiguration.from_dict(source[key])
    return result

  @staticmethod
  def expand_dict(input):
    result = {}
    for property in input:
      result[property] = input[property].to_dict() if input[property] else {}
    return result

  def to_dict(self):
    result = {}
    if self.protocol:
      result['protocol'] = self.protocol # 5
    if self.transport:
      result['transport'] = self.transport # 5
    if self.hostname:
      result['hostname'] = self.hostname # 5
    if self.port:
      result['port'] = self.port # 5
    if self.config_sync_sec:
      result['config_sync_sec'] = self.config_sync_sec # 5
    if self.client_id:
      result['client_id'] = self.client_id # 5
    if self.auth_provider:
      result['auth_provider'] = self.auth_provider.to_dict() # 4
    if self.nonce:
      result['nonce'] = self.nonce # 5
    return result
