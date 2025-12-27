#!/usr/bin/env python
__license__   = 'GPL v3'
__copyright__ = '2025, Comfy.n'
__docformat__ = 'restructuredtext en'


try:
    load_translations()
except NameError:
    pass

from calibre.customize import InterfaceActionBase

class VLFromSelectionPlugin(InterfaceActionBase):
    name = 'VL from selection'
    description = _('Create a Virtual Library from selected book IDs quickly, optionally applying tags to the selected books')
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Comfy.n'
    version = (1, 0, 3)
    minimum_calibre_version = (6, 25, 0)

    actual_plugin = 'calibre_plugins.VL_from_selection.action:VLFromSelectionAction'

    def is_customizable(self):
        return True

    def config_widget(self):
        from .config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        # Update the live toolbar icon immediately if the action is loaded.
        if getattr(self, 'actual_plugin_', None):
            try:
                self.actual_plugin_.rebuild_icon()
            except Exception:
                pass

