#!/usr/bin/env python
__license__   = 'GPL v3'
__copyright__ = '2025, Comfy.n'

from qt.core import QCheckBox, QLabel, QVBoxLayout, QWidget

from calibre.utils.config import JSONConfig, config_dir
import os
try:
    load_translations()
except NameError:
    pass


KEY_SHOW_CREATION_NOTIFICATION = 'show_creation_notification'
KEY_SWITCH_TO_NEW_VL = 'switch_to_new_vl'


# Remove legacy JSON config from config_dir root before instantiating JSONConfig
try:
    new_plugin_dir = os.path.join(config_dir, 'plugins', 'VL_from_selection')
    legacy_paths = [
        os.path.join(config_dir, 'plugins.VL_from_selection'),
        os.path.join(config_dir, 'plugins.VL_from_selection.json'),
    ]
    for legacy_path in legacy_paths:
        try:
            legacy_path = os.path.normpath(legacy_path)
            if os.path.isfile(legacy_path):
                os.remove(legacy_path)
        except Exception:
            pass
except Exception:
    pass

# Stored under calibre config_dir/plugins/VL_from_selection/
plugin_prefs = JSONConfig('plugins/VL_from_selection')
plugin_prefs.defaults[KEY_SHOW_CREATION_NOTIFICATION] = True
plugin_prefs.defaults[KEY_SWITCH_TO_NEW_VL] = True


class ConfigWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Input_Order_Swap approach: only set minimum height, let Calibre handle width
        self.setMinimumHeight(270)
        self.l = QVBoxLayout(self)
        self.l.addWidget(QLabel(_('Options:')))
        self.show_creation = QCheckBox(_('Show creation notification after creating a Virtual Library'), self)
        self.show_creation.setChecked(bool(plugin_prefs.get(KEY_SHOW_CREATION_NOTIFICATION, True)))
        self.l.addWidget(self.show_creation)

        self.switch_to_new_vl = QCheckBox(_('Switch to the new Virtual Library after creation'), self)
        self.switch_to_new_vl.setChecked(bool(plugin_prefs.get(KEY_SWITCH_TO_NEW_VL, True)))
        self.l.addWidget(self.switch_to_new_vl)

        self.l.addStretch(1)

    def save_settings(self):
        plugin_prefs[KEY_SHOW_CREATION_NOTIFICATION] = bool(self.show_creation.isChecked())
        plugin_prefs[KEY_SWITCH_TO_NEW_VL] = bool(self.switch_to_new_vl.isChecked())


# Safely remove any legacy prefs file left at the calibre config root by older
# code that used 'plugins.VL_from_selection' as the JSONConfig name. Only
# remove the legacy file if the new plugin config folder exists to avoid
# accidentally deleting unrelated files.
try:
    new_plugin_dir = os.path.join(config_dir, 'plugins', 'VL_from_selection')
    if os.path.isdir(new_plugin_dir):
        legacy_candidates = [
            os.path.join(config_dir, 'plugins.VL_from_selection'),
            os.path.join(config_dir, 'plugins.VL_from_selection.json'),
        ]
        for legacy_path in legacy_candidates:
            try:
                legacy_path = os.path.normpath(legacy_path)
                if os.path.isfile(legacy_path):
                    try:
                        os.remove(legacy_path)
                    except Exception:
                        # If removal fails, don't raise — leave the file and continue
                        pass
            except Exception:
                pass
except Exception:
    pass
