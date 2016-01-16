# example of curses: less command
# https://gist.github.com/avillafiorita/9e626ce370e1da6c6373
# osascript -e "tell application \"Terminal\" to set the font size of window 1 to $2"
# osascript -e "tell application \"Terminal\"  to set current settings of front window to settings set \"Pro\""
# @todo: use curses.wrapper to create initial screen 
# http://stackoverflow.com/questions/14004835/nodelay-causes-python-curses-program-to-exit
# @todo: smooth resize transitions
import atexit
import curses
import sys
import traceback

import cv2

class Page:
    def __init__(self, screen):
        self.screen = screen
        self.top = 0
        self.left = 0
        self._size = self.screen.getmaxyx()
        
        self.pad = curses.newpad(self.size[0], self.size[1])
        self.pad.nodelay(1)
        
        self.video = cv2.VideoCapture(0)
        self.video.set(3, self.size[1]) # CV_CAP_PROP_FRAME_WIDTH
        self.video.set(4, self.size[0]) # CV_CAP_PROP_FRAME_HEIGHT
        self.palette = ' .;-:!>7?CO$QHNM'
    
    @property
    def size(self):
        return self.screen.getmaxyx()

    def show(self):
        self.pad.refresh(self.top, self.left, 0, 0, self.size[0], self.size[1])
    
    def do_command(self):
        ch = self.pad.getch()
        if ch > -1:
            curses.flash()
            if ch == ord('q'): 
                sys.exit()
            if ch == curses.KEY_RESIZE:
                self.video.set(3, self.size[1]) # CV_CAP_PROP_FRAME_WIDTH
                self.video.set(4, self.size[0]) # CV_CAP_PROP_FRAME_HEIGHT

    def start(self):
        while True:
            self.pad.resize(self.size[0], self.size[1])

            self.loop()

            self.show()
            self.do_command()

    def loop(self):
        ret, frame = self.video.read()
        # convert to gray scale
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for h in range(0, len(frame)):
            for w in range(0, len(frame[h])):
                pixel = self.palette[int((frame[h][w]*len(self.palette))/(256))]
                self.pad.insstr(h, w, pixel)

        cv2.imshow('frame', frame)

def main():
    screen = curses.initscr()
    curses.noecho() # no echo key input
    curses.cbreak() # input with no-enter keyed
    curses.curs_set(0) # hide cursor
    
    page = Page(screen)
    page.start()

@atexit.register
def exit():
    curses.curs_set(1)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    traceback.print_last()


if __name__ == "__main__":
    main()
