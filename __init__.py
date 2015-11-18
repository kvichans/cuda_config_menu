''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on githab)
Version:
    '0.8.0 2015-11-18'
'''

import  os
import  cudatext        as app
from    cudatext    import ed
import  cudatext_cmd    as cmds
import  cudax_lib       as apx

# Menu config
PROC_MENU_TOP       = 'top'
PROC_MENU_TOP_FILE  = 'top-file'
PROC_MENU_TOP_EDIT  = 'top-edit'
PROC_MENU_TOP_SEL   = 'top-sel'
PROC_MENU_TOP_SR    = 'top-sr'
PROC_MENU_TOP_VIEW  = 'top-view'
PROC_MENU_TOP_OPTS  = 'top-op'
PROC_MENU_TOP_HELP  = 'top-help'
PROC_MENU_TEXT      = 'text'
PROC_MENU_RECENTS   = 'recents'
PROC_MENU_THEMES    = 'themes'
PROC_MENU_PLUGINS   = 'plugins'

# Localization
MENU_NO_FILE        = 'No menu config file "{}"'
MENU_NO_PRE_ID      = 'Skip config for id="{}" - no such main submenu'
MENU_CONFIG_OK      = 'Reconfig menus from "{}"'

pass;                           # Logging
pass;                           from pprint import pformat
pass;                           pfrm15=lambda d:pformat(d,width=15)
pass;                           LOG = (-2==-2)  # Do or dont logging.

def _reset_menu(mn_prnt_id, mn_items):
    pass;                       #LOG and apx.log('>>mn_prnt_id, mn_items={}',(mn_prnt_id, pfrm15(mn_items)))
    for mn_item in mn_items:
        cap     = mn_item.get('cap', '').strip()
        cmd     = mn_item.get('cmd', '').strip()
        subs    = mn_item.get('sub', [])
        if False:pass
        elif ''==cap:
            pass
        elif '-'==cap:
            # Sep!
            pass
            app.app_proc(           app.PROC_MENU_ADD, '{};{};{}'.format(mn_prnt_id, '',    cap))
        elif ''!=cmd:
            # Cmd!
            cmd = str(eval('cmds.'+cmd)) if cmd.startswith('cmd_') or cmd.startswith('cCommand_') else cmd
            app.app_proc(           app.PROC_MENU_ADD, '{};{};{}'.format(mn_prnt_id, cmd,   cap))
        elif subs:
            # Submenu!
            id_sub  = app.app_proc( app.PROC_MENU_ADD, '{};{};{}'.format(mn_prnt_id, 0,     cap))
            pass;               #LOG and apx.log('?? id_sub, subs={}',(id_sub, subs))
            _reset_menu(id_sub, subs)
            pass;               #LOG and apx.log('ok id_sub={}',(id_sub))
    pass;                       #LOG and apx.log('<<')
   #def _reset_menu

def config_menus(mn_cfg_json=''):
    ''' Reset some menus from config file
        File structure is dict with pairs
            {<menu_pre_key>:{<configs-pre>}, <menu_pre_key>:{<config-pre>} ...}
        <menu_pre_key> from list                            (default menu entries)
            "top" "top-file" "top-edit" "top-sel" "top-sr" "top-view" "top-op" "top-help" "text"
        <config-pre> is dict with pairs
            "how": "clear"|"add"                            ("add" to append (default), "clear" to remove prev content)
            "sub": [<config-item> ,<config-item> ...]
        <config-item> is dict with pairs
            "cap": <visible name>|"-"                       ("-" for separator)
            "cmd": <int command code>|<py-module,method>    (for cmd-item, ignored if "cap"=="-")
            "sub":[<config-item> ,<config-item> ...]        (for submenu, ignored if "cmd")
    '''
    mn_cfg_json = apx.get_opt('config_menus_from', mn_cfg_json) if not mn_cfg_json else mn_cfg_json
    pass;                       #LOG and apx.log('mn_cfg_json={}',mn_cfg_json)
    if not mn_cfg_json:    return app.msg_status(MENU_NO_FILE.format(mn_cfg_json))
    mn_cfg_json = os.path.join(app.app_path(app.APP_DIR_SETTINGS), mn_cfg_json)
    mn_cfg      = apx._json_loads(open(mn_cfg_json).read())
    pass;                       #LOG and apx.log('mn_cfg={}',pfrm15(mn_cfg))
    pre_list    = (PROC_MENU_TOP
                  ,PROC_MENU_TOP_FILE
                  ,PROC_MENU_TOP_EDIT
                  ,PROC_MENU_TOP_SEL
                  ,PROC_MENU_TOP_SR  
                  ,PROC_MENU_TOP_VIEW
                  ,PROC_MENU_TOP_OPTS
                  ,PROC_MENU_TOP_HELP
                  ,PROC_MENU_TEXT)
    for mn_pre_id, mn_pre in mn_cfg.items():
        if mn_pre_id not in pre_list:
            app.msg_status(MENU_NO_PRE_ID.format(mn_pre_id))
            continue # for mn_pre_id
        if mn_pre.get('how', 'add') == 'clear':
            app.app_proc(app.PROC_MENU_CLEAR, mn_pre_id)
        _reset_menu(mn_pre_id, mn_pre.get('sub', []))
    print(         MENU_CONFIG_OK.format(mn_cfg_json))
    app.msg_status(MENU_CONFIG_OK.format(mn_cfg_json))
   #def config_menus

class Command:
    def on_start(self, ed_self):
        config_menus()
       #def on_start
    def config_menus(self):
        config_menus()
       #def config_menus
   #class Command
