**VL from selection**

Create a Virtual Library from the currently selected books in Calibre.

Features

    Create a Virtual Library from selected book IDs with one action
    Optionally apply comma-separated tags to the selected books when creating the VL


Tips

On installation, choose "the context menu for the books in the library"

Installation

[Install from Calibre]

1. Open Calibre Preferences -> Plug-ins -> Get new plugins.
2. Select "VL from selection" from the plugin list and click [Install].
3. Restart Calibre.

[Load from file]

1. Download the plugin zip.
2. In Calibre, go to Preferences → Plugins → Load Plugin from File.
3. Select the downloaded zip file.
4. Restart Calibre.

Usage
Select one or more books in your library, then trigger the "VL from selection" action (toolbar/menu/keyboard shortcut*). Provide a name for the Virtual Library and optional tags, then confirm to create the VL.

Compatibility

    Calibre 6.25 or later
    Windows, macOS, Linux


Release notes
Spoiler:

version 1.0.3
Minor adjustment - set config JSON alongside plugin zip

version 1.0.2

    New config options — Added preferences to:
        Show creation notification after creating a Virtual Library (can be disabled)
        Switch to the new Virtual Library after creation (optional)
    Don't show this again — The creation confirmation dialog includes a "Don't show this again" checkbox; the choice is persisted in plugin prefs and also available in Preferences → Plugins → VL from selection.
    Shortcuts — Two unassigned actions are now registered in Calibre's Keyboard Shortcuts so you can assign keys to toggle:
        Toggle creation notification
        Toggle "switch to new VL"
    Translations — Updated Spanish translation to include the new strings.


Notes:

    Open Preferences → Plugins → VL from selection to change the new options.
    Assign shortcuts in Preferences → Keyboard Shortcuts (search "VL from selection") to toggle the options quickly; each toggle shows a brief confirmation popup.


version 1.0.1
- Icon implemented
- Spanish translation - thanks to @dunhill


License

This plugin is licensed under the GNU GPL v3. 
