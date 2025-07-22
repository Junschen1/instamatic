import ast
import datetime
import logging
import subprocess
import threading
import time
from pathlib import Path
from socket import *
import os
import tkinter as tk
from instamatic import config

HOST = config.settings.VM_server_host
PORT = config.settings.VM_server_port
# ENABLE_SHELXT = config.settings.ENABLE_SHELXT
BUFF = 1024
path_xds = config.settings.Win_XDS_PATH
Con_flag = True

def yes_action(window):
    # 当用户点击Yes按钮时关闭窗口并继续运行程序
    window.destroy()

def no_action(window):
    window.destroy()
    global Con_flag
    Con_flag=False


def win_ubuntu_start_xds_AtFolder(conn, shelxt, unitcell, spgr, composition):

    # path = "/media/sf_SharedWithVM/test_vm_server"

    while True:

        try:
            data = conn.recv(BUFF).decode()
        except ConnectionResetError:
            print('cRED experiment ended and connection was forcely closed.')
            print('A new cRED experiment will build a new connection.')
            break

        now = datetime.datetime.now().strftime('%H:%M:%S.%f')

        if not data:
            break

        print(f'{now} | {data}')
        if data == 'close':
            print(f'{now} | closing connection')
            conn.send(b'Connection closed')
            conn.close()
            break
        elif data == 'kill':
            print(f'{now} | closing down VM')
            print('closed down safely!')
            conn.send(b'Connection closed')
            conn.close()
            break
        else:
            conn.send(b'OK')
            data = ast.literal_eval(data)
            path = data['path']
            first_char = path[0].lower()
            path_win = '\\mnt\\'+first_char+path[1:]
            path_win = path_win.replace('\\', '/')
            path_win = path_win.replace(':', '')
            os.environ['PATH'] = os.environ['PATH'] + ';' + path_xds
            if shelxt:
                try:
                    p = subprocess.Popen('bash', stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    p.stdin.write(f"cd {path_win}\n".encode())
                    p.stdin.write(b"xds\n")
                    p.communicate()
                    print('xds insert')
                    time.sleep(1)
                    generate_xdsconv_input(path)
                    if Con_flag:
                        p2 = subprocess.Popen('bash', stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        p2.stdin.write(f"cd {path_win}\n".encode())
                        p2.stdin.write(b"xdsconv\n")
                        p2.communicate()
                        time.sleep(1)
                        generate_shelxt_input(unitcell, spgr, composition, path)
                        print("generate_shelxt_input complete")
                        time.sleep(1)
                        solve_structure_shelxt(path)
                    else:
                        print("Interrupted, waiting for input")
            
                except Exception as e:
                    print(e)
                    print('Because of the error auto structure solution could not be performed.')

    print('Connection closed')




def generate_shelxt_input(unitcell, spgr, composition, path):
    from edtools.make_shelx import comp2dict, get_latt_symm_cards, get_sfac
    composition = comp2dict(composition)
    if unitcell is None:
        with open(Path(path) / 'CORRECT.LP') as f:
            for line in f:
                if line.startswith(' UNIT_CELL_CONSTANTS='):
                    cell = list(map(float, line.strip('\n').split()[1:7]))
                elif line.startswith(' UNIT CELL PARAMETERS'):
                    cell = list(map(float, line.strip('\n').split()[3:9]))
    else:
        cell = [float(ucl) for ucl in unitcell]
    if spgr is None:
        with open(Path(path) / 'CORRECT.LP') as f:
            for line in f:
                if line.startswith(' SPACE GROUP NUMBER'):
                    spgr = int(line.strip('\n').split()[-1])
                elif line.startswith(' SPACE_GROUP_NUMBER='):
                    spgr = int(line.strip('\n').split()[1])
    else:
        spgr = str(spgr)
    wavelength = config.microscope.wavelength
    a, b, c, al, be, ga = cell
    spgr = str(spgr)
    out = Path(path) / 'shelx.ins'

    f = open(out, 'w')

    print(f'TITL {spgr}', file=f)
    print(f'CELL {wavelength:.4f} {a:6.3f} {b:6.3f} {c:6.3f} {al:7.3f} {be:7.3f} {ga:7.3f}', file=f)
    print('ZERR 1.00    0.000  0.000  0.000   0.000   0.000   0.000', file=f)

    LATT, SYMM = get_latt_symm_cards(spgr)

    print(LATT, file=f)
    for line in SYMM:
        print(line, file=f)

    UNIT = 'UNIT'
    for name, number in composition.items():
        SFAC = get_sfac(name)
        print(SFAC, file=f)
        UNIT += f' {number}'

    print(UNIT, file=f)
    print('TREF 5000', file=f)
    print('HKLF 4', file=f)
    print('END', file=f)
    print(f'SHELXT ins file generated at {path}.')


def generate_xdsconv_input(path):
    file_path = path + '\\CORRECT.LP'
    i = 0
    global Con_flag
    Con_flag = True
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in reversed(lines):
            i += 1
            # 检查该行是否以“    total”开头
            if line.startswith('    total'):
                fd = line.split()
                break
    fd[4] = fd[4].replace("%", "")
    if float(fd[4]) < 50:
        # 创建窗口
        window = tk.Tk()
        window.title("Attention!")

        # 创建标签
        label1 = tk.Label(window, text=f"Completeness<50% ({fd[4]}%)")
        label1.grid(row=0, column=1)

        label2 = tk.Label(window, text="Continue?")
        label2.grid(row=1, column=1)
        # 创建Yes按钮
        yes_button = tk.Button(window, text="Yes", command=lambda: yes_action(window))
        yes_button.grid(row=2, column=0)

        # 创建No按钮
        no_button = tk.Button(window, text="No", command=lambda: no_action(window))
        no_button.grid(row=2, column=2)
        
        timeout_id = window.after(20000, lambda: yes_action(window))
        window.protocol("WM_DELETE_WINDOW", lambda: [window.after_cancel(timeout_id), window.destroy()])
        window.mainloop()

    if Con_flag:
        i = len(lines) - i
        o = i - 10
        point = 0.8
        k = i
        width = 12
        print(f"| {'Resolution':<{width}} | {'Completeness':<{width}} | {'I/SIGMA':<{width}} | {'CC1/2':<{width}} |")
        j = o 
        while i - 1 > j : 
            j += 1
            print(f"| {lines[j].split()[0]:<{width}} | {lines[j].split()[4]:<{width}} | {lines[j].split()[8]:<{width}} | {lines[j].split()[10]:<{width}} |")
        while k - 1 > o:  # o 是你需要定义的下限索引
            k -= 1  # 递减索引
            if '*' in lines[k].split()[10] and float(lines[k].split()[8]) > 0.3:
                CC_value = lines[k].split()[10]
                cleaned_value = ''.join(filter(lambda x: x.isdigit() or x == '.', CC_value))
                CC_value = float(cleaned_value)
                if CC_value > 50:
                    point = float(lines[k].split()[0])
                    ISIGMA = lines[k].split()[8]
                    CC = lines[k].split()[10]
                    comp = lines[k].split()[4]
                    if point <0.8:
                        point = 0.8
                    break
        out = Path(path) / 'XDSCONV.INP'
        f = open(out, 'w')
        print(f"""
            INPUT_FILE= XDS_ASCII.HKL
            INCLUDE_RESOLUTION_RANGE= 20 {point} ! optional
            OUTPUT_FILE= shelx.hkl  SHELX    ! Warning: do _not_ name this file "temp.mtz" !
            FRIEDEL'S_LAW= FALSE             ! default is FRIEDEL'S_LAW=TRUE""", file=f)
        print(f'Wrote xdsconv input file at {path}.')
        print(f"Total data completeness = {fd[4]}%")
        print(f'Resolution cut by {point}')
        if point == 0.8:
            print(f'Finally, Resolution = {point}, Completeness = {lines[i-1].split()[4]}, CC1/2 = {lines[i-1].split()[10]}, I/SIGMA = {lines[i-1].split()[8]}')
        else :
            print(f'Finally, Resolution = {point}, Completeness = {comp}, CC1/2 = {CC}, I/SIGMA = {ISIGMA}')


def solve_structure_shelxt(path, ins_name='shelx'):
    CWD = str(path)
    cmd = ['shelxt', ins_name]
    print(f'SHELXT attempting at {path}...')
    p1 = subprocess.Popen(cmd, cwd=CWD, stdout=subprocess.PIPE)
    for line in p1.stdout:
        if b'R1  Rweak' in line:
            print(f'Possible solution found at {path}!!!')

    p1.wait()
    print('Shelxt finished running.')


def main():
    import argparse

    description = """
The script sets up socket connection between `instamatic` and `VirtualBox` software via `virtualbox` python API. Therefore, `VirtualBox` and the corresponding SDK need to be installed before running this command. This script is developed particularly for the possibility of running `XDS` under windows 7 or newer, a system which a lot of TEM computers may be using.

After installation of VirtualBox and the corresponding SDK, `XDS` needs to be installed correctly in the guest Ubuntu system. In addition, a shared folder between `VirtualBox` and windows system needs to be set up properly in order for the server to work.

The host and port are defined in `config/settings.yaml`.
"""

    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-shelxt',
                        action='store_true', dest='shelxt',
                        help='Run SHELXT when xds ASCII HKL file is generated.')

    parser.add_argument('-c', '--unitcell',
                        action='store', type=str, nargs=6, dest='unitcell',
                        metavar=('a', 'b', 'c', 'al', 'be', 'ga'),
                        help='Six numbers of the unit cell parameters.')

    parser.add_argument('-s', '--spgr',
                        action='store', type=str, dest='spgr',
                        help='Space group.')

    parser.add_argument('-m', '--composition',
                        action='store', type=str, nargs='+', dest='composition', metavar=('Xn', 'Ym'),
                        help='Unit cell composition, i.e. `-m H2 O1`.')

    parser.set_defaults(shelxt=False,
                        unitcell=None,
                        spgr=None,
                        composition=None)

    options = parser.parse_args()

    shelxt = options.shelxt
    unitcell = options.unitcell
    spgr = options.spgr
    composition = options.composition

    # print(shelxt, unitcell, spgr, composition)

    date = datetime.datetime.now().strftime('%Y-%m-%d')
    logfile = config.locations['logs'] / f'instamatic_xdsVM_server_{date}.log'
    logging.basicConfig(format='%(asctime)s | %(module)s:%(lineno)s | %(levelname)s | %(message)s',
                        filename=logfile,
                        level=logging.DEBUG)
    logging.captureWarnings(True)
    log = logging.getLogger(__name__)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)

    log.info(f'Indexing server (XDS) listening on {HOST}:{PORT}')
    print(f'Indexing server (XDS) listening on {HOST}:{PORT}')

    with s:
        while True:
            conn, addr = s.accept()
            log.info('Connected by %s', addr)
            print('Connected by', addr)
            threading.Thread(target=win_ubuntu_start_xds_AtFolder, args=(conn, shelxt, unitcell, spgr, composition)).start()

    # time.sleep(5)
    # vm_ubuntu_start_xds_AtFolder(session)
    # time.sleep(5)
    # close_down_vm_process(session)
    # time.sleep(5)
    # print("VM server closed down safely!")


if __name__ == '__main__':
    main()
