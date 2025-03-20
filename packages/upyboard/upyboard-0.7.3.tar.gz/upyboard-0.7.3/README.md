This tool is supports microcontrollers to which MicroPython is ported.

### Help
```sh
upy
```
or
```sh
upy --help
```

### Finding the serial port on a board with MicroPython
- Explore a serially connected MicroPython device.
- The MicroPython version and device type are printed.
- Currently supported devices are Digi XBee3(xbee3) and Raspberry Pi Pico 2 W(pico2).

```sh
upy scan
```

```output
COM3 (v1.12-1556-gcc82fa9 on 2021-06-22; XBee3 Zigbee with EFR32MG)
COM4 (v1.25.0-preview.180.g495ce91ca on 2025-01-06; Raspberry Pi Pico 2 W with RP2350)
```

### Option Rules
- Options and values can have spaces or omit spaces.
- Options and values can be inserted with the = character.

```sh
<option><value>  
<option> <value>
<option>=<value> 
```

### Environment file
- You can omit this option by saving the environment variables required to run the tool in the current path in a .vscode/.upy file.
- By defining SERIAL_PORT and DEVICE_TYPE in this file, you can omit the --sport and --type options to be included in each command.

```sh
SERIAL_PORT=<your_com_port_name>
DEVICE_TYPE=<your_device_type>
```

Example (.upy)
```sh
SERIAL_PORT=com3
DEVICE_TYPE=xbee3
```

### Initialize Microcontroller file system
- If you created a .vscode/.upy file in the current path, omit the --sport and --type options in all subsequent commands.
```sh
upy init
```
or, You can also use the --sport and --type options explicitly.
```sh
upy --sport <your_com_port_name> --type <your_device_type> init
```

### Check list of Microcontroller file systems
- If path is omitted, the output will be the files or directories contained in the top-level directory.

```sh
upy ls [<path>/][remote_directory]
```

### Put PC file or directroy into Microcontroller
- If path or remote name is omitted, a remote name identical to the local name is created in the top-level directory.
```sh
upy put <local_name> [[path][/remote_name]]
```

### Get Microcontroller file to PC
- Getting the current directory is not supported.
```sh
upy get <remote_file_name> <local_file_name>
```

### Delete Microcontroller file or directory
```sh
upy rm [path/]<remote_name>
```

### Executes the PC's MicroPython script by sequentially passing it to the Microcontroller
- Wait for serial input/output until the script finishes  
- To force quit in running state, press Ctrl+c

```sh
upy <micropython_script_file>
```
or
```sh
upy run [-i | -n] <micropython_script_file>
```

**Additional Options**
- -i: Display the pressed key in the terminal window (Echo on)
- -n: Does not wait for serial output, so it appears as if the program has terminated on the PC side.
  - Script continues to run on Microcontroller
  - Used to check data output serially from Microcontroller with other tools (PuTTY, etc.)
