Plugin for CudaText.
Config menu items on start app. 
Default config file is
	settings\menu.json
Other file can uses by opt
	"config_menus_from"

Author: Andrey Kvichanskiy (kvichans, at forum)


==========
What parts of menus can be configured?
==========
CudaText (for version "0.9.8") allows:
    Change all items of main menu (File/Edit/...).
    Change all items of File except submenu Open recent.
    Change all items of Edit, Selection, Search, View.
    No changeable items in Plugins, Options, Help (but its are complemented).
    Change all items of local menu for main text.
    No changeable items in other local menus.

Change all means that you can rename/skip/move all native items and can add any others. 
Indeed you can at first clear all native items and then to fill with needed. Or save native and add needed to the end.

Three submenus (Plugins, Options, Help) dont allow to clear but allow to add new items.

Filling likes to create a tree as you can add not only commands but submenus too. 
Note that some submenus are autofilled:
    "recents" - recent-files submenu (natively in File)
    "themes" - Color-themes submenu (natively in Options)
    "plugins" - Plugins submenu (natively as item of main menu)

Need commands you can find in two collections:
    Part of native commands (see names into py\cudatext_cmd.py start with cmd_ or cCommand_)
    All plugin commands (see install.inf files for all installed plugin or/and items of settings\plugins.json)

==========
Settings
==========
After plugin installation (and once app start) file menu.json appears in directory settings. 
It allows to repeat (not all but almost) native menus and it is good to start experiments.

Settings for plugin:
    Option "config_menus_from" point to config file name (as "menu.json") which will be searched into directory settings.
    Option "config_menus_on_start" with values true/false to apply config file when app starts.
    Option "config_menus_on_focus" with values true/false to apply config file when text editor gets focus. 
		Only true allows to use adaptive menus (lexer-menus).

Better to rename file menu.json to my-menu.json and to write new value in user.json for key "config_menus_from". 
Source menu.json can be updated in the future with upgrade of plugin/app.

Note that key "config_menus_from" can has different values for different lexers. 
Thus you can use lexer-menus. 
For this you can open current lexer settings (Options/Settings - more/Settings - lexer overide) and set value for key "config_menus_from".

Example:
    In settings/user.json
        "config_menus_from":"my-menu.json" (all my menus)
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
        "top","top-file","top-edit","top-sel","top-sr","top-view","top-op","top-help","text"
    You can use any subset of the list. Lexer-menus can rebuild only context menu ("text").
    Root key "top" uses to rebuild main menu. You can use other names (Find instead Search), change order, skip something (Help?) or add new items.
    Root key "text" uses to rebuild context (local) menu for editing text.
    Pair "how":"clear" uses to fill as empty. It is default.
    Pair "how":"add" uses to fill at end.

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
    Pair "cap":"-" uses to add menu separator.
    Values for key "cmd" are
        names from py\cudatext_cmd.py (start with cmd_ or cCommand_),
        strings "module,method" for any plugin module and method in it.
