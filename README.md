# AS9100 STEP Exporter

A Fusion 360 add-in for exporting STEP files with AS9100 compliant naming conventions and advanced file naming options.

## Overview

This add-in provides a streamlined interface for exporting STEP files from Fusion 360 with professional naming conventions that comply with AS9100 quality management standards. It offers flexible naming options including project names, version handling, author information, date appending, and customizable delimiters.

## Features

- **AS9100 Compliant Naming**: Generate file names that meet aerospace quality standards
- **Project Name Integration**: Automatically include Fusion 360 project names in file names
- **Version Number Handling**: Choose to include or exclude Fusion version numbers
- **Author Information**: Add custom author/engineer names to file names
- **Date Appending**: Automatically append current date in YYYY-MM-DD format
- **Flexible Delimiters**: Choose between underscores, dashes, dots, or spaces
- **Real-time Preview**: See the generated file name before exporting

## Installation

1. Download or clone this repository
2. Copy the entire `AS9100_STEP_Exporter` folder to your Fusion 360 add-ins directory:
   - **Windows**: `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`
   - **macOS**: `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`
3. Start Fusion 360
4. Go to **Tools** > **Scripts and Add-Ins**
5. Select the **Add-Ins** tab
6. Find "AS9100_STEP_Exporter" in the list
7. Select it and click **Run**
8. Check "Run on Startup" if you want it to load automatically
9. The add-in icon will apear in the Utilities > Add-ins toolbar and can be assigned a key command (I typically use "cmd/ctrl-e")
