import sys
import copy
import math
import os.path
from yaml2gcode.__version__ import __version__
from yaml import load, SafeLoader


def help():
    print('yaml2gcode file.yml [out.nc]')

def G00(x=None, y=None, z=None, cr=True, prefix='', suffix=''):
    # cmd += '; {} {} {}\nG00'.format(x, y, z)
    cmd = prefix + 'G00'
    if x:
        cmd += ' X{:.4f}'.format(x)
    if y:
        cmd += ' Y{:.4f}'.format(y)
    if z:
        cmd += ' Z{:.4f}'.format(z)
    cmd += suffix
    if cr:
        cmd += '\n'
    return cmd

def parseMacro(name, MACROS, prefix=''):
    if not name:
        return ''
    macroDef = MACROS[name]
    macroName = name
    if 'label' in macroDef:
        macroName = macroDef['label']
    gcode = '\n' + prefix + '; Macro: ' + macroName + '\n '
    if 'description' in macroDef:
        gcode += prefix + '; - ' + macroDef['description'] + '\n'
    for command in macroDef['commands']:
        if isinstance(command, str):
            if command[0] in ['G', 'M']:
                gcode += prefix +  command + '\n'
            else:
                gcode += prefix +  '; ToDO command??: ' + command + '\n'      
        else:
            gcode += parseInstructions(command, MACROS, prefix)
    return gcode

def polarArcVector(instructions, prefix=''):
    parts = splitLine(instructions)
    D = '2'
    R = 0.0
    S = 0.0
    E = 0.0
    for part in parts:
        match part[0]:
            case 'R':
                R = float(part[1:])
                if R < 0.0:
                    D = '3'
                    R = abs(R)
            case 'S':
                S = float(part[1:]) * math.pi / 180.0
            case 'E':
                E = float(part[1:]) * math.pi / 180.0
    if E < S:
        D = '3'
        R = abs(R)
    X1 = R * math.sin(S)
    Y1 = R * math.cos(S)
    X2 = R * math.sin(E)
    Y2 = R * math.cos(E)
    return prefix + 'G0{} X{:.4f} Y{:.4f} R{:.4f} ; polarArcVector\n'.format(D, X2-X1, Y2-Y1, R)

def polarVector(instructions, prefix=''):
    parts = splitLine(instructions)
    D = 1.0
    R = 0.0
    A = 0.0
    S = None
    for part in parts:
        match part[0]:
            case 'R':
                R = float(part[1:])
                if R < 0.0:
                    D = -1.0
                    R = -R
            case 'A':
                A = float(part[1:]) * math.pi / 180.0
            case 'S':
                S = float(part[1:]) * math.pi / 180.0
    X = R * math.sin(A)
    Y = R * math.cos(A)
    if S is not None:
        X -= R * math.sin(S)
        Y -= R * math.cos(S)
    return prefix + 'G00 X{:.4f} Y{:.4f} ; polarVector\n'.format(D * X, D * Y)

def splitLine(line):
    parts = line.split(' ')
    parts = [x for x in parts if x]
    return parts

def boxInstruction(instructions, prefix=''):
    parts = splitLine(instructions)
    print('BOX: ', parts)
    gcode = ''
    W = 0.0 # Width
    H = 0.0 # Height
    D = 0.0 # Depth
    s = 0.1 # Step
    d = 1   # Z step
    o = 0.0 # Z offstet from material

    for part in parts:
        match part[0]:
            case 'W':
                W = float(part[1:])
            case 'H':
                H = float(part[1:])
            case 'D':
                D = float(part[1:])
            case 's':
                s = float(part[1:])
            case 'd':
                d = float(part[1:])
            case 'o':
                o = float(part[1:])

    if o > 0:
        gcode += 'G01 Z{:.4f}'.format(o)
    gcode += 'G01 X{:.4f} Y{:.4f}'.format(-W/2, -H/2)
    Z = 0.0
    sig = 1.0
    dir = 1.0
    while Z < D:
        X = 0.0
        gcode += prefix + 'G01 Z{:.4f}\n'.format(-d)
        Z += d
        while X < W:
            gcode += prefix + 'G01 Y{:.4f}\n'.format(sig * H)
            sig *= -1.0
            X += s
            if X < W:
                gcode += prefix + 'G01 X{:.4f}\n'.format(dir * s)
        dir *= -1.0
    gcode += 'G00 X{:.4f} Y{:.4f} Z{:.4f}'.format(W/2, H/2, D)
    return gcode

def macroPath(instructions, MACROS, prefix=''):
    gcode = ''
    macro = ''
    oldX = 0.0
    oldY = 0.0
    prefixOut = prefix
    for line in instructions:
        parts = splitLine(line)
        if len(parts) < 2:
            gcode += prefix + '; ERROR: ' + line + '\n'
            continue
        X = float(parts[0]) - oldX
        Y = float(parts[1]) - oldY
        oldX = float(parts[0])
        oldY = float(parts[1])
        gcode += G00(X, Y, None, False, '', '')
        if len(parts) == 3:
            if parts[2] in MACROS:
                macro = parts[2]
                prefixOut += ' '
            else:
                gcode += prefix + '; ERROR: no macro named `' + parts[2] + '` found !!!\n'
        else:
            gcode += '\n'
        gcode += parseMacro(macro, MACROS, prefix)
    gcode += G00(-oldX, -oldY, None, True, '', '')
    return gcode

def repeatMacro(instructions, MACROS, prefix=''):
    gcode = ''
    # oldX = 0.0
    # oldY = 0.0
    # prefixOut = prefix
    parts = splitLine(instructions)
    macro = parts[0]
    count = int(parts[1])
    instruction = ' '.join(parts[2:])
    while count > 0:
        gcode += instruction + '\n'
        gcode += parseMacro(macro, MACROS, prefix)
        count = count - 1
    # gcode += G00(-oldX, -oldY, None, True, '', '')
    return gcode

def parseInstructions(command, MACROS, prefix=''):
    gcode = ''
    for instruction in command:
        match instruction:
            case 'box':
                gcode += boxInstruction(command[instruction], prefix + ' ')
            case 'macro':
                gcode += parseMacro(command[instruction], MACROS, prefix + ' ')
            case 'macroPath':
                gcode += macroPath(command[instruction], MACROS, prefix + ' ')
            case 'polarArcVector':
                gcode += polarArcVector(command[instruction], prefix + ' ')
            case 'polarVector':
                gcode += polarVector(command[instruction], prefix + ' ')
            case 'repeatMacro':
                gcode += repeatMacro(command[instruction], MACROS, prefix + ' ')
            case _:
                gcode += prefix + '; ToDO instruction: ' + instruction + '\n'
    return gcode

def parseCommands(commands, MACROS):
    gcode = ''
    for command in commands:
        gcode += parseInstructions(command, MACROS)
    return gcode

def main():
    DEBUG = True
    MACROS = {}
    yaml_file = ''
    out_file = 'out.nc'
    base_folder = ''
    gcode = ''

    if len(sys.argv) < 2:
        raise BaseException(1, 'Missing command line argument(s)!!!')

    yaml_file = sys.argv[1]
    if len(sys.argv) >= 3:
        out_file = sys.argv[2]

    if base_folder is not None:
        yaml_file = '{}{}'.format(base_folder, yaml_file)

    if not os.path.exists(yaml_file):
        raise BaseException(1, 'File \'{}\' does not exist!!!'.format(yaml_file))

    with open(yaml_file, 'r') as f:
        yaml_data = load(f, Loader=SafeLoader)

        if 'commands' not in yaml_data:
            raise BaseException(2, 'No commands found in yaml file!!!')

        if 'init' in yaml_data:
            for line in yaml_data['init']:
                gcode += line + "\n"
        
        if 'setup' in yaml_data:
            for line in yaml_data['setup']:
                gcode += line + "\n"

        if 'macros' in yaml_data:
            MACROS = yaml_data['macros']
            for macroName in MACROS:
                macro = MACROS[macroName]
                if 'aliasOf' in macro:
                    macro['commands'] = copy.deepcopy(MACROS[macro['aliasOf']['macro']]['commands'])
                    if 'rotate' in macro['aliasOf']:
                        rotation = float(macro['aliasOf']['rotate']) * math.pi / 180.0
                        for command in macro['commands']:
                            for instruction in command:
                                match instruction:
                                    case 'macroPath':
                                        coords = []
                                        for line in command[instruction]:
                                            parts = splitLine(line)
                                            print(parts)
                                            s = math.sin(rotation)
                                            c = math.cos(rotation)
                                            x = float(parts[0])
                                            y = float(parts[1])
                                            newX = x*c + y*s
                                            newY = - x*s + y*c
                                            parts[0] = '{:.4f}'.format(newX)
                                            parts[1] = '{:.4f}'.format(newY)
                                            coords.append(' '.join(parts))
                                        print(coords)
                                        command[instruction] = coords
                                        print('DEBUG: ', MACROS)
                                    case _:
                                        print('UNSUPORTED instruction: ', instruction)
                            
            print('macros loaded!!!')        
            if DEBUG:
                print('MACROS: ', MACROS)
    
        gcode += parseCommands(yaml_data['commands'], MACROS)

        if 'finish' in yaml_data:
            for line in yaml_data['finish']:
                gcode += line + "\n"
        else:
            gcode += "M30 G00 Z10 M5"

        f = open(out_file, "w")
        f.write(gcode)
        f.close()

if __name__ == '__main__':
    main()
