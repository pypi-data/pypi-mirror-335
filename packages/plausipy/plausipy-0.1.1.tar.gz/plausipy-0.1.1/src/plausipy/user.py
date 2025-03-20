from .paths import IDS_FILE, SETTINGS_FILE
from datetime import datetime
from enum import Enum
import json
import uuid

class Profile(Enum):
  USER = 'u'
  PACKAGE = 'p'
  ANONYMOUS = 'a'
  
  @property
  def score(self) -> int:
    return{
      Profile.USER: 100,
      Profile.PACKAGE: 10,
      Profile.ANONYMOUS: 1
    }[self]

  # make profile comparable
  def __lt__(self, other):
    return self.score < other.score
  
class Consent(Enum):
  ALLOW = 'y'
  DENY = 'n'
  ASK = 'a'
  
class Scope:
  def __init__(self, location: bool, usage: bool, system: bool, python: bool):
    self.location = location
    self.usage = usage
    self.system = system
    self.python = python
    
class TrackID:
  def __init__(self, profile: Profile, id: str):
    self.profile = profile
    self.id = id

class IDManager:
  
  def __init__(self):
    self._data = {}
    self._clean = True
    self.load()
  
  def _get_default_data(self) -> dict:
    return {
      "user": None,
      "packages": {},
      "anonymous": []
    }

  def _load_data(self) -> tuple[dict, bool]:
    try:
      with open(IDS_FILE, "r") as f:
        return json.load(f), True
    except:
      return self._get_default_data(), False

  def load(self) -> None:
    self._data, self._clean = self._load_data()
    
  def store(self) -> None:
    if not self._clean:
      self._clean = True
      
      # Ensure directory exists
      IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
      
      # Write data
      with open(IDS_FILE, "w") as f:
        json.dump(self._data, f)
        
  def _request_id(self) -> str:
    return str(uuid.uuid4())
      
  def get_id(self, profile: Profile, package: str | None) -> TrackID:

    # get id based on profile
    if profile == Profile.USER:
      if self._data["user"] is None:
        self._data["user"] = self._request_id()
        self._clean = False
        
      id = self._data["user"]
      
    elif profile == Profile.PACKAGE:
      if package not in self._data["packages"]:
        self._data["packages"][package] = self._request_id()
        self._clean = False
        
      id = self._data["packages"][package]
    
    elif profile == Profile.ANONYMOUS:
      id = self._request_id()
      self._data["anonymous"].append(id)
      self._clean = False
      
    # check
    assert id is not None, "ID not generated"
    
    # store
    self.store()
    
    # return
    return TrackID(profile, id)

class PackageSettings:
  def __init__(self, name: str, _data: dict | None, _on_change: callable):
    self.name = name
    self._data = _data or self._get_default_data()
    self._on_change = _on_change
       
  def _get_default_data(self) -> dict:
    return {
      "profile": Profile.PACKAGE.name,
      "consent": Consent.ASK.name,
      "updated_on": None
    }
       
  def _update(self):
    self._data["updated_on"] = datetime.now().isoformat()
    self._on_change(self._data)
    
  def reset(self, erase: bool = False):
    self._data = self._get_default_data()
    self._update()
    
    if erase:
      self._on_change(None)
    
  @property
  def consent(self) -> Consent:
    return Consent[self._data["consent"]]
  
  @consent.setter
  def consent(self, value: bool):
    self._data["consent"] = value.name
    self._update()
    
  @property
  def profile(self) -> Profile:
    return Profile[self._data["profile"]]
  
  @profile.setter
  def profile(self, value: Profile):
    self._data["profile"] = value.name
    self._update()
    
  @property
  def updated_on(self) -> datetime | None:
    return datetime.fromisoformat(self._data["updated_on"]) if self._data["updated_on"] else None

class Settings:
  def __init__(self):
    self._data = {}
    self.load()
  
  def _get_default_data(self) -> dict:
    return {
      "global": {
        "consent": Consent.ASK.name,
        "profile": Profile.PACKAGE.name,
        "updated_on": None,
      },
      "packages": {}
    }
    
  def _load_data(self) -> tuple[dict, bool]:
    try:
      with open(SETTINGS_FILE, "r") as f:
        return json.load(f), True
    except:
      return self._get_default_data(), False
    
  def reset(self):
    if SETTINGS_FILE.exists():
      SETTINGS_FILE.unlink()
    self.load()
    
  def load(self) -> None:
    self._data, self._clean = self._load_data()
    
  def store(self) -> None:
    # Ensure directory exists
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Write data
    with open(SETTINGS_FILE, "w") as f:
      json.dump(self._data, f)
      
  @property
  def profile(self) -> Profile:
    return Profile[self._data["global"]["profile"]]
  
  @profile.setter
  def profile(self, value: Profile):
    self._data["global"]["profile"] = value.name
    self._data["global"]["updated_on"] = datetime.now().isoformat()
    self.store()
    
  @property
  def consent(self) -> Consent:
    return Consent[self._data["global"]["consent"]]
  
  @consent.setter
  def consent(self, value: Consent):
    self._data["global"]["consent"] = value.name
    self._data["global"]["updated_on"] = datetime.now().isoformat()
    self.store()
    
  def _update_package(self, package: str, data: dict | None):
    if data is None:
      del self._data["packages"][package]
    else:
      self._data["packages"][package] = data
    self.store()
  
  def package(self, package: str) -> PackageSettings:
    return PackageSettings(
      package,
      self._data["packages"].get(package),
      lambda data: self._update_package(package, data)
    )
    
  @property
  def updated_on(self) -> datetime | None:
    return datetime.fromisoformat(self._data["global"]["updated_on"]) if self._data["global"]["updated_on"] else None