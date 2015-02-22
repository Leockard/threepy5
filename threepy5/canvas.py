# -*- coding: utf-8 -*-
"""
A window that can be drawn over in a free-hand style, with a custom
background. In threepy5, every Page has a Canvas, whose background is
set as the current view in that Page's Board. The overall result is that
the user can hand-draw "over" the Board. Some code copied from wxPython
demo code app doodle.py: http://www.wxpython.org/download.php.
"""

import wx
from utilities import AutoSize


######################
# CanvasBase Class
######################

class CanvasBase(wx.StaticBitmap):
    """CanvasBase is a StaticBitmap over which the user can draw by free-hand."""
    def __init__(self, parent, bitmap=wx.NullBitmap):
        super(CanvasBase, self).__init__(parent, bitmap=bitmap, style=wx.BORDER_NONE)
        self.thickness = 1
        self.colour = "BLACK"
        self.pen = wx.Pen(self.colour, self.thickness, wx.SOLID)
        self.lines = []
        self.pos = wx.Point(0,0)
        self.buffer = wx.EmptyBitmap(1, 1)
        self.offset = wx.Point(0, 0)
        
        self.InitBuffer()

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        
    ### Behavior functions
    
    def SetOffset(self, pt):
        self.offset = pt

    def GetOffset(self):
        return self.offset

    def DrawLines(self):
        """Redraws all the lines that have been drawn already."""
        dc = wx.MemoryDC(self.GetBitmap())
        dc.BeginDrawing()

        for colour, thickness, line in self.lines:
            pen = wx.Pen(colour, thickness, wx.SOLID)
            dc.SetPen(pen)
            for coords in line:
                x1, y1, x2, y2 = coords
                # draw the lines relative to the current offset
                dc.DrawLine(x1 - self.offset.x, y1 - self.offset.y,
                            x2 - self.offset.x, y2 - self.offset.y)
        
        dc.EndDrawing()
        self.SetBitmap(dc.GetAsBitmap())

        
    ### Auxiliary functions
    
    def InitBuffer(self):
        """Initialize the bitmap used for buffering the display."""
        size = self.GetClientSize()
        buf = wx.EmptyBitmap(max(1, size.width), max(1, size.height))
        dc = wx.BufferedDC(None, buf)

        # clear everything by painting over with bg colour        
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        self.DrawLines()
        self.buffer = buf

        
    ### Callbacks

    def OnLeftDown(self, ev):
        """Called when the left mouse button is pressed"""
        self.curLine = []
        self.pos = ev.GetPosition()

    def OnLeftUp(self, ev):
        """Called when the left mouse button is released"""
        "CanvasBase.LeftUp"
        self.lines.append((self.colour, self.thickness, self.curLine))
        self.curLine = []
            
    def OnMotion(self, ev):
        if ev.Dragging() and ev.LeftIsDown():
            # BufferedDC will paint first over self.GetBitmap()
            # and then copy everything to ClientDC(self)
            dc = wx.BufferedDC(wx.ClientDC(self), self.GetBitmap())
            dc.BeginDrawing()
            
            dc.SetPen(self.pen)
            new_pos = ev.GetPosition()

            # draw the lines with relative coordinates to the current view
            coords = (self.pos.x, self.pos.y, new_pos.x, new_pos.y)
            dc.DrawLine(*coords)

            # but store them in absolute coordinates
            coords = (self.pos.x + self.offset.x, self.pos.y + self.offset.y,
                      new_pos.x  + self.offset.x,  new_pos.y + self.offset.y)
            self.curLine.append(coords)
            self.pos = new_pos
            
            dc.EndDrawing()
            self.SetBitmap(dc.GetAsBitmap())

        
        
######################
# Canvas Class
######################

class Canvas(AutoSize):
    """An AutoSize object (which is a wx.Panel through wx.ScrolledWindow) which holds a Canvas as its only child."""
    
    def __init__(self, parent, size=wx.DefaultSize, pos=wx.DefaultPosition):
        super(Canvas, self).__init__(parent)

        # controls        
        ctrl = CanvasBase(self, bitmap=wx.NullBitmap)

        # boxes
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)
        box.Add(ctrl, proportion=1)

        # bindings
        self.Bind(wx.EVT_SHOW, self.OnShow)

        # finish up        
        self.ctrl = ctrl

                
    ### Behavior functions

    def SetOffset(self, pt):
        self.ctrl.SetOffset(pt)

    def GetOffset(self):
        return self.ctrl.GetOffset()

    def SetBackground(self, bmp):
        """Call to show the part that will be seen."""
        if bmp:
            self.ctrl.SetBitmap(bmp)
            self.FitToChildren()

    ### Auxiliary functions

    def Dump(self):
        """Unlike many other controls that dump a dict, we are dumping a list."""
        return self.ctrl.lines

    def Load(self, li):
        """Load from a list got from Canvas.Dump()"""
        self.ctrl.lines = li


    ### Callbacks

    def OnShow(self, ev):
        if ev.IsShown():
            self.ctrl.DrawLines()


###########################
# pdoc documentation setup
###########################
# __pdoc__ is the special variable from the automatic
# documentation generator pdoc.
# By setting pdoc[class.method] to None, we are telling
# pdoc to not generate documentation for said method.
__pdoc__ = {}
__pdoc__["field"] = None

# Since we only want to generate documentation for our own
# mehods, and not the ones coming from the base classes,
# we first set to None every method in the base class.
for field in dir(wx.StaticBitmap):
    __pdoc__['CanvasBase.%s' % field] = None
for field in dir(Canvas):
    __pdoc__['Canvas.%s' % field] = None

# Then, we have to add again the methods that we have
# overriden. See https://github.com/BurntSushi/pdoc/issues/15.
for field in CanvasBase.__dict__.keys():
    if 'CanvasBase.%s' % field in __pdoc__.keys():
        del __pdoc__['CanvasBase.%s' % field]
for field in Canvas.__dict__.keys():
    if 'Canvas.%s' % field in __pdoc__.keys():
        del __pdoc__['Canvas.%s' % field]
