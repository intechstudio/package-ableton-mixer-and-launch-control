# Ableton Script Installer Package

This package allows you to install Ableton Remote Scripts from the `scripts` folder to your Ableton User Library Remote Scripts folder.

## Installation

1. Clone the repository
2. Run `npm i` in the root folder
3. Run `npm run build` to build the necessary files
4. In the Editor at the Package Manager panel, either Approve the package at the top of the list if possible or use the `+ Add external package` button to add the **root** path of the package

## Usage

1. Add your Ableton Remote Script folders to the `scripts` folder in the package root
2. Each subfolder in `scripts` will appear as an install button in the preferences panel
3. Click the corresponding button to install the script to your Ableton User Library Remote Scripts folder

The default installation path on Windows is:

```
C:\Users\[username]\Documents\Ableton\User Library\Remote Scripts
```

## Adding Script Variants

To add a new script variant:

1. Create a new folder inside the `scripts` folder with your desired name
2. Place your Ableton Remote Script files (Python files, `__init__.py`, etc.) inside that folder
3. Rebuild the package with `npm run build`
4. The new variant will appear as a button in the preferences panel

## Customization

- **Package ID**: Update the `name` field in `package.json` and the corresponding references in `components/src/Preferences.svelte` (at `createPackageMessagePort()` call and `customElement` tag)
- **Package info**: Update `package.json` > `grid_editor` for description and component settings
