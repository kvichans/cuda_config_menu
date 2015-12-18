Plugin for CudaText.
Configures menus, top and context menu (on app start). 
Default config file:
	settings\menu.json
Other file can be set by option in user.json:
	"config_menus_from"

Author: Andrey Kvichanskiy (kvichans, at forum)


==========
What parts of menus can be configured?
==========

    Can change items of main menu (File, Edit, ...).
    Can change items of File except submenu "Open recent".
    Can change items of Edit, Selection, Search, View, Options, Help.
    Can change items of context menu for editor text.
    Not changeable items in other context menus (for gutter, for tab header...)

Can-change means that you can rename/remove/move all native items and can add any others. 
Indeed you can first clear all native items and then add needed ones. Or keep native items and add needed to the end.

Filling menus is like creating a tree, you can not only add items, but add submenus of any level.
Note that some submenus are autofilled:
    "recents" - recent-files submenu (natively in File)
    "themes" - Color-themes submenu (natively in Options)
    "plugins" - Plugins submenu (natively as item of main menu)

Needed commands you can find in two collections:
    Native commands (see names in file py\cudatext_cmd.py, which start with cmd_ or cCommand_)
    All plugins commands (see install.inf files for all installed plugins, or items in settings\plugins.json)

==========
Settings
==========
After plugin installation (and restart of app) file menu.json appears in directory settings. 
It allows to repeat (not all but most) native menus and it is good to start experiments.

Settings for plugin in user.json:
    Option "config_menus_from" - config file name (e.g. "menu.json") which will be read from dir settings.
    Option "config_menus_on_start" - values true/false - to apply config file when app starts.
    Option "config_menus_on_focus" - values true/false - to apply config file when text editor gets focus. 
		Only true-value here allows to use adaptive menus (menus for current lexer).

Better to rename file menu.json to my-menu.json and to write option "config_menus_from" in user.json. 
Original menu.json can be updated in the future with plugin update.

Note that option "config_menus_from" can have different values for different lexers. 
Thus you can use lexer-specific menus. 
For this you can open current lexer settings (Options/ Settings - more/ Settings - lexer overide) and set value for option "config_menus_from".

Example:
    In settings/user.json
        "config_menus_from":"my-menu.json" (sets all my menus)
    In settings/lexer Python.json
        "config_menus_from":"menu Python.json" (changes for menus to work with Python)
    In settings/lexer JSON.json
        "config_menus_from":"menu JSON.json" (changes for menus to work with JSON)

==========
JSON file format
==========
Brief view of file content:
{
  "top-file":{"how":"clear", ...all new items for native File menu...},
  "top-help":{"how":"add", ...additional items for native Help menu...},
}

Notes
    Root keys (like "top-file" and "top-help" above) must be only from the list
        "top",
        "top-file",
        "top-edit",
        "top-sel",
        "top-sr",
        "top-view",
        "top-op",
        "top-help",
        "text"
    You can use any subset of the list. 
    Lexer-menus can rebuild only context menu ("text").
    Root key "top" is to rebuild main menu. You can use other menuitem names (eg "Find" instead of "Search"), change order, skip something (e.g. Help) or add new items.
    Root key "text" is to rebuild context (local) menu for editor text.
    Pair "how":"clear" is to clear all items. It is default.
    Pair "how":"add" is to add items at end.

Brief view of one branch:
  "top-file":{
    sub:[
      {"cap":"Save file", "cmd":"cmd_FileSave"},
      {"cap":"Lines", 
       "sub":[
         {"cap":"Trim all", "cmd":"cCommand_TextTrimSpacesAll"},
         {"cap":"-"},
         {"cap":"My Split","cmd":"my_plug,split"},
       ],
      },
    ],
  },

Notes
    Value for key "cap" is caption for item or submenu.
    Pair "cap":"-" means menu separator.
    Values for key "cmd" are
        names from py\cudatext_cmd.py (starting with cmd_ or cCommand_),
        strings "module,method" for any plugin module and method in it.
