''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github)
Version:
    '1.1.06 2018-02-08'
'''

import  os, shutil, webbrowser, json, collections, re
import  cudatext            as app
from    cudatext        import ed
import  cudatext_cmd        as cmds
import  cudax_lib           as apx
from    .cd_plug_lib    import *

MIN_API_VER = '1.0.172' # menu_proc() <== PROC_MENU_*
MIN_API_VER = '1.0.185' # menu_proc() with hotkey,tag

VERSION     = re.split('Version:', __doc__)[1].split("'")[1]
VERSION_V,  \
VERSION_D   = VERSION.split(' ')

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

# I18N
_                   = get_translation(__file__)

pass;                           # Logging
pass;                           from pprint import pformat
pass;                           pfrm15=lambda d:pformat(d,width=15)
pass;                           LOG = (-2== 2)  # Do or dont logging.

last_file_cfg       = ('', 0)

CMD_NMS         = [nm for nm in dir(cmds) if nm.startswith('cCommand_') or nm.startswith('cmd_')]

def _reset_menu_old(mn_prnt_id, mn_items):
    pass;                      #LOG and apx.log('>>mn_prnt_id, mn_items={}',(mn_prnt_id, pfrm15(mn_items)))
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
            app.menu_proc(          mn_prnt_id, app.MENU_ADD, caption=cap)
        elif ''!=cmd:
            # Cmd!
            pass;              #LOG and apx.log('ok cmd={}',(cmd))
            cmd = str(eval('cmds.'+cmd)) if cmd in CMD_NMS else cmd
            app.menu_proc(          mn_prnt_id, app.MENU_ADD, command=cmd, caption=cap)
        elif subs:
            # Submenu!
            id_sub  = app.menu_proc(mn_prnt_id, app.MENU_ADD, command=cap)
            pass;              #LOG and apx.log('?? id_sub, subs={}',(id_sub, subs))
            _reset_menu_old(id_sub, subs)
            pass;              #LOG and apx.log('ok id_sub, subs={}',(id_sub, subs))
    pass;                      #LOG and apx.log('<<')
   #def _reset_menu_old

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
    if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update CudaText'))
    
    pass;                       LOG and log('mn_cfg_json={}',mn_cfg_json)
    global last_file_cfg
    config_menus_on_focus  = apx.get_opt('config_menus_on_focus', False, apx.CONFIG_LEV_USER)
    mn_cfg_json = mn_cfg_json \
                    if mn_cfg_json else \
                  apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE, apx.CONFIG_LEV_USER) \
                    if not config_menus_on_focus else \
                  apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
                  
    pass;                       LOG and apx.log('mn_cfg_json={}',mn_cfg_json)
    if not mn_cfg_json:    
        return app.msg_status(_('No menu config file'))
    mn_cfg_json = mn_cfg_json \
                    if os.path.exists(mn_cfg_json) else \
                  os.path.join(app.app_path(app.APP_DIR_SETTINGS), mn_cfg_json)
    if not os.path.exists(mn_cfg_json):
        last_file_cfg   = ('', 0)
        return app.msg_status(_('No menu config file "{}"').format(mn_cfg_json))

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
    if isinstance(mn_cfg, list):
        # New format
        _reset_menu_hnt(mn_cfg)
        print(         _('Loading menus "{}" ({})').format(mn_cfg_json.replace(app.app_path(app.APP_DIR_SETTINGS)+os.sep, ''), VERSION_V))
        app.msg_status(_('Loading menus "{}" ({})').format(mn_cfg_json.replace(app.app_path(app.APP_DIR_SETTINGS)+os.sep, ''), VERSION_V))
    else:
        # Old format
        pass;                   #LOG and apx.log('mn_cfg={}',pfrm15(mn_cfg))
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
                app.msg_status(_('Skip config for id="{}" - no such main submenu').format(mn_pre_id))
                continue # for mn_pre_id
            if mn_pre.get('how', 'add') == 'clear':
                app.menu_proc(  mn_pre_id, app.MENU_CLEAR)
            _reset_menu_old(    mn_pre_id, mn_pre.get('sub', []))
        print(         _('Loading menus "{}"').format(mn_cfg_json.replace(app.app_path(app.APP_DIR_SETTINGS), '')))
        app.msg_status(_('Loading menus "{}"').format(mn_cfg_json.replace(app.app_path(app.APP_DIR_SETTINGS), '')))
   #def config_menus

C1      = chr(1)
C2      = chr(2)
POS_FMT = 'pos={l},{t},{r},{b}'.format
GAP     = 5

SPEC_IDS= { 'recents':'_recents',  'langs':'_langs',  'enc':'_enc',  'lexers':'_lexers'
          ,'_recents':'_recents', '_langs':'_langs', '_enc':'_enc', '_lexers':'_lexers'
          ,  'plugins':'_plugins'
          , '_plugins':'_plugins'
          , '_oplugins':'_oplugins'
          , '_themes-ui':'_themes-ui'
          , '_themes-syntax':'_themes-syntax'
          }
def _reset_menu_hnt(mnu_list, prnt_id=None, _prnt_cap_path=''):
    if prnt_id is None:
        # Start with root nodes: toppest, capless
        pass;                   LOG and log('BGN',)
        for mnu_dict in mnu_list:
            pass;              #LOG and log('mnu_dict={}',mnu_dict)
            top_id  = mnu_dict['hint']
            pass;               LOG and log('top_id={}',top_id)
            app.menu_proc(                    top_id, app.MENU_CLEAR)
            _reset_menu_hnt(mnu_dict['sub'],  top_id)
        pass;                   LOG and log('END',)
        return
    # Tree sub-node
    pass;                       LOG and log('>> prnt_id={} _prnt_cap_path={}',prnt_id, _prnt_cap_path)
    pass;                      #LOG and log('mnu_list={}',mnu_list)
    for mnu_dict in mnu_list:
        pass;                  #LOG and log('mnu_dict={}',mnu_dict)
        cap     = mnu_dict.get('cap'    ,'')
        tag     = mnu_dict.get('tag'    ,'')
        hnt     = mnu_dict.get('hint'   ,'')
        cmd_s   = mnu_dict.get('cmd'    ,'')
        pass;                   LOG and log('cap,hnt,cmd_s={}',(cap,hnt,cmd_s))
        if False:pass
        elif ''==cap:
            pass;               LOG and log('Error "no cap": _prnt_cap_path={} mnu_dict={}',_prnt_cap_path,mnu_dict)
        elif '-'==cap:
            # Sep!
            pass
            app.menu_proc(          prnt_id, app.MENU_ADD, caption=cap)
        elif hnt in SPEC_IDS:
            # Autofilled core submenu
            pass;               LOG and log('>> prnt_id={}',prnt_id)
            pass;               LOG and log('?? use SPEC_IDS command={}',(SPEC_IDS[hnt]))
            app.menu_proc(          prnt_id, app.MENU_ADD, command=SPEC_IDS[hnt], caption=cap)
            pass;               LOG and log('ok use SPEC_IDS',())
        elif tag.startswith('auto_config:'):
            # Autofilled plugin submenu
            cmd4plug= tag[len('auto_config:'):]
            id_sub  = app.menu_proc(prnt_id, app.MENU_ADD, caption=cap, tag=tag)
            pass;              #log('cmd4plug, id_sub={}',(cmd4plug, id_sub))
            app.app_proc(           app.PROC_EXEC_PLUGIN, f('{},{}', cmd4plug, id_sub))
        elif hnt and hnt[0]=='_' and ':' in hnt:
            # Autofilled plugin submenu
            id_sub  = app.menu_proc(prnt_id, app.MENU_ADD, command=hnt, caption=cap)
            cmd4plug= hnt[1:].replace(':', ',')
            pass;               LOG and log('?? PROC_EXEC_PLUGIN id_sub={} cmd4plug={}',id_sub,cmd4plug)
            app.app_proc(           app.PROC_EXEC_PLUGIN, f('{},{}', cmd4plug, id_sub))
            pass;               LOG and log('ok PROC_EXEC_PLUGIN',id_sub)
        elif ',' in cmd_s or '.' in cmd_s or ';' in cmd_s:
            # Plugin Cmd!
            app.menu_proc(          prnt_id, app.MENU_ADD, command=cmd_s, caption=cap)
        elif cmd_s:
            # Core Cmd!
            if not hnt and cmd_s not in CMD_NMS:
                pass;           LOG and log('Error "unk cmd": _prnt_cap_path={} mnu_dict={}',_prnt_cap_path,mnu_dict)
                continue#for mnu_dict
            hnt     = hnt if hnt else str(eval('cmds.'+cmd_s))
            app.menu_proc(          prnt_id, app.MENU_ADD, command=hnt, caption=cap)
        else:
            # Submenu!
            hnt     = hnt if hnt else '0'
            id_sub  = app.menu_proc(prnt_id, app.MENU_ADD, command=hnt, caption=cap)
            pass;              #LOG and apx.log('?? id_sub, subs={}',(id_sub, subs))
            sub     = mnu_dict.get('sub')
            if not sub or not isinstance(sub, list):
                pass;           LOG and log('Error "no sub": _prnt_cap_path={} mnu_dict={}',_prnt_cap_path,mnu_dict)
                continue#for mnu_dict
            _reset_menu_hnt(sub, id_sub, _prnt_cap_path+'/'+cap)
        #for mnu_dict
        sub_dict= mnu_dict.get('sub'    ,None)
        
    pass;                       LOG and log('<< prnt_id={} _prnt_cap_path={}',prnt_id, _prnt_cap_path)
   #def _reset_menu_hnt

def _save_menu_to_json(save_to=None):
    cmD2cmN = {str(eval('cmds.'+cmdN)):cmdN for cmdN in CMD_NMS}
        
    OrdDct  = collections.OrderedDict
#   HINT2MID= dict( file    = 'top-file'
#                  ,edit    = 'top-edit'
#                  ,sel     = 'top-sel'
#                  ,search  = 'top-sr'
#                  ,view    = 'top-view'
#                  ,options = 'top-op'
#                  ,help    = 'top-help'
#                   )
    ENC2CMD = {'utf-8'          :'utf8bom'
              ,'utf-8 no bom'   :'utf8nobom'
              ,'utf-16 le'      :'utf16le'
              ,'utf-16 be'      :'utf16be'
              ,'iso-8859-1'     :'iso1'
              ,'iso-8859-2'     :'iso2'
              ,'macintosh'      :'mac'
              }

    def scan_menu_tree(prnt_id='', hnt_path='', dad_id='', prnt_nm=''):
        if not prnt_id:
            # Default roots
            pass;               LOG and log('BGN with roots',)
            mnu =  [OrdDct([('cap' ,'')
                           ,('hint','top')
                           ,('sub' ,scan_menu_tree('top')) ])
                   ,OrdDct([('cap' ,'')
                           ,('hint','text')
                           ,('sub' ,scan_menu_tree('text')) ])
                   ]
            pass;               LOG and log('END',)
            return mnu
        pass;                   LOG and log('>> prnt_id={}, hnt_path={}',prnt_id, hnt_path)
        nmu_its = app.menu_proc(prnt_id, app.MENU_ENUM)  ##??
#       pass;                   LOG and log('nmu_its={}',nmu_its)
        mnu         = []
        for nmu_it in nmu_its:
            pass;               LOG and log('nmu_it={}',nmu_it)
            nmn = nmu_it['cap']
            cmd = nmu_it['cmd']
            hnt = nmu_it['hint']
            mid = nmu_it['id']
            tag = nmu_it['tag']
            pass;               LOG and log('nmn,cmd,hnt,mid,tag={}',(nmn,cmd,hnt,mid.tag))

            if nmn=='-':
                # Sep
                mnu    += [OrdDct( [('cap' ,'-')])]
                continue 
            
            if hnt in SPEC_IDS :
                # Autofilled submenu
                pass;           LOG and LOG and log('auto spec',)
                mnu    += [OrdDct( [('cap' ,nmn)]
                                 + [('hint',hnt)] )]
                continue 
            
            if tag.startswith('auto_config:'):
                # Autofilled submenu as Tools
                mnu    += [OrdDct( [('cap' ,nmn)]
                                 + [('tag' ,tag)] )]
                continue 
            
            if hnt and hnt[0]=='_' and ':' in hnt:
                # Autofilled submenu as Tools
                mnu    += [OrdDct( [('cap' ,nmn)]
                                 + [('hint',hnt)] )]
                continue 
            
            if cmd==-1 and ('.' in hnt or ';' in hnt):
                # Plugin method
                mnu    += [OrdDct( [('cap', nmn)]
                                 + [('cmd', hnt)] )]
                continue 
            
            # SubMenu?
            is_sub  = bool(app.menu_proc(mid, app.MENU_ENUM))
            if is_sub:
                # SubMenu
                pass;           LOG and log('SubMenu: nmn,hnt,mid={}',(nmn,hnt,mid))
                submnu  = scan_menu_tree(mid, hnt_path+'/'+hnt, prnt_id, prnt_nm+'/'+nmn)
                mnu    += [OrdDct( [('cap' ,nmn)]
                                 +([('hint',hnt)] if hnt else [])
                                 + [('sub' ,submnu)] )]
                continue 

            # Core command!
            pass;               LOG and log('Core/plugin: nmn,hnt,cmd={}',(nmn,hnt,cmd))
            if False:pass
            elif '/enc/' in hnt_path or '/_enc/' in hnt_path:
                # Encoding cmd?
                cmd = nmn.lower()
                cmd = f('cmd_Encoding_{}_{}Reload'
                        ,ENC2CMD.get(cmd, cmd)
                        ,'' if '/enc_reload' in hnt_path else 'No')
            else:
                cmd = cmD2cmN.get(str(cmd), str(cmd))
#               cmd = cmD2cmN.get(hnt, hnt)
            pass;               LOG and log('Core/plugin: nmn,hnt,cmd={}',(nmn,hnt,cmd))
            mnu    += [OrdDct( [('cap' ,nmn)]
#                            +([('hint',hnt)] if hnt else [])
                             + [('cmd' ,cmd)] )]
#           pass;               break#only 1st cmd
           #for nmu_it
        pass;                   LOG and log('<< #mnu={} prnt_id={}, hnt_path={}',len(mnu), prnt_id, hnt_path)
        return mnu
            
#   top_id  = app.dlg_input('"top" or "text" or ""', '')
#   top_id  = top_id if top_id else ''
#   mnu     = scan_menu_tree(top_id)
    mnu     = scan_menu_tree()
    pass;                  #LOG and log('mnu={}',mnu)
    jstx    = json.dumps(mnu, indent=2, ensure_ascii=False)
    jstx    = re.sub(r'{\s*"'       ,r'{"'      ,jstx)
    jstx    = re.sub(r'(\d)\s+}'    ,r'\1}'     ,jstx)
    jstx    = re.sub(r'"\s*}'       ,r'"}'      ,jstx)
    jstx    = re.sub(r'"\s*,\s*"'   ,r'", "'    ,jstx)
    jstx    = re.sub(r'"\s*:\s*"'   ,r'":"'     ,jstx)
    jstx    = re.sub(r'\]\s*}'      ,r']}'      ,jstx)
    jstx    = re.sub(r'\},(\s+) {'  ,r'}\1,{'   ,jstx)
    jstx    = jstx.replace('  ]}', ']}')
    pass;                      #log('jstx={}',(jstx[0:200]))
    if not save_to:
        save_to = app.dlg_file(False, '', '', 'Config|*.json')
        if not save_to: return # app.msg_box(jstx, app.MB_OK)
    open(save_to, 'w', encoding='UTF-8').write(jstx)
   #def _save_menu_to_json

class Command:
    def __init__(self):
        self.loaded         = False
        self.config_menus_on_focus  = apx.get_opt('config_menus_on_focus', False)
    
    def _save_menu_to_json(self, save_to=None):
        ''' Save current menu to json-file
        '''
        FROM_API_VERSION= '1.0.132' # result of PROC_MENU_ENUM has item_id
        if app.app_api_version()<FROM_API_VERSION:  return app.msg_status(_('Need update CudaText'))
        _save_menu_to_json(save_to)
       #def _save_menu_to_json
        
    def on_start(self, ed_self):
#       if not apx.get_opt('config_menus_1st_done', False):
#           # Actions on first run
#           mn_cfg_src  = os.path.join(os.path.dirname(__file__)         , DEF_MENU_CFG_FILE)
#           mn_cfg_trg  = os.path.join(app.app_path(app.APP_DIR_SETTINGS), DEF_MENU_CFG_FILE)
#           pass;              #LOG and apx.log('mn_cfg_src, mn_cfg_trg={}',(mn_cfg_src, mn_cfg_trg))
#           if not os.path.exists(mn_cfg_trg):
#               shutil.copy(mn_cfg_src, mn_cfg_trg)
#           apx.set_opt('config_menus_1st_done', True)
#       pass;                   log('ed_self={}',(ed_self.get_filename()))
        pass;                  #LOG and log('??',())
        if apx.get_opt('config_menus_on_start', False):
            self.loaded    = True
            config_menus()
            pass;               top_its = app.menu_proc(    'top', app.MENU_ENUM)
            pass;              #log('top_its={}',top_its)
       #def on_start

#   def on_open(self, ed_self):
#       pass;                  #LOG and apx.log('')
#       config_menus()
#      #def on_open

    def on_focus(self, ed_self):
#       pass;                   log('ed_self={}',(ed_self.get_filename()))
        pass;                  #LOG and apx.log('')
        if self.config_menus_on_focus:
            self.loaded    = True
            config_menus()
       #def on_focus

    def config_menus(self):
        self.loaded    = True
        config_menus()
       #def config_menus

#   def config_menus_open(self):
#       cfg_json    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
#       cfg_json    = os.path.join(app.app_path(app.APP_DIR_SETTINGS), cfg_json)
#       app.file_open(cfg_json)
#      #def config_menus_open

#   def config_menus_help(self):
#       webbrowser.open_new_tab(REF_HELP_CFG_MENU)
#       app.msg_status(_('Opened in browser'))
#      #def config_menus_help

    def dlg_config(self):
        if app.app_api_version()<MIN_API_VER: return app.msg_status(_('Need update CudaText'))

        def rgb_to_int(r,g,b):    return r | (g<<8) | (b<<16)
        cfg_file    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE, apx.CONFIG_LEV_USER)
        cfg_on_start= apx.get_opt('config_menus_on_start', False)
        cfg_on_focus= apx.get_opt('config_menus_on_focus', False)
        vals=dict(file=cfg_file
                 ,on_s='1' if cfg_on_start else '0'
                 ,on_f='1' if cfg_on_focus else '0'
                 )
        while True:
            cnts=[
#                 dict(cid='save',tp='bt'   ,t=  5      ,l=5        ,w=350          ,cap=_('&Create config file...')    ,en=not self.loaded
                  dict(cid='save',tp='bt'   ,t=  5      ,l=5        ,w=350          ,cap=_('&Create config file with native menu...')
                                                                            ,hint=_('Save all current menus to file.'
                                                                                    '\rOnly for native CudaText menus.')+(
                                                                                  _('\rReload CudaText with '
                                                                                    '\r   [ ] Apply on start'))                             ) #  &c
#                                                                                   '\r   [ ] Apply on start')               if self.loaded else '')     ) #  &c
                 ,dict(           tp='clr'  ,t= 40,l=0,w=1000,h=1           ,props=f('0,{},0,0',rgb_to_int(185,185,185))                    ) #

                 ,dict(           tp='lb'   ,tid='edit' ,l=5        ,w=350          ,cap=_('Confi&g file (default folder is "settings")')   ) #  &g
                 ,dict(cid='edit',tp='bt'   ,t= 50      ,l=5+350-80 ,w=80           ,cap=_('&Open')                                         ) #  &o
                 ,dict(cid='file',tp='ed'   ,t= 75      ,l=5        ,w=350-80                                                               ) #  
                 ,dict(cid='brow',tp='bt'   ,tid='file' ,l=5+350-80 ,w=80           ,cap=_('Select&...')                                    ) #  &.
                 ,dict(cid='on_s',tp='ch'   ,t=110      ,l=5        ,w=100          ,cap=_('Apply on &start')
                                                                            ,hint=_('Once when CudaText starts')                            ) #  &s
                 ,dict(cid='on_f',tp='ch'   ,t=135      ,l=5        ,w=100          ,cap=_('Apply on &focus')
                                                                            ,hint=_("When any text gets focus, lexer's or common menu sets")) #  &f
                 ,dict(cid='just',tp='bt'   ,tid='on_s' ,l=5+120    ,w=150          ,cap=_('&Apply now')
                                                                            ,hint=_('Apply the file once'
                                                                                    '\rShift+Click - Control correctness of the file')      ) #  &a
                 ,dict(cid='help',tp='bt'   ,t=170      ,l=5        ,w=80           ,cap=_('&Help...')                                      ) #  &h
                 ,dict(cid='!'   ,tp='bt'   ,t=170      ,l=5+350-160,w=80           ,cap=_('Save')  ,props='1'                              ) #     default
                 ,dict(cid='-'   ,tp='bt'   ,t=170      ,l=5+350-80 ,w=80           ,cap=_('Close')                                         ) #  
                 ]
            btn, vals, chds = dlg_wrapper(f('{} ({})', _('Config menu'), VERSION_V), 5+350+5, 5+190+5, cnts, vals, focus_cid='file')
            if btn is None or btn=='-':    return
            scam    = app.app_proc(app.PROC_GET_KEYSTATE, '')
            btn_m   = scam + '/' + btn if scam and scam!='a' else btn   # smth == a/smth

            if False:pass
            elif btn=='!':
                # Checks
                cfg_path    = vals['file'] \
                                if os.path.exists(vals['file']) else \
                              os.path.join(app.app_path(app.APP_DIR_SETTINGS), vals['file'])
#               cfg_path    = os.path.join(app.app_path(app.APP_DIR_SETTINGS), vals['file'])
                if (vals['on_s']=='1' or vals['on_f']=='1') and not os.path.isfile(cfg_path):
                    app.msg_box(_('Choose existed file'), app.MB_OK)
                    continue #while
                # Saves
#               if  apx.get_opt('config_menus_from'
#                              ,DEF_MENU_CFG_FILE, apx.CONFIG_LEV_USER) !=  vals['file']:
#                   apx.set_opt('config_menus_from',                        vals['file'])
                if  apx.get_opt('config_menus_from'
                               ,DEF_MENU_CFG_FILE, apx.CONFIG_LEV_USER) !=  cfg_path:
                    apx.set_opt('config_menus_from',                        cfg_path.replace(app.app_path(app.APP_DIR_SETTINGS)+os.sep, '').replace('\\', '\\\\'))
                if  apx.get_opt('config_menus_on_start', False)         != (vals['on_s']=='1'):
                    apx.set_opt('config_menus_on_start',                    vals['on_s']=='1')
                if  apx.get_opt('config_menus_on_focus', False)         != (vals['on_f']=='1'):
                    apx.set_opt('config_menus_on_focus',                    vals['on_f']=='1')
                self.config_menus_on_focus  = apx.get_opt('config_menus_on_focus', False)
                return
            
            elif btn=='brow':
                cfg_file_new= app.dlg_file(True, vals['file'], app.app_path(app.APP_DIR_SETTINGS), 'Config|*.json')
                if not cfg_file_new:continue#while
                vals['file']    = cfg_file_new
                if os.path.dirname(vals['file'])==app.app_path(app.APP_DIR_SETTINGS):
                    vals['file']= os.path.basename(vals['file'])

            elif btn=='save':
                if self.loaded:
                    app.msg_box(_('You cannot create menu config now, '+
                                  'because custom menu is already loaded. '+
                                  'To enable creation of menu config, '+
                                  'uncheck the "Apply on start" and restart CudaText.'), app.MB_OK)
                    continue
                if self.loaded:
                    app.msg_box(_('Choose existed file'), app.MB_OK)
                    continue
                mn_trg  = os.path.join(app.app_path(app.APP_DIR_SETTINGS), DEF_MENU_CFG_FILE)
                save_to = app.dlg_file(False, mn_trg, app.app_path(app.APP_DIR_SETTINGS), 'Config|*.json')
                if not save_to:     continue#while
                self._save_menu_to_json(save_to)
                app.file_open(save_to)

            elif btn in ('edit', 'just'):
#           elif btn in ('edit', 'test', 'just'):
                cfg_path    = vals['file'] \
                                if os.path.exists(vals['file']) else \
                              os.path.join(app.app_path(app.APP_DIR_SETTINGS), vals['file'])
                if not os.path.isfile(cfg_path):
                    app.msg_box(_('Choose existed file'), app.MB_OK)
                    continue #while
                if btn=='edit':
                    app.file_open(cfg_path)
                try:
                    s = open(cfg_path).read()
                    s = re.sub(r'{(\s*),' , r'{\1 ', s)
                    s = re.sub(r',(\s*)}' , r' \1}', s)
                    s = re.sub(r'\[(\s*),', r'[\1 ', s)
                    s = re.sub(r',(\s*)\]', r' \1]', s)
                    json.loads(s)
                    if btn_m=='s/just':
#                   if btn=='test':
                        app.msg_box(_('Correct JSON'), app.MB_OK)
                except Exception as ex:
                    app.file_open(cfg_path)
                    mtch    = re.search(r': line (\d+) column (\d+)', str(ex))
                    if mtch:
                        # Navigate
                        ed.set_caret(int(mtch.group(2))-1, int(mtch.group(1))-1)
                    app.msg_box(_('JSON error:')+'\n\n'+str(ex), app.MB_OK)
                    continue #while
                if btn_m=='just':
                    self.loaded    = True
                    config_menus(cfg_path)
                
            elif btn=='help':
                HELP_BODY   = \
_('''Config file has JSON format.
Main container is list of items, which create menu elements.
  Examples of correct items in main container:
  {"cap":"", "hint":"text", "sub": [???]}          - context menu
  {"cap":"", "hint":"top", "sub": [???]}           - main menu
  {"cap":"&File", "hint":"top-file", "sub": [???]} - main menu, submenu File
  {"cap":"&Edit", "hint":"top-ed", "sub": [???]}   - main menu, submenu Edit
"cap" value can be any (in any language).
    Char "&" is hotkey accelerator character.
"hint" value can be any, but predefined values exist
  "text" is special hint for context menu
  "top" is special hint for main menu
  "recents", 
  "themes", 
  "langs", 
  "plugins" are special hints for autofilled submenus
"sub" value must be list of separator, commands or submenu items. 
Separator item: {"cap":"-"}
Command item:   {"cap":"<any>", "cmd":"???"}
"cmd" value can be:
  Identifiers cCommand_* or cmd_* from module cudatext_cmd.py
  <plugin>,<method>[,<param>] for plugin commands
Submenu item:   {"cap":"<any>", "hint":"<special/any>", "sub":[???]}
----------------------------------------
Convenient way to customize menu
1. Call "Create config file..." to get JSON copy of default CudaText menu.
2. Move/Copy/Translate/Delete/Insert items.
3. Save to new file and specify it as "Config file".
4. Turn on option "Apply on start".
----
Tips
1. Any command/submenu (except "text" and "top") can be used many times.
  For example submenu File can be copied to context menu.
2. Item {"cap":"", "hint":"top", "sub": []} hides main menu. 
  It's correct state. 
''')
                dlg_wrapper(_('Help for "Config menu"'), GAP*2+600, GAP*3+25+550,
                     [dict(cid='htx',tp='me'    ,t=GAP  ,h=550  ,l=GAP          ,w=600  ,props='1,1,1' ) #  ro,mono,border
                     ,dict(cid='-'  ,tp='bt'    ,t=GAP+550+GAP  ,l=GAP+600-90   ,w=90   ,cap='&Close'  )
                     ], dict(htx=HELP_BODY), focus_cid='htx')
           #while true

           #while True:
       #def dlg_config

#   def config_menus_settings(self):
#       cfg_file    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
#       cfg_on_start= apx.get_opt('config_menus_on_start', True)
#       cfg_on_focus= apx.get_opt('config_menus_on_focus', False)
#
#       at4btn      = top_plus_for_os('button')
#       at_l4b      = top_plus_for_os('label', 'button')
#       at_l4c      = top_plus_for_os('label', 'check')
#       at_b4c      = top_plus_for_os('button', 'check')
#       while True:
#           DLG_W, DLG_H= GAP+300+GAP, GAP+160+GAP
#           ans = app.dlg_custom('Settings for "Config menu"'   ,DLG_W, DLG_H, '\n'.join([]
#           +[C1.join(['type=label'     ,POS_FMT(l=GAP,             t=GAP,              r=DLG_W,b=0)
#                     ,'cap='+_('&Config file (default folder is "settings")')
#                     ])] # i= 0
#           +[C1.join(['type=edit'      ,POS_FMT(l=GAP,             t=GAP+18,           r=DLG_W-GAP-50,b=0)
#                     ,'val='+cfg_file
#                     ])] # i= 1
#           +[C1.join(['type=button'    ,POS_FMT(l=DLG_W-GAP-50,    t=GAP+18+at4btn,    r=DLG_W-GAP,b=0)
#                     ,'cap=&...'
#                     ])] # i= 2
#
#           +[C1.join(['type=label'     ,POS_FMT(l=GAP,             t=50+at_l4c,        r=GAP+150,b=0)
#                     ,'cap='+_('When configure:')
#                     ])] # i= 3
#           +[C1.join(['type=check'     ,POS_FMT(l=GAP+120,         t=50,               r=GAP+120+150,b=0)
#                     ,'cap='+_('On &start')
#                     ,'hint='+_('Once when CudaText starts')
#                     ,'val='+('1' if cfg_on_start else '0')
#                     ])] # i= 4
#           +[C1.join(['type=check'     ,POS_FMT(l=GAP+120,         t=75,               r=GAP+120+150,b=0)
#                     ,'cap='+_('On &focus')
#                     ,'hint='+_("When any text gets focus, lexer's or common menu sets")
#                     ,'val='+('1' if cfg_on_focus else '0')
#                     ])] # i= 5
#           +[C1.join(['type=button'     ,POS_FMT(l=GAP+120,        t=103+at_b4c,       r=DLG_W-GAP-50,b=0)
#                     ,'cap='+_('Just &now')
#                     ])] # i= 6
#
#           +[C1.join(['type=linklabel' ,POS_FMT(l=GAP,             t=DLG_H-30+at_l4b,  r=GAP+50,b=0)
#                     ,'cap=Help'
#                     ,'props='+REF_HELP_CFG_MENU #url
#                     ])] # i= 7
#           +[C1.join(['type=button'    ,POS_FMT(l=DLG_W-160,       t=DLG_H-30,         r=DLG_W-80,b=0)
#                     ,'cap=OK'
#                     ,'props=1' #default
#                     ])] # i= 8
#           +[C1.join(['type=button'    ,POS_FMT(l=DLG_W-75,        t=DLG_H-30,         r=DLG_W-GAP,b=0)
#                     ,'cap=Cancel'
#                     ])] # i= 9
#           ), 1)    # start focus
#           if ans is None:  
#               return None
#           (ans_i
#           ,vals)      = ans
#           vals        = vals.splitlines()
#           ans_s       = apx.icase(False,''
#                          ,ans_i== 2,'browse'
#                          ,ans_i== 6,'apply'
#                          ,ans_i== 8,'ok'
#                          ,ans_i== 9,'cancel'
#                          )
#           if ans_s == 'cancel':
#               return
#           cfg_file    = vals[ 1]
#           cfg_on_start= vals[ 4]=='1'
#           cfg_on_focus= vals[ 5]=='1'
#           
#           cfg_path    = os.path.join(app.app_path(app.APP_DIR_SETTINGS), cfg_file)
#           if False:pass
#           elif ans_s == 'ok':
#               #Checks
#               if (cfg_on_start or cfg_on_focus) and not os.path.isfile(cfg_path):
#                   app.msg_box(_('Choose existed file'), app.MB_OK)
#                   focused = 1
#                   continue #while
#               break #while
#           
#           elif ans_s=='apply':
#               if not os.path.isfile(cfg_path):
#                   app.msg_box(_('Choose existed file'), app.MB_OK)
#                   focused = 1
#                   continue #while
#               config_menus(cfg_path)
#           
#           elif ans_s=='browse':
#               cfg_file_new= app.dlg_file(True, cfg_file, app.app_path(app.APP_DIR_SETTINGS), 'Config|*.json')
#               if cfg_file_new is None:
#                   continue
#               cfg_file    = cfg_file_new
#               if os.path.dirname(cfg_file)==app.app_path(app.APP_DIR_SETTINGS):
#                   cfg_file= os.path.basename(cfg_file)
#          #while true
#
#       if cfg_file     != apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE):
#           apx.set_opt('config_menus_from',     cfg_file)
#       if cfg_on_start != apx.get_opt('config_menus_on_start', True):
#           apx.set_opt('config_menus_on_start', cfg_on_start)
#       if cfg_on_focus != apx.get_opt('config_menus_on_focus', False):
#           apx.set_opt('config_menus_on_focus', cfg_on_focus)
#      #def config_menus_settings
#
#   def config_menus_settings_old(self):
#       cfg_file    = apx.get_opt('config_menus_from', DEF_MENU_CFG_FILE)
#       cfg_on_start= apx.get_opt('config_menus_on_start', True)
#       cfg_on_focus= apx.get_opt('config_menus_on_focus', False)
#       anses       = app.dlg_input_ex(3, "Settings for 'Config menu'"
#                       , _('&Config file (default folder is "settings")'), cfg_file
#                       , _('On &start'), 'Y' if cfg_on_start else 'N'
#                       , _('On &focus'), 'Y' if cfg_on_focus else 'N'
#                       )
#       if anses is None:
#           return
#       if anses[0]!=cfg_file:
#           apx.set_opt('config_menus_from', anses[0])
#       if ('Y'==anses[1])!=cfg_on_start:
#           apx.set_opt('config_menus_on_start', ('Y'==anses[1]))
#       if ('Y'==anses[2])!=cfg_on_focus:
#           apx.set_opt('config_menus_on_focus', ('Y'==anses[2]))
#      #def config_menus_settings

    def translate(msg):
        return _(msg)
        foo = _(r'Config &menu...')
   #class Command

'''
ToDo
[ ][kv-kv][20nov15] Bind/unbind events
[ ][kv-kv][04apr16] Need Help for plugins with autofilled submenu
'''
