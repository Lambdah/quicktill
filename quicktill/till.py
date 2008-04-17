#!/usr/bin/env python

"""Entry point for the till application.  In normal use the application
will be started by calling main() from this module.

"""

import sys,curses,ui,keyboard,event,logging,td
import printer,tillconfig,event,foodorder,locale
from version import version

def start(stdwin):
    # The display is initialised at this point
    stdwin.nodelay(1) # Make getch() non-blocking

    # Initialise screen
    ui.init(stdwin)

    # Create pages for various functions
    fp=None
    for pagedef,hotkey,args in tillconfig.pages:
        p=ui.addpage(pagedef,hotkey,args)
        if fp is None: fp=p
    ui.selectpage(fp)

    # Enter main event loop
    event.eventloop()

def run():
    # Initialise logging
    log=logging.getLogger()
    log.info("Starting version %s"%version)
    try:
        td.init()
        # Copy keycaps from database to keyboard driver
        caps=td.keyboard_getcaps(tillconfig.kbtype)
        for keycode,keycap in caps:
            if ui.kb.setkeycap(keyboard.keycodes[keycode],keycap)==False:
                log.info("Deleting stale keycap for layout %d keycode %s"%(
                    tillconfig.kbtype,keycode))
                td.keyboard_delcap(tillconfig.kbtype,keycap)
        curses.wrapper(start)
    except:
        log.exception("Exception caught at top level")

    log.info("Shutting down")
    logging.shutdown()

    return event.shutdowncode

def main():
    """Usual main entry point for the till software, unless you are doing
    something strange.  Reads the location of its global configuration,
    command line options, and the global configuration, and then starts
    the program.

    """
    
    try:
        f=file("/etc/quicktill/configurl")
        configurl=f.readline()
        f.close()
    except:
        configurl=None
    from optparse import OptionParser
    import urllib
    usage="usage: %prog [options]"
    parser=OptionParser(usage,version=version)
    parser.add_option("-u", "--config-url", action="store",
                      type="string", dest="configurl",
                      help="URL of global till configuration file")
    parser.add_option("-c", "--config-name", action="store",
                      type="string", dest="configname",
                      help="Till type to use from configuration file")
    parser.add_option("-d", "--database", action="store",
                      type="string", dest="database",
                      help="Database connection string; overrides "
                      "configuration file")
    parser.set_defaults(configurl=configurl,configname="default",
                        database=None)
    (options,args)=parser.parse_args()
    if len(args)>0:
        parser.error("this program takes no arguments")
    if options.configurl==None:
        parser.error("No configuration URL provided in "
                     "/etc/quicktill/configurl or on command line")
    tillconfig.configversion=options.configurl
    f=urllib.urlopen(options.configurl)
    globalconfig=f.read()
    f.close()

    import imp
    g=imp.new_module("globalconfig")
    exec globalconfig in g.__dict__

    config=g.configurations.get(options.configname)
    if config is None:
        print ("Configuration \"%s\" does not exist.  "
               "Available configurations:"%options.configname)
        for i in g.configurations.keys():
            print "%s: %s"%(i,g.configurations[i]['description'])
        sys.exit(1)

    log=logging.getLogger()
    formatter=logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler=logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.ERROR)
    log.addHandler(handler)
    
    if 'printer' in config:
        printer.driver=config['printer'][0](*config['printer'][1])
    else:
        printer.driver=pdrivers.nullprinter()
    printer.kickout=printer.driver.kickout
    if 'labelprinter' in config:
        printer.labeldriver=config['labelprinter'][0](
            *config['labelprinter'][1])
    tillconfig.pages=config['pages']
    td.database=config.get('database')
    if options.database is not None: td.database=options.database
    ui.kb=config['kbdriver']
    tillconfig.kbtype=config['kbtype']
    foodorder.kitchenprinter=config.get('kitchenprinter')
    foodorder.menuurl=config.get('menuurl')
    tillconfig.pubname=config['pubname']
    tillconfig.pubnumber=config['pubnumber']
    tillconfig.pubaddr=config['pubaddr']
    tillconfig.vatrate=config['vatrate']
    tillconfig.vatno=config['vatno']
    tillconfig.companyaddr=config['companyaddr']
    tillconfig.currency=config['currency']
    tillconfig.cashback_limit=config['cashback_limit']
    if 'pricepolicy' in config:
        tillconfig.pricepolicy=config['pricepolicy']
    if 'qtystring' in config:
        tillconfig.qtystring=config['qtystring']
    if 'format_currency' in config:
        tillconfig.fc=config['format_currency']
    if 'priceguess' in config:
        tillconfig.priceguess=config['priceguess']

    locale.setlocale(locale.LC_ALL,'')
    sys.exit(run())

if __name__=='__main__':
    main()