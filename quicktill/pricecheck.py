"""Price lookup window.

"""

from __future__ import unicode_literals
from . import td,ui,keyboard,stock,linekeys

class pricecheck_keypress(object):
    """
    This class is a mixin for the various classes used by the price
    lookup user interface; it provides preprocessing of keypresses to
    spot line key presses.

    """
    def keypress(self,k):
        if hasattr(k,"line"):
            self.dismiss()
            bindings=linekeys.linemenu(k,pricecheck_window)
            if bindings==0:
                popup(prompt="There are no options on key \"%s\".  Press "
                      "another line key."%k.keycap)
        else:
            super(pricecheck_keypress,self).keypress(k)

class popup(pricecheck_keypress,ui.infopopup):
    def __init__(self,prompt="Press a line key."):
        ui.infopopup.__init__(
            self,[prompt],title="Price Check",
            dismiss=keyboard.K_CASH,colour=ui.colour_info)

class pricecheck_line_with_capacity(pricecheck_keypress,ui.menu):
    """
    Stockline with capacity -> display menu of items on sale on that line.

    """
    def __init__(self,stockline):
        sos=stockline.stockonsale
        f=ui.tableformatter(' r l r+l ')
        sl=[(f(x.id,x.stocktype.format(),x.ondisplay,x.instock),
             pricecheck_stockitem,(x,)) for x in sos]
        ui.menu.__init__(self,sl,title="%s (%s) - display capacity %d"%
                         (stockline.name,stockline.location,stockline.capacity),
                         blurb=("Choose a stock item for more information, or "
                                "press another line key."),
                         colour=ui.colour_info)

class pricecheck_stockitem(pricecheck_keypress,ui.listpopup):
    """
    A particular stock item on a line.

    """
    def __init__(self,stockitem):
        td.s.add(stockitem)
        ui.listpopup.__init__(self,
                              stock.stockinfo_linelist(stockitem.id),
                              title="Stock item %d"%stockitem.id,
                              dismiss=keyboard.K_CASH,
                              show_cursor=False,
                              colour=ui.colour_info)

def pricecheck_window(kb):
    """
    Given a keyboard binding, display a suitable popup window for
    information about it.  We're choosing between three classes
    defined in this file:

    no stock -> popup prompt
    line with capacity -> list of items on sale
    line without capacity -> stock info

    """
    td.s.add(kb)
    sos=kb.stockline.stockonsale
    if len(sos)==0:
        popup("There is no stock on '%s'.  Press another line key."%
              kb.stockline.name)
        return
    if kb.stockline.capacity:
        pricecheck_line_with_capacity(kb.stockline)
    else:
        pricecheck_stockitem(sos[0])