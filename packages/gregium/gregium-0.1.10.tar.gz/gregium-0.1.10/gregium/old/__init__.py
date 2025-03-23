"""
The (original) core of Gregium

See documentation in README.md file
"""

# Pygame Imports
import pygame, pygame.freetype, pygame.image

# Other Required Imports
import math
import zipfile
import os
import threading
import json
import sys
import time
from pathlib import Path
from pynput import keyboard

# Many lines have logging to output errors and what's happening
import logging

# Declaring Globals
LOGGER = logging.getLogger(__name__)
try:
    os.remove(os.getcwd()+"\\gregium.log")
except:
    pass
logging.basicConfig(filename='gregium.log', level=logging.DEBUG)
logging.debug(f"Logger created {time.ctime(time.time())}")
PATH = str(Path(__file__).parent.absolute())
WINDOW = None
SELECTEDBUTTON = None
SCRLX = 0
SCRLY = 0
MAINCLOCK = None
logging.info("Globals declared")

# Initializing Pygame
pygame.init()

def init(clock:pygame.Clock):
    logging.info("Init Ran")
    """
    Will define the global WINDOW (an other) variables to the current 
    working window, required for many functions to run

    *pygame.display.set_mode() must be run first to create the window
    """

    # Redefines global "WINDOW" to be the current working surface
    global WINDOW,MAINCLOCK
    WINDOW = pygame.display.get_surface()
    MAINCLOCK = clock

def alignPos(pos:tuple[float,float], 
             align:str="topLeft") -> tuple[float,float]:
    """
    Aligns a position to a corner of the window, possible corners to align to include, 
    topRight, topLeft, bottomRight, bottomLeft, centerRight, 
    centerLeft, centerTop, centerBottom, and center, 
    each of which scale relative to the size of the window.
    The default position is topLeft and running alignPos 
    with topLeft returns the same value; 
    bottomRight is the opposite corner and will add the 
    total x & y values of the window respectively.

    Will raise error if gregium.init() is not run first
    """

    # Make sure there is a window specified
    if WINDOW != None:
        
        # Set corner based on the value of "align"
        match align:
            case "topRight":
                return (pos[0]+WINDOW.get_width(),
                        pos[1])
            case "topLeft":
                return pos
            case "bottomRight":
                return (pos[0]+WINDOW.get_width(),
                        pos[1]+WINDOW.get_height())
            case "bottomLeft":
                return (pos[0],
                        pos[1]+WINDOW.get_height())
            case "centerRight":
                return (pos[0]+WINDOW.get_width(),
                        pos[1]+(WINDOW.get_height()/2))
            case "centerLeft":
                return (pos[0],pos[1]+(WINDOW.get_height()/2))
            case "centerBottom":
                return (pos[0]+(WINDOW.get_width()/2),
                        pos[1]+WINDOW.get_height())
            case "centerTop":
                return (pos[0]+(WINDOW.get_width()/2),
                        pos[1])
            case "center":
                return (pos[0]+(WINDOW.get_width()/2),
                        pos[1]+(WINDOW.get_height()/2))
            case _:
                return pos
                
    # If the window isn't loaded, throw an informational error
    else:
        raise Exception("Must run init first")

def animRGB(originalRGB:tuple[int,int,int],newRGB:tuple[int,int,int],steps:int):
    """
    Makes a list of all rgb values in order to transition from originalRGB to newRGB
    """

    # Get the modifiers
    rModif = (originalRGB[0]-newRGB[0])/steps
    gModif = (originalRGB[1]-newRGB[1])/steps
    bModif = (originalRGB[2]-newRGB[2])/steps

    # Generate a new list
    rgbList = []
    for step in range(steps-1):
        rgbList.append((originalRGB[0]-(rModif*step),originalRGB[1]-(gModif*step),originalRGB[2]-(bModif*step)))

    rgbList.append(newRGB)

    # Return the final list
    return rgbList

def rotate(origin:tuple[float,float], point:tuple[float,float], 
           angle:float) -> tuple[float,float]:
    """
    Will rotate a point counterclockwise around a given origin, 
    new point position is based on original distance to the origin, 
    angle must be given in degree form for function to work properly.

    *May have small rounding errors
    """

    # Converts the value of "angle" into radians
    ang = math.radians(angle)

    # Unpacks the "origin" and "point" variables
    ox, oy = origin
    px, py = point

    # Converts degrees to radians
    ang = math.radians(angle)

    # Split up point tuple
    ox, oy = origin
    px, py = point

    # Calculate new position based on angle
    qx = ox + math.cos(ang) * (px - ox) - math.sin(ang) * (py - oy)
    qy = oy + math.sin(ang) * (px - ox) + math.cos(ang) * (py - oy)

    # Return new position in the form of a tuple
    return (qx, qy)

def get_window_center() -> tuple[float,float]:
    """
    Returns the center of the current working window.

    *Will raise error if gregium.init() is not run first
    """

    # Get center & return
    return (WINDOW.get_width()/2,WINDOW.get_height()/2)

def position_center(original:tuple[float,float],
                    size:tuple[float,float]) -> tuple[float,float]:
    """
    Will return the coordinates required 
    (assuming shape is blitted from top-left corner) 
    in which the center of the object will be at original 
    for given size.

    *Not the same as get_center()
    """

    # Sutract size to make blitting pos (top-left) yield the center
    return (original[0]-(size[0]/2),original[1]-(size[1]/2))

def get_center(original:tuple[float,float],
                size:tuple[float,float]) -> tuple[float,float]:
    """
    Will return the center of the shape assuming the original 
    is in the top left of the given size.

    *Not the same as position_center()
    """
def get_rect_center(rect:pygame.Rect) -> tuple[float,float]:
    """
    Returns the center coordinates of the given pygame.Rect 
    element based on the x & y coordinates of it.
    """
    # Add width & height to rect to get center coordinates
    return (rect.x+rect.w/2,rect.y+rect.h/2)

#### ---- FONT HANDLER ---- ####
class FontType(type):
    def __init__(self):
        """
        Only used in Font.from_sys() and Font.from_file() so that 
        extensions such as pylance or other python extensions that 
        autocomplete will work correctly when initializing from the alternate methods.
        """
        self.font:pygame.freetype.Font = pygame.freetype.Font()
    
    def blit(self,text:str,pos:tuple[int,int],size:int=20,
             fgcolor:tuple[int,int,int]=(255,255,255),
             bgcolor:tuple[int,int,int]=None,
             angle:int=0):
        pass

    def blit_center(self,text:str,pos:tuple[int,int],size:int=20,
                    fgcolor:tuple[int,int,int]=(255,255,255),
                    bgcolor:tuple[int,int,int]=None,
                    angle:int=0):
        pass

    def blit_true_center(self,text:str,pos:tuple[int,int],size:int=20,
                         fgcolor:tuple[int,int,int]=(255,255,255),
                         bgcolor:tuple[int,int,int]=None,
                         angle:int=0):
        pass
    
class Font:
    def __init__(self,fontInst:pygame.freetype.Font):
        logging.info("Font Created")
        """
        Defines a font instance from a pygame.freetype.font, 
        font must have been initialized through pygame.freetype.font 
        unless using the 
        Font.from_sys() or Font.from_file() methods.
        gregium.Font allows easier blitting and modification of 
        fonts which pygame is unable to replicate.
        """
        self.font:pygame.freetype.Font = fontInst

    def blit(self,text:str,pos:tuple[int,int],size:int=20,
             fgcolor:tuple[int,int,int]=(255,255,255),
             bgcolor:tuple[int,int,int]=None,
             angle:int=0,altWindow:pygame.Surface=None):
        """
        Will blit text to the main working window at point pos unless altWindow is specified, 
        all parameters are the same as normal pygame.freetype.Font.render() or 
        pygame.freetype.Font.render_to() parameters; 
        font will be fully left-aligned based on the pos parameter.

        *Will raise an error if gregium.init() is not run first
        """

        # Sets working window to the main window if nothing is specified
        if altWindow == None:
            altWindow = WINDOW

        # Blits text onto specified window (or default if no window is provided)
        for layer,txt in enumerate(text.split("\n")):
            self.font.render_to(altWindow,(pos[0],pos[1]+(layer*size)),
                                txt,fgcolor,bgcolor,
                                size=size,rotation=angle)

    def blit_center(self,text:str,pos:tuple[int,int],size:int=20,
                    fgcolor:tuple[int,int,int]=(255,255,255),
                    bgcolor:tuple[int,int,int]=None,angle:int=0,
                    altWindow:pygame.Surface=None):
        """
        Will blit text to the main working window with center 
        located at point pos unless altWindow is specified, 
        all parameters are the same as normal pygame.freetype.Font.render() or 
        pygame.freetype.Font.render_to() parameters; 
        font will be fully left-aligned based on the pos parameter.

        *Will raise an error if gregium.init() is not run first
        """

        # Sets working window to the main window if nothing is specified
        if altWindow == None:
            altWindow = WINDOW

        # Blits center of the text onto coordinates in the 
        # specified window (or default if no window is provided)
        for layer,txt in enumerate(text.split("\n")):
            fgr = self.font.get_rect(txt,size=size,rotation=angle)
            self.font.render_to(
                altWindow,position_center((pos[0],pos[1]+(layer*size)),
                (fgr.w,fgr.h)),txt,fgcolor,bgcolor,size=size,rotation=angle)

    def blit_true_center(self,text:str,pos:tuple[int,int],size:int=20,
                         fgcolor:tuple[int,int,int]=(255,255,255),
                         bgcolor:tuple[int,int,int]=None,angle:int=0,
                         altWindow:pygame.Surface=None):
        """
        Will blit text to the main working window with 
        center located at point pos unless altWindow is specified, 
        all parameters are the same as normal pygame.freetype.Font.render() or 
        pygame.freetype.Font.render_to() parameters; 
        font will be fully center-aligned based on the pos parameter.

        *Will raise an error if gregium.init() is not run first
        """

        # Sets working window to the main window if nothing is specified
        if altWindow == None:
            altWindow = WINDOW

        # Splits text line by line to make each one centered
        splitTxt = text.split("\n")
        yOffS = ((len(splitTxt)-1)*size)/2
        for layer,txt in enumerate(splitTxt):
            fgr = self.font.get_rect(txt,size=size,rotation=angle)
            self.font.render_to(altWindow,position_center(
                (pos[0],pos[1]+(layer*size)-yOffS),
                (fgr.w,fgr.h)),txt,fgcolor,bgcolor,size=size,rotation=angle)

    @classmethod
    def from_sys(self,fontName:str) -> FontType:
        logging.info(f"Generating Font From SysFonts ({fontName})")
        """
        Will initialize the same font as the gregium.Font 
        method but instead from a system font using the pygame.freetype.SysFont method.
        """
        return self(pygame.freetype.SysFont(fontName,20))
    
    @classmethod
    def from_file(self,filePath:str) -> FontType:
        logging.info(f"Generating Font From File FP: {filePath}")
        """
        Will initialize the same font as the gregium.Font method
          but instead uses a font file path the same way the main gregium.Font is initialized 
          via the pygame.freetype.Font method.
        """
        return self(pygame.freetype.Font(filePath,20))

# Define font variable
SPACEMONO = Font.from_file(PATH+"\\editor\\SpaceMono-Regular.ttf")

#### ---- SPRITE HANDLER ---- ####
def SpriteOnlyImg(filePath:str,size:tuple[int,int]=None,
                  rotation:int=0,
                  hasOneImage:bool=True) -> tuple[pygame.Surface,pygame.Surface]:
    """
    Generates a pygame.Surface without class information
    First Surface is original image (for repeat changing)
    Second Surface is modified image to current settings, 
    if nothing is applied both surfaces will be the same
    If image load fails, empty surface will be 
    returned as well as having a warning

    *For memory reasons, it is recommended to almost always set hasOneImage to True. 
    """
    logging.info(f"Sprite Image Loading FP: {filePath}")

    try:
        # Loads the image based on the given file path
        imageO = pygame.image.load(filePath)
        image = imageO

        # Transforms the scale/rotation of the image if specified
        if size != None:
            image = pygame.transform.scale(image,size)
        if rotation != None:
            image = pygame.transform.rotate(image,rotation)

    # Warns user if the filepath is invalid
    except:
        logging.error(f"Image: {filePath} not found")
        imageO = pygame.Surface((1,1))
        image = imageO
    
    # Returns only the edited image, if user specifies to
    if hasOneImage:
        return image
    
    # Returns the original and edited image
    return [imageO,image]

class Sprite:
    def __init__(self,filePath:str,sheetSize:tuple[int,int]=None):
        logging.info(f"Sprite Loading FP: {filePath}")
        """
        Creates a basic sprite for rendering, with a sprite 
        image or sprite sheet loaded from the provided file path.
        If the sprite has an animation sheet, set the sheetSize 
        argument to the (rows, columns) of the sprite sheet.
        """

        try:
            # Loads the image and sets up variables of the class
            self.origImage = pygame.image.load(filePath).convert_alpha()
            self.width = self.origImage.get_width()
            self.height = self.origImage.get_height()
            self.rotation = 0
            self.inverted = False
            self.origScale = (self.width,self.height)
            self.scrollModif = 1
            self.imageBlitRect = pygame.Rect(0,0,1,1)
            self.dropshadow = pygame.Surface((5,5))
            self.fp = filePath

            # Sets up spritesheets for animation as specified by the user
            if sheetSize != None:
                self.is_sheet = True
                self.sheetSize = sheetSize
                self.sheetAnimMS = 1000
                self.sheetTick = 0
                self.width /= self.sheetSize[0]
                self.height /= self.sheetSize[1]
                self.imageRect = pygame.Rect(0,0,self.width,self.height)
                self.origScaleM = (self.width,self.height)

            # Disables sprite sheets and animation
            else:
                self.is_sheet = False
                self.sheetSize = (1,1)

            # Updates the sprite's image
            self.updateImage()
            
        # If an invalid argument is passed, nullify the image
        except Exception as e:
            logging.error(f"{e}")
            self.origImage = None
            self.is_sheet = False

    def updateImage(self):
        """
        Updates the image for animation/movement

        
        * The order should always be 
        #1 updateImage() 
        #2 updateDropShadow() only if applicable
        #3 tint_add/tint_mult
        #4 blit/blit_center/blit_pivot_center
        #5 testColl/testCollR unless you define the "pos" argument
        """
            
        # Return with a failed exit code if there is no image
        if self.origImage == None:
            return -1

        # If spritesheets are enabled, display the next sprite
        if self.is_sheet:
            self.imageBlit = pygame.transform.scale(
                self.origImage.subsurface(self.imageRect),
                                                    (self.width,
                                                    self.height))
        
        # Otherwise, redisplay the sprite
        else:
            self.imageBlit = pygame.transform.scale(
                self.origImage,
                (self.width,
                self.height))

        # Reposition the sprite and reset the sprite's Rect value
        if self.rotation != 0:
            self.imageBlit = pygame.transform.rotate(self.imageBlit,self.rotation)

        self.imageBlitRect.w,self.imageBlitRect.h = self.imageBlit.get_width(),self.imageBlit.get_height()

        return 1
    def updateDropShadow(self):
        """
        Generates a drop shadow for the current frame of the sprite

        *Required for any drop shadow to render at all and run every frame of drop shadow before blit
        """

        # Get copy of current image but grayscaled
        self.dropshadow = pygame.transform.grayscale(self.imageBlit)
        self.dropshadow.fill((0,0,0),special_flags=pygame.BLEND_MIN)
        self.dropshadow.set_alpha(128)

    def tint_add(self,rgb:tuple[int,int,int]):
        """Tint the sprite with the given color"""
        
        # Return with a failed exit code if there is no image
        if self.origImage == None:
            return -1
        
        # Tints the sprite with the rgb color
        self.imageBlit.fill(rgb,special_flags=pygame.BLEND_RGB_ADD)

        return 1

    def tint_mult(self,rgb:tuple[int,int,int]):
        """
        Multiplies each pixel on sprite by rgb tint
        """

        # Return with a failed exit code if there is no image
        if self.origImage == None:
            return -1
        
        # Tints the sprite by multiplication
        self.imageBlit.fill(rgb,special_flags=pygame.BLEND_RGB_MULT)

        return 1

    def blit(self,window:pygame.Surface,xy:tuple[int,int],dropShadow:tuple[int,int]=(0,0)):
        """
        Blits the targeted sprite onto the given surface. 
        The top left of the sprite will be positioned at the provided coordinate 
        pair PLUS the current SCRLX and SCRLY (x + SCRLX, y + SCRLY).
        Dropshadow argument controls the x and y offset of the dropshadow (0,0 does not render)
        """

        # Return with a failed exit code if there is no image
        if self.origImage == None:
            return -1
        
        # Blits the sprite using existing class variables and arguments
        newXy = (xy[0]+(SCRLX*self.scrollModif),
                 xy[1]+(SCRLY*self.scrollModif))
        self.imageBlitRect.x,self.imageBlitRect.y = newXy

        # Blit drop shadow before main Blit if required
        if dropShadow != (0,0):
            window.blit(self.dropshadow,(newXy[0]+dropShadow[0],newXy[1]+dropShadow[1]))

        window.blit(self.imageBlit,newXy)

        return 1
    
    def blit_center(self,window:pygame.Surface,xy:tuple[int,int],
                    dropShadow:tuple[int,int]=(0,0)):
        """
        Blits the targeted sprite onto the given surface. 
        The center of the sprite will be positioned at the provided 
        coordinate pair PLUS the current SCRLX and SCRLY (x + SCRLX, y + SCRLY).
        Dropshadow argument controls the x and y offset of the dropshadow (0,0 does not render)
        """

        # Return with a failed exit code if there is no image
        if self.origImage == None:
            return -1
        
        # Blits the sprite's center at the given coordinates
        newXy = ((xy[0]-self.imageBlitRect.w/2)+(SCRLX*self.scrollModif),
                                (xy[1]-self.imageBlitRect.h/2)+(SCRLY*self.scrollModif))
        self.imageBlitRect.x,self.imageBlitRect.y = newXy

        # Blit drop shadow before main Blit if required
        if dropShadow != (0,0):
            window.blit(self.dropshadow,(newXy[0]+dropShadow[0],newXy[1]+dropShadow[1]))

        window.blit(self.imageBlit,newXy)

        return 1
    
    def blit_pivot_center(self,window:pygame.Surface,
                          xy:tuple[int,int],
                          pivot:tuple[int,int],angle:float,
                          dropShadow:tuple[int,int]=(0,0)):
        """
        Blits the targeted sprite onto the given surface. 
        The center of the sprite will be positioned at the provided coordinate 
        pair PLUS the current SCRLX and SCRLY (x + SCRLX, y + SCRLY). The sprite 
        will be rotated around the coordinate point of the “pivot” argument by 
        COUNTERCLOCKWISE by the number of degrees represented by the “angle” argument.
        Dropshadow argument controls the x and y offset of the dropshadow (0,0 does not render)
        """

        # Return with a failed exit code if there is no image
        if self.origImage == None:
            return -1
        
        # Blit the image at the center, but changed around the pivot point
        newPoint = rotate(pivot,xy,angle)
        newXy = ((newPoint[0]-self.imageBlitRect.w/2)+(SCRLX*self.scrollModif),
                 (newPoint[1]-self.imageBlitRect.h/2)+(SCRLY*self.scrollModif))
        self.imageBlitRect.x,self.imageBlitRect.y = newXy

        # Blit drop shadow before main Blit if required
        if dropShadow != (0,0):
            window.blit(self.dropshadow,(newXy[0]+dropShadow[0],newXy[1]+dropShadow[1]))

        window.blit(self.imageBlit,(newXy[0],newXy[1]))
        
        return 1

    def blitFixed(self, window:pygame.Surface, dropShadow:tuple[int,int]=(0,0)):
        """
        Blits the targeted sprite onto the given surface. 
        The sprite will be positioned at its same previous coordinate 
        pair PLUS the current SCRLX and SCRLY (x + SCRLX, y + SCRLY).
        The dropshadow on this blit is instead a relative position to where it last was
        """

        # Blit the sprite on the given window at its previous coordinates
        window.blit(self.imageBlit, (self.imageBlitRect.x+(SCRLX*self.scrollModif), self.imageBlitRect.y+(SCRLY*self.scrollModif)))

        # Blit dropshadow
        if dropShadow != (0,0):
            window.blit(self.dropshadow, (self.imageBlitRect.x+(SCRLX*self.scrollModif),self.imageBlitRect.y+(SCRLY*self.scrollModif)))

        return 1
        
    def testColl(self,otherSprite,
                 pos:tuple[int,int]=None,
                 otherSpritePos:tuple[int,int]=None) -> bool:
        """
        Tests to see if the sprite collides with another sprite 
        (must be gregium.sprite type),
        if either pos argument is not supplied it will use the most 
        recent position blitted by the sprite as the position 
        (scroll is taken into account)
        """

        # Set pos values if none is given
        if pos != None:
            self.imageBlitRect.x,self.imageBlitRect.y = pos

        if otherSpritePos != None:
            otherSprite.imageBlitRect.x = otherSpritePos[0]
            otherSprite.imageBlitRect.y = otherSpritePos[1]

        # Run the test on each sprites rect
        if self.imageBlitRect.colliderect(otherSprite.imageBlitRect):

            return True
        
        # If the test fail (doesn't return true), return false instead
        return False
    
    def testCollR(self,*otherRects:pygame.Rect,
                  pos:tuple[int,int]=None) -> bool:
        """
        Tests to see if the sprite collides with any other rects 
        (must be pygame.Rect type)
        if the pos argument is not supplied it will use the most 
        recent position blitted by the sprite as the position 
        (scroll is taken into account)
        """

        # Set pos value if none is given
        if pos != None:
            self.imageBlitRect.x,self.imageBlitRect.y = pos

        # Do test on each rect
        for sprite in otherRects:

            if self.imageBlitRect.colliderect(sprite):

                return True
            
        # If all tests fail (never returns true), return false instead
        return False
    
    def updateSheet(self):
        """
        Updates the active sprite in the spritesheet. 
        This function should be used in the game loop and, 
        in most cases, should be updated every frame. 
        By changing the “sheetAnimMS” value it will change 
        how long (in ms) it takes for each frame of the sprite to update
        """

        # If the sheet is due for updating update it
        while self.sheetTick >= self.sheetAnimMS:
            self.sheetTick -= self.sheetAnimMS

            # Move the position of the pointer
            self.imageRect.x += self.origScaleM[0]

            # If pointer is
            if self.imageRect.x >= self.origScale[0]:
                self.imageRect.x = 0
                self.imageRect.y += self.origScaleM[1]

            # If pointer rect is below bottom of image reset it
            if self.imageRect.y >= self.origScale[1]:
                self.imageRect.y = 0

        # Increment Tick
        self.sheetTick += events.clockTime

    def scale(self,scale:float=None,width:float=None,height:float=None):
        """
        Scales the sprite by scale argument factor, 
        there should be only 1 input unless you 
        are changing both width and height 
        (don't do scale & width or scale & height it will not work correctly)
        If either width or height is blank it is assumed to use automatic
        and will scale based on the other changed value
        """

        # If scale factor is set multiple width & height by it
        if scale != None:
            self.width *= scale
            self.height *= scale

        # If only one of the width/height values are added 
        # calculate the value that should be multiplied 
        # to yield auto scaling
        elif (width == None) ^ (height == None):
            if width == None:
                self.width *= height/self.height
                self.height = height
            if height == None:
                self.height *= width/self.width
                self.width = width

        # If both values are given set each
        elif width != None and height != None:
            self.width = width
            self.height = height

        else:

            logging.error(f"No mode specified for {self}.scale method")
            return -1

        # Return success
        return 1
    
    def setFp(self,fp):
        self.fp = fp

        # Updates & loads new Fp
        try:
            self.origImage = pygame.image.load(self.fp).convert_alpha()
            self.width = self.origImage.get_width()
            self.height = self.origImage.get_height()
            self.rotation = 0
            self.inverted = False
            self.origScale = (self.width,self.height)

        except Exception as e:
            logging.error(f"{e}")
            self.origImage = None
            self.is_sheet = False

    def getFp(self):
        return self.fp

    filePath = property(getFp,setFp)
        

#### ---- ZIP HANDLER ---- ####
class ziphandle:
    
    @staticmethod
    def zipFolder(folder:str,zipPath:str) -> None:
        """
        Zips a folder without recursion
        """
        with zipfile.ZipFile(zipPath,"w") as zip:
            for file in os.listdir(folder):
                zip.write(folder+"\\"+file)

class EV_Initializer:
    def __init__(self):
        """
        Used only in gregium to set up events, there is no reason to 
        initialize this class outside of its initialization in gregium
        """

        # Setup events
        self.other = []
        self.quit = False
        self.mouseDown = False
        self.mouseUp = False
        self.mousePos = (0,0)
        self.keyInput = ""
        self.highlighted = True
        self.enter = False
        self.heldKeys = []
        self.clockTime = 0

    def clearEvent(self):
        """Resets all events to default values (use before event loop)"""

        # Clear all required events & update pygame mouse
        self.other = []
        self.quit = False
        self.mouseDown = False
        self.mouseUp = False
        self.mousePos = pygame.mouse.get_pos()
        self.enter = False
        self.clockTime = MAINCLOCK.get_time()

    def supplyEvent(self,event:pygame.event.Event):
        """
    Gives pygame events to gregium 
    (events supplied must be from pygame.event.get()
    from each for iteration, to put it simply use 
    <for event in pygame.event.get()> 
    and use this function with event as param)
    """
        
        global SELECTEDBUTTON

        # Match event to output
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.enter = True
                self.heldKeys.append(event.key)
            case pygame.KEYUP:
                self.heldKeys.remove(event.key)
            case pygame.QUIT:
                self.quit = True
            case pygame.MOUSEBUTTONDOWN:
                if SELECTEDBUTTON != None:
                    self.keyInput = ""
                SELECTEDBUTTON = None
                self.mouseDown = True
            case pygame.MOUSEBUTTONUP:
                self.mouseUp = True
            case pygame.WINDOWFOCUSGAINED:
                self.highlighted = True
            case pygame.WINDOWFOCUSLOST:
                self.highlighted = False
            case _:
                self.other.append(event.type)

# Initialize Events
events = EV_Initializer()

def on_press(key):
    """
    Module only function, binds all keypresses and events to a respective value
    """
    global events

    # Adds character if screen is highlighted
    if events.highlighted:
        try:
            events.keyInput += key.char

        # If it is a special character (backspace/space) that isn't a 
        # <char> then do respective action (backspace/space)
        except AttributeError:
            if key == keyboard.Key.backspace:
                events.keyInput = events.keyInput[:-1]
            elif key == keyboard.Key.space:
                events.keyInput += " "

def keyHandler():
    """
    Module only function, catches all key press events to be processed by on_press funciton
    """
    with keyboard.Listener(on_press=on_press) as listener:
        global listenerE
        listenerE = listener
        listener.join()

# Start running keyHandler
threading.Thread(target=keyHandler,args=()).start()
logging.info("KeyHandler Loaded")

#### ---- BUTTON HANDLER ---- ####

class button:
    def __init__(self,pos:tuple[float,float],
                 size:tuple[float,float],
                 color:tuple[int,int,int]=(255,255,255),
                 outline:tuple[int,int,int]=(0,0,0),
                 outlineThick:int=5,suppliedFont:Font=SPACEMONO,
                 text:str="",textCol:tuple[int,int,int]=(0,0,0),
                 textSize:int=25,
                 colorHighlight:tuple[int,int,int]=(200,200,200),
                 outlineHighlight:tuple[int,int,int]=(55,55,55),
                 align:str="topLeft",
                 rounding:int=0):
        """
        Generates a simple button. The following arguments can be provided to customize the button:
pos: a tuple that determines the (x, y) coordinates of where to place the top left corner of the button.
size: a tuple that determines the width and height of the button, respectively.
color: an RGB tuple that fills the button with the given RGB color. Defaults to (255, 255, 255), which is white.
outline: an RGB tuple that fills the button's border with the given RGB color. Has no effect if outlineThick is zero, i.e. there is no border.
outlineThick: an integer that determines the thickness of the button's border in pixels. Defaults to five (5) pixels.
suppliedFont: a Font object that should be set up with gregium's Font instantiator. Defaults to None, which will load the SpaceMono font.
text: a string that represents text inside the button. By default, there is no text.
textCol: an RGB tuple that specifies what color the text should be. Defaults to (0, 0, 0), which is black.
textSize: an integer that represents the size of the text in standard text size (1/72th of an inch equals 1 text size point).
colorHighlight: an RGB tuple that fills in the background of only the text with the provided RGB color. Defaults to (200, 200, 200), which is gray.
outlineHighlight: an RGB tuple that fills the outline of the text with the given RGB color. Defaults to (55, 55, 55), which is dark gray.
align: a string that specifies how the text should be aligned within the button.
rounding: follows general rules of pygame rect rounding, higher values yield more rounding
        """
        logging.info("Generating Button")

        # Initialize class variables
        self.pos = list(pos)
        self.align = align
        rectPos = alignPos(pos,align)
        self.rect = pygame.Rect(rectPos[0],rectPos[1],size[0],size[1])
        self.outlineCol = outline
        self.outlineColH = outlineHighlight
        self.color = color
        self.colorH = colorHighlight
        self.textCol = textCol
        self.text = text
        self.fontSize = textSize
        self.fontS = suppliedFont
        self.renderText = len(text)>0 and suppliedFont != None
        self.renderOutline = outlineThick > 0
        self.outlineThick = outlineThick
        self.hasClicked = False
        self.rounding = rounding

    def render(self):
        global BUTTONRENDERFUNC

        """
        Renders button with resulting int being
        0: no collision
        1: mouse collision
        2: mouse clicked on collision (pressed up and down)
        3: mouse pressed down on collision
        """

        # Initializing variables, checking for collision with current mouse position
        rtrn = 0
        rectPos = alignPos(self.pos,self.align)
        self.rect.x,self.rect.y = rectPos[0],rectPos[1]
        self.coll = self.rect.collidepoint(events.mousePos[0],events.mousePos[1])

        # Check if mouse is simply hovering over the react
        if self.coll and not self.hasClicked:
            if events.mouseDown:
                self.hasClicked = True
            
            rtrn = 1

        # Check if a click event is active
        if self.hasClicked:
            rtrn = 3

            # Check if the click is completed (mouse is pressed and released)
            if self.coll and events.mouseUp:
                rtrn = 2
                self.hasClicked = False
            elif events.mouseUp or not self.coll:
                self.hasClicked = False
        
        # Render Button
        BUTTONRENDERFUNC(self)

        # Finish function
        return rtrn

## -- DEFAULT BUTTON RENDER CODE -- ##
def defaultButtonRender(self:button):
    """
    The default rendering for a gregium button, 
    any alternatives must change BUTTONRENDERFUNC and have 1 
    argument (name can be anything) and will pass in the button class
    """
    # Draw an outline if a thickness was provided
    if self.coll and not self.hasClicked:
        pygame.draw.rect(WINDOW,self.colorH,self.rect,border_radius=self.rounding)
        if self.renderOutline:
            pygame.draw.rect(WINDOW,self.outlineColH,self.rect,self.outlineThick,border_radius=self.rounding)

    else:
        # Draw and render the rectangle onto the window
        pygame.draw.rect(WINDOW,self.color,self.rect,border_radius=self.rounding)
        

        # Draw an outline if a thickness was provided
        if self.renderOutline:
            pygame.draw.rect(WINDOW,self.outlineCol,self.rect,self.outlineThick,border_radius=self.rounding)

    # Render text if text and font were provided
    if self.renderText:
        self.fontS.blit_true_center(self.text,get_rect_center(self.rect),self.fontSize,fgcolor=self.textCol)

# Sets default render code
BUTTONRENDERFUNC = defaultButtonRender

class textBox:    
    def __init__(self,pos:tuple[float,float],size:tuple[float,float],color:tuple[int,int,int]=(255,255,255),outline:tuple[int,int,int]=(0,0,0),outlineThick:int=5,suppliedFont:Font=SPACEMONO,text:str="",textCol:tuple[int,int,int]=(0,0,0),textSize:int=25,colorHighlight:tuple[int,int,int]=(200,200,200),outlineHighlight:tuple[int,int,int]=(55,55,55),align:str="topLeft",maxTextLength:int=-1,rounding:int=0):
        """
        Documentation comes later, bad code comes first :thumbsup:
        """
        logging.info("Generating Textbox")
        if suppliedFont == None:
            raise SyntaxError("Must have font for textBox")
        
        # Make a button with same stats as supplied by user
        self.buttonMain = button(pos=pos,size=size,color=color,outline=outline,outlineThick=outlineThick,suppliedFont=suppliedFont,text=text,textCol=textCol,textSize=textSize,colorHighlight=colorHighlight,outlineHighlight=outlineHighlight,align=align,rounding=rounding)

        # Initialize other vars
        self.text = ""
        self.defaultText = text
        self.maxTextLength = maxTextLength

    def render(self):
        global SELECTEDBUTTON,events

        isSelected = SELECTEDBUTTON == self

        # Enforce max text length
        if len(self.text) > self.maxTextLength and self.maxTextLength > 0:
            self.text[:-(len(self.text)-self.maxTextLength)]

        # Set the text of the button (if no text has been inputted make default and if there is text add it to button)
        if self.text == "":
            if isSelected:
                self.buttonMain.text = f">{self.defaultText}<"
            else:
                self.buttonMain.text = self.defaultText
        else:
            if isSelected:
                self.buttonMain.text = f">{self.text}<"
            else:
                self.buttonMain.text = self.text

        # Render button and get clicks
        output = self.buttonMain.render()
        if output == 2:

            # Set the global selected button to this button when clicked
            SELECTEDBUTTON = self
            events.keyInput = self.text

        if isSelected:
            self.text = events.keyInput
            if events.enter:
                return "ENTER"

class alertBox:
    def __init__(self,suppliedFont:Font=SPACEMONO,buttons:tuple=("ok",),
                 title:str=None,
                 color:tuple[int,int,int]=(0,0,0),
                 outline:tuple[int,int,int]=(255,255,255),
                 textCol:tuple[int,int,int]=(255,255,255),
                 rounding:int=0):
        """
        suppliedFont: a gregium Font object that alters the font of alert text.
buttons: a tuple with as many strings as desired, strings will be converted to buttons and spread horizontally across the box, if the amount of buttons is only 1, use ('buttonText',) as opposed to ('buttonText') to prevent errors in generation. These buttons will be displayed on the alert as options to click on. An example of buttons that can be added are “Accept” or “Deny” buttons.
title: a string containing the title that will be displayed on the alert. The alert's title can be multi-line if \\n is put in the string. Defaults to None.
color: an RGB tuple that will fill the background color of the entire alert box with that RGB color. Defaults to (0, 0, 0), which is white.
outline: an RGB tuple of the outline of the alert box. Defaults to (255, 255, 255), which is black.
textCol: an RGB tuple that will change the text color using that RGB color. Defaults to (255, 255, 255), which is black.

        """
        logging.info("Generating AlertBox")

        # Initializing class variables
        self.buttons = buttons
        wc = get_window_center()
        self.color = color
        self.outline = outline
        self.box = pygame.Rect(wc[0]-350,wc[1]-250,700,500)
        self.buttonW = (660-(20*(len(buttons)-1)))/len(buttons)
        self.button = button((0,wc[1]+130),(self.buttonW,100),color,outline,text="Loading...",textCol=textCol,suppliedFont=suppliedFont,rounding=rounding)
        self.rounding = rounding
        self.buttonClickData = [False for x in range(len(buttons))]
        self.title = title
        self.font = suppliedFont

    def render(self):
        """
        Render an alert. Will return 0 on no buttons pressed. Returns the pressed button if one is clicked
        """

        # Prepare and draw the alert
        outP = 0
        wc = get_window_center()
        self.box.x,self.box.y = wc[0]-350,wc[1]-250
        pygame.draw.rect(WINDOW,self.color,self.box)
        pygame.draw.rect(WINDOW,self.outline,self.box,5)
        self.font.blit_center(self.title,(wc[0],wc[1]-200),size=40)

        # Loop through all given buttons
        for n, buttonN in enumerate(self.buttons):
            self.button.pos[0],self.button.pos[1] = (((self.buttonW+20)*n)+wc[0]-330),wc[1]+130
            self.button.text = buttonN
            self.button.hasClicked = self.buttonClickData[n]

            # If a button is clicked, output that button
            if self.button.render() == 2:
                outP = buttonN
            self.buttonClickData[n] = self.button.hasClicked

        return outP

def cmdParseSeg(segment:str,requestedType:str,min="N/A",max="N/A"):
    """Function for parsing strings, integers, floats, and json"""

    # Check for different types of the material to parse
    match requestedType:

        case "str":
            # Remove all double quotes in strings
            return segment.replace("\"","")

        case "int":
            try:
                # Make sure the integer is within the range of (min, max)
                segNum = int(segment)
                if min != "N/A":
                    if segNum < min:
                        return (6,"Value outside of accepted range")
                if max != "N/A":
                    if segNum > max:
                        return (6,"Value outside of accepted range")
                return segNum
            
            # Return with exit code 5 if argument was invalid
            except:
                return (5,"Could not make into an Integer")
            
        
        case "float":
            try:
                # Make sure the float is within the range of (min, max)
                segNum = float(segment)
                if min != "N/A":
                    if not segNum >= min:
                        return (6,"Value outside of accepted range")
                if max != "N/A":
                    if not segNum <= max:
                        return (6,"Value outside of accepted range")
                return segNum
            
            # Return with exit code 7 if argument was invalid
            except:
                return (7,"Could not make into an Float")
            
        case "json":
            try:
                # Return a parsed python object of the given segment
                return json.loads(segment)
            
            # Return with exit code 8 if something fails (usually an invalid json)
            except Exception as e:
                return (8,"Json error: "+e)
                
class CLI:
    def __init__(self,tree:dict={}):

        logging.info("CLI Generated")
        """
        Make easy command interpreters that can be used outside, or inside terminal
        """
        self.cmds = tree

    def addCmd(self,commandDict:dict):
        """
        add a new command! Syntax is as follows
        {"name":{"root":{"type":"*","var":"test","next":"foo"},"foo":{"type":"*","var":"test2","next":"etc"}}}

        *Types include, str, json, int, float, literal, func
        int & float can have min and max
        literal must have a list of outputs
        func must have a "run" variable instead of next and var and the "run" variable must have the function in it
        you can input multiple commands by having multiple in the furthest outside dict
        repeat commands will not get overwritten but will instead throw an error
        """
        for cmd in commandDict:
            self.cmds[cmd] = commandDict[cmd]

    def helpcmd(self,*args):
        """Generate a help message for using commands"""

        cmdList = ""

        # Return a specific help message for a given command
        if len(args) > 0:
            cmdD = self.cmds[args[0]]
            for cmdSeg in cmdD:
                cmdList += f"{cmdSeg}:{cmdD[cmdSeg]}\n"
            return f'{args[0]}:\n{cmdList}'
        
        # Return a list of every existing command
        for cmd in self.cmds:
            cmdList += f'{cmd}\n'
        return f'Commands:\n{cmdList}Type help (command) for specific syntax'
    
    def run(self,cmd:str) -> tuple[int,str]:
        """
        Read a full command from a string and output code (error, return) or (0, return) on success
        """

        # Initial split
        newCmd = cmd.split(" ")

        # Recombine strings and json
        cmdRun = []
        isOpenStr = False
        openJsonIndex = 0
        sectionComb = ""

        # Check each section
        for section in newCmd:

            # Add each section to the combined section
            sectionComb += section
            wasOpenStr = False

            # Check each letter of the section
            for ltr in section:

                # Check to see if all json
                if wasOpenStr and openJsonIndex == 0:
                    return (1,"String must end at parameter end") 
                
                # Check for '"' in the string
                if ltr == "\"":
                    isOpenStr = not isOpenStr

                    # If a string is closed, make sure it is noted
                    if not isOpenStr:
                        wasOpenStr = True

                # If a { is found outside a string, increase the json index by 1 (json depth)
                if ltr == "{" and not isOpenStr:
                    openJsonIndex += 1

                # If a } is found outside a string, increase the json index by 1 (json depth)
                if ltr == "}" and not isOpenStr:
                    openJsonIndex -= 1
                
                # Prevent negative open json
                if openJsonIndex < 0:
                    return (2,"Closed json before opening")
                
            # If there is nothing left in the parameter, add it to the sections of command to run
            if not isOpenStr and openJsonIndex == 0:
                cmdRun.append(sectionComb)
                sectionComb = ""
            else:

                # Otherwise continue to loop through
                sectionComb += " "

        # Raise error if json is still open
        if openJsonIndex > 0:
            return (3,"Not all json instances have been closed")
            
        # Run the help command (if applicable)
        if cmdRun[0] == "help":

            # Run help command with specific command (if applicable)
            if len(cmdRun) > 1:
                if cmdRun[1] in self.cmds:
                    return self.helpcmd(cmdRun[1])
                else:
                    return self.helpcmd()
            else:
                return self.helpcmd()

        # Check if command exists
        if cmdRun[0] in self.cmds:

            # Prepare variables for reading
            isReadingStart = False
            nextIndex = "root"
            cmd = self.cmds[cmdRun[0]]
            supArgs = {}

            # Check each parameter in the command
            for item in cmdRun:

                # Only start once the command name is passed
                if isReadingStart:

                    # Check which type of parameter it is (literal,func,or other)
                    match cmd[nextIndex]["type"]:

                        # If type is literal, change the next section based on which name is supplied
                        case "literal":
                            nextFound = cmd[nextIndex]["next"]

                            # If the entered output is invalid, raise an error
                            if item in nextFound:
                                nextIndex = item
                            else:
                                return (9,"Could not find next literal")
                            
                        # Is func is run without all arguments handle, raise "error"
                        case "func":
                            return (10,"Too many arguments")
                        
                        # Otherwise handle it with "cmdParseSeg" function
                        case _:

                            # Check for function min or max
                            relMin = "N/A"
                            relMax = "N/A"
                            if "min" in cmd[nextIndex]:
                                relMin = cmd[nextIndex]["min"]
                            if "max" in cmd[nextIndex]:
                                relMax = cmd[nextIndex]["max"]

                            # Get the parsed output
                            parsedSeg = cmdParseSeg(item,cmd[nextIndex]["type"],relMin,relMax)

                            # Add the output to the arguments for the final function
                            if type(parsedSeg) != tuple:
                                supArgs[cmd[nextIndex]["var"]] = parsedSeg

                                # Continue to the next section of the command
                                nextIndex = cmd[nextIndex]["next"]
                            else:
                                return parsedSeg
                isReadingStart = True

            # If function is not yet due to run, not enough arguments have been supplied
            if nextIndex != "func":
                return (11,"Not enough arguments")
            
            # Run the command's function and return
            return cmd[nextIndex]["run"](kwargs=supArgs)
                
        else:
            return (4, "Command not found")

def stop():
    logging.debug("Gregium Stopped\n\n")
    """Stops the gregium engine"""

    try:
        # Attempts to stop the key listener
        listenerE.stop()
    except:
        # The key handler has not been made and is not required to stop
        pass

    # Quit python
    os._exit(1)

logging.info("Gregium Fully Prepared")