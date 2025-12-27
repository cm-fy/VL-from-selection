from __future__ import annotations

from datetime import datetime

try:
    from qt.core import QInputDialog, QMessageBox, QCheckBox
except Exception:
    from PyQt5.Qt import QInputDialog, QMessageBox, QCheckBox

try:
    load_translations()
except NameError:
    pass


from qt.core import QMenu, QAction

from calibre.gui2.actions import InterfaceAction
from calibre.gui2 import Application
from . import common_icons
from .config import plugin_prefs, KEY_SHOW_CREATION_NOTIFICATION
from .config import KEY_SWITCH_TO_NEW_VL


class VLFromSelectionAction(InterfaceAction):

    action_spec = (
        _('VL from selection'),
        None,
        _('Create a Virtual Library from selected book IDs'),
        None,
    )

    def genesis(self):
        # Connect the action; toolbar/menu placement is handled by Calibre preferences.
        self.qaction.triggered.connect(self.create_virtual_library_from_selection)

        # Set up the icon resources and theme-aware icon
        common_icons.set_plugin_icon_resources(self.name, {})
        self.rebuild_icon()

        # Listen for theme changes to update the icon instantly
        app = Application.instance()
        if app:
            app.palette_changed.connect(self.rebuild_icon)

        # Register this action in Preferences -> Keyboard shortcuts (unassigned by default)
        try:
            self.gui.keyboard.register_shortcut(
                'plugin:vl_from_selection:create_vl',
                'VL from selection: create virtual library',
                description=_('Create a persistent Virtual Library from selected book IDs'),
                action=self.qaction,
                group='VL from selection',
                persist_shortcut=True,
            )

            # Create QActions for toggles
            self.toggle_show_notification_action = QAction(_('Toggle: Show creation notification after creating a Virtual Library'), self.gui)
            self.toggle_show_notification_action.triggered.connect(self.toggle_show_notification)
            self.toggle_switch_to_new_vl_action = QAction(_('Toggle: Switch to the new Virtual Library after creation'), self.gui)
            self.toggle_switch_to_new_vl_action.triggered.connect(self.toggle_switch_to_new_vl)

            # Add actions to the top-level GUI so shortcuts will trigger them reliably
            try:
                self.gui.addAction(self.toggle_show_notification_action)
                self.gui.addAction(self.toggle_switch_to_new_vl_action)
            except Exception:
                pass

            # Add toggle actions as children of the main action so Calibre lists them
            try:
                self.qaction.addAction(self.toggle_show_notification_action)
                self.qaction.addAction(self.toggle_switch_to_new_vl_action)
            except Exception:
                pass

            self.gui.keyboard.register_shortcut(
                'plugin:vl_from_selection:toggle_show_notification',
                'VL from selection: toggle show notification',
                description=_('Toggle: Show creation notification after creating a Virtual Library'),
                action=self.toggle_show_notification_action,
                group='VL from selection',
                persist_shortcut=True,
            )
            self.gui.keyboard.register_shortcut(
                'plugin:vl_from_selection:toggle_switch_to_new_vl',
                'VL from selection: toggle switch to new VL',
                description=_('Toggle: Switch to the new Virtual Library after creation'),
                action=self.toggle_switch_to_new_vl_action,
                group='VL from selection',
                persist_shortcut=True,
            )
        except Exception:
            pass
    def toggle_show_notification(self):
        current = bool(plugin_prefs.get(KEY_SHOW_CREATION_NOTIFICATION, True))
        plugin_prefs[KEY_SHOW_CREATION_NOTIFICATION] = not current
        state = _('ON') if plugin_prefs[KEY_SHOW_CREATION_NOTIFICATION] else _('OFF')
        QMessageBox.information(self.gui, _('VL from selection'),
            _('Show creation notification: {}').format(state))

    def toggle_switch_to_new_vl(self):
        current = bool(plugin_prefs.get(KEY_SWITCH_TO_NEW_VL, True))
        plugin_prefs[KEY_SWITCH_TO_NEW_VL] = not current
        state = _('ON') if plugin_prefs[KEY_SWITCH_TO_NEW_VL] else _('OFF')
        QMessageBox.information(self.gui, _('VL from selection'),
            _('Switch to new Virtual Library after creation: {}').format(state))

    # The customize_plugin method is no longer needed since the menu is removed.

    def rebuild_icon(self):
        icon = common_icons.get_icon('images/iconplugin.png')
        self.qaction.setIcon(icon)

    def create_virtual_library_from_selection(self):
        ids = []
        try:
            ids = list(self.gui.library_view.get_selected_ids(as_set=True) or [])
        except Exception:
            try:
                ids = list(self.gui.library_view.get_selected_ids() or [])
            except Exception:
                ids = []

        if not ids:
            QMessageBox.information(self.gui, _('VL from selection'), _('No books selected.'))
            return

        ids = sorted({int(x) for x in ids if x is not None})
        query = self._build_id_query(ids)

        db = getattr(self.gui, 'current_db', None)
        if db is None or getattr(db, 'new_api', None) is None:
            QMessageBox.warning(self.gui, _('VL from selection'), _('Could not access the current database.'))
            return

        default_name = self._default_vl_name()
        dlg = QInputDialog(self.gui)
        dlg.setWindowTitle(_('Create Virtual Library'))
        dlg.setLabelText(_('Virtual Library name:'))
        dlg.setTextValue(default_name)
        dlg.resize(400, 80)  # Make dialog wider
        ok = dlg.exec_()
        name = dlg.textValue() if ok else ''
        if not ok:
            return
        name = (name or '').strip() or default_name

        # Optional tags
        tags_to_apply = ''
        try:
            tags_to_apply, ok2 = QInputDialog.getText(
                self.gui,
                _('Optional tags'),
                _('Apply tag(s) to selected books? (comma-separated, blank for none):'),
                text='',
            )
            if not ok2:
                # treat cancel as "no tags"
                tags_to_apply = ''
        except Exception:
            tags_to_apply = ''

        try:
            from calibre.gui2.search_restriction_mixin import MAX_VIRTUAL_LIBRARY_NAME_LENGTH
            max_len = int(MAX_VIRTUAL_LIBRARY_NAME_LENGTH)
        except Exception:
            max_len = 40

        try:
            virt_libs = db.new_api.pref('virtual_libraries', {}) or {}
        except Exception:
            virt_libs = {}

        name = self._make_unique_name(name, virt_libs, max_len)
        virt_libs[name] = query

        try:
            db.new_api.set_pref('virtual_libraries', virt_libs)
        except Exception as e:
            QMessageBox.warning(self.gui, _('VL from selection'), _('Failed to save Virtual Library: {}').format(e))
            return

        if tags_to_apply:
            self._apply_tags_to_books(db, ids, tags_to_apply)

        # Switch to it if user preference is enabled
        try:
            if bool(plugin_prefs.get(KEY_SWITCH_TO_NEW_VL, True)):
                self.gui.apply_virtual_library(name)
        except Exception:
            pass

        # Show creation notification unless user disabled it in prefs
        try:
            show = bool(plugin_prefs.get(KEY_SHOW_CREATION_NOTIFICATION, True))
        except Exception:
            show = True

        if show:
            m = QMessageBox(self.gui)
            m.setIcon(QMessageBox.Information)
            m.setWindowTitle(_('VL from selection'))
            m.setText(_('Created Virtual Library "{name}" with {n} book(s).').format(name=name, n=len(ids)))
            cb = QCheckBox(_("Don't show this again"))
            try:
                m.setCheckBox(cb)
            except Exception:
                pass
            m.exec_()
            try:
                if cb.isChecked():
                    plugin_prefs[KEY_SHOW_CREATION_NOTIFICATION] = False
            except Exception:
                pass

    def _default_vl_name(self) -> str:
        ts = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        return _('Selection {ts}').format(ts=ts)

    def _make_unique_name(self, name: str, virt_libs: dict, max_len: int) -> str:
        base = name.strip() or _('Selection')
        # keep within max length
        base = base[:max_len]
        if base not in virt_libs:
            return base
        i = 2
        while True:
            suffix = f' ({i})'
            candidate = (base[: max_len - len(suffix)] + suffix) if max_len > len(suffix) else base[:max_len]
            if candidate not in virt_libs:
                return candidate
            i += 1

    def _build_id_query(self, ids: list[int]) -> str:
        # Only use id:X or id:Y (no id:X-Y), since Calibre doesn't support id ranges.
        if not ids:
            return 'id:false'
        return ' or '.join(f'id:{i}' for i in ids)

    def _apply_tags_to_books(self, db, book_ids: list[int], tags_s: str) -> None:
        tags = [t.strip() for t in (tags_s or '').split(',') if t.strip()]
        if not tags:
            return
        api = db.new_api
        updates = {}
        for book_id in book_ids:
            try:
                existing = list(api.field_for('tags', book_id) or [])
            except Exception:
                existing = []
            merged = list(existing)
            for t in tags:
                if t not in merged:
                    merged.append(t)
            updates[book_id] = merged
        if updates:
            try:
                api.set_field('tags', updates)
            except Exception:
                # fallback: write one by one
                for book_id, merged in updates.items():
                    try:
                        api.set_field('tags', {book_id: merged})
                    except Exception:
                        pass
            try:
                m = self.gui.library_view.model()
                m.refresh_ids(tuple(book_ids))
            except Exception:
                pass
