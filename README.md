# HOTchop
## Version 1.0

HOTchop is a tool for extracting BSP HOT files based on either
the TDNR (Ticket Document Number) or the TRNN (Transaction Number).
With the extracted transactions, HOTchop recalculates all total records (BOT93, BOT94, BCT95 and BFT99) 
based on rules defined in the IATA DISH (Data Interchange Specifications Handbook),
so that the output file can be used directly by revenue accounting systems conforming to the IATA DISH.
(Reference: IATA DISH Rev.22 PDF available on IATA website)

## ✅ Key features
- Recalculates all total records based on rules defined in the IATA DISH.
- A Graphical user interface (GUI) is available for setting the argument (input file, output file and chop criteria)
- As another option, the command-line interface (CLI) can be used to provide the same functionality as the GUI.
- Automatic identification of line break code(LF / CRLF) from the initial 1000 characters of the HOT file.
- HOT file is compatible with IATA dish 22.0 or later
- In order to avoid any potential conflict with the original file, both TIME and FSQN in BFH01 are set at random.

## 📄 License

This software is licensed under the [MIT License](LICENSE) for personal and non-commercial use.

For commercial use, redistribution, or integration into proprietary products,  
please contact the author to obtain a commercial license:
📧 takesobt@yahoo.com

This software is intentionally designed for niche use cases (e.g. airline HOT file processing).
If you're interested in adapting or using this tool in an enterprise context, please contact the author.

## 🔧 HOTchop requires the poetry to be developed and processed.

Install dependencies with Poetry:

```bash
poetry install
poetry run python -m hotchop.cli ...
```

### 💡 about tkinter

This GUI application uses the Python standard library `tkinter`.
Installation is usually not required on Windows/macOS, but if you want to use it on Linux or Docker, the following is required:

[Ubuntu]
sudo apt install python3-tk


## 🚀 How to use GUI
Run the following command to launch the graphical interface:

```bash
poetry run python gui.py --log
```
| Argument          | Required | Description                                  |
|-------------------|----------|----------------------------------------------|
| --log             | ❌       | Output logs to hotchop.log and stdout        |

![GUI with TDNR criteria](GUI_TDNR.png)

1. The input file selection dialogue is displayed.
2. The output file selection dialogue is displayed.
3. The criteria input box contains the default TDNR characters.
   Following processing, the results will be displayed for each criterion as outlined below.
   - 9992423207406 OK → This TDNR exists in the input HOT file and has been successfully extracted.
   - 9992423239061 __ → This TDNR does not exist in the input HOT file.
4. Start processing HOT chopper
5. Exit button

![GUI with TRNN criteria](GUI_TRNN.png)

- The criteria input box contains the default TRNN characters.
  Following processing, the results will be displayed for each criterion as outlined below.
  - 000101 OK → This TRNN exists in the input HOT file and has been successfully extracted.
  - 000203 __ → This TRNN does not exist in the input HOT file.

## 🚀 How to use CLI

### There are 6 arArguments
```bash
poetry run python -m hotchop.cli input_path output_path chop_criteria --criteria_type TDNR --overwrite --log
```
| Argument          | Required | Description                                  |
|-------------------|----------|----------------------------------------------|
| input_path        | ✅       | Path to the HOT file                         |
| output_path       | ✅       | Path to save the chopped HOT file            |
| chop_criteria     | ✅       | Comma-separated list of TDNR or TRNN values  |
| --criteria_type   | ❌       | Type of criteria: TDNR (default) or TRNN     |
| --overwrite       | ❌       | Overwrite output file if it already exists   |
| --log             | ❌       | Output logs to hotchop.log and stdout        |

Following processing, the results will be displayed both in terminal and logfile for each criterion as outlined below.
- criteria_type TDNR
  - 9992423207406 OK → This TDNR exists in the input HOT file and has been successfully extracted.
  - 9992423239061 __ → This TDNR does not exist in the input HOT file.
- criteria_type TRNN
  - 000101 OK → This TRNN exists in the input HOT file and has been successfully extracted.
  - 000203 __ → This TRNN does not exist in the input HOT file.

### HOT chop by the TDNR criteria(Please note that TDNR is the default criteria type and can be abbreviated.)
```bash
poetry run python -m hotchop.cli testdata/Input.txt testdata/output.txt 9992423207406,9992423239061 --criteria_type TDNR --overwrite --log
poetry run python -m hotchop.cli testdata/Input.txt testdata/output.txt 9992423207406,9992423239061 --overwrite --log
```
### HOT chop by the TRNN criteria
```bash
poetry run python -m hotchop.cli testdata/Input.txt testdata/output.txt 1,2,3 --criteria_type TRNN --overwrite --log
```
### If you want to overwrite an existing .txt file
・By default, if there is a .txt file with the same name in the output destination, processing is aborted.
・If --overwrite is specified, existing files are forcibly overwritten.
```bash
poetry run python -m hotchop.cli testdata/Input.txt testdata/output.txt 1,2,3 --criteria_type TRNN --overwrite
```
### To output a log file
・--log will output INFO / ERROR log to hotchop.log file
```bash
poetry run python -m hotchop.cli testdata/Input.txt testdata/output.txt 1,2,3 --criteria_type TRNN --overwrite --log
```