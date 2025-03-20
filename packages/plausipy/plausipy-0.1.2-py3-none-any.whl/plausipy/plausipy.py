from .paths import DATA_DIR, LOG_DIR
import json
import requests
from .user import IDManager, Profile
from .utils import get_package_version, get_localtion_data, get_usage_data, get_system_data, get_python_data, get_package_tree
from . import logger
from .info import show_tracking_info, _print_box
from datetime import datetime
import safe_exit
import uuid

API_ENDPOINT = "https://plausipy.moontec.de/api/packages/all/records"

class Record:
  
  @classmethod
  def getUserLocation(cls):
    if not hasattr(cls, "_user_location"):
      cls._user_location = get_localtion_data()
    return cls._user_location
  
  @classmethod
  def getUserUsage(cls):
    if not hasattr(cls, "_user_usage"):
      cls._user_usage = get_usage_data()
    return cls._user_usage
  
  @classmethod
  def getUserSystem(cls):
    if not hasattr(cls, "_user_system"):
      cls._user_system = get_system_data()
    return cls._user_system
  
  @classmethod
  def getUserPython(cls):
    if not hasattr(cls, "_user_python"):
      cls._user_python = get_python_data()
    return cls._user_python

class Plausipy:
  
  _id = str(uuid.uuid4())
  _pps: list = []
  _termination_event_registered = False
 
  @classmethod
  def registerTerminationEvent(cls, key: str):
    """
    Register safe exit once
    """

    # check if already registered
    if cls._termination_event_registered:
      logger.info("Termination event already registered.")
      return
    
    # register
    safe_exit.register(cls.terminate)
    cls._key = key
    cls._termination_event_registered = True
      
  @classmethod  
  def terminate(cls):
    """
    Indicate to plausipy that the trackable execution has ended.
    This usually meand that the program is terminated.
    """
    
    # TODO: maybe disabled on class level makes more sense when it's a user input, however, we also want
    #       to allow disabling tracking on a package level while dependency tracking is still active.
    
    #  log
    logger.info("Terminating plausipy")
    
    # stop all plausipy instances that are not already stopped
    for pp in cls._pps:
      if pp._started_on and not pp._ended_on:
        pp.stop()
        
    # print data
    print("\033[90m", end="")
    _print_box("Plausipy", json.dumps(cls.json(), indent=2))
    print("\033[0m", end="")
        
    # store data
    cls.store()
        
    # send data
    cls.send()
  
  @classmethod
  def json(cls) -> dict:
    """
    Get the data in a json format
    """
        
    # gather general information
    granted_profile = Profile.USER
    consented = True
    
    return {
      "uuid": cls._id,
      "ppy": {
        "version": get_package_version("plausipy"),
      },
      "user": {
        "profile": granted_profile.name,
        "consented": consented,
        "location": Record.getUserLocation(),
        "system": Record.getUserSystem(),
        "python": Record.getUserPython(),
        "timestamp": datetime.now().isoformat(),
      },
      "app": [pp._app_json() for pp in cls._pps if pp.allowed],
    }
   
  @classmethod
  def store(cls):
    """
    Store the data in a file
    """
    
    # get data
    data = cls.json()
    
    # get directory
    file = DATA_DIR / f"{cls._id}.json"
    
    # ensure file exists
    file.parent.mkdir(parents=True, exist_ok=True)
    
    # write data
    with open(file, "w") as f:
      json.dump(data, f)
      
  @classmethod
  def send(cls):
    """
    Send the data to the server
    """
        
    # make request
    data = cls.json()
    logger.info("Sending data to server")
    logger.info(json.dumps(data, indent=2))
    
    # prepare header
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {cls._key}",
      "Accept": "application/json",
      "User-Agent": "plausipy"
    }
    
    # send data
    response = requests.post(API_ENDPOINT, json=data, headers=headers)
    
    # check response
    if response.status_code == 200:
      logger.info("Data sent successfully")
    else:
      logger.error("Data could not be sent: %s", response.text)
    
  def __init__(self, 
      app_name: str, 
      app_key: str, 
      profile: Profile = Profile.PACKAGE, 
      start: bool = False,
      endpoint: str | None = None
    ):
    
    # log
    logger.info("Initializing plausipy for %s", app_name)
           
    # ptree
    self._ptree = get_package_tree()
    logger.info("Package tree: %s", self._ptree)

           
    # api endpoint
    if endpoint:
      global API_ENDPOINT
      logger.info("Setting API endpoint to %s", endpoint)
      API_ENDPOINT = endpoint
      
    # register self and terminate event
    self._pps.append(self)
    self.registerTerminationEvent(app_key)    
              
    # app info
    self._id = str(uuid.uuid4())
    self._app_name = app_name
    self._app_key = app_key
     
    # parameter
    self.disabled = False
    self._consented: bool | None = None
    self._ppy_version = get_package_version("plausipy")
    self._version = get_package_version(self._app_name)
    self._requested_profile = profile
    self.profile = profile.USER # TODO: read from user config and use minimal default

    # ...
    self._returncode = None
    self._started_on = None
    self._ended_on = None
    self._initial_usage = None
    self._memory_delta = None
    self._data = {}

    # start tracking
    if start:
      self.start()
        
  def consent(self, refresh: bool = False):

    # check if consent is already given
    if self._consented is not None and not refresh:
      logger.info("Consent already given, plausipy consent event is ignored.")
      return
    
    if self._consented is not None and refresh:
      logger.info("Consent already given, refreshing consent as requestesd.")
    
    # ask for consent
    self._consented = show_tracking_info(self._app_name, self.profile)
    
  def start(self):
    """
    Indicate to plausipy that the trackable execution has started.
    This usually means that the program is started.
    """
    
    # abort if disabled
    if self.disabled:
      logger.info("Tracking is disabled, plausipy start event is ignored.")
      return
    
    # plausipy user consent and transparancy
    if self._consented is None:
      self.consent()
      
    if not self._consented:
      logger.info("Tracking is not allowed, plausipy start event is ignored.")
      return
          
    # start run
    self._started_on = datetime.now()
    
    # capture initial usage
    self._initial_usage = get_usage_data()
        
  def stop(self):
    
    # stop
    self._ended_on = datetime.now()
    
    # update usage
    final_usage = get_usage_data()
    memory_delta = final_usage["memory"] - self._initial_usage["memory"]
    self._memory_delta = memory_delta
      
  @property
  def profile(self) -> Profile:
    """
    Get the profile of the current track-id
    """
    return min(self._requested_profile, self._granted_profile)
  
  @profile.setter
  def profile(self, value: Profile):
    """
    Set the granted profile and update the track-id
    NOTE: a granted profile larger than the requested profile has no effect
    """
    self._granted_profile = value
    self._track_id = IDManager().get_id(self.profile, self._app_name)
     
  @property
  def returncode(self) -> int | None:
    """
    Get the return code of the run
    """
    return self._returncode
  
  @returncode.setter
  def returncode(self, value: int):
    """
    Set the return code of the run
    """
    self._returncode = value
     
  @property
  def allowed(self) -> bool:
    return not self.disabled and self._consented
     
  def setData(self, **kwargs):
    """
    Set data for the current run
    """
    self._data.update(kwargs)
     
  def _app_json(self) -> dict:    
    parent_package = self._ptree[2] if len(self._ptree) > 2 else None
    parent_version = get_package_version(parent_package)
    runtime = (self._ended_on - self._started_on).total_seconds() if self._ended_on else 0
    cpu = self._initial_usage["cpu"] if self._initial_usage else None
    
    return {
      "uuid": self._id,
      "name": self._app_name,
      "key": self._app_key,
      "version": self._version,
      "profile": self._requested_profile.name,
      "user": self._track_id.id,
      "parent": parent_package,
      "parent_version": parent_version,
      "returncode": self._returncode,
      "runtime": runtime,
      "cpu": cpu,
      "memory": self._memory_delta,
      "data": self._data
    }
    