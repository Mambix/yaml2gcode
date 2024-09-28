# yaml2gcode
[![Coverage Status](https://coveralls.io/repos/github/Mambix/yaml2gcode/badge.svg?branch=master)](https://coveralls.io/github/Mambix/yaml2gcode?branch=master)
[![PyPI](https://img.shields.io/pypi/v/yaml2gcode.svg)](https://pypi.python.org/pypi/yaml2gcode)
Easily generate GCODE from yaml definitions

# installation
This is WORK IN PROGRESS, including documentation so bare with me here :)
```
pip3 install yaml2gcode
```

# usage
In order to run this tool create a `yaml` file in your project folder.
This file will contain instructions which yaml2gcode tool will execute.
Then you can run the tool in your folder and it will use `yml` file to execute instructions:
```
yaml2gcode inputfile.yml [out.nc]
```
If out file is not provided it will save generated GCODE in `ouy.nc` file.

# yml file structure
```yaml
units: mm|inch
description: short description of the file
material: short description of the material the GCODE is inteded for
notes:
  - array of notes that do not get copied into GCODE
  - Like where should 0,0,0 postion be set up to start executing code
  - What router needs to be used for this code (6mm roundball for example)
parameters: this JSON section contains parameters used for automatic calculations
dimensions:
  width: windth of the product
  height: height of the product
init:
  - this array contains GCODE that is added to the start of the program
  - like for example coordinate system, feed rate...
finish:
  - this array holds code that is executed at the end of the program
  - like end program, return to origin ...
macros:
  - this section contains chunks of code that are often repeated
  - is explained in more details in the following section
commands:
  - this section holds commands to be executed in order to make the final product
  - detailed explanation also in the following section
```

## Commands
There are few commands that will help you with putting a program together.
Each array element represents a command that needs to be executed or a macro.
There are some built in commands that you can use so you do not need to write 
yourown macros for same functionalitty.

### GCODE
GCODE is directly copied into end program. For example:
```yaml
commands:
  - G00 X0.5
```

### macro
This will simply execute a macro
```yaml
commands:
  - macro: hole-M5
```

### macroPath
This command will execute a macro in specified locations. Think of it as a tool path where coordinates tell the machine where to move and what macro to execute at that location. Usefull when
you for example need to make multiple holes at specific locations. If no macro is specified in the line then the last macro set is used, If provided then new macro is used until it is swapped again.
It will be more clear with an example:
```yaml
- macroPath:
  - -12 0 hole-M4
  - 0 12
  - 12 0 hole-M5
  - 0 -12
```
In this example the machine will move -12 units in X direction and then execute `hole-M4` macro.
After that it will move 12 units in Y direction and execute `hole-M4` macro again. Then it will move 12 units in X direction executing macro `hole-M5`, moving again -12 units in Y direction and finshing with executing `hole-M5` macro again.

### repeatMacro
This one is useful for when you need to repeat same steps in Z direction. For example you 
need to make several passes to cut through the material. In the code below `hole-M5-perimeter` macro will be executed `3 times` running command `G01 Z-2.05` before each execution. So in this case
we cut through 6mm of material in 3 passes ending 6.15mm deep.
```yaml
commands:
  - repeatMacro: hole-M5-perimeter 3 G01 Z-2.05
```

### polarVector
`polarVector` has two parameters, `radius` and `angle`. This one is usefull when you need to move to a certain location that is easier defined in polar coordinates rather then calculating X and Y manually. Note is that this move is relative, not absolute!.
```yaml
commands:
  - polarVector: R16.5 A20
```
The code will move the tool away from current location by `16.5` units at a `20` degree angle. 

### polarArcVector
`polarArcVector` has three parameters, `radius`, `startAngle` and `endAngle`. This one is usefull when you need to move to a certain location on and arc and it is easier defined in polar coordinates rather then calculating start and end points manually. Note that this move is relative, not absolute and in straight line!.
```yaml
commands:
  - polarArcVector: R16.5 S20 E70
```

## Macros
This is a simple example of M5 sized holes that need to be drilled multiple times
so that M5 bolts can be mounted.
```yaml
macros:
  hole-M5-perimeter:
    commands:
      - G02 X-1 R0.5
      - G02 X1 R0.5
  hole-M5:
    label: hole-M5
    notes: screw hole
    commands:
      - G00 X0.5
      - G01 Z-1
      - repeatMacro: hole-M5-perimeter 3 G01 Z-2.05
      - G00 Z7.15
      - G00 X-0.5
```
This example actually contains two macros named `hole-M5` and `hole-M5-perimeter`.
`hole-M5` is the one that is called from the main program. `hole-M5-perimeter` is just a subroutine 
that needs to be repeated multiple times inside `hole-M5` macro.

## Examples
```yaml

```


# ToDO:
This is a list of things that are planned to be implemented in future versions.
If you have a suggestion you can open a ticket to be discussed and added to the list.
- [ ] Documentation
- [ ] Examples
- [ ] Implement variables
- [ ] Automated tests
- [ ] GCODE optimisation
- [ ] Pass GCODE paramenters as command line parameters

# Sponsors
If you like the project and/or find it usefull please consider sponsoring it.
Issues/Suggestions from sponsors will be prioritised.
