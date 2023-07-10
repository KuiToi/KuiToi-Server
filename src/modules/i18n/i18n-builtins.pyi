class i18n:
    # Basic phases
    hello: str = data["hello"]
    config_path: str = data["config_path"]
    init_ok: str = data["init_ok"]
    start: str = data["start"]
    stop: str = data["stop"]

    # Server auth
    auth_need_key: str = data["auth_need_key"]
    auth_empty_key: str = data["auth_empty_key"]
    auth_cannot_open_browser: str = data["auth_cannot_open_browser"]
    auth_use_link: str = data["auth_use_link"]

    # GUI phases
    GUI_yes: str = data["GUI_yes"]
    GUI_no: str = data["GUI_no"]
    GUI_ok: str = data["GUI_ok"]
    GUI_cancel: str = data["GUI_cancel"]
    GUI_need_key_message: str = data["GUI_need_key_message"]
    GUI_enter_key_message: str = data["GUI_enter_key_message"]
    GUI_cannot_open_browser: str = data["GUI_cannot_open_browser"]

    # Command: man
    man_message_man: str = data["man_message_man"]
    help_message_man: str = data["help_message_man"]
    man_for: str = data["man_for"]
    man_message_not_found: str = data["man_message_not_found"]
    man_command_not_found: str = data["man_command_not_found"]

    # Command: help
    man_message_help: str = data["man_message_help"]
    help_message_help: str = data["help_message_help"]
    help_command: str = data["help_command"]
    help_message: str = data["help_message"]
    help_message_not_found: str = data["help_message_not_found"]

    # Command: stop
    man_message_stop: str = data["man_message_stop"]
    help_message_stop: str = data["help_message_stop"]

    # Command: exit
    man_message_exit: str = data["man_message_exit"]
    help_message_exit: str = data["help_message_exit"]

    data = {
  "": "Basic phases",
  "hello": "Hello from KuiToi-Server!",
  "config_path": "Use {} for config.",
  "init_ok": "Initializing ready.",
  "start": "Server started!",
  "stop": "Goodbye!",

  "": "Server auth",
  "auth_need_key": "BEAM key needed for starting the server!",
  "auth_empty_key": "Key is empty!",
  "auth_cannot_open_browser": "Cannot open browser: {}",
  "auth_use_link": "Use this link: {}",

  "": "GUI phases",
  "GUI_yes": "Yes",
  "GUI_no": "No",
  "GUI_ok": "Ok",
  "GUI_cancel": "Cancel",
  "GUI_need_key_message": "BEAM key needed for starting the server!\nDo you need to open the web link to obtain the key?",
  "GUI_enter_key_message": "Please type your key:",
  "GUI_cannot_open_browser": "Cannot open browser.\nUse this link: {}",

  "": "Command: man",
  "man_message_man": "man - display the manual page for COMMAND.\nUsage: man COMMAND",
  "help_message_man": "Display the manual page for COMMAND.",
  "man_for": "Manual for command",
  "man_message_not_found": "man: Manual message not found.",
  "man_command_not_found": "man: command \"{}\" not found!",

  "": "Command: help",
  "man_message_help": "help - display names and brief descriptions of available commands.\nUsage: help [--raw]\nThe `help` command displays a list of all available commands along with a brief description of each command.",
  "help_message_help": "Display names and brief descriptions of available commands",
  "help_command": "Command",
  "help_message": "Help message",
  "help_message_not_found": "No help message found",

  "": "Command: stop",
  "man_message_stop": "stop - Just shutting down the server.\nUsage: stop",
  "help_message_stop": "Server shutdown.",

  "": "Command: exit",
  "man_message_exit": "exit - Just shutting down the server.\nUsage: stop",
  "help_message_exit": "Server shutdown."
}
