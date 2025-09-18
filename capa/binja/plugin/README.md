![capa explorer](../../../.github/capa-explorer-logo.png)

# capa explorer for Binary Ninja

capa explorer is a Binary Ninja plugin that integrates the FLARE team's open-source framework, capa, with Binary Ninja. capa is a framework that uses a well-defined collection of rules to identify capabilities in a program. You can run capa against a PE file, ELF file, or shellcode and it tells you what it thinks the program can do. For example, it might suggest that the program is a backdoor, can install services, or relies on HTTP to communicate.

capa explorer runs capa analysis on your Binary Ninja database without needing access to the original binary file. Once a database has been analyzed, capa explorer helps you identify interesting areas of a program by showing you which rules matched and where.

## Features

- **Program Analysis**: Run capa analysis directly within Binary Ninja
- **Interactive Results**: Click on results to navigate to relevant addresses in the disassembly
- **Rule Matching**: See which capa rules matched and why
- **Background Processing**: Analysis runs in background thread without blocking Binary Ninja

## Getting Started

### Installation

You can install capa explorer using the following steps:

1. Install capa and its dependencies using pip:
    ```
    $ pip install flare-capa
    ```

2. Download and extract the [official capa rules](https://github.com/mandiant/capa-rules/releases) that match the version of capa you have installed
   - Use the following command to view the version of capa you have installed:
   ```commandline
   $ pip show flare-capa
   OR
   $ capa --version
   ```

3. Copy [capa_explorer.py](https://raw.githubusercontent.com/mandiant/capa/master/capa/binja/plugin/capa_explorer.py) to your Binary Ninja plugins directory
   - Find your plugin directory via Binary Ninja's preferences or typically located at:
     - Windows: `%APPDATA%\Binary Ninja\plugins`
     - macOS: `~/Library/Application Support/Binary Ninja/plugins`
     - Linux: `~/.binaryninja/plugins`

### Supported File Types

capa explorer is limited to the file types supported by capa, which include:

* Windows x86 (32- and 64-bit) PE files  
* Windows x86 (32- and 64-bit) shellcode
* ELF files on various operating systems

### Usage

1. Open Binary Ninja and load a supported file type
2. Open capa explorer by navigating to `Tools > FLARE capa explorer`
3. Select the `Program Analysis` tab  
4. Click the `Settings` button to specify your capa rules directory (first time only)
5. Click the `Analyze` button to run capa analysis

The first time you run capa explorer you will be asked to specify a local directory containing capa rules to use for analysis. We recommend downloading and extracting the [official capa rules](https://github.com/mandiant/capa-rules/releases) that match the version of capa you have installed.

#### Tips for Program Analysis

* Start analysis by clicking the `Analyze` button
* The plugin remembers your capa rules directory selection between sessions
* Reset the plugin by clicking the `Reset` button  
* Change your local capa rules directory by clicking the `Settings` button
* Double-click on a result to navigate to the associated address in Binary Ninja
* Analysis runs in a background thread so you can continue using Binary Ninja

### Requirements

capa explorer supports Binary Ninja with Python 3.10+ and has been tested with recent versions of Binary Ninja. The plugin requires:

* Binary Ninja (recent versions with Python plugin support)
* Python 3.10 or later
* PySide2 or PySide6 (usually included with Binary Ninja)
* flare-capa package

If you encounter issues with your specific setup, please open a new [Issue](https://github.com/mandiant/capa/issues).

## Development

capa explorer is packaged with capa so you will need to install capa locally for development. You can install capa locally by following the steps outlined in `Method 3: Inspecting the capa source code` of the [capa installation guide](https://github.com/mandiant/capa/blob/master/doc/installation.md#method-3-inspecting-the-capa-source-code). 

Once installed, copy [capa_explorer.py](https://raw.githubusercontent.com/mandiant/capa/master/capa/binja/plugin/capa_explorer.py) to your plugins directory to install capa explorer in Binary Ninja.

### Components

capa explorer consists of two main components:

* A [feature extractor](https://github.com/mandiant/capa/tree/master/capa/features/extractors/binja) built on top of Binary Ninja's analysis engine
  * This component uses Binary Ninja's Python API to extract [capa features](https://github.com/mandiant/capa-rules/blob/master/doc/format.md#extracted-features) from your binaries such as strings, disassembly, and control flow; these extracted features are used by capa to find feature combinations that result in a rule match
* An [interactive user interface](https://github.com/mandiant/capa/tree/master/capa/binja/plugin) for displaying and exploring capa rule matches  
  * This component integrates the feature extractor and capa, providing an interactive user interface to explore rule matches found by capa using features extracted directly from your Binary Ninja analysis

## Differences from IDA Plugin

This Binary Ninja plugin focuses on the core exploration functionality:

* **Program Analysis**: Full capa analysis with rule matching and result exploration
* **Navigation**: Click results to jump to relevant addresses  
* **Background Processing**: Non-blocking analysis

Currently **not implemented** (but may be added in future versions):
* Rule generation functionality
* Advanced rule editing capabilities
* Some advanced UI features from the IDA version

## Troubleshooting

**Plugin doesn't appear in Tools menu:**
- Verify Binary Ninja can import the `binaryninja` module in its Python environment
- Check that all dependencies (especially `flare-capa`) are installed in Binary Ninja's Python environment
- Look for error messages in Binary Ninja's log window

**Analysis fails:**
- Ensure you have a valid capa rules directory selected
- Verify the binary type is supported by capa
- Check Binary Ninja's log for detailed error messages

**UI issues:**
- Ensure your Binary Ninja version includes PySide2 or PySide6
- Try restarting Binary Ninja after installing the plugin