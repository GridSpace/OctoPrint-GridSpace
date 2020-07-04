# GridSpace to OctoPrint Spooler

Allows for direct printing from GridSpace's Kiri:Moto slicer. Also adds an embedded frame tab for running Kiri:Moto inside the OctoPrint web interface.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)

or manually using this URL:

`https://github.com/GridSpace/OctoPrint-GridSpace/archive/master.zip`

## Kiri:Moto

In order to spool from [Kiri:Moto](https://grid.space/kiri/) to your OctoPrint instance, you will need to enable Grid:Local under "Setup &gt; Preferences"

![Setup](https://static.grid.space/img/Kiri-Setup.png)

This module allows more direct and effortless spooling than the traditional OctoPrint export option (unchecked here) which requires you to install certificates on your OctoPrint server and enable or override obscure http security restrictions.

![Preferences](https://static.grid.space/img/Kiri-Preferences.png)

When the module is active, a new tab will become available that creates an IFrame for Kiri:Moto

![IFrame](https://static.grid.space/img/Kiri-In-OctoPrint.png)

The export dialog in [Kiri:Moto](https://grid.space/kiri/) will now also show any local OctoPrint instances on your network and allow you to send files directly to them.
