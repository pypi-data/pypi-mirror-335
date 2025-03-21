#!/usr/bin/env python3
"""
 These modules should contain one function each...


# for loading df: ======= taken from gregory_on_line: ascgeneric
#
 - load asc        df, ininame,start = load_asc( f+avadisc[num]  )

 - select_channels()
 - load_ini_file()



   ascdf,ascfilename,iascfilename, ascstart = histo_io.select_asc_to_load( ii ,
                                                            folder = config.CONFIG[target]['data_folder']) # FULL DF

   ascdf_chan = ascgeneric.select_channels(ascdf, int(cmd),  delete_original = True) # if no delete, problems
                TRGHOLD,PEAKHOLD, TIMEWIN_US,ECALIBa, ECALIBb = ascgeneric.load_ini_file( iascfilename , int(cmd) )
                TIMEWIN_US = PEAKHOLD

  if ascdf_chan is not None:
    if 'dtus' in ascdf_chan: # never happens
         print("X... YOU NEED TO RELOAD BEFORE SELECTING DIFFERENT CHANNEL")
     else:
         ascdf_chan = ascgeneric.enhance_dt(ascdf_chan)
         ascgeneric.asc_stat_print(ascdf_chan, TIMEWIN_US, filename = ascfilename , TRGHOLD = TRGHOLD)
         t0 = ascdf_chan['time'].min()
         t1 = ascdf_chan['time'].max()
         rate = len(ascdf_chan)/(t1-t0) # divided by total time
         runtime = dt.timedelta( seconds = t1-t0 )
         if   'c_erlang2' in canvases:
             if ascdf_chan is not None:
                 local_generate_erlangs()

                        deadttot = ascgeneric.asc_stat_print(ascdf_chan, TIMEWIN_US,  filename = ascfilename,  TRGHOLD = TRGHOLD)
                        ascgeneric.asc_stat_print(ascdf, TIMEWIN_US,  filename = ascfilename, TRGHOLD = TRGHOLD)
                        histt = ascgeneric.histo_time( ascdf_chan, "time" , binlo, binhi )

                        hiene = ascgeneric.histo_energy( ascdf_chan , calibration = (ECALIBa, ECALIBb) )

"""

from fire import Fire
from console import fg,bg
from codeframe import config
from codeframe import objects


KNOWN_COMMANDS_LOCAL_TYPE = "OBJ"

def main(*args,**kwargs):
    #print(f"{fg.dimgray}D... main() @fn_print: args/kwargs.../{args}/{kwargs}/{fg.default}")
    #print(f"D... main() @fn_show: args/kwargs.../{args}/{kwargs}/")
    oname = ""
    if len(args)==0:
        print("D...  give me an object: allowed objects:",objects.get_objects_list_names() )
        return None
    # === printing

    oname = args[0]

    # print( oname,"?", list( objects.get_objects_list() ) )

    if objects.object_exists(oname):
        print(f"i... printing {fg.green}{oname}{fg.default}  ")
        #objects.list_objects(  )

        obj = objects.get_object( oname )

        #print(f"i... exists  {fg.green}{oname}{fg.default} == {obj} ")
        if obj is None:
            print(f"i... {fg.red} cant get  {oname}{fg.default}")
            return False
        #print( "D... type==",type(obj) ,"   ....... prepare")
        #print( obj.__dict__ )
        #obj.print()
        #print(obj.get_name() )
        #print(obj.about() )
        #print(obj.abouts() )
        if "printme" in dir(obj):
            #print("D...    printme is there...")
            obj.printme()
        else:
            return False
        #print(f"i... obj function called  {fg.green}{oname}{fg.default}  ")

    else:
        print(f"i... {fg.red} NOT showing {oname}{fg.default}")

    return True

if __name__=="__main__":
    Fire(main)
