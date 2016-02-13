''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '0.9.3 2016-02-13'
'''

import  os, shutil, webbrowser, sys
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

DEF_MENU_CFG_FILE   = 'menu.json'
REF_HELP_CFG_MENU   = 'https://github.com/kvichans/cuda_config_menu/wiki/Help-for-config-menu-with-JSON-files'

# Localization
LC_MENU_NO_FILE     = 'No menu config file "{}"'
LC_MENU_NO_PRE_ID   = 'Skip config for id="{}" - no such main submenu'
LC_MENU_CONFIG_OK   = 'OK config menus from "{}"'
LC_MENU_CONFIG_FILE = '&Config file (default folder is "settings")'
LC_CONFIG_HOW_APPLY = 'When configure:'
LC_CONFIG_ON_START  = 'On &start'
LC_CONFIG_ON_START_H= 'Once when CudaText starts'
LC_CONFIG_ON_FOCUS  = 'On &focus'
LC_CONFIG_ON_FOCUS_H= "When any text gets focus, lexer's or common menu sets"
LC_CONFIG_NOW       = 'Just &now'
LC_CHOOSE_FILE      = 'Choose existed file'

pass;                           # Logging
pass;                           from pprint import pformat
pass;                           pfrm15=lambda d:pformat(d,width=15)
pass;                           LOG = (-2==-2)  # Do or dont logging.

last_file_cfg       = ('', 0)

CMD_NMS         = [nm for nm in dir(cmds) if nm.startswith('cCommand_') or nm.startswith('cmd_')]

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
            cmd = str(eval('cmds.'+cmd)) if cmd in CMD_NMS else cmd
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
    global last_file_cfg
    mn_cfg_json = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE) if not mn_cfg_json else mn_cfg_json
    pass;                       #LOG and apx.log('mn_cfg_json={}',mn_cfg_json)
    if not mn_cfg_json:    
        return app.msg_status(LC_MENU_NO_FILE.format(mn_cfg_json))
    mn_cfg_json = os.path.join(app.app_path(app.APP_DIR_SETTINGS), mn_cfg_json)
    if not os.path.exists(mn_cfg_json):
        last_file_cfg   = ('', 0)
        return app.msg_status(LC_MENU_NO_FILE.format(mn_cfg_json))

    # Try to skip config as the json is same as the last applied
    curr_file_cfg   =   (mn_cfg_json
                       , os.path.getmtime(mn_cfg_json))
    skip            = ( (curr_file_cfg[0] == last_file_cfg[0]) 
                    and (curr_file_cfg[1] <= last_file_cfg[1]) )
    if skip:
        pass;                  #LOG and apx.log('Skip as same as last mn_cfg_json={}',mn_cfg_json)
        return
    last_file_cfg   =    curr_file_cfg

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
            app.msg_status(LC_MENU_NO_PRE_ID, _PRE_ID.format(mn_pre_id))
            continue # for mn_pre_id
        if mn_pre.get('how', 'add') == 'clear':
            app.app_proc(app.PROC_MENU_CLEAR, mn_pre_id)
        _reset_menu(mn_pre_id, mn_pre.get('sub', []))
    print(         LC_MENU_CONFIG_OK.format(mn_cfg_json))
    app.msg_status(LC_MENU_CONFIG_OK.format(mn_cfg_json))
   #def config_menus

C1      = chr(1)
C2      = chr(2)
POS_FMT = 'pos={l},{t},{r},{b}'.format
GAP     = 5
def top_plus_for_os(what_control, base_control='edit'):
    ''' Addition for what_top to align text with base.
        Params
            what_control    'check'/'label'/'edit'/'button'/'combo'/'combo_ro'
            base_control    'check'/'label'/'edit'/'button'/'combo'/'combo_ro'
    '''
    if what_control==base_control:
        return 0
    env = sys.platform
    if base_control=='edit': 
        if env=='win32':
            return apx.icase(what_control=='check',    1
                            ,what_control=='label',    3
                            ,what_control=='button',  -1
                            ,what_control=='combo_ro',-1
                            ,what_control=='combo',    0
                            ,True,                     0)
        if env=='linux':
            return apx.icase(what_control=='check',    1
                            ,what_control=='label',    5
                            ,what_control=='button',   1
                            ,what_control=='combo_ro', 0
                            ,what_control=='combo',   -1
                            ,True,                     0)
        if env=='darwin':
            return apx.icase(what_control=='check',    2
                            ,what_control=='label',    3
                            ,what_control=='button',   0
                            ,what_control=='combo_ro', 1
                            ,what_control=='combo',    0
                            ,True,                     0)
        return 0
       #if base_control=='edit'
    return top_plus_for_os(what_control, 'edit') - top_plus_for_os(base_control, 'edit')
   #def top_plus_for_os

at4chk  = top_plus_for_os('check')
at4lbl  = top_plus_for_os('label')
at4btn  = top_plus_for_os('button')

class Command:
    def __init__(self):
        self.config_menus_on_focus  = apx.get_opt('config_menus_on_focus', False)
    
    def on_start(self, ed_self):
        if not apx.get_opt('config_menus_1st_done', False):
            # Actions on first run
            mn_cfg_src  = os.path.join(os.path.dirname(__file__)         , DEF_MENU_CFG_FILE)
            mn_cfg_trg  = os.path.join(app.app_path(app.APP_DIR_SETTINGS), DEF_MENU_CFG_FILE)
            pass;              #LOG and apx.log('mn_cfg_src, mn_cfg_trg={}',(mn_cfg_src, mn_cfg_trg))
            if not os.path.exists(mn_cfg_trg):
                shutil.copy(mn_cfg_src, mn_cfg_trg)
            apx.set_opt('config_menus_1st_done', True)
        if apx.get_opt('config_menus_on_start', True):
            config_menus()
       #def on_start

#   def on_open(self, ed_self):
#       pass;                  #LOG and apx.log('')
#       config_menus()
#      #def on_open

    def on_focus(self, ed_self):
        pass;                  #LOG and apx.log('')
        if self.config_menus_on_focus:
            config_menus()
       #def on_focus

    def config_menus(self):
        config_menus()
       #def config_menus

    def config_menus_open(self):
        cfg_json    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
        cfg_json    = os.path.join(app.app_path(app.APP_DIR_SETTINGS), cfg_json)
        app.file_open(cfg_json)
       #def config_menus_open

    def config_menus_help(self):
        webbrowser.open_new_tab(REF_HELP_CFG_MENU)
        app.msg_status('Opened in browser')
       #def config_menus_help

    def config_menus_settings(self):
        cfg_file    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
        cfg_on_start= apx.get_opt('config_menus_on_start', True)
        cfg_on_focus= apx.get_opt('config_menus_on_focus', False)

        at_l4b      = top_plus_for_os('label', 'button')
        at_l4c      = top_plus_for_os('label', 'check')
        at_b4c      = top_plus_for_os('button', 'check')
        while True:
            DLG_W, DLG_H= GAP+300+GAP, GAP+160+GAP
            ans = app.dlg_custom('Settings for "Config menu"'   ,DLG_W, DLG_H, '\n'.join([]
            +[C1.join(['type=label'     ,POS_FMT(l=GAP,             t=GAP,              r=DLG_W,b=0)
                      ,'cap='+LC_MENU_CONFIG_FILE
                      ])] # i= 0
            +[C1.join(['type=edit'      ,POS_FMT(l=GAP,             t=GAP+18,           r=DLG_W-GAP-50,b=0)
                      ,'val='+cfg_file
                      ])] # i= 1
            +[C1.join(['type=button'    ,POS_FMT(l=DLG_W-GAP-50,    t=GAP+18+at4btn,    r=DLG_W-GAP,b=0)
                      ,'cap=&...'
                      ])] # i= 2

            +[C1.join(['type=label'     ,POS_FMT(l=GAP,             t=50+at_l4c,        r=GAP+150,b=0)
                      ,'cap='+LC_CONFIG_HOW_APPLY
                      ])] # i= 3
            +[C1.join(['type=check'     ,POS_FMT(l=GAP+120,         t=50,               r=GAP+120+150,b=0)
                      ,'cap='+LC_CONFIG_ON_START
                      ,'hint='+LC_CONFIG_ON_START_H
                      ,'val='+('1' if cfg_on_start else '0')
                      ])] # i= 4
            +[C1.join(['type=check'     ,POS_FMT(l=GAP+120,         t=75,               r=GAP+120+150,b=0)
                      ,'cap='+LC_CONFIG_ON_FOCUS
                      ,'hint='+LC_CONFIG_ON_FOCUS_H
                      ,'val='+('1' if cfg_on_focus else '0')
                      ])] # i= 5
            +[C1.join(['type=button'     ,POS_FMT(l=GAP+120,        t=103+at_b4c,       r=DLG_W-GAP-50,b=0)
                      ,'cap='+LC_CONFIG_NOW
                      ])] # i= 6

            +[C1.join(['type=linklabel' ,POS_FMT(l=GAP,             t=DLG_H-30+at_l4b,  r=GAP+50,b=0)
                      ,'cap=Help'
                      ,'props='+REF_HELP_CFG_MENU #url
                      ])] # i= 7
            +[C1.join(['type=button'    ,POS_FMT(l=DLG_W-160,       t=DLG_H-30,         r=DLG_W-80,b=0)
                      ,'cap=OK'
                      ,'props=1' #default
                      ])] # i= 8
            +[C1.join(['type=button'    ,POS_FMT(l=DLG_W-75,        t=DLG_H-30,         r=DLG_W-GAP,b=0)
                      ,'cap=Cancel'
                      ])] # i= 9
            ), 1)    # start focus
            if ans is None:  
                return None
            (ans_i
            ,vals)      = ans
            vals        = vals.splitlines()
            ans_s       = apx.icase(False,''
                           ,ans_i== 2,'browse'
                           ,ans_i== 6,'apply'
                           ,ans_i== 8,'ok'
                           ,ans_i== 9,'cancel'
                           )
            if ans_s == 'cancel':
                return
            cfg_file    = vals[ 1]
            cfg_on_start= vals[ 4]=='1'
            cfg_on_focus= vals[ 5]=='1'
            
            cfg_path    = os.path.join(app.app_path(app.APP_DIR_SETTINGS), cfg_file)
            if False:pass
            elif ans_s == 'ok':
                #Checks
                if (cfg_on_start or cfg_on_focus) and not os.path.isfile(cfg_path):
                    app.msg_box(LC_CHOOSE_FILE, app.MB_OK)
                    focused = 1
                    continue #while
                break #while
            
            elif ans_s=='apply':
                if not os.path.isfile(cfg_path):
                    app.msg_box(LC_CHOOSE_FILE, app.MB_OK)
                    focused = 1
                    continue #while
                config_menus(cfg_path)
            
            elif ans_s=='browse':
                cfg_file_new= app.dlg_file(True, cfg_file, app.app_path(app.APP_DIR_SETTINGS), 'Config|*.json')
                if cfg_file_new is None:
                    continue
                cfg_file    = cfg_file_new
                if os.path.dirname(cfg_file)==app.app_path(app.APP_DIR_SETTINGS):
                    cfg_file= os.path.basename(cfg_file)
           #while true

        if cfg_file     != apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE):
            apx.set_opt('config_menus_from',     cfg_file)
        if cfg_on_start != apx.get_opt('config_menus_on_start', True):
            apx.set_opt('config_menus_on_start', cfg_on_start)
        if cfg_on_focus != apx.get_opt('config_menus_on_focus', False):
            apx.set_opt('config_menus_on_focus', cfg_on_focus)
       #def config_menus_settings

    def config_menus_settings_old(self):
        cfg_file    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
        cfg_on_start= apx.get_opt('config_menus_on_start', True)
        cfg_on_focus= apx.get_opt('config_menus_on_focus', False)
        anses       = app.dlg_input_ex(3, "Settings for 'Config menu'"
                        , LC_MENU_CONFIG_FILE, cfg_file
                        , LC_CONFIG_ON_START, 'Y' if cfg_on_start else 'N'
                        , LC_CONFIG_ON_FOCUS, 'Y' if cfg_on_focus else 'N'
                        )
        if anses is None:
            return
        if anses[0]!=cfg_file:
            apx.set_opt('config_menus_from', anses[0])
        if ('Y'==anses[1])!=cfg_on_start:
            apx.set_opt('config_menus_on_start', ('Y'==anses[1]))
        if ('Y'==anses[2])!=cfg_on_focus:
            apx.set_opt('config_menus_on_focus', ('Y'==anses[2]))
       #def config_menus_settings
   #class Command

'''
ToDo
[ ][kv-kv][20nov15] Bind/unbind events
'''
