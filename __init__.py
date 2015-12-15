''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on githab)
Version:
    '0.9.2 2015-12-15'
'''

from .cd_config_menu import Command as CommandRLS

RLS  = CommandRLS()
class Command:
    def on_start(self, ed_self):    return RLS.on_start(ed_self)
    def config_menus(self):         return RLS.config_menus()
    def config_menus_open(self):    return RLS.config_menus_open()
    def config_menus_help(self):    return RLS.config_menus_help()
    def config_menus_settings(self):return RLS.config_menus_settings()
   #class Command
