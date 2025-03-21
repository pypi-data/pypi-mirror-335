#!/usr/bin/env python3

# to override print <= can be a big problem with exceptions
#
# colors in d f_table _fg _bg columns:
# see
# https://github.com/mixmastamyk/console/blob/master/console/color_tables_x11.py#L112
#

import sys
import os
from fire import Fire
from codeframe.version import __version__
from codeframe import config # -------- config at the beginning.....!!!!!
# AND load config after all modules import config !
from codeframe.config import move_cursor
from codeframe import topbar
from codeframe import key_enter
from codeframe import mmapwr
from codeframe import interpreter
from codeframe import objects # I have no reach from remote-keyboard BUT from mainkb

from codeframe import installation

#### -------   TABLE CAPABILIITES ------ from codeframe  import d f_table
from codeframe.df_table import create_dummy_df, show_table, \
    inc_dummy_df, crtable
# from codeframe import libs_one
# from codeframe import libs_two

import pandas as pd


import time
import datetime as dt
from console import fg, bg, fx
# -------- This was earlier forcolors, now TERMINALX
#from blessings import Terminal
import os
from pyfiglet import Figlet
import signal

# ====================== for separate terminal keyboard using mmap
#from prompt_toolkit.styles import Style
from prompt_toolkit.cursor_shapes import CursorShape, ModalCursorShapeConfig

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter, NestedCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

import json # transfe list to string and back

# ==================================================================
# ==================================================================
# ==================================================================
# =====EDIT: remove 2x SHOWS========================================
SHOW_LOGO_TABLE = False
SHOW_TIME = False
SHOW_COMMAND_LINE = True
RUN_MMAP_INPUT = True  #  INTERACTIVE MMAP-INTERACTIVE

# ======= EDIT: For Selection from DF TABLE True ====================
RUN_SELECT_FROM_TABLE = False

termsize = config.get_terminal_columns() # os.get_terminal_size().columns


def handle_sigwinch(signum: signal.Signals, qqq):
    # pylint: disable=unused-argument
    #print("WINCH SIGNAL:",type(qqq), qqq)
    #os.system("reset")
    return None


# ----this DOES IT
#  for FONTS in `pyfiglet -l`; do echo $FONTS; pyfiglet $FONTS -f $FONTS; done | less
figlet = Figlet(font="slant")
# figle2 = Figlet(font="roman")
# figle2 = Figlet(font="standard")
figle2 = Figlet(font="ansi_regular")


def print_logo():
    """
    print fromt page + time
    """
    global termsize
    # global figlet, filg

    word = " codeframe"

    print("")
    print(figlet.renderText(word))
    print(figle2.renderText(dt.datetime.now().strftime("%H:%M:%S ")))
    print(
        f"DO YOU WANT TO INSTALL ME ?... Run me with your  \
{fg.green}'projectname'{fg.default} as a parameter"
    )
    print(f"do you want to show me ?  run with {fg.green}'show'{fg.default} as a parameter ")
    print(f"                            {fg.green}'.t'{fg.default} for show table ")
    print(f"                            {fg.green}'.d'{fg.default} for show date ")
    print(f"                            {fg.green}'.h'{fg.default} for show help (not working) ")
    print(f"                            {fg.green}'.r'{fg.default} for reset terminal ")
    print(f"do you want to quit ?  type {fg.green}'.q'{fg.default}  ")
    #print(f"    terminal width = {termsize} {os.get_terminal_size().columns}")


def autoreset_terminal():
    """
    call every loop
    """
    global termsize
    termsize2 = os.get_terminal_size().columns
    #print("TS???", termsize, termsize2)
    if termsize != termsize2:
        print("i... RESET TERMINAL")
        os.system("reset")
        #terminal.clear()
        termsize = termsize2
        move_cursor(1, 1)
        #print("X")

# ***************************************************************************************
# ***************************************************************************************
#
#   MAIN :  default logo = True
#             server and detached_keyb False
#
#
# ***************************************************************************************
# ***************************************************************************************
# =============EDIT: put completely your parameters ==================
def main(projectname=None, debug=False, keyboard_remote_start = False, servermode = False, logo=False, table=False):
    """
    Tool to create a new project.\n
    When the parameter 'projectname' is given: new project (in folder named 'projectname') is created

    Parameters:
    :param projectname THIS WILL GENERATE NEW PROJECT with these modules
    :param keyboard_remote_start: just start a standalone prompt
    :param servermode wait for commands via mmap... to be used with -k
    :param logo it is True for convenient showup
    :param table enable selection from the df-table
    """
    global RUN_SELECT_FROM_TABLE, SHOW_LOGO_TABLE, SHOW_TIME, RUN_MMAP_INPUT
    if debug:
        print("D... Debug ON")
        config.DEBUG = True
        config.CFG_DEBUG = True
    else:
        config.DEBUG = False
        config.CFG_DEBUG = False

    # =========EDIT:  for sure you know already if t use table or not......
    if table:
        RUN_SELECT_FROM_TABLE = True

    # ------------- important to initialize all commands from interpretter
    # =====  EDIT: remove interpretter initialization if NO PYTHON FILES and NO COMMANDS =========
    interpreter.init_interpretter()
    SHOW_LOGO_TABLE = logo # CHANGE
    SHOW_TIME = logo #CHANGE


    # ======== DEFINE THE CONFIG FILE HERE ======== load_config
    # after all modules import config
    # BEFORE FIRST PARSING
    config.CONFIG["filename"] = "~/.config/codeframe/cfg.json"
    config.CONFIG["history"] = "~/.config/codeframe/history"
    config.load_config()
    directory = config.CONFIG['filename']
    directory = os.path.expanduser(directory)
    if not os.path.exists(directory):
        print("W... saving default configuration")
        config.save_config()
    with open("/tmp/codeframe.log", "a") as f:
        f.write(f'i... ************************************************\n')
        f.write(f'i... {dt.datetime.now()}\n')
        #f.write(f'i... in config loaded: PATH ==  {config.CONFIG["services"]} \n')


    # ========================================
    #   First command parsing #############
    #-----------------------------------------


    # if projectname is None:
    #     print("version: ", __version__)
    #     print(f"         USE   -h for help                ")
    #     print(f"         USE   show ... for demo              ")
    #     print(f"         USE   show -l -t  ... for FULL demo  ")
    #     sys.exit(0)

    ##===================================================================
    #  FORST COMMAND SYSTEM -  CLI ************************************
    #--------------------------------------------------------------------


    if projectname == "h":
        # HELP
        print("version: ", __version__, file=sys.stderr)
        print("i... trying to HELP ",  file=sys.stderr)
        print("""
 a ... add job to cron (from the allowesd directory structure
 r ... RUN job in screen
 d ... delete job from cron
 c ... show comment
 e ... enter SCREEN
 t ... show time slice
 p ... show fullpath ... emacs `cronvice p tele01`
 h ... this help
""")
        sys.exit(0)


    if not projectname is None:
        print("version: ", __version__)
        print("X... unsupported command")
        sys.exit(0)


    # =========================================================================
    #
    #--------------------------------------------------------------------------

    # ========== EDIT:   remove completely the servermode if running only in the same terminal
    if not servermode: RUN_MMAP_INPUT = False
    # GLobal clear terminal
    if debug:
        print(__version__)
    #else:

    signal.signal(signal.SIGWINCH, handle_sigwinch)



    # ==================================================== #########################
    # ==================================================== ######################### remote
    #               command prompt - separate thread
    #  this is probably a standalone keyboard interface ==========================
    # ============= EDIT:  replace keyoard_remote_start with FALSE if you use single terminal interface
    if keyboard_remote_start:
        #prompt_completer = WordCompleter( interpreter.KNOWN_COMMANDS )
        prompt_completer = NestedCompleter.from_nested_dict( interpreter.KNOWN_COMMANDS_DICT )
        #allobjects = interpreter.allobjects #  ['obj1']
        multilineinput = False
        config.myPromptSession = PromptSession(
            history=FileHistory( os.path.expanduser(config.CONFIG["history"]) )
        ) #, multiline=Trueinp
        inp = ""
        myname = os.path.splitext(os.path.basename(__file__))[0]

        # --------!!! this is not visible
        print(f"i...  input interface to {fg.orange}{myname}{fg.default} application. .q to quit all; .h to help.")
        #loopn = 0
        while (inp!=".q"):
            #loopn+=1
            inp = config.myPromptSession.prompt("> ",
                                                cursor=CursorShape.BLINKING_UNDERLINE,
                                                multiline=multilineinput,
                                                completer=prompt_completer,
                                                complete_while_typing=False,
                                                wrap_lines=True, # no noew lines
                                                mouse_support=False,  #middlemouse
                                                auto_suggest=AutoSuggestFromHistory()
                                                )
            if inp==".h":
                # ------------- all this is not visible-!!!
                print("H...  HELP:")
                print("H...  .t   table+logo")
                print("H...  .d   disable logo and time")
                print("H...  .r   reset terminal")
                print("H... known commands: ", "  ".join(interpreter.KNOWN_COMMANDS )  )
            elif inp==".r":
                pass
            elif inp==".d":
                pass
            elif inp==".t":
                pass
            elif inp==".q":
                mmapwr.mmwrite(inp)
            else:
                # SOME REAL COMMUNICATION WITH THE OPERATION THREAD ----
                # If not finished -->> wait for it;
                #   and get name of
                #print(loopn)
                mmapwr.mmwrite(inp)
                done = False
                ii = 1
                #esc = chr(27)
                #cc=f'a{esc}[5m_'
                cc=" "
                spinner = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
                while not done:
                    # res = mmapwr.mmread(  ) # read response
                    ii+=1
                    res = mmapwr.mmread_n_clear( mmapwr.MMAPRESP  )
                    res = res.strip() # strin newline
                    print("\r",spinner[ii%8], end=cc, flush=True)

                    # if ii%2==0:
                    #     print(spinner[0], end="\r", flush=True)
                    # else:
                    #     print(spinner[3], end="\r", flush=True)
                    #print(f"... input was /{inp}/==/{res}/..result of read   len(inp):", len(inp), "  ...res:",len(res) )
                    # if res.strip()==inp.strip(): # BEFORE SENDING OBJ
                    if res.strip().find( inp.strip() )==0:
                        parts = res.strip().split("###")
                        if len(parts)>1:
                            obj_names = json.loads( parts[-1] )
                            #print("D... received objnames:", obj_names, type(obj_names))
                            #print(f" YES::::.../{inp}/==/{res}/.. ?")
                            # I need to append newly created objects to the autocomplete.....DIFFICULTY 9
                            interpreter.allobjects = obj_names #.append( f"o{loopn}" ) # TSTING
                            print(f"  {fg.dimgray}... known:",interpreter.allobjects,fg.default)
                            #objects.get_objects_list_names()
                            for i in interpreter.KNOWN_COMMANDS_LOCAL_OBJ:
                                interpreter.KNOWN_COMMANDS_DICT[i] = {}
                                for j in interpreter.allobjects:
                                    interpreter.KNOWN_COMMANDS_DICT[i][j] = None
                            prompt_completer = NestedCompleter.from_nested_dict( interpreter.KNOWN_COMMANDS_DICT )

                        done = True
                    #else:
                    #    print(f" NONO:::.../{inp}/==/{res}/.. ?")
                    time.sleep(0.25)
                #print("... konec prikazu")


        # print(inp)
        return
    # ==================================================== ######################### END
    #           command prompt - separate thread
    # ==================================================== ######################### END


    if projectname == "install":
        #installation.main(projectname)
        print(f"{fg.red} INSTALLATION STARTED ******************************************** : {fg.default}")
        print(f"{fg.cyan} ... project name : {bg.cyan}{fg.white}{projectname}{fg.default}{bg.default}")
        print(f"{fg.yellow} ... creating folder {bg.yellow}{fg.black}{projectname}{bg.default}{fg.yellow} with all stuff inside : {bg.default}{fg.default}")
        print("*" * 40)
        installation.main(projectname)
        sys.exit(0)

    # ===================== top bar and commads from kdb ==========
    os.system("reset")
    # when I put reset later, it occludes the 1st red inpput command

    #top = topbar.TopBar(bgcolor=bg.blue)
    #top2 = top.add(bgcolor=bg.black)

    top = topbar.TopBar(bgcolor="auto")#bg.blue)
    top2 = top.add_bar(bgcolor=bg.black)
    top.add_element("time", 15,10 + 12, dt.datetime.now().strftime('%H:%M:%S') , fg.white + fx.bold)
    top.add_element("tag", 1,13, "mode" , fg.black + fx.italic)
    #top.add_element("host", -10,10, topbar.get_hostname() , fg.black )

    #top.add_element("host", -10,10, get_hostname(), bg.orange + fx.bold + fg.blue)
    top2.add_element("cmd", 1,22, ">", fg.white + fx.bold + bg.red)


    # ========================= INITIAL cmd key setting....
    cmd = ""
    enter = False
    key = None
    a, b = (" ", " ")

    # KEYTHREAD THIS MUST BE HERE.....toi catch 1st letter
    #   only return         key, enter, abc = kthread.get_global_key()
    #                       key:mayreact on q;     enter==hit ; abc=>(a,b) for display.
    kthread = None
    # ============= EDIT: for one-terminal - NO MMAP , put False inplace of RUN_MMAP_INPUT
    if RUN_MMAP_INPUT:
        # THis goes when mmap active
        #print("i...   MMAP ACTIVE ...........................")
        kthread = key_enter.MmapSimulatedKeyboard(ending=".q")
    else:
        #print("D...    MMAP NOT ACTIVE, using SSHKEYB.............")
        kthread = key_enter.KeyboardThreadSsh(ending=".q")
    # whatabout to have other terminal feeding mmapfile

    selection = None

    move_cursor(1, 1)

    dfmain = create_dummy_df() # pd.DataFrame([["Server", 3, 1], ["NAS", 4, 4] ], columns=['a', 'b', 'c'])

    #################################################################
    #################################################################
    #          INFINITE           L O O P
    #################################################################
    #################################################################
    count = 0
    while True:
        count += 1
        autoreset_terminal()
        # ===EDIT: comment SHOW and SHOW if not needed, leave curson
        if (SHOW_LOGO_TABLE):
            # DEBUG terminalx.clear()
            move_cursor(1, 9)
            if SHOW_TIME:
                print_logo()

            # time.sleep(0.05)

        #if ( count % 3) == 0:
        # ========= INTENSIVE OPERATIONS ======================
        if count % 1 == 0:
            #config.mycron.read() # update the situation ... use object from config
            dfnew = inc_dummy_df(dfmain) # crtable()  #
            # ========== EDIT ==== check here if the tablde/dataframe DIFFER ===========*********
            if False:
            #if (not dfnew['screen'].equals(dfmain['screen'])  ) or  (not dfnew['cron'].equals(dfmain['cron'])  ):
            #    dfmain = dfnew
                os.system("reset")
            show_table(dfmain, selection)
            print(".d SHOWTIM .t SHOWTABLE .r RESET ...xxx  1-.. select")
            move_cursor(1, 9)
            #for tag in config.INSIDE_PROC_OBJ.keys():
            #    if not config.INSIDE_PROC_OBJ[tag].poll() is None:
            #        config.INSIDE_LAST_RUN[tag] = dt.datetime.now() - config.INSIDE_LAST_RUN[tag]
            #        #config.INSIDE_PROC_OBJ.pop(tag) # no more store this element
        #
        # RUN OPERATION ON TABLE
        #
        #df = inc_dummy_df(df)

        key, enter, abc = kthread.get_global_key()
        (a, b) = abc  # unpack tuple

        #################################################################
        #          KEYBOARD ANALYSIS  #second command level #############
        if enter:
            #print()
            #print("--------------------------------------ENTER pressed")
            if len(key.strip()) == 0:
                pass
            elif key.strip() == ".q":
                # print("X...   quit requested ..........................")
                # no space to wait for the next loop
                feedback = f"{key}###{json.dumps(objects.get_objects_list_names())}"
                mmapwr.mmwrite( feedback , mmapwr.MMAPRESP) #
                break
            elif key.strip().find(".r") == 0:
                os.system("reset")
                move_cursor(1,9)
            # =========== EDIT: comment out if needed ===================================
            elif key.strip().find(".t") == 0:
                SHOW_LOGO_TABLE = not SHOW_LOGO_TABLE
            elif key.strip().find(".d") == 0:
                SHOW_TIME = not SHOW_TIME
            else:
                cmd = key.strip()
                # some command must come..... not possible to have only ""
                # ======================================================== INTERPRETER
                #if cmd==".t":
                #elif cmd==".d":
                #elif cmd==".r":
                #else:
                if config.DEBUG:
                    print(f"{fg.gray}D... calling interpreter from bin*main {fg.default}")
                # ----
                if RUN_SELECT_FROM_TABLE: # FLIP FLOP MODE
                    # list of row numbers from column 'n' :  assume whole word is list of rows:
                    if selection is not None and selection != "":
                        #if config.DEBUG: print(f"{fg.gray}D... selecting from table {fg.default}")
                        # but I dont need interpretter in this simple case.........
                        # ============ EDIT: I just guess that you dont want to use the general INTERPRETTER HERE *******
                        #interpreter.main( f"{cmd} {selection}"  )
                        if SHOW_LOGO_TABLE:
                            df_subset = show_table(dfmain, selection, return_subdf=True)
                        for index, row in df_subset.iterrows():
                            print(f"Index: {index}, Row: {row.to_dict()}")
                            scrname = row['screen'] #list(df_subset['screen'])[index]
                            print(scrname)
                            #print( type(scrname) ) # ******** THIRD COMMAND LEVEL ON SELECTION
                            if cmd == 'e':
                                libs_screen.enter_screen(scrname)
                            elif cmd == 's':
                                libs_screen.stop_screen(scrname)
                            else:
                                print("... UNKNOWN COMMAND")
                            #time.sleep(3)
                        selection = ""
                        #autoreset_terminal()
                        os.system("reset")
                    else:
                        if config.DEBUG: print(f"{fg.gray}D... selecting from table {fg.default}")
                        selection = cmd
                else:# EVERY COMMAND MODE
                    # =========== NOT selection  FLIP/FLOP MODE ===============
                    interpreter.main( cmd )

                # ======================================================== INTERPRETER
            #print(f"----------- {cmd}; table_selection:{selection}--------------------- ***")
            #print("...writeback try:", key)
            #print(" oL=", objects.get_objects_list_names() )

            feedback = f"{key}###{json.dumps(objects.get_objects_list_names())}"
            mmapwr.mmwrite( feedback , mmapwr.MMAPRESP) #
            #print("...writeback done",key)
        else:
            cmd = ""

        TAGTAB = "----"
        if RUN_SELECT_FROM_TABLE:
            if selection is not None and selection != "":
                TAGTAB = f"{fg.blue}{bg.yellow}command mode{fg.default}{bg.default}"
            else:
                TAGTAB = f"{fg.green}select mode{fg.default}"
#         top.print_to(
#             2,
#             f"{TAGTAB}{fg.white}{fx.bold}    {dt.datetime.now().strftime('%H:%M:%S')}\
# {fx.default}{fg.default}",
#         )
        top.update_element("time",  f"{dt.datetime.now().strftime('%H:%M:%S')}"    )

        #
        #  commandline at TOP#2, cursor  a_b; option not to show
        #
        if (not SHOW_COMMAND_LINE) or (  (key is not None) and (len(key) == 0) ):
            #top2.print_to(0, f"{fg.cyan}{bg.black}{' '*termsize}{bg.black}")
            top2.update_element( "cmd", f"{' '*termsize}")
        else:
            # command input is on the 2nd TOP line
            # top2.print_to(
            #     0,
            #     f"{fg.white}{bg.red} > {fx.bold}{a.strip()}{fg.yellow}_{fg.white}{b.strip()}\
            # {fx.default}{fg.default}{bg.default} ",
            # )
            top2.update_element( "cmd", f"> {fx.bold}{a.strip()}{fg.yellow}_{fg.white}{b.strip()}{fx.default}{fg.default}{bg.default}" )

        # PLACE THE TOPBAR INPLACE
        top.place()
        time.sleep(0.1)


# ====================================================================


if __name__ == "__main__":
    Fire(main)
    #print("*********************************")
