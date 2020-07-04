# GridSpace to OctoPrint Print Plugin

Allows for direct printing from GridSpace's Kiri:Moto slicer. Also adds an embedded frame tab for running Kiri:Moto inside the OctoPrint web interface.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html)

or manually using this URL:

    https://github.com/GridSpace/OctoPrint-GridSpace/archive/master.zip

## Kiri:Moto

In order to spool from [Kiri:Moto](https://grid.space/kiri/) to your OctoPrint instance, you will need to enable Grid:Local under "Setup &gt; Preferences"

![Setup](https://static.grid.space/img/Kiri-Setup.png)

![Preferences](https://static.grid.space/img/Kiri-Preferences.png)

When the module is active, a new tab will become available that iframes Kiri:Moto

![IFrame](https://static.grid.space/img/Kiri-In-OctoPrint.png)

The export dialog in Kiri:Moto will now also show any local OctoPrint instances on your network and allow you to spool files directly to them.
