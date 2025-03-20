import json
import argparse
from tabulate import tabulate
from datetime import datetime
from copy import deepcopy
from .paths import LOG_DIR, DATA_DIR, IDS_FILE
from .user import IDManager, Settings, Profile, Consent
from .utils import get_localtion_data, get_usage_data, get_system_data, get_python_data

# module logger
import logging
logger = logging.getLogger(__name__)

def records_list() -> None:
  
  # print records
  table = []
  for record in list(DATA_DIR.glob("*.json")):

    # load record
    with open(record, "r") as f:
      data = json.load(f)
      logger.debug(f"Extracting data from record {record}: {data}")
      
    # extract data
    timestamp = data["user"]["timestamp"]
    request_id = data["uuid"]
    for app in data["app"]:
      run_id = app["uuid"]
      profile = app["profile"]
      package = app["name"]
    
      # table
      table.append([request_id, profile, package, timestamp])
      
  # sort by started_on
  table = sorted(table, key=lambda x: x[3], reverse=True)  
  
  # format started_on yyyy-mm-dd hh:mm:ss
  for row in table:
    row[3] = row[3].replace("T", " ").replace("Z", "").split(".")[0]
  
  # print table
  print(tabulate(table, headers=["ID", "Profile", "Package", "Started On"]))

def _get_run_ids_for_stem(run_id: str) -> list[str]:
  record_files = list(DATA_DIR.glob("*.json"))
  return [record.stem for record in record_files if record.stem.startswith(run_id)]

def _complete_run_if(run_id: str) -> str | None:
  run_ids = _get_run_ids_for_stem(run_id)
  if len(run_ids) == 1:
    return run_ids[0]
  return None

def _flatten_json(data: dict, parent_key: str = "", sep: str = " / ") -> dict:
  items = []
  for k, v in data.items():
    new_key = f"{parent_key}{sep}{k}" if parent_key else k
    if isinstance(v, dict):
      items.extend(_flatten_json(v, new_key, sep=sep).items())
    else:
      items.append((new_key, v))
  return dict(items)

def record_show(run_id: str) -> None:

  # complete run_id
  if len(run_id) < 36:
    run_id = _complete_run_if(run_id)
    assert run_id, f"Run with id {run_id} does not exist"
    
  # get record file
  record_file = DATA_DIR / f"{run_id}.json"
  assert record_file.exists(), f"Record with id {run_id} does not exist"
  
  # check if record exists
  if not record_file.exists():
    print(f"Record with id {run_id} does not exist")
    return
  
  # load record
  with open(record_file, "r") as f:
    record = json.load(f)
    
  # print record information
  table = [[
    app["uuid"],
    app["name"],
    app["profile"],
    app["version"],
    record["user"]["timestamp"],
    app["runtime"],
  ] for app in record["app"]]
  
  print(tabulate(table, headers=["ID", "Package", "Profile", "Version", "Started On", "Runtime"]))
  print()
  
  # print user information
  fdata = _flatten_json(record["user"])
  table = [[k, v] for k, v in fdata.items()]
  print(tabulate(table, headers=["Key", "Value"]))
  
  # print data
  # for app in record["app"]:
  #   fdata = _flatten_json(app)
  #   table = [[k, v] for k, v in fdata.items()]
  #   print(tabulate(table, headers=["Key", "Value"]))

def records_overview() -> None:
  
  # get all records
  record_files = list(DATA_DIR.glob("*.json"))
  
  # load data
  packages = {}
  for record_file in record_files:
    
    # read record file
    with open(record_file, "r") as f:
        record = json.load(f)
        
    for app in record["app"]:
      
      # extract run data
      package = app["name"]
      profile = app["profile"].lower()
      runtime = app["runtime"]
      started_on = record["user"]["timestamp"]
    
      # create empty package entry
      if package not in packages:
        packages[package] = {
          "user": 0,
          "package": 0,
          "anonymous": 0,
          "runtime": 0,
          "last_execution": None
        }
        
      # update package entry
      packages[package][profile] += 1
      packages[package]["runtime"] += runtime
      packages[package]["last_execution"] = started_on if packages[package]["last_execution"] is None else max(packages[package]["last_execution"], started_on)
        
  # create table
  table = []
  for package, data in packages.items():
    table.append([
      package,
      data["user"],
      data["package"],
      data["anonymous"],
      data["runtime"] / (data["user"] + data["package"] + data["anonymous"]),
      data["last_execution"]
    ])
    
  # print table
  print(tabulate(table, headers=["Package", "User", "Package", "Anonymous", "Average Runtime", "Last Execution"]))
  
def print_settings(settings: Settings, old_settings: Settings | None = None) -> None:
    
  # get settings
  consent = settings.consent
  profile = settings.profile
  
  # get old settings
  old_consent = old_settings.consent if old_settings else consent
  old_profile = old_settings.profile if old_settings else profile

  # create table
  row = []
  
  # consent
  if consent != old_consent:
    row.append(f"{old_consent.name} \033[31m->\033[0m \033[1m{consent.name}\033[0m")
  else:
    row.append(consent.name)
    
  # profile
  if profile != old_profile:
    row.append(f"{old_profile.name} \033[31m->\033[0m \033[1m{profile.name}\033[0m")
  else:
    row.append(profile.name)
    
  # updated on 
  row.append(settings.updated_on)
    
  # print table
  print(tabulate([row], headers=["Consent", "Profile", "Updated On"]))

  
def cli() -> None:

  # create parser
  parser = argparse.ArgumentParser(description="Plausipy CLI")
  subparsers = parser.add_subparsers(dest="command")
  
  # list command
  subparsers.add_parser("list", help="List all stored data")
  
  # overview command
  subparsers.add_parser("overview", help="Show an overview of all stored data")
  
  # show command
  show_parser = subparsers.add_parser("show", help="Show a specific stored data")
  show_parser.add_argument("run_id", type=str, help="The id of the run to show")
  
  # delete command
  subparsers.add_parser("delete", help="Delete a specific stored data")
  
  # clear command
  clear_parser = subparsers.add_parser("clear", help="Delete all stored data")
  group = clear_parser.add_mutually_exclusive_group(required=True)
  group.add_argument("--runs", action="store_true", help="Delete all stored runs")
  group.add_argument("--ids", action="store_true", help="Delete all stored ids")
  group.add_argument("--logs", action="store_true", help="Delete all stored logs")
  group.add_argument("--all", action="store_true", help="Delete all stored data")
  
  # profile command
  settings = subparsers.add_parser("settings", help="Specify the settings for plausipy and packages")
  settings.add_argument("package", type=str, nargs='?', default=None, help="The package name")
  consent_group = settings.add_mutually_exclusive_group()
  consent_group.add_argument("--yes", "--allow", "-y", action="store_true", help="Consent to (allow) tracking")
  consent_group.add_argument("--no", "--deny", "-n", action="store_true", help="Disallow tracking") 
  consent_group.add_argument("--ask", "-a", action="store_true", help="Ask for consent every time")
  settings.add_argument("--profile", "-p", type=str, choices=[p.value for p in Profile], help="Set the tracking profile")
  settings.add_argument("--reset", action="store_true", help="Reset the settings to factory defaults")
  settings.add_argument("--raw", action="store_true", help="Print raw settings")
  
  # me command
  subparsers.add_parser("me", help="Show information the user provides / aggregated of the user")
  
  # parse arguments
  args = parser.parse_args()
  
  # execute command
  if args.command == "list":
    logger.debug("List all stored data")
    records_list()
    
  elif args.command == "overview":
    logger.debug("Show an overview of all stored data")
    records_overview()
    
  elif args.command == "show":
    logger.debug(f"Show a specific stored data with id {args.run_id}")
    record_show(args.run_id)
    
  elif args.command == "delete":
    logger.debug("Delete a specific stored data")
    print("\033[31mWARNING: This functionality is not yet implemented\033[0m")   
    
    # just print all tracking ids that would be used for deletion of one or multiple records
    # NOTE: when a package makes anonymous calls, it is not possible to delete data for that specific pacakge only without risking a sensitive link on the user's system
    # NOTE: in general, albeit this information beeing local, unless it is encrypted, it's not really safe. So we should either minimize the information or encrypt local records for transparency.
     
    id_manager = IDManager()
    data = id_manager._data
    print(json.dumps(data, indent=2))
     
  elif args.command == "clear":
    
    # ask for confirmation
    if not input("Are you sure you want to delete all stored data? (y/n): ").lower().startswith("y"):
      print("Aborted")
      return
    
    if args.runs or args.all:
      for record in DATA_DIR.glob("*.json"):
        record.unlink()
      print("Deleted all stored runs")
    
    if args.ids or args.all:
      if IDS_FILE.exists():
        IDS_FILE.unlink()
      print("Deleted all stored ids")
    
    if args.logs or args.all:
      for log in LOG_DIR.glob("*.log*"):
        log.unlink()
      print("Deleted all stored logs")
    
  elif args.command == "settings":
    logger.debug("Specify the settings for plausipy and packages")
    
    # get settings provider
    settings = Settings()
    
    if args.package is not None:
      settings = settings.package(args.package)
      
    # get old settings
    old_settings = deepcopy(settings)

    # reset settings
    if args.reset:
      logger.info("Resetting settings for package %s", args.package)
      settings.reset()

    # specify consent (saves automatically)
    assert sum([args.yes, args.no, args.ask]) <= 1, "Only one of --allow, --no, --ask can be set"
    if args.yes:
      settings.consent = Consent.ALLOW
    elif args.no:
      settings.consent = Consent.DENY
    elif args.ask:
      settings.consent = Consent.ASK
              
    # specify profile (saves automatically)
    if args.profile:
      settings.profile = Profile(args.profile)
      
    # print settings
    if args.raw:
      print(json.dumps(settings._data, indent=2))
    else:
      print_settings(settings, old_settings)
    
  elif args.command == "me":
    logger.debug("Show information the user provides / aggregated of the user")

    # collect the information the user provides
    data = {
      "Location": {k.capitalize(): v for k, v in get_localtion_data().items()},
      "Usage": {k.capitalize(): v for k, v in get_usage_data().items()},
      "System": {k.capitalize(): v for k, v in get_system_data().items()},
      "Python": {k.capitalize(): v for k, v in get_python_data().items()},
      "Timestamp": str(datetime.now()),
    }
    
    # flatten
    data = _flatten_json(data)
    
    # print data
    table = [[k, v] for k, v in data.items()]
    print(tabulate(table))

  else:
    logger.debug("No command provided, display help")
    parser.print_help()