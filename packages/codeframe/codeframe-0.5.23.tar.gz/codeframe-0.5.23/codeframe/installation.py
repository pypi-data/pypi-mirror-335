#!/usr/bin/env python3
"""
Core of any project with all tui tricks

I need to create a version that works from pip installed code
for the moment
this unit will go through and copy unit by unit
"""
import os
from fire import Fire
from console import fg,bg
import subprocess  as sp
import sys





from contextlib import contextmanager

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def pack_before_publishing():
    """
    Some files do not survive pip upload:
    """
    PREPACK = ['README.org','distcheck.sh',
     'requirements.txt',
     '.bumpversion.cfg',
     'setup.py',
     '.gitignore',
     'bin/codeframe',
     'bin_codeframe.py',
    'codeframe/__init__.py']


def die():
    sys.exit(1)

def run_or_die( cmd , debug = False):
    #print()
    res = 0
    if type(cmd)==list:
        try:
            if debug: print("exe...", cmd)
            res = sp.check_call( cmd2 )
        except:
            res= 1
            print(f"X... {fg.red} error running /{bg.white}{cmd}{bg.default}/{fg.default}")
    if res != 0: die()

    if cmd.find("&")>=0:  die()
    if cmd.find("|")>=0:  die()
    if cmd.find("'")>=0:  die()
    #if cmd.find('"')>=0:  die() # for sed
    if cmd.find('$')>=0:  die()
    if cmd.find('%')>=0:  die()
    if cmd.find('#')>=0:  die()
    if cmd.find('!')>=0:  die()
    if cmd.find('(')>=0:  die()
    if cmd.find(')')>=0:  die()
    res = 0
    #print()
    try:
        if debug: print("Exe...", cmd)
        cmd2 = cmd.split()
        for i in range(len(cmd2)):
            #print(i, cmd2[i])
            cmd2[i] = cmd2[i].strip('"')
        #print(cmd2)
        if debug: print("Exe...", cmd2)
        res = sp.check_call( cmd2 )
        if debug: print("ok",res)
    except:
        res =1
        print(f"X... {fg.red} error running /{bg.white}{cmd}{bg.default}/{fg.default}")
    #print()
    if res != 0: die()


def main( name ):
    """
    1. stage - mkdir and check local existence
    2. stage - copy modules and replace codeframe
    THESE ARE NOT SEEN IN PIP3 INSTALLATION:
  -----------
    README.org
    distcheck.sh
    requirements.txt
    .bumpversion.cfg
    setup.py
    .gitignore
    bin/codeframe
    bin_codeframe.py
    codeframe/__init__.py
   -----------  put them into some container before publishing

    """
    # f'bin/{name}',
    # f'bin_{name}',
    # f'{name}/__init__.py'
    #
    #  MODULES THAT ARE THE PART OF THE SYSTEM
    #
    modules = ['version','key_enter','topbar','config','README.org','distcheck.sh','requirements.txt','.bumpversion.cfg','setup','.gitignore','df_table',
               'bin/codeframe','bin_codeframe','codeframe/__init__.py','mmapwr.py','interpreter.py', 'cmd_parser.py','objects.py',
               'fn_lo.py', 'fn_load.py', 'fn_show.py']


    # softlink these modules from subdirectory
    #
    #  WHAT IS NEEDED TO SOFT LINK
    #
    lnmod = ['version','key_enter','topbar','config','df_table', 'mmapwr.py','interpreter.py','cmd_parser.py','objects.py',
             'fn_lo.py', 'fn_load.py', 'fn_show.py']

    # POSTINIT, create  also COPA = f"~/.config/{proj}/cfg.json"
    #init = ['git','test','config',f'ln bin/{name}']


    ## prepare the structure or check existing commands
    #
    #
    #
    prep = [f'mkdir  {name}',f'mkdir -p {name}/bin',f'mkdir -p {name}/data',f'mkdir -p {name}/{name}','which pandoc']

    ######################################################### mkdirs....
    if os.path.exists(name):
        print(fg.red, f"... {name} ALREADY EXISTS: I cannot work ...", fg.default)
        sys.exit(1)

    for i in prep:
        print(f" PREP.. {i:22s}", end="")
        run_or_die(i)
        print(fg.green,'[OK]',fg.default)


    ######################################################### exists,cp,repl
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print(fg.blue,dir_path,fg.default)
    for i in modules:
        #print(" SPL",os.path.splitext(i))
        fname = i

        # NO .dotf, NO .ext, NO bin/xxx  ===> PY
        if os.path.splitext(i)[-1] == "" and i[0]!='.' and i.find("/")<0:
            fname = f"{i}.py"

        EX = f"{fg.red}[xx]{fg.default}"
        SRC = f"{dir_path}/{fname}"
        print(f" {fname:22s} ", end="", flush = True)


        # exists? ######################################### GO THROUGH FEW POSSIBILITIES
        if not os.path.exists( SRC ):
            print(fg.cyan,"*",fg.default, end="")#"... searching {SRC} ...", end = "")
            SRC = f"{dir_path}/data/installation_files/{fname}"
            #print(f"... switching to  {SRC} ...")
        else:
            print(fg.cyan," ",fg.default, end="")#"... searching {SRC} ...", end = "")



        if os.path.exists( SRC ):
            EX = f"{fg.cyan}[exist]{fg.default}"
            print(f" {EX} ", end="", flush = True)

            DST = fname
            DST = DST.replace("codeframe",name)
            #name.replace("codeframe",name)

            ################################# copy
            CP = f"cp {SRC} {name}/{DST}"
            #print(CP)
            run_or_die(CP)
            EX = f"{fg.green}[cp]{fg.default}"
            print(f" {EX} ", end="", flush = True)

            ################################### sed- codefame -> newname
            #with open(f"{name}/{DST}") as f:
            SED = f'sed -i "s/codeframe/{name}/gI" {name}/{DST}'
            #print(SED)
            run_or_die(SED)
            EX = f"{fg.green}[Repl]{fg.default}"
            print(f" {EX} ", end="", flush = True)

            ################################# ln -s
            if i in lnmod:
                with cd(name):
                    with cd(name):
                        LNS = f'ln -s ../{fname}'
                        #print(LNS)
                        run_or_die(LNS)
                        EX = f"{fg.orange}[ln -s]{fg.default}"
                        print(f" {EX} ", end="", flush = True)

        else:
            print(fg.red, f"X... NOT FOUND", fg.default , end = "")
        print(f"")
        # open read open write cd ln -s


    ############ replace import installation ##################
    SRC = f"{name}/bin_{name}.py"
    SED = f'sed -i  "/installation/d" {SRC}'
    print("",SED,end=" ")
    run_or_die(SED)
    EX = f"{fg.green}[rm 'import installation']{fg.default}"
    print(f" {EX} ", end="", flush = True)
    print()


    ##################### readme #########################
    SRC = f"{name}/README.org"
    DST = f"{name}/README.md"
    with open(SRC,"w") as f:
        f.write(f"""
* {name}
/barebones made by codeframe/

*Purpose:* ={name}= is

** Example

#+begin_src python
 # example
#+end_src


** Installation

#+begin_src sh
 pip3 install {name}
#+end_src

** Usage

""")
    CMD = f' pandoc -i {SRC} -o {DST}'
    print(CMD, end="")
    run_or_die(CMD)
    EX = f"{fg.green}[README]{fg.default}"
    print(f" {EX} ",  flush = True)
    print()


    ##################### version  #########################
    SRC = f"{name}/version.py"
    with open(SRC,"w") as f:
        f.write('__version__="0.0.1-dev0"\n')

    #--------------- update .bumpversion.cfg
    SRC2 =  f"{name}/.bumpversion.cfg"
    BMP = "current_version=0.0.1-dev0"
    SED = f'sed -i "/.*current_version\s=.*/c\{BMP}" {SRC2}'
    #print(SED)
    run_or_die(SED)


    CMD = "bumpversion patch"
    with cd(f"{name}"):
        run_or_die(CMD)

    with open(SRC) as f:
        aaa=f.read()
    print(aaa.strip(), end = "")
    EX = f"{fg.green}[version]{fg.default}"
    print(f" {EX} ",  flush = True)
    print()

    ##################### SETUP  #########################
    SRC = f"{name}/setup.py"
    USER = os.getlogin()

    SED = f'sed -i "s/codeframe/{name}/" {SRC}'
    #print(SED)
    run_or_die(SED)


    SED = fr"sed -i s/\w\+@gmail.com/{USER}@gmail.com/ {SRC}"
    #print(SED)
    run_or_die(SED)

    SED = fr'sed -i s@http://.\+"@http://gitlab.com/{USER}/{name}"@ {SRC}'
    #print(SED)
    run_or_die(SED)

    SED = fr'sed -i s@https://.\+"@https://gitlab.com/{USER}/{name}"@ {SRC}'
    #print(SED)
    run_or_die(SED)

    SED= r"sed -i s@package_data=.\\+@package_data=\{"+f'"{name}":'+'["data/testik"]\},@ '+fr' {SRC}'
    SED= r"sed -i s@package_data=.\+@package_data=\{"+f'"{name}":'+'["data/testik"]\},@ '+fr' {SRC}'
    SED= r"sed -i s@package_data=.\+@package_data={"+f'"{name}":'+'["data/testik"]},@ '+fr' {SRC}'
    #print(SED)
    run_or_die(SED, debug = True)

    SED= fr'sed -i "/installation_files/d"  {SRC}'
    print(SED)
    run_or_die(SED, debug = True)


    with open(SRC) as f:
        ali = f.readlines()
    ali = [x for x in ali if x.find('url')>0 ]
    print(ali[0].rstrip(), end="")

    EX = f"{fg.green}[setup]{fg.default}"
    print(f" {EX} ",  flush = True)


    #return
    ##################### git  #########################
    CMD = "git init"
    with cd(f"{name}"):
        run_or_die(CMD)
    EX = f"{fg.green}[git init]{fg.default}"
    print(f" {EX} ", end="", flush = True)
    print()
    CMD = "git add ."
    with cd(f"{name}"):
        run_or_die(CMD)
    EX = f"{fg.green}[git add]{fg.default}"
    print(f" {EX} ", end="", flush = True)

    CMD = "git commit -a -m the_very_first_commit"
    with cd(f"{name}"):
        run_or_die(CMD)
    EX = f"{fg.green}[git add]{fg.default}"
    print(f" {EX} ", end="", flush = True)
    print()




    print("============================ i am done now. (next test? config?)")


if __name__=="__main__":
    Fire(main)
