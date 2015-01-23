# card.py
# Card classes. The windows that go in a BoardBase.

import wx
import os
import wx.richtext as rt
import wx.lib.newevent as ne
import cardbar as CardBar
from utilities import EditText



######################
# Card Class
######################

class Card(wx.Panel):
    BORDER_WIDTH = 2
    BORDER_THICK = 5
    CardEvent, EVT_CARD_DELETE = ne.NewCommandEvent()
    bar = None
    
    def __init__(self, parent, label, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        """Base class for every window that will be placed on Board. Override SetupUI()."""
        super(Card, self).__init__(parent, id, pos, size, style)
        if Card.bar == None:
            Card.bar = CardBar.Create(self.GetParent())

        self.label = label


    ### Behavior functions

    def __del__(self):
        pass

    def GetLabel(self):
        return self.label

    def ShowBar(self):
        CardBar.Associate(self)
        self.bar.Show()
        
    def HideBar(self):
        self.bar.Hide()

    def BarDelete(self):
        """Called by CardBar when the close button is pressed."""
        # simply raise a CardEvent. BoardBase should know what to do
        event = self.CardEvent(id=wx.ID_ANY, card=self)
        self.GetEventHandler().ProcessEvent(event)        
    
                
    ### Auxiliary functions
        
    def InitUI(self):
        """Override me!"""
        pass

    def Dump(self):
        """Override me!"""


class CardEvent(wx.Event):
    def __init__(self):
        print "creating new card event"

    
######################
# Class Header
######################

class Header(Card):
    MIN_WIDTH = 150
    DEFAULT_SZ = (150, 32)
    DEFAULT_TITLE = ""
    
    def __init__(self, parent, label, id=wx.ID_ANY, pos=wx.DefaultPosition, header = "Header...", size=DEFAULT_SZ):
        super(Header, self).__init__(parent, label, id=id, pos=pos, size=size,
                                     style = wx.BORDER_RAISED|wx.TAB_TRAVERSAL)
        self.InitUI()
        self.header.SetValue(header)
        self.len = len(self.GetHeader())


    ### Behavior Functions
    def GetHeader(self):
        return self.header.GetValue()

    ### Auxiliary functions
    def InitUI(self):
        # Controls
        txt = EditText(self)
        txt.SetHint("Header...")
        txt.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        
        # Boxes
        vbox = wx.BoxSizer(wx.VERTICAL)                
        vbox.Add(txt, proportion=0, flag=wx.ALL|wx.EXPAND, border=Card.BORDER_WIDTH)
        
        self.header = txt
        self.SetSizer(vbox)
        self.Show(True)

    def Dump(self):
        """Returns a dict with all the information contained."""
        sz = self.GetSize()
        print "dumping sz"
        return {"class": "Header",
                "label": self.label,
                "pos": self.GetPosition(),
                "width": sz.width,
                "height": sz.height,
                "header": self.GetHeader()}

    
    ### Callbacks

    def OnKeyUp(self, ev):
        # calculate the sizes to compare
        new_len = len(self.GetHeader())

        sw, sh = self.GetSize()
        
        dc = wx.WindowDC(self)
        dc.SetFont(self.header.GetFont())
        tw, th = dc.GetTextExtent(self.GetHeader())
        print "new text size: ", (tw, th)

        # if we're too short: elongate
        if new_len > self.len and tw + 20 > sw:
            print "we're too short"
            self.SetSize((tw + 25, sh))

        # if we're too long: shorten
        # but not more than the minimum size!
        if new_len < self.len and sw > self.MIN_WIDTH and tw - 20 < sw:
            print "we're too long: ", sw
            self.SetSize((tw + 10, sh))

        self.len = new_len
        
        # important!
        ev.Skip()

            

######################
# Class Content
######################

class Content(Card):
    # sizes
    DEFAULT_SZ   = (250, 150)
    COLLAPSED_SZ = (250, 30)
    BIG_SZ       = (350, 250)
    KIND_BTN_SZ  = (33, 23)

    # default control contents
    DEFAULT_TITLE   = ""
    DEFAULT_CONTENT = ""
    
    # kind labels
    DEFAULT_LBL     = "kind"    
    CONCEPT_LBL    = "C"
    ASSUMPTION_LBL = "A"
    RESEARCH_LBL   = "R"
    FACT_LBL       = "F"
    DEFAULT_LBL_LONG    = "kind"
    CONCEPT_LBL_LONG    = "Concept"
    ASSUMPTION_LBL_LONG = "Assumption"
    RESEARCH_LBL_LONG   = "Research"
    FACT_LBL_LONG       = "Fact"
    LONG_LABELS = {CONCEPT_LBL: CONCEPT_LBL_LONG, ASSUMPTION_LBL: ASSUMPTION_LBL_LONG, RESEARCH_LBL: RESEARCH_LBL_LONG, FACT_LBL: FACT_LBL_LONG, DEFAULT_LBL: DEFAULT_LBL_LONG}

    # colours
    # DEFAULT_CL    = (220, 218, 213, 255)

    # thanks paletton.com!        
    COLOURS = {}
    COLOURS[DEFAULT_LBL]    = {"border": (220, 218, 213, 255), "bg": (255, 255, 255, 255)}
    COLOURS[CONCEPT_LBL]    = {"border": (149, 246, 214, 255), "bg": (242, 254, 250, 255)}
    COLOURS[ASSUMPTION_LBL] = {"border": (255, 188, 154, 255), "bg": (255, 247, 243, 255)}
    COLOURS[RESEARCH_LBL]   = {"border": (255, 232, 154, 255), "bg": (255, 252, 243, 255)}
    COLOURS[FACT_LBL]       = {"border": (169, 163, 247, 255), "bg": (245, 244, 254, 255)}

    # content text colours
    # CONCEPT_CNT_CL    = (24, 243, 171, 255)
    # ASSUMPTION_CNT_CL = (255, 102, 25, 255)
    # RESEARCH_CNT_CL   = (255, 202, 25, 255)
    # FACT_CNT_CL       = (68, 54, 244, 255)
    

    def __init__(self, parent, label, id=wx.ID_ANY, pos=wx.DefaultPosition, size=DEFAULT_SZ, title="", kind=DEFAULT_LBL, content=""):
        super(Content, self).__init__(parent, label, id=id, pos=pos, size=size,
                                      style=wx.BORDER_RAISED|wx.TAB_TRAVERSAL)

        self.InitUI()
        self.SetKind(kind)
        if title: self.title.SetValue(title)
        if content: self.content.SetValue(content)

        
    ### Behavior functions

    def Collapse(self):
        if not self.IsCollapsed():
            self.content.Hide()
            self.SetSize(self.COLLAPSED_SZ)

    def Uncollapse(self):
        if self.IsCollapsed():
            self.content.Show()
            self.SetSize(self.DEFAULT_SZ)

    def IsCollapsed(self):
        return not self.content.IsShown()

    def GetTitle(self):
        return self.title.GetValue()

    def GetContent(self):
        return self.content.GetValue()
    
    def GetKind(self, long=False):
        if long: return self.LONG_LABELS[self.kindbut.GetLabel()]
        else:    return self.kindbut.GetLabel()

    def SetKind(self, kind):
        if kind == "kind": self.kindbut.SetLabel("kind")
        else:              self.kindbut.SetLabel(kind[0])
        self.SetColours(kind)

    
    ### Auxiliary functions
    
    def InitUI(self):
        # controls
        title = EditText(self)
        title.SetHint("Title...")
        
        kindbut = wx.Button(self, label = "kind", size=Content.KIND_BTN_SZ, style=wx.BORDER_NONE)
        kindbut.SetOwnFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False))
        
        content = wx.TextCtrl(self, size=(10, 10), style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_NO_VSCROLL)
        
        # boxes
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(title,   proportion=1, flag=wx.ALL|wx.EXPAND, border=Card.BORDER_WIDTH)
        hbox1.Add(kindbut, proportion=0, flag=wx.ALL,           border=Card.BORDER_WIDTH)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(content, proportion=1, flag=wx.EXPAND, border=Card.BORDER_THICK)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)
        vbox.Add(hbox1, proportion=0, flag=wx.ALL|wx.EXPAND, border=Card.BORDER_WIDTH)
        vbox.Add(hbox2, proportion=1, flag=wx.ALL|wx.EXPAND, border=Card.BORDER_THICK)
        
        # bindings
        kindbut.Bind(wx.EVT_BUTTON, self.OnKindPressed)
        content.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.kindbut = kindbut
        self.title = title
        self.content = content
        self.Show(True)

    def Dump(self):
        pos = self.GetPosition()
        return {"class": "Content",
                "label": self.label,
                "pos": (pos.x, pos.y),
                "kind": self.GetKind(),
                "title": self.GetTitle(),
                "content": self.GetContent(),
                "collapsed": self.IsCollapsed()}

    def SetColours(self, kind):
        self.SetBackgroundColour(self.COLOURS[kind]["border"])
        self.title.SetFirstColour(self.COLOURS[kind]["border"])
        self.title.SetSecondColour(self.COLOURS[kind]["bg"])
        self.content.SetBackgroundColour(self.COLOURS[kind]["bg"])


    ### Callbacks

    def OnKeyDown(self, ev):
        # skip TAB, so that we don't input \t and tab traversal still works
        if ev.GetKeyCode() != 9:
            ev.ResumePropagation(True)
            ev.Skip()
        else:
            self.Navigate(wx.MouseState().ShiftDown())

    def OnKindPressed(self, ev):
        ctrl = ev.GetEventObject()
        rect = ctrl.GetRect()
        pos = ctrl.GetPosition() + (rect.width, rect.height)
        self.PopupMenu(KindSelectMenu(self), pos)


            
class KindSelectMenu(wx.Menu):
    def __init__(self, card):
        super(KindSelectMenu, self).__init__()
        self.card = card

        A_item = wx.MenuItem(self, wx.NewId(), "Assumption")
        C_item = wx.MenuItem(self, wx.NewId(), "Concept")
        R_item = wx.MenuItem(self, wx.NewId(), "Research")
        F_item = wx.MenuItem(self, wx.NewId(), "Fact")
        N_item = wx.MenuItem(self, wx.NewId(), "None")

        self.AppendItem(A_item)
        self.AppendItem(C_item)
        self.AppendItem(R_item)        
        self.AppendItem(F_item)
        self.AppendItem(N_item)

        self.Bind(wx.EVT_MENU, lambda ev: self.OnSelect(ev, Content.ASSUMPTION_LBL), A_item)
        self.Bind(wx.EVT_MENU, lambda ev: self.OnSelect(ev, Content.CONCEPT_LBL), C_item)
        self.Bind(wx.EVT_MENU, lambda ev: self.OnSelect(ev, Content.RESEARCH_LBL), R_item)
        self.Bind(wx.EVT_MENU, lambda ev: self.OnSelect(ev, Content.FACT_LBL), F_item)
        self.Bind(wx.EVT_MENU, lambda ev: self.OnSelect(ev, Content.DEFAULT_LBL), N_item)

        
    # Callbacks
    def OnSelect(self, ev, kind):
        # my parent is the control that displayed the menu
        if isinstance(self.card, Content):
            self.card.SetKind(kind)



######################
# Class Image
######################            

class Image(Card):
    DEFAULT_SZ = (50, 50)
    DEFAULT_PATH = ""
    
    def __init__(self, parent, label, path=None, id=wx.ID_ANY, pos=wx.DefaultPosition, size=DEFAULT_SZ):
        super(Image, self).__init__(parent, label, id=id, pos=pos, size=size, style=wx.BORDER_RAISED)
        self.btn = None
        self.InitUI(path)
        self.path = path


    ### Behavior funtions

    def SetImage(self, path):
        bmp = wx.Bitmap(path)
        img = wx.StaticBitmap(self)
        img.SetBitmap(bmp)
        img.SetSize(bmp.GetSize())
        
        if self.btn:
            self.btn.Hide()
            del self.btn
            self.btn = None

        self.path = path
        self.GetSizer().Add(img, proportion=1, flag=wx.ALL|wx.EXPAND, border=self.BORDER_THICK)
        self.Fit()

    ### Auxiliary functions
    
    def InitUI(self, path=None):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        if not path:
            btn = wx.BitmapButton(self, bitmap=wx.ArtProvider.GetBitmap(wx.ART_MISSING_IMAGE), size=self.DEFAULT_SZ)
            vbox.Add(btn, proportion=1, flag=wx.ALL|wx.EXPAND, border=self.BORDER_THICK)
            self.btn = btn
            btn.Bind(wx.EVT_BUTTON, self.OnButton)
        else:
            self.SetImage(path)        

    def Dump(self):
        pos = self.GetPosition()
        return {"class": "Image",
                "label": self.label,
                "pos": (pos.x, pos.y),
                "path": self.path}

        
    ### Callbacks

    def OnButton(self, ev):
        fd = wx.FileDialog(self, "Save", os.getcwd(), "", "All files (*.*)|*.*",
                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if fd.ShowModal() == wx.ID_CANCEL: return # user changed her mind
        self.SetImage(fd.GetPath())
