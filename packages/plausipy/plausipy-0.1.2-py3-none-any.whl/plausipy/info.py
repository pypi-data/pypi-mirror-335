import shutil
from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.key_binding import KeyBindings
from .user import Profile, Consent, Settings

def show_tracking_info(package: str, profile: Profile) -> bool:
    
  # if consent is
  # - ask: we ask the user for profile user and package, and inform the user about the data collection when the profile is anonymous
  # - deny: we deny the tracking, if the package says it is mandatory, we raise an exception (need to define to what extend tracking should be enforcable and downgradable)
  # - allow: tracking is allowed and will pass without any notice or interaction
    
    
  # todo: refine text promt and include precise information of the collected data and the requested profile
  title = "Usage Data Collection Information"
  message = "This package collects anonymous user information. This information is used to improve the package and to provide better services to the users. The information collected includes the package name, the package version, the user's operating system, the user's Python version, location information, the runtime and returncode. The information is collected anonymously and is not used to identify individual users. Tracking of an individual user across multiple executions of this package and other packages using tracking sercvives can be possible depending on the profile. The usage can not be connected to you as an individuum."
    
  # get settings
  settings = Settings().package(package)
  
  # check if consent is already given
  if settings.consent == Consent.ALLOW:
    return True

  elif settings.consent == Consent.DENY:
    # TODO: implement & handle mandatory tracking
    # NOTE: also consider --no-tracking option, will need some refactoring, centralize logic for most transparency
    # -> if deny + mandatory: ask
    # -> if deny + not mandatory: return fasle
    return False
    
  if settings.consent == Consent.ASK:
    if profile == Profile.ANONYMOUS:
      
      # inform user and continue
      _print_box(title, message)
      return True
    
    else:
      
      # ask user for consent
      options = [
        ("Allow tracking", "y"),
        ("Deny tracking", "n"),
        ("Ask every time", "a")
      ]
      selected_index = _print_interactive_box(title, message, options)
      consent = Consent(options[selected_index][1])    
      
      # update settings
      settings.consent = consent
      
      # continue unless the user denies tracking
      #  TODO: implement & handle mandatory tracking
      return consent != Consent.DENY
    
def _print_box(title: str, message: str, options: list[tuple[str,str]] | None = None, selected_index: int = 0):
    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns

    # Create a border
    border = "═" * (terminal_width - 2)  # -2 for borders on both sides
    
    # print top border
    print("╔" + border + "╗")
    
    # Print title
    title_line = f" {title} ".center(terminal_width - 2)  # Center title
    print("║" + title_line + "║")
    
    # Print message
    message_lines = message.split('\n')
    
    # split all lines at the terminal width if they are too long
    # Process lines that are too long
    i = 0
    while i < len(message_lines):
        line = message_lines[i]
        if len(line) > terminal_width - 4:
            # Find the last space or dash before the width limit
            split_pos = terminal_width - 4
            for j in range(terminal_width - 4, 0, -1):
                if line[j] in [' ', '-']:
                    split_pos = j + 1
                    break
            
            # Split the line
            message_lines[i] = line[:split_pos].rstrip()
            message_lines.insert(i + 1, line[split_pos:].lstrip())
        i += 1
    
    for line in message_lines:
        message_line = f" {line} ".ljust(terminal_width - 2)  # Left justify message
        print("║" + message_line + "║")

    # Print a new line before options
    print("║" + " " * (terminal_width - 2) + "║")

    # Print options horizontally
    if options is not None and len(options) > 0:
        options_line = "  ".join([f"{'●' if i == selected_index else '○'} {options[i][0]} ({options[i][1]})" for i in range(len(options))])
        print("║" + options_line.center(terminal_width - 2) + "║")
    
    # brint bottom border
    print("╚" + border + "╝")

def _print_interactive_box(title: str, message: str, options: list[tuple[str,str]]) -> int:

    selected_index = 0    
    session = PromptSession()
    kb = KeyBindings()

    # Key bindings for arrow keys
    @kb.add('left')
    def _(event):
        nonlocal selected_index
        selected_index = (selected_index - 1) % len(options)
        refresh_display(selected_index)

    @kb.add('right')
    def _(event):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(options)
        refresh_display(selected_index)

    @kb.add('tab')
    def _(event):
        nonlocal selected_index
        selected_index = (selected_index + 1) % len(options)
        refresh_display(selected_index)

    @kb.add('enter')
    def _(event):
        session.app.exit()

    # Adding shortcut keys for options
    for index, (option, shortcut) in enumerate(options):
        @kb.add(shortcut)
        def _(event, index=index):
            nonlocal selected_index
            selected_index = index
            session.app.exit()

    def refresh_display(selected_index):
        clear()  # Clear the console
        _print_box(title, message, options, selected_index)

    # Display the initial options
    refresh_display(selected_index)

    # display prompt 
    session.prompt(key_bindings=kb)
        
    # return (sync)
    return selected_index

