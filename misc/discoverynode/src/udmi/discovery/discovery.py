"""Framework class for"""

import abc
import atexit
import enum
from functools import wraps
import logging
import sched
import threading
import traceback
from typing import Any, Callable
import udmi.schema.config
import udmi.schema.state
import time
import copy
import datetime

RUNNER_LOOP_INTERVAL = 0.1
ACTION_START = 1
ACTION_STOP = -1

def catch_exceptions_to_state(method: Callable):
  """Decorator which propogates errors up to the state.

  Args:
    method: method to wrap
  """

  @wraps(method)
  def _impl(self, *args, **kwargs):
    try:
      return method(self, *args, **kwargs)
    except Exception as err:
      self.mark_error_from_exception(err)
  return _impl


def main_task(method: Callable):
  """Decorator which marks discovery as `done` when wrapped functoin returns.

  Args:
    method: method to wrap
  """

  @wraps(method)
  def _impl(self, *args, **kwargs):
    method(self, *args, **kwargs)
    self.state.phase = states.FINISHED

  return _impl


class states(enum.StrEnum):
  # Discovery service has been initialized but is not doing anytihng
  INITIALIZED = "initialized"

  # Discovery is scheduled in the future
  PENDING = "pending"

  # Receieved the signal to start (from config block, or next interval)
  STARTING = "starting"

  # Discovery has started
  STARTED = "started"

  # Recieved the signal to cancel (e.g. from config message change)
  CANCELLING = "cancelling"

  # Discovery has been cancelled
  CANCELLED = "cancelled"

  # Discovery has finished the scan
  FINISHED = "finished"
  
  # Discovery has finished because the interval is over
  SCHEDULED = "scheduled"

  # Some error occured during processing
  ERROR = "error"


class DiscoveryController(abc.ABC):
  
  # Thi
  MAX_THRESHOLD_GENERATION = -10 # [5s]


  @property
  @abc.abstractmethod
  def scan_family(self):
    """The primary `scan_family` for this discovery component.

    E.g. ipv4, bacnet
    """
    pass

  @abc.abstractmethod
  def start_discovery(self):
    """Trigger the start of discovery.

    This method should:
      - Setup and clear any required variables, e.g. dictionaries,
      memory/previously remembered results

    This method should NOT:
      - Change the state
    """
    pass

  @abc.abstractmethod
  def stop_discovery(self):
    """Trigger stopping discovery and clean shutdown of any discovery processes, threads, etc

    This should may be called:
      - exceptions from discovery component
      - errors starting discovery
      - to stop discovery (because the config has changed)
      - stop discovery before (because interval has passed)
      - script is exiting (through atexit)cript is exiting (through atexit)

    As such, it should be safe from any malfunctioning

    This method should:
      - Return only when all subcomponents have been shut down
      - Log any relevant counters for troubleshooting
    """
    pass

  # Generation, provided by external source
  generation: None | str = None

  def __init__(self, state: udmi.schema.state.State, publisher: Callable):
    self.state = udmi.schema.state.Discovery()
    self.publisher = publisher
    state.discovery.families[self.scan_family] = self.state
    self.config = None
    self.mutex = threading.Lock()
    self.scheduler_thread = None
    self.scheduler_thread_stopped = threading.Event()
    atexit.register(self._stop)

  def _status_from_exception(self, err: Exception) -> None:
    """Create state in status"""
    self.state.status = udmi.schema.state.Status(
        category="discovery.error", level=500, message=str(err)
    )

  def mark_error_from_exception(self, err: Exception) -> None:
    """Helper function to mark"""
    self.state.phase = states.ERROR
    self._status_from_exception(err)
    logging.exception(err)

  def _start(self):
    logging.info("Starting discovery for %s", type(self).__name__)
    self.state.status = None
    self.state.phase = states.STARTING
    try:
      self.start_discovery()
      self.state.phase = states.STARTED
    except Exception as err:
      self.mark_error_from_exception(err)
    logging.info("Started... %s", type(self).__name__)

  def _stop(self):
    logging.info("Stopping discovery for %s", type(self).__name__)
    if self.state.phase not in [states.STARTING, states.STARTED]:
      logging.info("Not stopping because state was %s", self.state.phase)
      return
    logging.info("Stopped %s", type(self).__name__)

    self.state.status = None
    self.state.phase = states.CANCELLING
    try:
      self.stop_discovery()
      self.state.phase = states.CANCELLED
    except Exception as err:
      self.mark_error_from_exception(err)

  def validate_config(config: udmi.schema.config.DiscoveryFamily):
    if config.scan_duration_sec > config.scan_interval_sec:
      raise RuntimeError("scan duration cannot be greater than interval")
    
    if config.scan_duration_sec < 0 or config.scan_interval_sec < 0:
      raise RuntimeError("scan duration or interval cannot be negative")

  @catch_exceptions_to_state
  def scheduler(self, start_time:int, config: udmi.schema.config.DiscoveryFamily):
    """ The scheduler starts 
    
    """
    next_action_time = start_time
    
    # Initial execution of the scheduler is always to start a discovery
    next_action = ACTION_START
    self.state.phase = states.SCHEDULED


    scan_interval_sec = config.scan_interval_sec if config.scan_interval_sec is not None else 0
    # Set the duration to match the interval duration so that the scheduled stop logic is simpler
    # if neither are set, this sets it to 0 (the default)
    scan_duration_sec = config.scan_duration_sec if config.scan_duration_sec is not None else scan_interval_sec
    
    while not self.scheduler_thread_stopped.is_set():
      if time.monotonic() > next_action_time:
        with self.mutex:
          if config != self.config:
            logging.info("config has change, exiting")
            # Check that the config has not changed whilst the scheduler was waiting to acquire the lock
            return
          
          # make a copy of the current action so next_acction can be safelty mutated
          current_action = next_action
          
          if current_action == ACTION_START:
            self._start()
            
            if scan_duration_sec > 0:
              next_action = ACTION_STOP
              next_action_time = time.monotonic() + scan_duration_sec
              logging.info("scheduled discovery stop for %s in %d seconds", type(self).__name__, scan_duration_sec)
            else:
              # the scan runs indefinitely, exit the scheduler
              logging.info("%s discovery running indefinitely", type(self).__name__)
              return
            
          elif current_action == ACTION_STOP:
            self._stop()

            # If the scan is repetitive, schedule the next start
            if scan_interval_sec > 0:
              next_action = ACTION_START
              sleep_interval = scan_interval_sec - scan_duration_sec
              next_action_time = time.monotonic() + sleep_interval
              logging.info("scheduled discovery start for %s in %d seconds", type(self).__name__, scan_duration_sec)
              self.state.phase = states.SCHEDULED
            else:
              # The scan is not repetitive, exit the scheduler
              return
          
      time.sleep(RUNNER_LOOP_INTERVAL)
    
  @catch_exceptions_to_state
  def controller(self, config_dict: None | dict[str:Any]):
    """Main discovery controller which manages discovery sub-class.

    Args:
      config_dict: Complete UDMI configuration as a dictionary
    """
    logging.info("received config")
    with self.mutex:
      discovery_config_dict = config_dict["discovery"]["families"].get(
          self.scan_family
      )

      # Create a new config dict (always new)
      config = (
          udmi.schema.config.DiscoveryFamily(**discovery_config_dict)
          if discovery_config_dict
          else None
      )

      # Identical config, do nothing
      if config == self.config:
        return

      # config has changed
      # Stop any running discovery
      self.config = config
      self._stop()
      
      # Stop discovery scheduler if it exists
      if self.scheduler_thread:
        self.scheduler_thread_stopped.set()
        self.scheduler_thread.join()
      
      # Discovery config empty
      if not config:
        return
      

      generation = datetime.datetime.strptime(f"{config.generation}+0000", "%Y-%m-%dT%H:%M:%SZ%z")
      time_delta_from_now = generation - datetime.datetime.now(tz=datetime.timezone.utc)
      seconds_from_now = time_delta_from_now.total_seconds()

      if seconds_from_now < self.MAX_THRESHOLD_GENERATION:
        raise RuntimeError(f"generation start time ({seconds_from_now} from now exceeds allowable threshold {self.MAX_THRESHOLD_GENERATION})")
      logging.info(f"discovery {config} starts in {seconds_from_now} seconds")

      self.scheduler_thread_stopped.clear()
      self.scheduler_thread = threading.Thread(
          target=self.scheduler, args=[time.monotonic() + seconds_from_now, copy.copy(config)], daemon=True
      )
      self.scheduler_thread.start()

  def done(self):
    self.state.phase = states.FINISHED
