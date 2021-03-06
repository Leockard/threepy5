#!/usr/bin/python

import wx
import threepy5

__all__ = ["threepy5", "deck", "canvas", "card", "view", "box", "utilities"]

if __name__ == "__main__":
    app = wx.App()
    frame = threepy5.ThreePyFiveFrame(None)
    app.MainLoop()
