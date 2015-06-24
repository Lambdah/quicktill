"""User interface for members of staff to items to a structured,
generic event log.  Events can be one-off (eg. "we refused a sale to
someone who appeared to be underage") or repeating (eg. "fire alarm
tested ok this week").

This is expected to be used for things like:

 * Regular testing, eg. fire alarm, gas safety, etc.

 * Regular maintenance, eg. keg line cleaning, ice maker cleaning

 * Regulatory compliance, eg. staff re-training on age-related sales,
   and logging of refusals

"""

# User interfaces to define:
# Create event type - web interface only?
# Add event of a particular type
# View events by type
# View events by date
# List events by deadline

import datetime
from . import ui,user,td,keyboard
from .models import User,EventType,EventDetailTemplate,Event,EventDetail

class AddEvent(ui.dismisspopup):
    def __init__(self,eventtype):
        """Add an event.  eventtype is the 'slug'.

        """
        evt=td.s.query(EventType).get(eventtype)
        if not evt:
            ui.infopopup(["Event type '{}' does not exist.".format(eventtype)],
                         title="Error")
            return
        currentuser=ui.current_user()
        if not currentuser:
            ui.infopopup(["There is no current user.  Events can only be "
                          "recorded when a user is logged in."],
                         title="Error")
            return
        (mh,mw)=ui.stdwin.getmaxyx()
        w=mw
        enabled_templates=[x for x in evt.templates if x.enabled]
        promptlen=max(len(x.description) for x in enabled_templates)+2
        doubleheight=promptlen>(mw/2)
        # Dialog height will be:
        # One blank line
        # One or two lines per detail
        # One line for deadline, if required
        # One line for note
        # One blank line
        # Button to save event
        # One blank line
        # Top and bottom borders
        ui.dismisspopup.__init__(
            self,7+len(enabled_templates)*(2 if doubleheight else 1)+ \
            (0 if evt.interval is None else 1),w,
            title=evt.description,colour=ui.colour_input)
        y=2
        self.fieldlist=[]
        # XXX create fields for details
        for f in enabled_templates:
            self.addstr(y,2,"{}:".format(f.description))
            if doubleheight: y=y+1
            field=ui.editfield(y,2+promptlen,w-4-promptlen)
            self.fieldlist.append(field)
            y=y+1
        if evt.interval:
            self.addstr(y,2,"Next deadline: ")
            self.deadlinefield=ui.datefield(
                y,17,f=datetime.date.today()+datetime.timedelta(days=evt.interval))
            y=y+1
            self.fieldlist.append(self.deadlinefield)
        self.addstr(y,2,"Notes: ")
        self.notefield=ui.editfield(y,17,w-19)
        self.fieldlist.append(self.notefield)
        y=y+2
        button=ui.buttonfield(y,w/2-4,8,"Save")
        self.fieldlist.append(button)
        ui.map_fieldlist(self.fieldlist)
        self.fieldlist[0].focus()
