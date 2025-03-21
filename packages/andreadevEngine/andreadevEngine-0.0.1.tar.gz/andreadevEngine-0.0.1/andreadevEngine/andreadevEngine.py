#Andrea Manzone
#This is AndreaDev Python Engine :)
#Version 1.0.0

import pygame, random, math, enum, os

#Initialize modules
pygame.init()
pygame.font.init()

#==================== UTILITY ====================

class Engine():
    """
    STATIC CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    The engine takes care of the application stuff.
    It runs the game loop.


    NOTES:
    Change the Engine's variables before calling SetUp function.


    ATTRIBUTES:

    STATIC:
    -ProjectTitle:                      string                  the name of your project (will appear in the window's caption)
    -ApplicationRunning:                bool                    controls the state of the application (if it's set to false, the game loop will not run and the application will be closed)
    -deltaTime:                         float                   time (in seconds) from the last frame
    -framesPerSeconds:                  int                     how many times per seconds your game loop is set to run
    -clock:                             pygame.time.Clock       the pygame's clock is used to set FPS and deltaTime
    -escapeKeyClosesApplication:        bool                    if True, pressing the escape key will cause the application to close

    INSTANCE:
    None


    FUNCTIONS:

    STATIC:
    -SetUp
    -GameLoop

    INSTANCE:
    None

    SYSTEM:
    -__UpdateScreen
    -__DrawScreen
    -__FillScreen
    -__Awake
    -__Start
    -__Update
    -__CheckIfQuit
    -__Exit

    """

    #Project name
    ProjectTitle = 'New Project' 

    #Application
    ApplicationRunning = False
    deltaTime = 0
    framesPerSeconds = 60
    clock = pygame.time.Clock()
    escapeKeyClosesApplication = True
 
    def SetUp():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Sets up the engine:
        -sets application state to Running
        -initializes the gameObject list used to keep track of active gameobjects
        -initializes the component list used to keep track of active components

        NOTES:
        This will NOT start the game loop, so you can do other setups before that.
        When you're ready, call Engine.GameLoop() to start it.
        This does not create the Screen. You have to create it by instantiating the Screen class.

        PARAMETERS:

        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        #application stuff
        Engine.ApplicationRunning = True

        #management of the gameobjects and components
        global GameObjects
        global Components 
        GameObjects = []
        Components = []

    def __UpdateScreen():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Updates the screen.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Screen._Screen__UpdateScreen()

    def __DrawScreen():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the draw() method on all the gameObjects and then on all the components.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
            gameObject.Draw()

        for component in Components:
            component.Draw()
        
    def __FillScreen():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Fills the screen and camera.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Screen._Screen__FillScreen()

        for camera in Camera.cameras:
            camera.Refresh()

    def __Awake():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the Awake() function on all the gameObjects and then on all the components.

        NOTES:
        This is called by the Engine.GameLoop() function before Engine.__Start(). 
        It is never called again.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
                gameObject.Awake()

        for component in Components:
            component.Awake()

    def __Start():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the Start() function on all the gameObjects and then on all the components.

        NOTES:
        This is called by the Engine.GameLoop() function after Engine.__Awake() and before the actual application loop (the infinite while loop) 
        It is never called again.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
                gameObject.Start()

        for component in Components:
            component.Start()

    def __Update():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the Update() function on all the gameObjects and then the ColliderUpdate() function on all the squareColliders and then the Update() function on all the components.

        NOTES:
        This is called by the Engine.GameLoop() function before Engine.__Start(). 
        It is never called again.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
                gameObject.Update()

        #Sort of 'Physics' update. Doing this makes calling the SquareCollider.Move method superficial
        for collider in SquareCollider.SquareColliders:
            collider.ColliderUpdate()

        for component in Components:
            component.Update()

    def __CheckIfQuit():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Checks when to close the application.

        NOTES:
        If Engine.escapeKeyClosesApplication is True, you can close the application using the escape key.
        If it is not True, you can't.

        This actually sets Engine.ApplicationRunning to False, so in Engine.GameLoop() is then called Engine.__Exit().

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        #Chiude l'applicazione con il tasto 'esc'
        if Engine.escapeKeyClosesApplication == True:
            if Input.escape_key_pressed:
                Engine.ApplicationRunning = False  
            
        #Chiude l'applicazione se si clicca la "x" sulla finestra
        if Input._Input__Quit:
            Engine.ApplicationRunning = False 
                
    def __Exit():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the OnExit() function on all the gameObjects, and then on all the components.
        Then calls pygame.quit().

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
                gameObject.OnExit()

        for component in Components:
            component.OnExit()

        pygame.quit()
              
    def GameLoop():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Starts the main loop of the application. 

        NOTES:
        Note that the execution will not exit this function as in this method there is an infinite loop, so any code after this function will be executed when this function is exited, so when you close the game.
        
        This is very important so here you find the function code to see how it works:
        
        def GameLoop():
            Engine.__Awake()
            Engine.__Start()

            while Engine.ApplicationRunning == True:
                #FPS
                Engine.clock.tick(Engine.framesPerSeconds)

                #DeltaTime in seconds (Engine.clock.get_time() returns it in milliseconds)
                Engine.deltaTime = Engine.clock.get_time() / 1000

                Input._Input__CheckInput()
                Engine.__Update()
                Input._Input__CancelOneFrameInput()
                Engine.__FillScreen()
                Engine.__DrawScreen()
                Engine.__UpdateScreen()
                Engine.__CheckIfQuit()

            Engine.__Exit()
            

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        Engine.__Awake()
        Engine.__Start()

        while Engine.ApplicationRunning == True:
            #FPS
            Engine.clock.tick(Engine.framesPerSeconds)

            #DeltaTime in seconds (Engine.clock.get_time() returns it in milliseconds)
            Engine.deltaTime = Engine.clock.get_time() / 1000

            Input._Input__CheckInput()
            Engine.__Update()
            Input._Input__CancelOneFrameInput()
            Engine.__FillScreen()
            Engine.__DrawScreen()
            Engine.__UpdateScreen()
            Engine.__CheckIfQuit()

        Engine.__Exit()

class Screen():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    The Screen class manages the screen (mind-blowing :O ).
    Creates the window of the application (often called 'screen' here).


    NOTES:
    The static variables are the same on the instance because anyway Pygame allows for only one window (I think because the windows or something related to it manages the events and inputs ecc.), so it's more comfortable to have them static too.
    The variables for width, height and size are for read-only use because the values of the screen are saved in them when it's created, but it does not depend from them.
    'screen' refers to the window of the application, because it is the screen of our game.


    ATTRIBUTES:

    STATIC:
    -width:                 int                 the width of the screen (in pixels)
    -height:                int                 the height of the screen (in pixels)
    -size:                  Vector2             the width and height of the screen (in pixels)
    -backgroundColor:       ColorRGB            the background color of the screen
    -screen:                pygame.Surface      represents the screen (the window of your project)
    -fillScreen:            bool                True means that the screen is refreshed with the background color, False means it isn't
    -updateScreen:          bool                True means that the screen is updated and the next frame will be drawn, False means basically freezing the screen


    INSTANCE:
    -width:                 int                 the width of the screen (in pixels)
    -height:                int                 the height of the screen (in pixels)
    -size:                  Vector2             the width and height of the screen (in pixels)
    -backgroundColor:       ColorRGB            the background color of the screen
    -screen:                pygame.Surface      represents the screen (the window of your project)
    -fillScreen:            bool                True means that the screen is refreshed with the background color, False means it isn't
    -updateScreen:          bool                True means that the screen is updated and the next frame will be drawn, False means basically freezing the screen


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__

    SYSTEM:
    -__FillScreen
    -__UpdateScreen

"""

    def __init__(self, width = 500, height = 500, backgroundColor = (0,0,0), fillScreen = True, updateScreen = True):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates the screen.

        NOTES:
        The default of backgroundColor is the tuple (0,0,0) and not a ColorRGB because this code is written before the ColorRGB class. 

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -width:                 int                 the width of the screen (in pixels)
        -height:                int                 the height of the screen (in pixels)
        -backgroundColor:       ColorRGB            the background color of the screen
        -fillScreen:            bool                True means that the screen is refreshed with the background color, False means it isn't
        -updateScreen:          bool                True means that the screen is updated and the next frame will be drawn, False means basically freezing the screen


        DEFAULTS OF OPTIONAL VALUES:
        -width:                 int                 500
        -height:                int                 500
        -backgroundColor:       tuple               (0,0,0)
        -fillScreen:            bool                True
        -updateScreen:          bool                True
        """

        Screen.width = width
        Screen.height = height
        Screen.backgroundColor = backgroundColor
        Screen.fillScreen = fillScreen
        Screen.updateScreen = updateScreen
        Screen.size = Vector2(Screen.width, Screen.height)
        Screen.screen = pygame.display.set_mode(Screen.size.Vector2ToTuple())
        self.width = width
        self.height = height
        self.backgroundColor = backgroundColor
        self.fillScreen = fillScreen
        self.updateScreen = updateScreen
        self.size = Vector2(self.width, self.height)
        self.screen = Screen.screen
        pygame.display.set_caption(Engine.ProjectTitle)

    def __FillScreen():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Fills the screen with the Screen.backgroundColor if Screen.fillScreen is True.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
        """

        if Screen.fillScreen == True:
            if type(Screen.backgroundColor) == ColorRGB:
                Screen.screen.fill(Screen.backgroundColor.color)
            else:
                Screen.backgroundColor = ColorRGB.ConvertToColorRGB(Screen.backgroundColor)
                if type(Screen.backgroundColor) == ColorRGB:
                    Screen.screen.fill(Screen.backgroundColor.color)
                else:
                    assert 1 == 0,  "TypeError: the parameter ‘Screen.backgroundColor' has to be type of 'ColorRGB’ or must be convertible to it (See ColorGB.ConvertToColorRGB() method)!"

    def __UpdateScreen():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the pygame.display.update() if Screen.updateScreen is True.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
        """

        if Screen.updateScreen == True:
            pygame.display.update()

class Mathf():
    """
    STATIC CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Some math functions.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    None


    FUNCTIONS:

    STATIC:
    -Clamp

    INSTANCE:
    None

    SYSTEM:
    None
    """

    def Clamp(number, min, max):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Limits the range of a value between two extremes and returns it.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -number:        int or float        the value to clamp
        -min:           int or float        the parameter 'number' must not be lower than this value
        -max:           int or float        the parameter 'number' must not be higher than this value

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if number < min:
            return min

        if number > max:
            return max

        else:
            return number

class Input():
    """
    STATIC CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Class that takes care of all the key inputs.

    Use keyName_key_pressed to verify if the key identified by the keyName is held down
    Use keyName_key_down to verify if the key identified by the keyName has been pressed down this frame
    Use keyName_key_up to verify if the key identified by the keyName has been released up this frame
    
    Use mouseButton_MouseClick_down to verify if the button identified by the mouseButton (left, right ecc.) has been pressed down this frame
    Use mouseButton_MouseClick_pressed to verify if the button identified by the mouseButton (left, right ecc.) is held down
    Use mouseButton_MouseClick_up to verify if the button identified by the mouseButton (left, right ecc.) has been released up this frame


    NOTES:
    If you can't find a specific key, there is a list of their names in the attributes section.


    ATTRIBUTES:

    STATIC:
    -backspace_key:                         int             the pygame keycode for this key
    -tab_key:                               int             the pygame keycode for this key
    -clear_key:                             int             the pygame keycode for this key
    -return_key:                            int             the pygame keycode for this key
    -pause_key:                             int             the pygame keycode for this key
    -escape_key:                            int             the pygame keycode for this key
    -space_key:                             int             the pygame keycode for this key
    -exclaimationMark_key:                  int             the pygame keycode for this key
    -quotedbl_key:                          int             the pygame keycode for this key
    -hashtag_key:                           int             the pygame keycode for this key
    -dollar_key:                            int             the pygame keycode for this key
    -eCommercial_key:                       int             the pygame keycode for this key
    -quote_key:                             int             the pygame keycode for this key
    -leftParentesis_key:                    int             the pygame keycode for this key
    -rightParentesis_key:                   int             the pygame keycode for this key
    -asterisk_key:                          int             the pygame keycode for this key
    -plus_key:                              int             the pygame keycode for this key
    -comma_key:                             int             the pygame keycode for this key
    -minus_key:                             int             the pygame keycode for this key
    -dot_key:                               int             the pygame keycode for this key
    -slash_key:                             int             the pygame keycode for this key
    -number0_key:                           int             the pygame keycode for this key
    -number1_key:                           int             the pygame keycode for this key
    -number2_key:                           int             the pygame keycode for this key
    -number3_key:                           int             the pygame keycode for this key
    -number4_key:                           int             the pygame keycode for this key
    -number5_key:                           int             the pygame keycode for this key
    -number6_key:                           int             the pygame keycode for this key
    -number7_key:                           int             the pygame keycode for this key
    -number8_key:                           int             the pygame keycode for this key
    -number9_key:                           int             the pygame keycode for this key
    -colon_key:                             int             the pygame keycode for this key
    -semicolon_key:                         int             the pygame keycode for this key
    -lessArrow_key:                         int             the pygame keycode for this key
    -equal_key:                             int             the pygame keycode for this key
    -greaterArrow_key:                      int             the pygame keycode for this key
    -questionMark_key:                      int             the pygame keycode for this key
    -at_key:                                int             the pygame keycode for this key
    -leftBracket_key:                       int             the pygame keycode for this key
    -backslash_key:                         int             the pygame keycode for this key
    -rightBracket_key:                      int             the pygame keycode for this key
    -caret_key:                             int             the pygame keycode for this key
    -underscore_key:                        int             the pygame keycode for this key
    -backquote_key:                         int             the pygame keycode for this key
    -a_key:                                 int             the pygame keycode for this key
    -b_key:                                 int             the pygame keycode for this key
    -c_key:                                 int             the pygame keycode for this key
    -d_key:                                 int             the pygame keycode for this key
    -e_key:                                 int             the pygame keycode for this key
    -f_key:                                 int             the pygame keycode for this key
    -g_key:                                 int             the pygame keycode for this key
    -h_key:                                 int             the pygame keycode for this key
    -i_key:                                 int             the pygame keycode for this key
    -j_key:                                 int             the pygame keycode for this key
    -k_key:                                 int             the pygame keycode for this key
    -l_key:                                 int             the pygame keycode for this key
    -m_key:                                 int             the pygame keycode for this key
    -n_key:                                 int             the pygame keycode for this key
    -o_key:                                 int             the pygame keycode for this key
    -p_key:                                 int             the pygame keycode for this key
    -q_key:                                 int             the pygame keycode for this key
    -r_key:                                 int             the pygame keycode for this key
    -s_key:                                 int             the pygame keycode for this key
    -t_key:                                 int             the pygame keycode for this key
    -u_key:                                 int             the pygame keycode for this key
    -v_key:                                 int             the pygame keycode for this key
    -w_key:                                 int             the pygame keycode for this key
    -x_key:                                 int             the pygame keycode for this key
    -y_key:                                 int             the pygame keycode for this key
    -z_key:                                 int             the pygame keycode for this key
    -delete_key:                            int             the pygame keycode for this key
    -keypad0_key:                           int             the pygame keycode for this key
    -keypad1_key:                           int             the pygame keycode for this key
    -keypad2_key:                           int             the pygame keycode for this key
    -keypad3_key:                           int             the pygame keycode for this key
    -keypad4_key:                           int             the pygame keycode for this key
    -keypad5_key:                           int             the pygame keycode for this key
    -keypad6_key:                           int             the pygame keycode for this key
    -keypad7_key:                           int             the pygame keycode for this key
    -keypad8_key:                           int             the pygame keycode for this key
    -keypad9_key:                           int             the pygame keycode for this key
    -keypadPeriod_key:                      int             the pygame keycode for this key
    -keypadDivide_key:                      int             the pygame keycode for this key
    -keypadMultiply_key:                    int             the pygame keycode for this key
    -keypadMinus_key:                       int             the pygame keycode for this key
    -keypadPlus_key:                        int             the pygame keycode for this key
    -keypadEnter_key:                       int             the pygame keycode for this key
    -keypadEquals_key:                      int             the pygame keycode for this key
    -keypadUp_key:                          int             the pygame keycode for this key
    -keypadDown_key:                        int             the pygame keycode for this key
    -keypadRight_key:                       int             the pygame keycode for this key
    -keypadLeft_key:                        int             the pygame keycode for this key
    -keypadInsert_key:                      int             the pygame keycode for this key
    -keypadHome_key:                        int             the pygame keycode for this key
    -keypadEnd_key:                         int             the pygame keycode for this key
    -keypadPageUp_key:                      int             the pygame keycode for this key
    -keypadPageDown_key:                    int             the pygame keycode for this key
    -F1_key:                                int             the pygame keycode for this key
    -F2_key:                                int             the pygame keycode for this key
    -F3_key:                                int             the pygame keycode for this key
    -F4_key:                                int             the pygame keycode for this key
    -F5_key:                                int             the pygame keycode for this key
    -F6_key:                                int             the pygame keycode for this key
    -F7_key:                                int             the pygame keycode for this key
    -F8_key:                                int             the pygame keycode for this key
    -F9_key:                                int             the pygame keycode for this key
    -F10_key:                               int             the pygame keycode for this key
    -F11_key:                               int             the pygame keycode for this key
    -F12_key:                               int             the pygame keycode for this key
    -F13_key:                               int             the pygame keycode for this key
    -F14_key:                               int             the pygame keycode for this key
    -F15_key:                               int             the pygame keycode for this key
    -lockNumber_key:                        int             the pygame keycode for this key
    -capsLock_key:                          int             the pygame keycode for this key
    -scrolLock_key:                         int             the pygame keycode for this key
    -rightShift_key:                        int             the pygame keycode for this key
    -leftShift_key:                         int             the pygame keycode for this key
    -rightControl_key:                      int             the pygame keycode for this key
    -leftControl_key:                       int             the pygame keycode for this key
    -rightAlt_key:                          int             the pygame keycode for this key
    -leftAlt_key:                           int             the pygame keycode for this key
    -rightMeta_key:                         int             the pygame keycode for this key
    -leftMeta_key:                          int             the pygame keycode for this key
    -leftWindows_key:                       int             the pygame keycode for this key
    -rightWindows_key:                      int             the pygame keycode for this key
    -mode_key:                              int             the pygame keycode for this key
    -help_key:                              int             the pygame keycode for this key
    -print_key:                             int             the pygame keycode for this key
    -sysreq_key:                            int             the pygame keycode for this key
    -break_key:                             int             the pygame keycode for this key
    -menu_key:                              int             the pygame keycode for this key
    -power_key:                             int             the pygame keycode for this key
    -euro_key:                              int             the pygame keycode for this key
    -androidBack_button:                    int             the pygame keycode for this button
    -left_mouseClick_event:                 int             the pygame keycode for this mouse button
    -right_mouseClick_event:                int             the pygame keycode for this mouse button
    -middle_mouseClick_event                int             the pygame keycode for this mouse button
    -scrollUp_mouseWheel_event:             int             the pygame keycode for this mouse button
    -scrollDown_mouseWheel_event:           int             the pygame keycode for this mouse button
    -right_mouseClick_tuple:                int             it is used to get the right mouse button when input is checked 
    -left_mouseClick_tuple:                 int             it is used to get the right mouse button when input is checked  
    -middle_mouseClick_tuple:               int             it is used to get the right mouse button when input is checked 
    -backspace_key_pressed:                 bool            if True it means the key is held down
    -tab_key_pressed:                       bool            if True it means the key is held down
    -clear_key_pressed:                     bool            if True it means the key is held down
    -return_key_pressed:                    bool            if True it means the key is held down
    -pause_key_pressed:                     bool            if True it means the key is held down
    -escape_key_pressed:                    bool            if True it means the key is held down
    -space_key_pressed:                     bool            if True it means the key is held down
    -exclaimationMark_key_pressed:          bool            if True it means the key is held down
    -quotedbl_key_pressed:                  bool            if True it means the key is held down
    -hashtag_key_pressed:                   bool            if True it means the key is held down
    -dollar_key_pressed:                    bool            if True it means the key is held down
    -eCommercial_key_pressed:               bool            if True it means the key is held down
    -quote_key_pressed:                     bool            if True it means the key is held down
    -leftParentesis_key_pressed:            bool            if True it means the key is held down
    -rightParentesis_key_pressed:           bool            if True it means the key is held down
    -asterisk_key_pressed:                  bool            if True it means the key is held down
    -plus_key_pressed:                      bool            if True it means the key is held down
    -comma_key_pressed:                     bool            if True it means the key is held down
    -minus_key_pressed:                     bool            if True it means the key is held down
    -dot_key_pressed:                       bool            if True it means the key is held down
    -slash_key_pressed:                     bool            if True it means the key is held down
    -number0_key_pressed:                   bool            if True it means the key is held down
    -number1_key_pressed:                   bool            if True it means the key is held down
    -number2_key_pressed:                   bool            if True it means the key is held down
    -number3_key_pressed:                   bool            if True it means the key is held down
    -number4_key_pressed:                   bool            if True it means the key is held down
    -number5_key_pressed:                   bool            if True it means the key is held down
    -number6_key_pressed:                   bool            if True it means the key is held down
    -number7_key_pressed:                   bool            if True it means the key is held down
    -number8_key_pressed:                   bool            if True it means the key is held down
    -number9_key_pressed:                   bool            if True it means the key is held down
    -colon_key_pressed:                     bool            if True it means the key is held down
    -semicolon_key_pressed:                 bool            if True it means the key is held down
    -lessArrow_key_pressed:                 bool            if True it means the key is held down
    -equal_key_pressed:                     bool            if True it means the key is held down
    -greaterArrow_key_pressed:              bool            if True it means the key is held down
    -questionMark_key_pressed:              bool            if True it means the key is held down
    -at_key_pressed:                        bool            if True it means the key is held down
    -leftBracket_key_pressed:               bool            if True it means the key is held down
    -backslash_key_pressed:                 bool            if True it means the key is held down
    -rightBracket_key_pressed:              bool            if True it means the key is held down
    -caret_key_pressed:                     bool            if True it means the key is held down
    -underscore_key_pressed:                bool            if True it means the key is held down
    -backquote_key_pressed:                 bool            if True it means the key is held down
    -a_key_pressed:                         bool            if True it means the key is held down
    -b_key_pressed:                         bool            if True it means the key is held down
    -c_key_pressed:                         bool            if True it means the key is held down
    -d_key_pressed:                         bool            if True it means the key is held down
    -e_key_pressed:                         bool            if True it means the key is held down
    -f_key_pressed:                         bool            if True it means the key is held down
    -g_key_pressed:                         bool            if True it means the key is held down
    -h_key_pressed:                         bool            if True it means the key is held down
    -i_key_pressed:                         bool            if True it means the key is held down
    -j_key_pressed:                         bool            if True it means the key is held down
    -k_key_pressed:                         bool            if True it means the key is held down
    -l_key_pressed:                         bool            if True it means the key is held down
    -m_key_pressed:                         bool            if True it means the key is held down
    -n_key_pressed:                         bool            if True it means the key is held down
    -o_key_pressed:                         bool            if True it means the key is held down
    -p_key_pressed:                         bool            if True it means the key is held down
    -q_key_pressed:                         bool            if True it means the key is held down
    -r_key_pressed:                         bool            if True it means the key is held down
    -s_key_pressed:                         bool            if True it means the key is held down
    -t_key_pressed:                         bool            if True it means the key is held down
    -u_key_pressed:                         bool            if True it means the key is held down
    -v_key_pressed:                         bool            if True it means the key is held down
    -w_key_pressed:                         bool            if True it means the key is held down
    -x_key_pressed:                         bool            if True it means the key is held down
    -y_key_pressed:                         bool            if True it means the key is held down
    -z_key_pressed:                         bool            if True it means the key is held down
    -delete_key_pressed:                    bool            if True it means the key is held down
    -keypad0_key_pressed:                   bool            if True it means the key is held down
    -keypad1_key_pressed:                   bool            if True it means the key is held down
    -keypad2_key_pressed:                   bool            if True it means the key is held down
    -keypad3_key_pressed:                   bool            if True it means the key is held down
    -keypad4_key_pressed:                   bool            if True it means the key is held down
    -keypad5_key_pressed:                   bool            if True it means the key is held down
    -keypad6_key_pressed:                   bool            if True it means the key is held down
    -keypad7_key_pressed:                   bool            if True it means the key is held down
    -keypad8_key_pressed:                   bool            if True it means the key is held down
    -keypad9_key_pressed:                   bool            if True it means the key is held down
    -keypadPeriod_key_pressed:              bool            if True it means the key is held down
    -keypadDivide_key_pressed:              bool            if True it means the key is held down
    -keypadMultiply_key_pressed:            bool            if True it means the key is held down
    -keypadMinus_key_pressed:               bool            if True it means the key is held down
    -keypadPlus_key_pressed:                bool            if True it means the key is held down
    -keypadEnter_key_pressed:               bool            if True it means the key is held down
    -keypadEquals_key_pressed:              bool            if True it means the key is held down
    -keypadUp_key_pressed:                  bool            if True it means the key is held down
    -keypadDown_key_pressed:                bool            if True it means the key is held down
    -keypadRight_key_pressed:               bool            if True it means the key is held down
    -keypadLeft_key_pressed:                bool            if True it means the key is held down
    -keypadInsert_key_pressed:              bool            if True it means the key is held down
    -keypadHome_key_pressed:                bool            if True it means the key is held down
    -keypadEnd_key_pressed:                 bool            if True it means the key is held down
    -keypadPageUp_key_pressed:              bool            if True it means the key is held down
    -keypadPageDown_key_pressed:            bool            if True it means the key is held down
    -F1_key_pressed:                        bool            if True it means the key is held down
    -F2_key_pressed:                        bool            if True it means the key is held down
    -F3_key_pressed:                        bool            if True it means the key is held down
    -F4_key_pressed:                        bool            if True it means the key is held down
    -F5_key_pressed:                        bool            if True it means the key is held down
    -F6_key_pressed:                        bool            if True it means the key is held down
    -F7_key_pressed:                        bool            if True it means the key is held down
    -F8_key_pressed:                        bool            if True it means the key is held down
    -F9_key_pressed:                        bool            if True it means the key is held down
    -F10_key_pressed:                       bool            if True it means the key is held down
    -F11_key_pressed:                       bool            if True it means the key is held down
    -F12_key_pressed:                       bool            if True it means the key is held down
    -F13_key_pressed:                       bool            if True it means the key is held down
    -F14_key_pressed:                       bool            if True it means the key is held down
    -F15_key_pressed:                       bool            if True it means the key is held down
    -lockNumber_key_pressed:                bool            if True it means the key is held down
    -capsLock_key_pressed:                  bool            if True it means the key is held down
    -scrolLock_key_pressed:                 bool            if True it means the key is held down
    -rightShift_key_pressed:                bool            if True it means the key is held down
    -leftShift_key_pressed:                 bool            if True it means the key is held down
    -rightControl_key_pressed:              bool            if True it means the key is held down
    -leftControl_key_pressed:               bool            if True it means the key is held down
    -rightAlt_key_pressed:                  bool            if True it means the key is held down
    -leftAlt_key_pressed:                   bool            if True it means the key is held down
    -rightMeta_key_pressed:                 bool            if True it means the key is held down
    -leftMeta_key_pressed:                  bool            if True it means the key is held down
    -leftWindows_key_pressed:               bool            if True it means the key is held down
    -rightWindows_key_pressed:              bool            if True it means the key is held down
    -mode_key_pressed:                      bool            if True it means the key is held down
    -help_key_pressed:                      bool            if True it means the key is held down
    -print_key_pressed:                     bool            if True it means the key is held down
    -sysreq_key_pressed:                    bool            if True it means the key is held down
    -break_key_pressed:                     bool            if True it means the key is held down
    -menu_key_pressed:                      bool            if True it means the key is held down
    -power_key_pressed:                     bool            if True it means the key is held down
    -euro_key_pressed:                      bool            if True it means the key is held down
    -androidBack_button_pressed:            bool            if True it means the button is held down
    -left_mouseClick_pressed:               bool            if True it means the button is held down
    -right_mouseClick_pressed:              bool            if True it means the button is held down
    -middle_mouseClick_pressed              bool            if True it means the button is held down
    -scrollUp_mouseWheel_pressed:           bool            if True it means the button is held down
    -scrollDown_mouseWheel_pressed:         bool            if True it means the button is held down
    -backspace_key_down:                    bool            if True it means the key has been pressed in this frame
    -tab_key_down:                          bool            if True it means the key has been pressed in this frame
    -clear_key_down:                        bool            if True it means the key has been pressed in this frame
    -return_key_down:                       bool            if True it means the key has been pressed in this frame
    -pause_key_down:                        bool            if True it means the key has been pressed in this frame
    -escape_key_down:                       bool            if True it means the key has been pressed in this frame
    -space_key_down:                        bool            if True it means the key has been pressed in this frame
    -exclaimationMark_key_down:             bool            if True it means the key has been pressed in this frame
    -quotedbl_key_down:                     bool            if True it means the key has been pressed in this frame
    -hashtag_key_down:                      bool            if True it means the key has been pressed in this frame
    -dollar_key_down:                       bool            if True it means the key has been pressed in this frame
    -eCommercial_key_down:                  bool            if True it means the key has been pressed in this frame
    -quote_key_down:                        bool            if True it means the key has been pressed in this frame
    -leftParentesis_key_down:               bool            if True it means the key has been pressed in this frame
    -rightParentesis_key_down:              bool            if True it means the key has been pressed in this frame
    -asterisk_key_down:                     bool            if True it means the key has been pressed in this frame
    -plus_key_down:                         bool            if True it means the key has been pressed in this frame
    -comma_key_down:                        bool            if True it means the key has been pressed in this frame
    -minus_key_down:                        bool            if True it means the key has been pressed in this frame
    -dot_key_down:                          bool            if True it means the key has been pressed in this frame
    -slash_key_down:                        bool            if True it means the key has been pressed in this frame
    -number0_key_down:                      bool            if True it means the key has been pressed in this frame
    -number1_key_down:                      bool            if True it means the key has been pressed in this frame
    -number2_key_down:                      bool            if True it means the key has been pressed in this frame
    -number3_key_down:                      bool            if True it means the key has been pressed in this frame
    -number4_key_down:                      bool            if True it means the key has been pressed in this frame
    -number5_key_down:                      bool            if True it means the key has been pressed in this frame
    -number6_key_down:                      bool            if True it means the key has been pressed in this frame
    -number7_key_down:                      bool            if True it means the key has been pressed in this frame
    -number8_key_down:                      bool            if True it means the key has been pressed in this frame
    -number9_key_down:                      bool            if True it means the key has been pressed in this frame
    -colon_key_down:                        bool            if True it means the key has been pressed in this frame
    -semicolon_key_down:                    bool            if True it means the key has been pressed in this frame
    -lessArrow_key_down:                    bool            if True it means the key has been pressed in this frame
    -equal_key_down:                        bool            if True it means the key has been pressed in this frame
    -greaterArrow_key_down:                 bool            if True it means the key has been pressed in this frame
    -questionMark_key_down:                 bool            if True it means the key has been pressed in this frame
    -at_key_down:                           bool            if True it means the key has been pressed in this frame
    -leftBracket_key_down:                  bool            if True it means the key has been pressed in this frame
    -backslash_key_down:                    bool            if True it means the key has been pressed in this frame
    -rightBracket_key_down:                 bool            if True it means the key has been pressed in this frame
    -caret_key_down:                        bool            if True it means the key has been pressed in this frame
    -underscore_key_down:                   bool            if True it means the key has been pressed in this frame
    -backquote_key_down:                    bool            if True it means the key has been pressed in this frame
    -a_key_down:                            bool            if True it means the key has been pressed in this frame
    -b_key_down:                            bool            if True it means the key has been pressed in this frame
    -c_key_down:                            bool            if True it means the key has been pressed in this frame
    -d_key_down:                            bool            if True it means the key has been pressed in this frame
    -e_key_down:                            bool            if True it means the key has been pressed in this frame
    -f_key_down:                            bool            if True it means the key has been pressed in this frame
    -g_key_down:                            bool            if True it means the key has been pressed in this frame
    -h_key_down:                            bool            if True it means the key has been pressed in this frame
    -i_key_down:                            bool            if True it means the key has been pressed in this frame
    -j_key_down:                            bool            if True it means the key has been pressed in this frame
    -k_key_down:                            bool            if True it means the key has been pressed in this frame
    -l_key_down:                            bool            if True it means the key has been pressed in this frame
    -m_key_down:                            bool            if True it means the key has been pressed in this frame
    -n_key_down:                            bool            if True it means the key has been pressed in this frame
    -o_key_down:                            bool            if True it means the key has been pressed in this frame
    -p_key_down:                            bool            if True it means the key has been pressed in this frame
    -q_key_down:                            bool            if True it means the key has been pressed in this frame
    -r_key_down:                            bool            if True it means the key has been pressed in this frame
    -s_key_down:                            bool            if True it means the key has been pressed in this frame
    -t_key_down:                            bool            if True it means the key has been pressed in this frame
    -u_key_down:                            bool            if True it means the key has been pressed in this frame
    -v_key_down:                            bool            if True it means the key has been pressed in this frame
    -w_key_down:                            bool            if True it means the key has been pressed in this frame
    -x_key_down:                            bool            if True it means the key has been pressed in this frame
    -y_key_down:                            bool            if True it means the key has been pressed in this frame
    -z_key_down:                            bool            if True it means the key has been pressed in this frame
    -delete_key_down:                       bool            if True it means the key has been pressed in this frame
    -keypad0_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad1_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad2_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad3_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad4_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad5_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad6_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad7_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad8_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypad9_key_down:                      bool            if True it means the key has been pressed in this frame
    -keypadPeriod_key_down:                 bool            if True it means the key has been pressed in this frame
    -keypadDivide_key_down:                 bool            if True it means the key has been pressed in this frame
    -keypadMultiply_key_down:               bool            if True it means the key has been pressed in this frame
    -keypadMinus_key_down:                  bool            if True it means the key has been pressed in this frame
    -keypadPlus_key_down:                   bool            if True it means the key has been pressed in this frame
    -keypadEnter_key_down:                  bool            if True it means the key has been pressed in this frame
    -keypadEquals_key_down:                 bool            if True it means the key has been pressed in this frame
    -keypadUp_key_down:                     bool            if True it means the key has been pressed in this frame
    -keypadDown_key_down:                   bool            if True it means the key has been pressed in this frame
    -keypadRight_key_down:                  bool            if True it means the key has been pressed in this frame
    -keypadLeft_key_down:                   bool            if True it means the key has been pressed in this frame
    -keypadInsert_key_down:                 bool            if True it means the key has been pressed in this frame
    -keypadHome_key_down:                   bool            if True it means the key has been pressed in this frame
    -keypadEnd_key_down:                    bool            if True it means the key has been pressed in this frame
    -keypadPageUp_key_down:                 bool            if True it means the key has been pressed in this frame
    -keypadPageDown_key_down:               bool            if True it means the key has been pressed in this frame
    -F1_key_down:                           bool            if True it means the key has been pressed in this frame
    -F2_key_down:                           bool            if True it means the key has been pressed in this frame
    -F3_key_down:                           bool            if True it means the key has been pressed in this frame
    -F4_key_down:                           bool            if True it means the key has been pressed in this frame
    -F5_key_down:                           bool            if True it means the key has been pressed in this frame
    -F6_key_down:                           bool            if True it means the key has been pressed in this frame
    -F7_key_down:                           bool            if True it means the key has been pressed in this frame
    -F8_key_down:                           bool            if True it means the key has been pressed in this frame
    -F9_key_down:                           bool            if True it means the key has been pressed in this frame
    -F10_key_down:                          bool            if True it means the key has been pressed in this frame
    -F11_key_down:                          bool            if True it means the key has been pressed in this frame
    -F12_key_down:                          bool            if True it means the key has been pressed in this frame
    -F13_key_down:                          bool            if True it means the key has been pressed in this frame
    -F14_key_down:                          bool            if True it means the key has been pressed in this frame
    -F15_key_down:                          bool            if True it means the key has been pressed in this frame
    -lockNumber_key_down:                   bool            if True it means the key has been pressed in this frame
    -capsLock_key_down:                     bool            if True it means the key has been pressed in this frame
    -scrolLock_key_down:                    bool            if True it means the key has been pressed in this frame
    -rightShift_key_down:                   bool            if True it means the key has been pressed in this frame
    -leftShift_key_down:                    bool            if True it means the key has been pressed in this frame
    -rightControl_key_down:                 bool            if True it means the key has been pressed in this frame
    -leftControl_key_down:                  bool            if True it means the key has been pressed in this frame
    -rightAlt_key_down:                     bool            if True it means the key has been pressed in this frame
    -leftAlt_key_down:                      bool            if True it means the key has been pressed in this frame
    -rightMeta_key_down:                    bool            if True it means the key has been pressed in this frame
    -leftMeta_key_down:                     bool            if True it means the key has been pressed in this frame
    -leftWindows_key_down:                  bool            if True it means the key has been pressed in this frame
    -rightWindows_key_down:                 bool            if True it means the key has been pressed in this frame
    -mode_key_down:                         bool            if True it means the key has been pressed in this frame
    -help_key_down:                         bool            if True it means the key has been pressed in this frame
    -print_key_down:                        bool            if True it means the key has been pressed in this frame
    -sysreq_key_down:                       bool            if True it means the key has been pressed in this frame
    -break_key_down:                        bool            if True it means the key has been pressed in this frame
    -menu_key_down:                         bool            if True it means the key has been pressed in this frame
    -power_key_down:                        bool            if True it means the key has been pressed in this frame
    -euro_key_down:                         bool            if True it means the key has been pressed in this frame
    -androidBack_button_down:               bool            if True it means the button has been pressed in this frame
    -left_mouseClick_down:                  bool            if True it means the button has been pressed in this frame
    -right_mouseClick_down:                 bool            if True it means the button has been pressed in this frame
    -middle_mouseClick_down                 bool            if True it means the button has been pressed in this frame
    -scrollUp_mouseWheel_down:              bool            if True it means the button has been pressed in this frame
    -scrollDown_mouseWheel_down:            bool            if True it means the button has been pressed in this frame
    -backspace_key_up:                      bool            if True it means the key has been released in this frame
    -tab_key_up:                            bool            if True it means the key has been released in this frame
    -clear_key_up:                          bool            if True it means the key has been released in this frame
    -return_key_up:                         bool            if True it means the key has been released in this frame
    -pause_key_up:                          bool            if True it means the key has been released in this frame
    -escape_key_up:                         bool            if True it means the key has been released in this frame
    -space_key_up:                          bool            if True it means the key has been released in this frame
    -exclaimationMark_key_up:               bool            if True it means the key has been released in this frame
    -quotedbl_key_up:                       bool            if True it means the key has been released in this frame
    -hashtag_key_up:                        bool            if True it means the key has been released in this frame
    -dollar_key_up:                         bool            if True it means the key has been released in this frame
    -eCommercial_key_up:                    bool            if True it means the key has been released in this frame
    -quote_key_up:                          bool            if True it means the key has been released in this frame
    -leftParentesis_key_up:                 bool            if True it means the key has been released in this frame
    -rightParentesis_key_up:                bool            if True it means the key has been released in this frame
    -asterisk_key_up:                       bool            if True it means the key has been released in this frame
    -plus_key_up:                           bool            if True it means the key has been released in this frame
    -comma_key_up:                          bool            if True it means the key has been released in this frame
    -minus_key_up:                          bool            if True it means the key has been released in this frame
    -dot_key_up:                            bool            if True it means the key has been released in this frame
    -slash_key_up:                          bool            if True it means the key has been released in this frame
    -number0_key_up:                        bool            if True it means the key has been released in this frame
    -number1_key_up:                        bool            if True it means the key has been released in this frame
    -number2_key_up:                        bool            if True it means the key has been released in this frame
    -number3_key_up:                        bool            if True it means the key has been released in this frame
    -number4_key_up:                        bool            if True it means the key has been released in this frame
    -number5_key_up:                        bool            if True it means the key has been released in this frame
    -number6_key_up:                        bool            if True it means the key has been released in this frame
    -number7_key_up:                        bool            if True it means the key has been released in this frame
    -number8_key_up:                        bool            if True it means the key has been released in this frame
    -number9_key_up:                        bool            if True it means the key has been released in this frame
    -colon_key_up:                          bool            if True it means the key has been released in this frame
    -semicolon_key_up:                      bool            if True it means the key has been released in this frame
    -lessArrow_key_up:                      bool            if True it means the key has been released in this frame
    -equal_key_up:                          bool            if True it means the key has been released in this frame
    -greaterArrow_key_up:                   bool            if True it means the key has been released in this frame
    -questionMark_key_up:                   bool            if True it means the key has been released in this frame
    -at_key_up:                             bool            if True it means the key has been released in this frame
    -leftBracket_key_up:                    bool            if True it means the key has been released in this frame
    -backslash_key_up:                      bool            if True it means the key has been released in this frame
    -rightBracket_key_up:                   bool            if True it means the key has been released in this frame
    -caret_key_up:                          bool            if True it means the key has been released in this frame
    -underscore_key_up:                     bool            if True it means the key has been released in this frame
    -backquote_key_up:                      bool            if True it means the key has been released in this frame
    -a_key_up:                              bool            if True it means the key has been released in this frame
    -b_key_up:                              bool            if True it means the key has been released in this frame
    -c_key_up:                              bool            if True it means the key has been released in this frame
    -d_key_up:                              bool            if True it means the key has been released in this frame
    -e_key_up:                              bool            if True it means the key has been released in this frame
    -f_key_up:                              bool            if True it means the key has been released in this frame
    -g_key_up:                              bool            if True it means the key has been released in this frame
    -h_key_up:                              bool            if True it means the key has been released in this frame
    -i_key_up:                              bool            if True it means the key has been released in this frame
    -j_key_up:                              bool            if True it means the key has been released in this frame
    -k_key_up:                              bool            if True it means the key has been released in this frame
    -l_key_up:                              bool            if True it means the key has been released in this frame
    -m_key_up:                              bool            if True it means the key has been released in this frame
    -n_key_up:                              bool            if True it means the key has been released in this frame
    -o_key_up:                              bool            if True it means the key has been released in this frame
    -p_key_up:                              bool            if True it means the key has been released in this frame
    -q_key_up:                              bool            if True it means the key has been released in this frame
    -r_key_up:                              bool            if True it means the key has been released in this frame
    -s_key_up:                              bool            if True it means the key has been released in this frame
    -t_key_up:                              bool            if True it means the key has been released in this frame
    -u_key_up:                              bool            if True it means the key has been released in this frame
    -v_key_up:                              bool            if True it means the key has been released in this frame
    -w_key_up:                              bool            if True it means the key has been released in this frame
    -x_key_up:                              bool            if True it means the key has been released in this frame
    -y_key_up:                              bool            if True it means the key has been released in this frame
    -z_key_up:                              bool            if True it means the key has been released in this frame
    -delete_key_up:                         bool            if True it means the key has been released in this frame
    -keypad0_key_up:                        bool            if True it means the key has been released in this frame
    -keypad1_key_up:                        bool            if True it means the key has been released in this frame
    -keypad2_key_up:                        bool            if True it means the key has been released in this frame
    -keypad3_key_up:                        bool            if True it means the key has been released in this frame
    -keypad4_key_up:                        bool            if True it means the key has been released in this frame
    -keypad5_key_up:                        bool            if True it means the key has been released in this frame
    -keypad6_key_up:                        bool            if True it means the key has been released in this frame
    -keypad7_key_up:                        bool            if True it means the key has been released in this frame
    -keypad8_key_up:                        bool            if True it means the key has been released in this frame
    -keypad9_key_up:                        bool            if True it means the key has been released in this frame
    -keypadPeriod_key_up:                   bool            if True it means the key has been released in this frame
    -keypadDivide_key_up:                   bool            if True it means the key has been released in this frame
    -keypadMultiply_key_up:                 bool            if True it means the key has been released in this frame
    -keypadMinus_key_up:                    bool            if True it means the key has been released in this frame
    -keypadPlus_key_up:                     bool            if True it means the key has been released in this frame
    -keypadEnter_key_up:                    bool            if True it means the key has been released in this frame
    -keypadEquals_key_up:                   bool            if True it means the key has been released in this frame
    -keypadUp_key_up:                       bool            if True it means the key has been released in this frame
    -keypadDown_key_up:                     bool            if True it means the key has been released in this frame
    -keypadRight_key_up:                    bool            if True it means the key has been released in this frame
    -keypadLeft_key_up:                     bool            if True it means the key has been released in this frame
    -keypadInsert_key_up:                   bool            if True it means the key has been released in this frame
    -keypadHome_key_up:                     bool            if True it means the key has been released in this frame
    -keypadEnd_key_up:                      bool            if True it means the key has been released in this frame
    -keypadPageUp_key_up:                   bool            if True it means the key has been released in this frame
    -keypadPageDown_key_up:                 bool            if True it means the key has been released in this frame
    -F1_key_up:                             bool            if True it means the key has been released in this frame
    -F2_key_up:                             bool            if True it means the key has been released in this frame
    -F3_key_up:                             bool            if True it means the key has been released in this frame
    -F4_key_up:                             bool            if True it means the key has been released in this frame
    -F5_key_up:                             bool            if True it means the key has been released in this frame
    -F6_key_up:                             bool            if True it means the key has been released in this frame
    -F7_key_up:                             bool            if True it means the key has been released in this frame
    -F8_key_up:                             bool            if True it means the key has been released in this frame
    -F9_key_up:                             bool            if True it means the key has been released in this frame
    -F10_key_up:                            bool            if True it means the key has been released in this frame
    -F11_key_up:                            bool            if True it means the key has been released in this frame
    -F12_key_up:                            bool            if True it means the key has been released in this frame
    -F13_key_up:                            bool            if True it means the key has been released in this frame
    -F14_key_up:                            bool            if True it means the key has been released in this frame
    -F15_key_up:                            bool            if True it means the key has been released in this frame
    -lockNumber_key_up:                     bool            if True it means the key has been released in this frame
    -capsLock_key_up:                       bool            if True it means the key has been released in this frame
    -scrolLock_key_up:                      bool            if True it means the key has been released in this frame
    -rightShift_key_up:                     bool            if True it means the key has been released in this frame
    -leftShift_key_up:                      bool            if True it means the key has been released in this frame
    -rightControl_key_up:                   bool            if True it means the key has been released in this frame
    -leftControl_key_up:                    bool            if True it means the key has been released in this frame
    -rightAlt_key_up:                       bool            if True it means the key has been released in this frame
    -leftAlt_key_up:                        bool            if True it means the key has been released in this frame
    -rightMeta_key_up:                      bool            if True it means the key has been released in this frame
    -leftMeta_key_up:                       bool            if True it means the key has been released in this frame
    -leftWindows_key_up:                    bool            if True it means the key has been released in this frame
    -rightWindows_key_up:                   bool            if True it means the key has been released in this frame
    -mode_key_up:                           bool            if True it means the key has been released in this frame
    -help_key_up:                           bool            if True it means the key has been released in this frame
    -print_key_up:                          bool            if True it means the key has been released in this frame
    -sysreq_key_up:                         bool            if True it means the key has been released in this frame
    -break_key_up:                          bool            if True it means the key has been released in this frame
    -menu_key_up:                           bool            if True it means the key has been released in this frame
    -power_key_up:                          bool            if True it means the key has been released in this frame
    -euro_key_up:                           bool            if True it means the key has been released in this frame
    -androidBack_button_up:                 bool            if True it means the button has been released in this frame
    -left_mouseClick_up:                    bool            if True it means the button has been released in this frame
    -right_mouseClick_up:                   bool            if True it means the button has been released in this frame
    -middle_mouseClick_up                   bool            if True it means the button has been released in this frame
    -scrollUp_mouseWheel_up:                bool            if True it means the button has been released in this frame
    -scrollDown_mouseWheel_up:              bool            if True it means the button has been released in this frame
    -__Quit:                                bool            if True it means that the quit event has occurred. Usually it is the red cross to close the application
    -mouse_position:                        Vector2         the position of the mouse on the screen 
    
    INSTANCE:
    None


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    None

    SYSTEM:
    -__CheckInput
    -__CheckDownInput
    -__CheckPressedInput
    -__CheckUpInput
    -__CheckQuit
    -__CheckKeysPressedInput
    -__CheckKeysDownInput
    -__CheckKeysUpInput
    -__CheckMousePressedInput
    -__CheckMouseDownInput
    -__CheckMouseUpInput
    -__GetMousePosition
    -__CancelOneFrameInput

    """

    
    #Yes, all of this because I think it's more readable and I like it in this way. 100% commitement and useless extra code :)
    

    #ALL the key and mouse costants of pygame
    #region
    #Keys
    backspace_key = pygame.K_BACKSPACE
    tab_key = pygame.K_TAB
    clear_key = pygame.K_CLEAR
    return_key = pygame.K_RETURN
    pause_key = pygame.K_PAUSE  
    escape_key = pygame.K_ESCAPE
    space_key = pygame.K_SPACE
    exclaimationMark_key = pygame.K_EXCLAIM 
    quotedbl_key = pygame.K_QUOTEDBL
    hashtag_key = pygame.K_HASH
    dollar_key = pygame.K_DOLLAR
    eCommercial_key = pygame.K_AMPERSAND
    quote_key = pygame.K_QUOTE
    leftParentesis_key = pygame.K_LEFTPAREN
    rightParentesis_key = pygame.K_RIGHTPAREN
    asterisk_key = pygame.K_ASTERISK
    plus_key = pygame.K_PLUS 
    comma_key = pygame.K_COMMA 
    minus_key = pygame.K_MINUS 
    dot_key = pygame.K_PERIOD
    slash_key = pygame.K_SLASH
    number0_key = pygame.K_0
    number1_key = pygame.K_1
    number2_key = pygame.K_2
    number3_key = pygame.K_3
    number4_key = pygame.K_4
    number5_key = pygame.K_5
    number6_key = pygame.K_6
    number7_key = pygame.K_7
    number8_key = pygame.K_8
    number9_key = pygame.K_9
    
    colon_key = pygame.K_COLON
    semicolon_key = pygame.K_SEMICOLON
    lessArrow_key = pygame.K_LESS
    equal_key = pygame.K_EQUALS
    greaterArrow_key = pygame.K_GREATER
    questionMark_key = pygame.K_QUESTION 
    at_key = pygame.K_AT
    leftBracket_key = pygame.K_LEFTBRACKET
    backslash_key = pygame.K_BACKSLASH
    rightBracket_key = pygame.K_RIGHTBRACKET
    caret_key = pygame.K_CARET
    underscore_key = pygame.K_UNDERSCORE
    backquote_key = pygame.K_BACKQUOTE
    
    a_key = pygame.K_a
    b_key = pygame.K_b
    c_key = pygame.K_c
    d_key = pygame.K_d
    e_key = pygame.K_e
    f_key = pygame.K_f
    g_key = pygame.K_g
    h_key = pygame.K_h
    i_key = pygame.K_i
    j_key = pygame.K_j
    k_key = pygame.K_k
    l_key = pygame.K_l
    m_key = pygame.K_m
    n_key = pygame.K_n
    o_key = pygame.K_o
    p_key = pygame.K_p
    q_key = pygame.K_q
    r_key = pygame.K_r
    s_key = pygame.K_s
    t_key = pygame.K_t
    u_key = pygame.K_u
    v_key = pygame.K_v
    w_key = pygame.K_w
    x_key = pygame.K_x
    y_key = pygame.K_y
    z_key = pygame.K_z
    
    delete_key = pygame.K_DELETE 
    keypad0_key = pygame.K_KP0
    keypad1_key = pygame.K_KP1
    keypad2_key = pygame.K_KP2
    keypad3_key = pygame.K_KP3
    keypad4_key = pygame.K_KP4
    keypad5_key = pygame.K_KP5
    keypad6_key = pygame.K_KP6
    keypad7_key = pygame.K_KP7
    keypad8_key = pygame.K_KP8
    keypad9_key = pygame.K_KP9
    keypadPeriod_key = pygame.K_KP_PERIOD
    keypadDivide_key = pygame.K_KP_DIVIDE
    keypadMultiply_key = pygame.K_KP_MULTIPLY
    keypadMinus_key = pygame.K_KP_MINUS
    keypadPlus_key = pygame.K_KP_PLUS
    keypadEnter_key = pygame.K_KP_ENTER
    keypadEquals_key = pygame.K_KP_EQUALS
    keypadUp_key = pygame.K_UP
    keypadDown_key = pygame.K_DOWN
    keypadRight_key = pygame.K_RIGHT
    keypadLeft_key = pygame.K_LEFT
    keypadInsert_key = pygame.K_INSERT
    keypadHome_key = pygame.K_HOME
    keypadEnd_key = pygame.K_END
    keypadPageUp_key = pygame.K_PAGEUP
    keypadPageDown_key = pygame.K_PAGEDOWN
    
    F1_key = pygame.K_F1
    F2_key = pygame.K_F2
    F3_key = pygame.K_F3
    F4_key = pygame.K_F4
    F5_key = pygame.K_F5
    F6_key = pygame.K_F6
    F7_key = pygame.K_F7
    F8_key = pygame.K_F8
    F9_key = pygame.K_F9
    F10_key = pygame.K_F10
    F11_key = pygame.K_F11
    F12_key = pygame.K_F12
    F13_key = pygame.K_F13
    F14_key = pygame.K_F14
    F15_key = pygame.K_F15

    lockNumber_key = pygame.K_NUMLOCK
    capsLock_key = pygame.K_CAPSLOCK
    scrolLock_key = pygame.K_SCROLLOCK
    rightShift_key = pygame.K_RSHIFT
    leftShift_key = pygame.K_LSHIFT
    rightControl_key = pygame.K_RCTRL
    leftControl_key = pygame.K_LCTRL
    rightAlt_key = pygame.K_RALT
    leftAlt_key = pygame.K_LALT
    rightMeta_key = pygame.K_RMETA
    leftMeta_key = pygame.K_LMETA
    leftWindows_key = pygame.K_LSUPER
    rightWindows_key = pygame.K_RSUPER
    mode_key = pygame.K_MODE
    help_key = pygame.K_HELP
    print_key = pygame.K_PRINT
    sysreq_key = pygame.K_SYSREQ
    break_key = pygame.K_BREAK
    menu_key = pygame.K_MENU
    power_key = pygame.K_POWER 
    euro_key = pygame.K_EURO
    androidBack_button = pygame.K_AC_BACK

    #Mouse
    left_mouseClick_event = 1
    right_mouseClick_event = 2
    middle_mouseClick_event = 3
    scrollUp_mouseWheel_event = 4
    scrollDown_mouseWheel_event = 5

    left_mouseClick_tuple = 0
    right_mouseClick_tuple = 1
    middle_mouseClick_tuple = 2

    mouse_position = (0,0)

    #endregion

    #bool used to check if a key or mouse button is hold down
    #region
    #Keys
    backspace_key_pressed = False
    tab_key_pressed = False
    clear_key_pressed = False
    return_key_pressed = False
    pause_key_pressed = False
    escape_key_pressed = False
    space_key_pressed = False
    exclaimationMark_key_pressed = False
    quotedbl_key_pressed = False
    hashtag_key_pressed = False
    dollar_key_pressed = False
    eCommercial_key_pressed = False
    quote_key_pressed = False
    leftParentesis_key_pressed = False
    rightParentesis_key_pressed = False
    asterisk_key_pressed = False
    plus_key_pressed = False 
    comma_key_pressed = False
    minus_key_pressed = False
    dot_key_pressed = False
    slash_key_pressed = False
    
    number0_key_pressed = False
    number1_key_pressed = False
    number2_key_pressed = False
    number3_key_pressed = False
    number4_key_pressed = False
    number5_key_pressed = False
    number6_key_pressed = False
    number7_key_pressed = False
    number8_key_pressed = False
    number9_key_pressed = False
    
    colon_key_pressed = False
    semicolon_key_pressed = False
    lessArrow_key_pressed = False
    equal_key_pressed = False
    greaterArrow_key_pressed = False
    questionMark_key_pressed = False
    at_key_pressed = False
    leftBracket_key_pressed = False
    backslash_key_pressed = False
    rightBracket_key_pressed = False
    caret_key_pressed = False
    underscore_key_pressed = False
    backquote_key_pressed = False
    
    a_key_pressed = False
    b_key_pressed = False
    c_key_pressed = False
    d_key_pressed = False
    e_key_pressed = False
    f_key_pressed = False
    g_key_pressed = False
    h_key_pressed = False
    i_key_pressed = False
    j_key_pressed = False
    k_key_pressed = False
    l_key_pressed = False
    m_key_pressed = False
    n_key_pressed = False
    o_key_pressed = False
    p_key_pressed = False
    q_key_pressed = False
    r_key_pressed = False
    s_key_pressed = False
    t_key_pressed = False
    u_key_pressed = False
    v_key_pressed = False
    w_key_pressed = False
    x_key_pressed = False
    y_key_pressed = False
    z_key_pressed = False

    delete_key_pressed = False
    keypad0_key_pressed = False
    keypad1_key_pressed = False
    keypad2_key_pressed = False
    keypad3_key_pressed = False
    keypad4_key_pressed = False
    keypad5_key_pressed = False
    keypad6_key_pressed = False
    keypad7_key_pressed = False
    keypad8_key_pressed = False
    keypad9_key_pressed = False
    keypadPeriod_key_pressed = False
    keypadDivide_key_pressed = False
    keypadMultiply_key_pressed = False
    keypadMinus_key_pressed = False
    keypadPlus_key_pressed = False
    keypadEnter_key_pressed = False
    keypadEquals_key_pressed = False
    keypadUp_key_pressed = False
    keypadDown_key_pressed = False
    keypadRight_key_pressed = False
    keypadLeft_key_pressed = False
    keypadInsert_key_pressed = False
    keypadHome_key_pressed = False
    keypadEnd_key_pressed = False
    keypadPageUp_key_pressed = False
    keypadPageDown_key_pressed = False
    
    F1_key_pressed = False
    F2_key_pressed = False
    F3_key_pressed = False
    F4_key_pressed = False
    F5_key_pressed = False
    F6_key_pressed = False
    F7_key_pressed = False
    F8_key_pressed = False
    F9_key_pressed = False
    F10_key_pressed = False
    F11_key_pressed = False
    F12_key_pressed = False
    F13_key_pressed = False
    F14_key_pressed = False
    F15_key_pressed = False

    lockNumber_key_pressed = False
    capsLock_key_pressed = False
    scrolLock_key_pressed = False
    rightShift_key_pressed = False
    leftShift_key_pressed = False
    rightControl_key_pressed = False
    leftControl_key_pressed = False
    rightAlt_key_pressed = False
    leftAlt_key_pressed = False
    rightMeta_key_pressed = False
    leftMeta_key_pressed = False
    leftWindows_key_pressed = False
    rightWindows_key_pressed = False
    mode_key_pressed = False
    help_key_pressed = False
    print_key_pressed = False
    sysreq_key_pressed = False
    break_key_pressed = False
    menu_key_pressed = False
    power_key_pressed = False
    euro_key_pressed = False
    androidBack_button_pressed = False

    #Mouse
    left_mouseClick_pressed = False
    right_mouseClick_pressed = False
    middle_mouseClick_pressed = False
    scrollUp_mouseWheel_pressed = False
    scrollDown_mouseWheel_pressed = False

    #endregion

    #bool to check if a key is pressed down (only the frame is pressed, only one time)
    #region
    #Keys
    backspace_key_down = False 
    tab_key_down = False
    clear_key_down = False
    return_key_down = False
    pause_key_down = False
    escape_key_down = False
    space_key_down = False
    exclaimationMark_key_down = False
    quotedbl_key_down = False
    hashtag_key_down = False
    dollar_key_down = False
    eCommercial_key_down = False
    quote_key_down = False
    leftParentesis_key_down = False
    rightParentesis_key_down = False
    asterisk_key_down = False
    plus_key_down = False 
    comma_key_down = False
    minus_key_down = False
    dot_key_down = False
    slash_key_down = False
    
    number0_key_down = False
    number1_key_down = False
    number2_key_down = False
    number3_key_down = False
    number4_key_down = False
    number5_key_down = False
    number6_key_down = False
    number7_key_down = False
    number8_key_down = False
    number9_key_down = False
    
    colon_key_down = False
    semicolon_key_down = False
    lessArrow_key_down = False
    equal_key_down = False
    greaterArrow_key_down = False
    questionMark_key_down = False
    at_key_down = False
    leftBracket_key_down = False
    backslash_key_down = False
    rightBracket_key_down = False
    caret_key_down = False
    underscore_key_down = False
    backquote_key_down = False
    
    a_key_down = False
    b_key_down = False
    c_key_down = False
    d_key_down = False
    e_key_down = False
    f_key_down = False
    g_key_down = False
    h_key_down = False
    i_key_down = False
    j_key_down = False
    k_key_down = False
    l_key_down = False
    m_key_down = False
    n_key_down = False
    o_key_down = False
    p_key_down = False
    q_key_down = False
    r_key_down = False
    s_key_down = False
    t_key_down = False
    u_key_down = False
    v_key_down = False
    w_key_down = False
    x_key_down= False
    y_key_down = False
    z_key_down = False

    delete_key_down = False
    keypad0_key_down = False
    keypad1_key_down = False
    keypad2_key_down = False
    keypad3_key_down = False
    keypad4_key_down = False
    keypad5_key_down = False
    keypad6_key_down = False
    keypad7_key_down = False
    keypad8_key_down = False
    keypad9_key_down = False
    keypadPeriod_key_down = False
    keypadDivide_key_down = False
    keypadMultiply_key_down = False
    keypadMinus_key_down = False
    keypadPlus_key_down = False
    keypadEnter_key_down = False
    keypadEquals_key_down = False
    keypadUp_key_down= False
    keypadDown_key_down = False
    keypadRight_key_down = False
    keypadLeft_key_down = False
    keypadInsert_key_down = False
    keypadHome_key_down = False
    keypadEnd_key_down = False
    keypadPageUp_key_down = False
    keypadPageDown_key_down = False
    
    F1_key_down = False
    F2_key_down = False
    F3_key_down= False
    F4_key_down = False
    F5_key_down = False
    F6_key_down = False
    F7_key_down = False
    F8_key_down = False
    F9_key_down = False
    F10_key_down = False
    F11_key_down = False
    F12_key_down = False
    F13_key_down = False
    F14_key_down = False
    F15_key_down = False

    lockNumber_key_down = False
    capsLock_key_down = False
    scrolLock_key_down = False
    rightShift_key_down = False
    leftShift_key_down = False
    rightControl_key_down = False
    leftControl_key_down = False
    rightAlt_key_down = False
    leftAlt_key_down = False
    rightMeta_key_down = False
    leftMeta_key_down = False
    leftWindows_key_down = False
    rightWindows_key_down = False
    mode_key_down = False
    help_key_down = False
    print_key_down = False
    sysreq_key_down = False
    break_key_down = False
    menu_key_down = False
    power_key_down = False
    euro_key_down = False
    androidBack_button_down = False

    #Mouse
    left_mouseClick_down = False
    right_mouseClick_down = False
    middle_mouseClick_down = False
    scrollUp_mouseWheel_down = False
    scrollDown_mouseWheel_down = False
    #endregion

    #bool to check if a key is released up (only the frame is released, only one time)
    #region
    backspace_key_up = False
    tab_key_up = False
    clear_key_up = False
    return_key_up = False
    pause_key_up = False
    escape_key_up = False
    space_key_up = False
    exclaimationMark_key_up = False
    quotedbl_key_up = False
    hashtag_key_up = False
    dollar_key_up = False
    eCommercial_key_up = False
    quote_key_up = False
    leftParentesis_key_up = False
    rightParentesis_key_up = False
    asterisk_key_up = False
    plus_key_up = False 
    comma_key_up = False
    minus_key_up = False
    dot_key_up = False
    slash_key_up = False
    
    number0_key_up = False
    number1_key_up = False
    number2_key_dup = False
    number3_key_up = False
    number4_key_up = False
    number5_key_up = False
    number6_key_up = False
    number7_key_up = False
    number8_key_up = False
    number9_key_up = False
    
    colon_key_up = False
    semicolon_key_up = False
    lessArrow_key_up = False
    equal_key_up = False
    greaterArrow_key_up = False
    questionMark_key_up = False
    at_key_up = False
    leftBracket_key_up = False
    backslash_key_up = False
    rightBracket_key_up = False
    caret_key_up = False
    underscore_key_up = False
    backquote_key_up = False
    
    a_key_up = False
    b_key_up = False
    c_key_up = False
    d_key_up = False
    e_key_up = False
    f_key_up = False
    g_key_up = False
    h_key_up = False
    i_key_up = False
    j_key_up = False
    k_key_up = False
    l_key_up = False
    m_key_up = False
    n_key_up = False
    o_key_up = False
    p_key_up = False
    q_key_up = False
    r_key_up = False
    s_key_up = False
    t_key_up = False
    u_key_up = False
    v_key_up = False
    w_key_up = False
    x_key_up = False
    y_key_up = False
    z_key_up = False

    delete_key_up = False
    keypad0_key_up = False
    keypad1_key_up = False
    keypad2_key_up = False
    keypad3_key_up = False
    keypad4_key_up = False
    keypad5_key_up = False
    keypad6_key_up = False
    keypad7_key_up = False
    keypad8_key_up = False
    keypad9_key_up = False
    keypadPeriod_key_up = False
    keypadDivide_key_up = False
    keypadMultiply_key_up = False
    keypadMinus_key_up = False
    keypadPlus_key_up = False
    keypadEnter_key_up = False
    keypadEquals_key_up = False
    keypadUp_key_up = False
    keypadDown_key_up = False
    keypadRight_key_up = False
    keypadLeft_key_up = False
    keypadInsert_key_up = False
    keypadHome_key_up = False
    keypadEnd_key_up = False
    keypadPageUp_key_up = False
    keypadPageDown_key_up = False
    
    F1_key_up = False
    F2_key_up = False
    F3_key_up = False
    F4_key_up = False
    F5_key_up = False
    F6_key_up = False
    F7_key_up = False
    F8_key_up = False
    F9_key_up = False
    F10_key_up = False
    F11_key_up = False
    F12_key_up = False
    F13_key_up = False
    F14_key_up = False
    F15_key_up = False

    lockNumber_key_up = False
    capsLock_key_up = False
    scrolLock_key_up = False
    rightShift_key_up = False
    leftShift_key_up = False
    rightControl_key_up = False
    leftControl_key_up = False
    rightAlt_key_up = False
    leftAlt_key_up = False
    rightMeta_key_up = False
    leftMeta_key_up = False
    leftWindows_key_up = False
    rightWindows_key_up = False
    mode_key_up = False
    help_key_up = False
    print_key_up = False
    sysreq_key_up = False
    break_key_up = False
    menu_key_up = False
    power_key_up = False
    euro_key_up = False
    androidBack_button_up = False

    #Mouse
    left_mouseClick_up = False
    right_mouseClick_up = False
    middle_mouseClick_up = False
    scrollUp_mouseWheel_up = False
    scrollDown_mouseWheel_up = False
    #endregion

    #Quit Event
    #region
    __Quit = False
    #endregion
   
    #Check Inputs
    #region
    def __CheckInput():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        This function first pumps the event to the pygame event's queue  and then calls all the other functions to check properly the inputs.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        #Adds all the events to the events queue
        pygame.event.pump()

        #Get the all the events and keys pressed
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        #Checks Down and Up inputs for keys and mouse
        for event in events:
            Input.__CheckDownInput(event)
            Input.__CheckUpInput(event)
            Input.__CheckQuit(event)

        #Checks Pressed inputs for keys and mouse
        Input.__CheckPressedInput(keys, mouse)

        #Gets mouse position
        Input.__GetMousePosition()

    def __CheckDownInput(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Checks the down input for keys and mouse by calling the relative functions.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Input.__CheckKeysDownInput(event)
        Input.__CheckMouseDownInput(event)

    def __CheckPressedInput(keys, mouse):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Checks the pressed input for keys and mouse by calling the relative functions.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -keys:          list        the list of the keys returned by pygame.key.get_pressed()
        -mouse:         list        the list of the keys returned by pygame.mouse.get_pressed()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Input.__CheckKeysPressedInput(keys)
        Input.__CheckMousePressedInput(mouse)

    def __CheckUpInput(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Checks the up input for keys and mouse by calling the relative functions.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Input.__CheckKeysUpInput(event)
        Input.__CheckMouseUpInput(event)

    def __CheckQuit(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Checks if the quit event has occurred.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if event.type == pygame.QUIT:
            Input.__Quit = True
    #endregion



    #Checks inputs for keys
    #region
    def __CheckKeysPressedInput(keys):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Set the values of the keys being pressed (keyName_key_pressed)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -keys           list        the list of the keys returned by pygame.key.get_pressed()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Input.backspace_key_pressed = keys[Input.backspace_key]
        Input.tab_key_pressed = keys[Input.tab_key]
        Input.clear_key_pressed = keys[Input.clear_key]
        Input.return_key_pressed = keys[Input.return_key]
        Input.pause_key_pressed = keys[Input.pause_key]
        Input.escape_key_pressed = keys[Input.escape_key]
        Input.space_key_pressed = keys[Input.space_key]
        Input.exclaimationMark_key_pressed = keys[Input.exclaimationMark_key]
        Input.quotedbl_key_pressed = keys[Input.quotedbl_key]
        Input.hashtag_key_pressed = keys[Input.hashtag_key]
        Input.dollar_key_pressed = keys[Input.dollar_key]
        Input.eCommercial_key_pressed = keys[Input.eCommercial_key]
        Input.quote_key_pressed = keys[Input.quote_key]
        Input.leftParentesis_key_pressed = keys[Input.leftParentesis_key]
        Input.rightParentesis_key_pressed = keys[Input.rightParentesis_key]
        Input.asterisk_key_pressed = keys[Input.asterisk_key]
        Input.plus_key_pressed = keys[Input.plus_key]
        Input.comma_key_pressed = keys[Input.comma_key]
        Input.minus_key_pressed = keys[Input.minus_key]
        Input.dot_key_pressed = keys[Input.dot_key]
        Input.slash_key_pressed = keys[Input.slash_key]
    
        Input.number0_key_pressed = keys[Input.number0_key]
        Input.number1_key_pressed = keys[Input.number1_key]
        Input.number2_key_pressed = keys[Input.number2_key]
        Input.number3_key_pressed = keys[Input.number3_key]
        Input.number4_key_pressed = keys[Input.number4_key]
        Input.number5_key_pressed = keys[Input.number5_key]
        Input.number6_key_pressed = keys[Input.number6_key]
        Input.number7_key_pressed = keys[Input.number7_key]
        Input.number8_key_pressed = keys[Input.number8_key]
        Input.number9_key_pressed = keys[Input.number9_key]
    
        Input.colon_key_pressed = keys[Input.colon_key]
        Input.semicolon_key_pressed = keys[Input.semicolon_key]
        Input.lessArrow_key_pressed = keys[Input.lessArrow_key]
        Input.equal_key_pressed = keys[Input.equal_key]
        Input.greaterArrow_key_pressed = keys[Input.greaterArrow_key]
        Input.questionMark_key_pressed = keys[Input.questionMark_key]
        Input.at_key_pressed = keys[Input.at_key]
        Input.leftBracket_key_pressed = keys[Input.leftBracket_key]
        Input.backslash_key_pressed = keys[Input.backslash_key]
        Input.rightBracket_key_pressed = keys[Input.rightBracket_key]
        Input.caret_key_pressed = keys[Input.caret_key]
        Input.underscore_key_pressed = keys[Input.underscore_key]
        Input.backquote_key_pressed = keys[Input.backquote_key]
    
        Input.a_key_pressed = keys[Input.a_key]
        Input.b_key_pressed = keys[Input.b_key]
        Input.c_key_pressed = keys[Input.c_key]
        Input.d_key_pressed = keys[Input.d_key]
        Input.e_key_pressed = keys[Input.e_key]
        Input.f_key_pressed = keys[Input.f_key]
        Input.g_key_pressed = keys[Input.g_key]
        Input.h_key_pressed = keys[Input.h_key]
        Input.i_key_pressed = keys[Input.i_key]
        Input.j_key_pressed = keys[Input.j_key]
        Input.k_key_pressed = keys[Input.k_key]
        Input.l_key_pressed = keys[Input.l_key]
        Input.m_key_pressed = keys[Input.m_key]
        Input.n_key_pressed = keys[Input.n_key]
        Input.o_key_pressed = keys[Input.o_key]
        Input.p_key_pressed = keys[Input.p_key]
        Input.q_key_pressed = keys[Input.q_key]
        Input.r_key_pressed = keys[Input.r_key]
        Input.s_key_pressed = keys[Input.s_key]
        Input.t_key_pressed = keys[Input.t_key]
        Input.u_key_pressed = keys[Input.u_key]
        Input.v_key_pressed = keys[Input.v_key]
        Input.w_key_pressed = keys[Input.w_key]
        Input.x_key_pressed = keys[Input.x_key]
        Input.y_key_pressed = keys[Input.y_key]
        Input.z_key_pressed = keys[Input.z_key]

        Input.delete_key_pressed = keys[Input.delete_key]
        Input.keypad0_key_pressed = keys[Input.keypad0_key]
        Input.keypad1_key_pressed = keys[Input.keypad1_key]
        Input.keypad2_key_pressed = keys[Input.keypad2_key]
        Input.keypad3_key_pressed = keys[Input.keypad3_key]
        Input.keypad4_key_pressed = keys[Input.keypad4_key]
        Input.keypad5_key_pressed = keys[Input.keypad5_key]
        Input.keypad6_key_pressed = keys[Input.keypad6_key]
        Input.keypad7_key_pressed = keys[Input.keypad7_key]
        Input.keypad8_key_pressed = keys[Input.keypad8_key]
        Input.keypad9_key_pressed = keys[Input.keypad9_key]
        Input.keypadPeriod_key_pressed = keys[Input.keypadPeriod_key]
        Input.keypadDivide_key_pressed = keys[Input.keypadDivide_key]
        Input.keypadMultiply_key_pressed = keys[Input.keypadMultiply_key]
        Input.keypadMinus_key_pressed = keys[Input.keypadMinus_key]
        Input.keypadPlus_key_pressed = keys[Input.keypadPlus_key]
        Input.keypadEnter_key_pressed = keys[Input.keypadEnter_key]
        Input.keypadEquals_key_pressed = keys[Input.keypadEquals_key]
        Input.keypadUp_key_pressed = keys[Input.keypadUp_key]
        Input.keypadDown_key_pressed = keys[Input.keypadDown_key]
        Input.keypadRight_key_pressed = keys[Input.keypadRight_key]
        Input.keypadLeft_key_pressed = keys[Input.keypadLeft_key]
        Input.keypadInsert_key_pressed = keys[Input.keypadInsert_key]
        Input.keypadHome_key_pressed = keys[Input.keypadHome_key]
        Input.keypadEnd_key_pressed = keys[Input.keypadEnd_key]
        Input.keypadPageUp_key_pressed = keys[Input.keypadPageUp_key]
        Input.keypadPageDown_key_pressed = keys[Input.keypadPageDown_key]
    
        Input.F1_key_pressed = keys[Input.F1_key]
        Input.F2_key_pressed = keys[Input.F2_key]
        Input.F3_key_pressed = keys[Input.F3_key]
        Input.F4_key_pressed = keys[Input.F4_key]
        Input.F5_key_pressed = keys[Input.F5_key]
        Input.F6_key_pressed = keys[Input.F6_key]
        Input.F7_key_pressed = keys[Input.F7_key]
        Input.F8_key_pressed = keys[Input.F8_key]
        Input.F9_key_pressed = keys[Input.F9_key]
        Input.F10_key_pressed = keys[Input.F10_key]
        Input.F11_key_pressed = keys[Input.F11_key]
        Input.F12_key_pressed = keys[Input.F12_key]
        Input.F13_key_pressed = keys[Input.F13_key]
        Input.F14_key_pressed = keys[Input.F14_key]
        Input.F15_key_pressed = keys[Input.F15_key]

        Input.lockNumber_key_pressed = keys[Input.lockNumber_key]
        Input.capsLock_key_pressed = keys[Input.capsLock_key]
        Input.scrolLock_key_pressed = keys[Input.scrolLock_key]
        Input.rightShift_key_pressed = keys[Input.rightShift_key]
        Input.leftShift_key_pressed = keys[Input.leftShift_key]
        Input.rightControl_key_pressed = keys[Input.rightControl_key]
        Input.leftControl_key_pressed = keys[Input.leftControl_key]
        Input.rightAlt_key_pressed = keys[Input.rightAlt_key]
        Input.leftAlt_key_pressed = keys[Input.leftAlt_key]
        Input.rightMeta_key_pressed = keys[Input.rightMeta_key]
        Input.leftMeta_key_pressed = keys[Input.leftMeta_key]
        Input.leftWindows_key_pressed = keys[Input.leftWindows_key]
        Input.rightWindows_key_pressed = keys[Input.rightWindows_key]
        Input.mode_key_pressed = keys[Input.mode_key]
        Input.help_key_pressed = keys[Input.help_key]
        Input.print_key_pressed = keys[Input.print_key]
        Input.sysreq_key_pressed = keys[Input.sysreq_key]
        Input.break_key_pressed = keys[Input.break_key]
        Input.menu_key_pressed = keys[Input.menu_key]
        Input.power_key_pressed = keys[Input.power_key]
        Input.euro_key_pressed = keys[Input.euro_key]
        Input.androidBack_button_pressed = keys[Input.androidBack_button]
                
    def __CheckKeysDownInput(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Set the values of the keys being pressed down this frame (keyName_key_down)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if event.type == pygame.KEYDOWN: 

                if event.key == Input.backspace_key:
                    Input.backspace_key_down = True

                if event.key == Input.tab_key:
                    Input.tab_key_down = True

                if event.key == Input.clear_key:
                    Input.clear_key_down = True

                if event.key == Input.return_key:
                    Input.return_key_down = True
                
                if event.key == Input.pause_key:
                    Input.pause_key_down = True
                
                if event.key == Input.escape_key:
                    Input.escape_key_down = True
                
                if event.key == Input.space_key:
                    Input.space_key_down = True
                
                if event.key == Input.exclaimationMark_key:
                    Input.exclaimationMark_key_down = True
                
                if event.key == Input.quotedbl_key:
                    Input.quotedbl_key_down = True

                if event.key == Input.hashtag_key:
                    Input.hashtag_key_down = True

                if event.key == Input.dollar_key:
                    Input.dollar_key_down = True

                if event.key == Input.eCommercial_key:
                    Input.eCommercial_key_down = True

                if event.key == Input.quote_key:
                    Input.quote_key_down = True

                if event.key == Input.leftParentesis_key:
                    Input.leftParentesis_key_down  = True

                if event.key == Input.rightParentesis_key:
                    Input.rightParentesis_key_down = True

                if event.key == Input.asterisk_key:
                    Input.asterisk_key_down = True

                if event.key == Input.plus_key:
                    Input.plus_key_down = True

                if event.key == Input.comma_key:
                    Input.comma_key_down = True

                if event.key == Input.minus_key:
                    Input.minus_key_down = True

                if event.key == Input.dot_key:
                    Input.dot_key_down = True

                if event.key == Input.slash_key:
                    Input.slash_key_down = True

                if event.key == Input.number0_key:
                    Input.number0_key_down = True

                if event.key == Input.number1_key:
                    Input.number1_key_down = True

                if event.key == Input.number2_key:
                    Input.number2_key_down = True

                if event.key == Input.number3_key:
                    Input.number3_key_down = True

                if event.key == Input.number4_key:
                    Input.number4_key_down = True

                if event.key == Input.number5_key:
                    Input.number5_key_down = True

                if event.key == Input.number6_key:
                    Input.number6_key_down = True

                if event.key == Input.number7_key:
                    Input.number7_key_down = True

                if event.key == Input.number8_key:
                    Input.number8_key_down = True

                if event.key == Input.number9_key:
                    Input.number9_key_down = True

                if event.key == Input.colon_key:
                    Input.colon_key_down = True

                if event.key == Input.semicolon_key:
                    Input.semicolon_key_down = True

                if event.key == Input.lessArrow_key:
                    Input.lessArrow_key_down = True

                if event.key == Input.equal_key:
                    Input.equal_key_down = True

                if event.key == Input.greaterArrow_key:
                    Input.greaterArrow_key_down = True

                if event.key == Input.questionMark_key:
                    Input.questionMark_key_down = True

                if event.key == Input.at_key:
                    Input.at_key_down = True

                if event.key == Input.leftBracket_key:
                    Input.leftBracket_key_down = True

                if event.key == Input.backslash_key:
                    Input.backslash_key_down = True

                if event.key == Input.rightBracket_key:
                    Input.rightBracket_key_down = True

                if event.key == Input.caret_key:
                    Input.caret_key_down = True

                if event.key == Input.underscore_key:
                    Input.underscore_key_down = True

                if event.key == Input.backquote_key:
                    Input.backquote_key_down = True

                if event.key == Input.a_key:
                    Input.a_key_down = True

                if event.key == Input.b_key:
                    Input.b_key_down = True

                if event.key == Input.c_key:
                    Input.c_key_down = True

                if event.key == Input.d_key:
                    Input.d_key_down = True

                if event.key == Input.e_key:
                    Input.e_key_down = True

                if event.key == Input.f_key:
                    Input.f_key_down = True

                if event.key == Input.g_key:
                    Input.g_key_down = True

                if event.key == Input.h_key:
                    Input.h_key_down = True

                if event.key == Input.i_key:
                    Input.i_key_down = True

                if event.key == Input.j_key:  
                    Input.j_key_down = True

                if event.key == Input.k_key:
                    Input.k_key_down = True

                if event.key == Input.l_key:
                    Input.l_key_down = True

                if event.key == Input.m_key:
                    Input.m_key_down = True

                if event.key == Input.n_key:
                    Input.n_key_down = True

                if event.key == Input.o_key:
                    Input.o_key_down = True

                if event.key == Input.p_key:
                    Input.p_key_down = True

                if event.key == Input.q_key:
                    Input.q_key_down = True

                if event.key == Input.r_key:
                    Input.r_key_down = True

                if event.key == Input.s_key:
                    Input.s_key_down = True

                if event.key == Input.t_key:
                    Input.t_key_down = True

                if event.key == Input.u_key:
                    Input.u_key_down = True

                if event.key == Input.v_key:
                    Input.v_key_down = True

                if event.key == Input.w_key:
                    Input.w_key_down = True

                if event.key == Input.x_key:
                    Input.x_key_down = True

                if event.key == Input.y_key:
                    Input.y_key_down = True

                if event.key == Input.z_key:
                    Input.z_key_down = True

                if event.key == Input.delete_key:
                    Input.delete_key_down = True

                if event.key == Input.keypad0_key:
                    Input.keypad0_key_down = True

                if event.key == Input.keypad1_key:
                    Input.keypad1_key_down = True

                if event.key == Input.keypad2_key:
                    Input.keypad2_key_down = True

                if event.key == Input.keypad3_key:
                    Input.keypad3_key_down = True

                if event.key == Input.keypad4_key:
                    Input.keypad4_key_down = True
                
                if event.key == Input.keypad5_key:
                    Input.keypad5_key_down = True

                if event.key == Input.keypad6_key:
                    Input.keypad6_key_down = True

                if event.key == Input.keypad7_key:
                    Input.keypad7_key_down = True

                if event.key == Input.keypad8_key:
                    Input.keypad8_key_down = True

                if event.key == Input.keypad9_key:
                    Input.keypad9_key_down = True

                if event.key == Input.keypadPeriod_key:
                    Input.keypadPeriod_key_down = True

                if event.key == Input.keypadDivide_key:
                    Input.keypadDivide_key_down = True

                if event.key == Input.keypadMultiply_key:
                    Input.keypadMultiply_key_down = True

                if event.key == Input.keypadMinus_key:
                    Input.keypadMinus_key_down = True

                if event.key == Input.keypadPlus_key:
                    Input.keypadPlus_key_down = True

                if event.key == Input.keypadEnter_key:
                    Input.keypadEnter_key_down = True

                if event.key == Input.keypadEquals_key:
                    Input.keypadEquals_key_down = True

                if event.key == Input.keypadUp_key:
                    Input.keypadUp_key_down = True

                if event.key == Input.keypadDown_key:
                    Input.keypadDown_key_down = True

                if event.key == Input.keypadRight_key:
                    Input.keypadRight_key_down = True

                if event.key == Input.keypadLeft_key:
                    Input.keypadLeft_key_down = True

                if event.key == Input.keypadInsert_key:
                    Input.keypadInsert_key_down = True
                
                if event.key == Input.keypadHome_key:
                    Input.keypadHome_key_down = True

                if event.key == Input.keypadEnd_key:
                    Input.keypadEnd_key_down = True

                if event.key == Input.keypadPageUp_key:
                    Input.keypadPageUp_key_down = True
                
                if event.key == Input.keypadPageDown_key:
                    Input.keypadPageDown_key_down = True

                if event.key == Input.F1_key:
                    Input.F1_key_down = True

                if event.key == Input.F2_key:
                    Input.F2_key_down = True

                if event.key == Input.F3_key:
                    Input.F3_key_down = True

                if event.key == Input.F4_key:
                    Input.F4_key_down = True

                if event.key == Input.F5_key:
                    Input.F5_key_down = True

                if event.key == Input.F6_key:
                    Input.F6_key_down = True

                if event.key == Input.F7_key:
                    Input.F7_key_down = True

                if event.key == Input.F8_key:
                    Input.F8_key_down = True

                if event.key == Input.F9_key:
                    Input.F9_key_down = True

                if event.key == Input.F10_key:
                    Input.F10_key_down = True

                if event.key == Input.F11_key:
                    Input.F11_key_down = True

                if event.key == Input.F12_key:
                    Input.F12_key_down = True

                if event.key == Input.F13_key:
                    Input.F13_key_down = True

                if event.key == Input.F14_key:
                    Input.F14_key_down = True

                if event.key == Input.F15_key:
                    Input.F15_key_down = True

                if event.key == Input.scrolLock_key:
                    Input.scrolLock_key_down = True

                if event.key == Input.capsLock_key:
                    Input.capseLock_key_down = True

                if event.key == Input.rightShift_key:
                    Input.leftShift_key_down = True

                if event.key == Input.rightControl_key:
                    Input.rightControl_key_down = True

                if event.key == Input.lockNumber_key:
                    Input.lockNumber_key_down = True

                if event.key == Input.leftShift_key:
                    Input.leftShift_key_down = True

                if event.key == Input.leftControl_key:
                    Input.leftControl_key_down = True

                if event.key == Input.rightAlt_key:
                    Input.rightAlt_key_down = True

                if event.key == Input.leftAlt_key:
                    Input.leftAlt_key_down = True

                if event.key == Input.rightMeta_key:
                    Input.rightMeta_key_down = True

                if event.key == Input.leftMeta_key:
                    Input.leftMeta_key_down = True

                if event.key == Input.leftWindows_key:
                    Input.leftWindows_key_down = True

                if event.key == Input.rightWindows_key:
                    Input.rightWindows_key_down = True

                if event.key == Input.mode_key:
                    Input.mode_key_down = True

                if event.key == Input.help_key:
                    Input.help_key_down = True

                if event.key == Input.print_key:
                    Input.print_key_down = True

                if event.key == Input.sysreq_key:
                    Input.sysreq_key_down = True

                if event.key == Input.break_key:
                    Input.break_key_down = True

                if event.key == Input.menu_key:
                    Input.menu_key_down = True

                if event.key == Input.power_key:
                    Input.power_key_down = True

                if event.key == Input.euro_key:
                    Input.euro_key_down = True

                if event.key == Input.androidBack_button:
                    Input.androidBack_button_down = True
            
    def __CheckKeysUpInput(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Set the values of the keys being released up this frame (keyName_key_up)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if event.type == pygame.KEYUP:
                
                if event.key == Input.backspace_key:
                    Input.backspace_key_up = True

                if event.key == Input.tab_key:
                    Input.tab_key_up = True

                if event.key == Input.clear_key:
                    Input.clear_key_up = True

                if event.key == Input.return_key:
                    Input.return_key_up = True
                
                if event.key == Input.pause_key:
                    Input.pause_key_up = True
                
                if event.key == Input.escape_key:
                    Input.escape_key_up = True
                
                if event.key == Input.space_key:
                    Input.space_key_up = True
                
                if event.key == Input.exclaimationMark_key:
                    Input.exclaimationMark_key_up = True
                
                if event.key == Input.quotedbl_key:
                    Input.quotedbl_key_up = True

                if event.key == Input.hashtag_key:
                    Input.hashtag_key_up = True

                if event.key == Input.dollar_key:
                    Input.dollar_key_up = True

                if event.key == Input.eCommercial_key:
                    Input.eCommercial_key_up = True

                if event.key == Input.quote_key:
                    Input.quote_key_up = True

                if event.key == Input.leftParentesis_key:
                    Input.leftParentesis_key_up  = True

                if event.key == Input.rightParentesis_key:
                    Input.rightParentesis_key_up = True

                if event.key == Input.asterisk_key:
                    Input.asterisk_key_up = True

                if event.key == Input.plus_key:
                    Input.plus_key_up = True

                if event.key == Input.comma_key:
                    Input.comma_key_up = True

                if event.key == Input.minus_key:
                    Input.minus_key_up = True

                if event.key == Input.dot_key:
                    Input.dot_key_up = True

                if event.key == Input.slash_key:
                    Input.slash_key_up = True

                if event.key == Input.number0_key:
                    Input.number0_key_up = True

                if event.key == Input.number1_key:
                    Input.number1_key_up = True

                if event.key == Input.number2_key:
                    Input.number2_key_up = True

                if event.key == Input.number3_key:
                    Input.number3_key_up = True

                if event.key == Input.number4_key:
                    Input.number4_key_up = True

                if event.key == Input.number5_key:
                    Input.number5_key_up = True

                if event.key == Input.number6_key:
                    Input.number6_key_up = True

                if event.key == Input.number7_key:
                    Input.number7_key_up = True

                if event.key == Input.number8_key:
                    Input.number8_key_up = True

                if event.key == Input.number9_key:
                    Input.number9_key_up = True

                if event.key == Input.colon_key:
                    Input.colon_key_up = True

                if event.key == Input.semicolon_key:
                    Input.semicolon_key_up = True

                if event.key == Input.lessArrow_key:
                    Input.lessArrow_key_up = True

                if event.key == Input.equal_key:
                    Input.equal_key_up = True

                if event.key == Input.greaterArrow_key:
                    Input.greaterArrow_key_up = True

                if event.key == Input.questionMark_key:
                    Input.questionMark_key_up = True

                if event.key == Input.at_key:
                    Input.at_key_up = True

                if event.key == Input.leftBracket_key:
                    Input.leftBracket_key_up = True

                if event.key == Input.backslash_key:
                    Input.backslash_key_up = True

                if event.key == Input.rightBracket_key:
                    Input.rightBracket_key_up = True

                if event.key == Input.caret_key:
                    Input.caret_key_up = True

                if event.key == Input.underscore_key:
                    Input.underscore_key_up = True

                if event.key == Input.backquote_key:
                    Input.backquote_key_up = True

                if event.key == Input.a_key:
                    Input.a_key_up = True

                if event.key == Input.b_key:
                    Input.b_key_up = True

                if event.key == Input.c_key:
                    Input.c_key_up = True

                if event.key == Input.d_key:
                    Input.d_key_up = True

                if event.key == Input.e_key:
                    Input.e_key_up = True

                if event.key == Input.f_key:
                    Input.f_key_up = True

                if event.key == Input.g_key:
                    Input.g_key_up = True

                if event.key == Input.h_key:
                    Input.h_key_up = True

                if event.key == Input.i_key:
                    Input.i_key_up = True

                if event.key == Input.j_key:  
                    Input.j_key_up = True

                if event.key == Input.k_key:
                    Input.k_key_up = True

                if event.key == Input.l_key:
                    Input.l_key_up = True

                if event.key == Input.m_key:
                    Input.m_key_up = True

                if event.key == Input.n_key:
                    Input.n_key_up = True

                if event.key == Input.o_key:
                    Input.o_key_up = True

                if event.key == Input.p_key:
                    Input.p_key_up = True

                if event.key == Input.q_key:
                    Input.q_key_up = True

                if event.key == Input.r_key:
                    Input.r_key_up = True

                if event.key == Input.s_key:
                    Input.s_key_up = True

                if event.key == Input.t_key:
                    Input.t_key_up = True

                if event.key == Input.u_key:
                    Input.u_key_up = True

                if event.key == Input.v_key:
                    Input.v_key_up = True

                if event.key == Input.w_key:
                    Input.u_key_up = True

                if event.key == Input.x_key:
                    Input.x_key_up = True

                if event.key == Input.y_key:
                    Input.y_key_up = True

                if event.key == Input.z_key:
                    Input.z_key_up = True

                if event.key == Input.delete_key:
                    Input.delete_key_up = True

                if event.key == Input.keypad0_key:
                    Input.keypad0_key_up = True

                if event.key == Input.keypad1_key:
                    Input.keypad1_key_up = True

                if event.key == Input.keypad2_key:
                    Input.keypad2_key_up = True

                if event.key == Input.keypad3_key:
                    Input.keypad3_key_up = True

                if event.key == Input.keypad4_key:
                    Input.keypad4_key_up = True
                
                if event.key == Input.keypad5_key:
                    Input.keypad5_key_up = True

                if event.key == Input.keypad6_key:
                    Input.keypad6_key_up = True

                if event.key == Input.keypad7_key:
                    Input.keypad7_key_up = True

                if event.key == Input.keypad8_key:
                    Input.keypad8_key_up = True

                if event.key == Input.keypad9_key:
                    Input.keypad9_key_up = True

                if event.key == Input.keypadPeriod_key:
                    Input.keypadPeriod_key_up = True

                if event.key == Input.keypadDivide_key:
                    Input.keypadDivide_key_up = True

                if event.key == Input.keypadMultiply_key:
                    Input.keypadMultiply_key_up = True

                if event.key == Input.keypadMinus_key:
                    Input.keypadMinus_key_up = True

                if event.key == Input.keypadPlus_key:
                    Input.keypadPlus_key_up = True

                if event.key == Input.keypadEnter_key:
                    Input.keypadEnter_key_up = True

                if event.key == Input.keypadEquals_key:
                    Input.keypadEquals_key_up = True

                if event.key == Input.keypadUp_key:
                    Input.keypadUp_key_up = True

                if event.key == Input.keypadDown_key:
                    Input.keypadDown_key_up = True

                if event.key == Input.keypadRight_key:
                    Input.keypadRight_key_up = True

                if event.key == Input.keypadLeft_key:
                    Input.keypadLeft_key_up = True

                if event.key == Input.keypadInsert_key:
                    Input.keypadInsert_key_up = True
                
                if event.key == Input.keypadHome_key:
                    Input.keypadHome_key_up = True

                if event.key == Input.keypadEnd_key:
                    Input.keypadEnd_key_up = True

                if event.key == Input.keypadPageUp_key:
                    Input.keypadPageUp_key_up = True
                
                if event.key == Input.keypadPageDown_key:
                    Input.keypadPageDown_key_up = True

                if event.key == Input.F1_key:
                    Input.F1_key_up = True

                if event.key == Input.F2_key:
                    Input.F2_key_up = True

                if event.key == Input.F3_key:
                    Input.F3_key_up = True

                if event.key == Input.F4_key:
                    Input.F4_key_up = True

                if event.key == Input.F5_key:
                    Input.F5_key_up = True

                if event.key == Input.F6_key:
                    Input.F6_key_up = True

                if event.key == Input.F7_key:
                    Input.F7_key_up = True

                if event.key == Input.F8_key:
                    Input.F8_key_up = True

                if event.key == Input.F9_key:
                    Input.F9_key_up = True

                if event.key == Input.F10_key:
                    Input.F10_key_up = True

                if event.key == Input.F11_key:
                    Input.F11_key_up = True

                if event.key == Input.F12_key:
                    Input.F12_key_up = True

                if event.key == Input.F13_key:
                    Input.F13_key_up = True

                if event.key == Input.F14_key:
                    Input.F14_key_up = True

                if event.key == Input.F15_key:
                    Input.F15_key_up = True

                if event.key == Input.scrolLock_key:
                    Input.scrolLock_key_up = True

                if event.key == Input.capsLock_key:
                    Input.capseLock_key_up = True

                if event.key == Input.rightShift_key:
                    Input.leftShift_key_up = True

                if event.key == Input.rightControl_key:
                    Input.rightControl_key_up = True

                if event.key == Input.lockNumber_key:
                    Input.lockNumber_key_up = True

                if event.key == Input.leftShift_key:
                    Input.leftShift_key_up = True

                if event.key == Input.leftControl_key:
                    Input.leftControl_key_up = True

                if event.key == Input.rightAlt_key:
                    Input.rightAlt_key_up = True

                if event.key == Input.leftAlt_key:
                    Input.leftAlt_key_up = True

                if event.key == Input.rightMeta_key:
                    Input.rightMeta_key_up = True

                if event.key == Input.leftMeta_key:
                    Input.leftMeta_key_up = True

                if event.key == Input.leftWindows_key:
                    Input.leftWindows_key_up = True

                if event.key == Input.rightWindows_key:
                    Input.rightWindows_key_up = True

                if event.key == Input.mode_key:
                    Input.mode_key_up = True

                if event.key == Input.help_key:
                    Input.help_key_up = True

                if event.key == Input.print_key:
                    Input.print_key_up = True

                if event.key == Input.sysreq_key:
                    Input.sysreq_key_up = True

                if event.key == Input.break_key:
                    Input.break_key_up = True

                if event.key == Input.menu_key:
                    Input.menu_key_up = True

                if event.key == Input.power_key:
                    Input.power_key_up = True

                if event.key == Input.euro_key:
                    Input.euro_key_up = True

                if event.key == Input.androidBack_button:
                    Input.androidBack_button_up = True
    #endregion

    #Checks inputs for mouse
    #region
    def __CheckMousePressedInput(mouse):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Set the values of the mouse buttons being pressed (mouseButton_MouseClick_pressed)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -keys           list        the list of the keys returned by pygame.key.get_pressed()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Input.left_mouseClick_pressed = mouse[Input.left_mouseClick_tuple]
        Input.middle_mouseClick_pressed = mouse[Input.middle_mouseClick_tuple]
        Input.right_mouseClick_pressed = mouse[Input.right_mouseClick_tuple]

    def __CheckMouseDownInput(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Set the values of the mouse buttons being pressed down this frame (mouseButton_MouseClick_down)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == Input.left_mouseClick_event:
                Input.left_mouseClick_down = True

            if event.button == Input.right_mouseClick_event:
                Input.right_mouseClick_down = True

            if event.button == Input.middle_mouseClick_event:
                Input.right_mouseClick_down = True

            if event.button == Input.scrollUp_mouseWheel_event:
                Input.scrollUp_mouseClick_down = True

            if event.button == Input.scrollDown_mouseWheel_event:
                Input.scrollDown_mouseClick_down = True

    def __CheckMouseUpInput(event):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Set the values of the mouse buttons being released up this frame (mouseButton_MouseClick_up)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -event:     pygame.event    the pygame event of the input contained in the list returned by pygame.event.get()

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == Input.left_mouseClick_event:
                Input.left_mouseClick_up = True

            if event.button == Input.right_mouseClick_event:
                Input.right_mouseClick_up = True

            if event.button == Input.middle_mouseClick_event:
                Input.right_mouseClick_up = True

            if event.button == Input.scrollUp_mouseWheel_event:
                Input.scrollUp_mouseClick_up = True

            if event.button == Input.scrollDown_mouseWheel_event:
                Input.scrollDown_mouseClick_up = True
    
    def __GetMousePosition():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Gets the position of the mouse and stores it in Input.mouse_position of type Vector2

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        Input.mouse_position = Vector2.ConvertToVector2(pygame.mouse.get_pos())
    #endregion

    #Cancel One frame Input
    def __CancelOneFrameInput():
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Resets keyName_key_down, keyName_key_up, mouseButton_MouseClick_down and mouseButton_MouseClick_up to False. 

        NOTES:
        This is called at the end of the game loop after Update.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        #KeyDown Inputs
        #region
        Input.backspace_key_down = False
        Input.tab_key_down = False
        Input.clear_key_down = False
        Input.return_key_down = False
        Input.pause_key_down = False
        Input.escape_key_down = False
        Input.space_key_down = False
        Input.exclaimationMark_key_down = False
        Input.quotedbl_key_down = False
        Input.hashtag_key_down = False
        Input.dollar_key_down = False
        Input.eCommercial_key_down = False
        Input.quote_key_down = False
        Input.leftParentesis_key_down = False
        Input.rightParentesis_key_down = False
        Input.asterisk_key_down = False
        Input.plus_key_down = False 
        Input.comma_key_down = False
        Input.minus_key_down = False
        Input.dot_key_down = False
        Input.slash_key_down = False
    
        Input.number0_key_down = False
        Input.number1_key_down = False
        Input.number2_key_down = False
        Input.number3_key_down = False
        Input.number4_key_down = False
        Input.number5_key_down = False
        Input.number6_key_down = False
        Input.number7_key_down = False
        Input.number8_key_down = False
        Input.number9_key_down = False
    
        Input.colon_key_down = False
        Input.semicolon_key_down = False
        Input.lessArrow_key_down = False
        Input.equal_key_down = False
        Input.greaterArrow_key_down = False
        Input.questionMark_key_down = False
        Input.at_key_down = False
        Input.leftBracket_key_down = False
        Input.backslash_key_down = False
        Input.rightBracket_key_down = False
        Input.caret_key_down = False
        Input.underscore_key_down = False
        Input.backquote_key_down = False
    
        Input.a_key_down = False
        Input.b_key_down = False
        Input.c_key_down = False
        Input.d_key_down = False
        Input.e_key_down = False
        Input.f_key_down = False
        Input.g_key_down = False
        Input.h_key_down = False
        Input.i_key_down = False
        Input.j_key_down = False
        Input.k_key_down = False
        Input.l_key_down = False
        Input.m_key_down = False
        Input.n_key_down = False
        Input.o_key_down = False
        Input.p_key_down = False
        Input.q_key_down = False
        Input.r_key_down = False
        Input.s_key_down = False
        Input.t_key_down = False
        Input.u_key_down = False
        Input.v_key_down = False
        Input.w_key_down = False
        Input.x_key_down= False
        Input.y_key_down = False
        Input.z_key_down = False

        Input.delete_key_down = False
        Input.keypad0_key_down = False
        Input.keypad1_key_down = False
        Input.keypad2_key_down = False
        Input.keypad3_key_down = False
        Input.keypad4_key_down = False
        Input.keypad5_key_down = False
        Input.keypad6_key_down = False
        Input.keypad7_key_down = False
        Input.keypad8_key_down = False
        Input.keypad9_key_down = False
        Input.keypadPeriod_key_down = False
        Input.keypadDivide_key_down = False
        Input.keypadMultiply_key_down = False
        Input.keypadMinus_key_down = False
        Input.keypadPlus_key_down = False
        Input.keypadEnter_key_down = False
        Input.keypadEquals_key_down = False
        Input.keypadUp_key_down= False
        Input.keypadDown_key_down = False
        Input.keypadRight_key_down = False
        Input.keypadLeft_key_down = False
        Input.keypadInsert_key_down = False
        Input.keypadHome_key_down = False
        Input.keypadEnd_key_down = False
        Input.keypadPageUp_key_down = False
        Input.keypadPageDown_key_down = False
    
        Input.F1_key_down = False
        Input.F2_key_down = False
        Input.F3_key_down= False
        Input.F4_key_down = False
        Input.F5_key_down = False
        Input.F6_key_down = False
        Input.F7_key_down = False
        Input.F8_key_down = False
        Input.F9_key_down = False
        Input.F10_key_down = False
        Input.F11_key_down = False
        Input.F12_key_down = False
        Input.F13_key_down = False
        Input.F14_key_down = False
        Input.F15_key_down = False

        Input.lockNumber_key_down = False
        Input.capsLock_key_down = False
        Input.scrolLock_key_down = False
        Input.rightShift_key_down = False
        Input.leftShift_key_down = False
        Input.rightControl_key_down = False
        Input.leftControl_key_down = False
        Input.rightAlt_key_down = False
        Input.leftAlt_key_down = False
        Input.rightMeta_key_down = False
        Input.leftMeta_key_down = False
        Input.leftWindows_key_down = False
        Input.rightWindows_key_down = False
        Input.mode_key_down = False
        Input.help_key_down = False
        Input.print_key_down = False
        Input.sysreq_key_down = False
        Input.break_key_down = False
        Input.menu_key_down = False
        Input.power_key_down = False
        Input.euro_key_down = False
        Input.androidBack_button_down = False

        Input.left_mouseClick_down = False
        Input.right_mouseClick_down = False
        Input.middle_mouseClick_down = False
        Input.scrollUp_mouseWheel_down = False
        Input.scrollDown_mouseWheel_down = False
        #endregion

        #KeyUp Inputs
        #region
        Input.backspace_key_up = False
        Input.tab_key_up = False
        Input.clear_key_up = False
        Input.return_key_up = False
        Input.pause_key_up = False
        Input.escape_key_up = False
        Input.space_key_up = False
        Input.exclaimationMark_key_up = False
        Input.quotedbl_key_up = False
        Input.hashtag_key_up = False
        Input.dollar_key_up = False
        Input.eCommercial_key_up = False
        Input.quote_key_up = False
        Input.leftParentesis_key_up = False
        Input.rightParentesis_key_up = False
        Input.asterisk_key_up = False
        Input.plus_key_up = False 
        Input.comma_key_up = False
        Input.minus_key_up = False
        Input.dot_key_up = False
        Input.slash_key_up = False
    
        Input.number0_key_up = False
        Input.number1_key_up = False
        Input.number2_key_dup = False
        Input.number3_key_up = False
        Input.number4_key_up = False
        Input.number5_key_up = False
        Input.number6_key_up = False
        Input.number7_key_up = False
        Input.number8_key_up = False
        Input.number9_key_up = False
    
        Input.colon_key_up = False
        Input.semicolon_key_up = False
        Input.lessArrow_key_up = False
        Input.equal_key_up = False
        Input.greaterArrow_key_up = False
        Input.questionMark_key_up = False
        Input.at_key_up = False
        Input.leftBracket_key_up = False
        Input.backslash_key_up = False
        Input.rightBracket_key_up = False
        Input.caret_key_up = False
        Input.underscore_key_up = False
        Input.backquote_key_up = False
    
        Input.a_key_up = False
        Input.b_key_up = False
        Input.c_key_up = False
        Input.d_key_up = False
        Input.e_key_up = False
        Input.f_key_up = False
        Input.g_key_up = False
        Input.h_key_up = False
        Input.i_key_up = False
        Input.j_key_up = False
        Input.k_key_up = False
        Input.l_key_up = False
        Input.m_key_up = False
        Input.n_key_up = False
        Input.o_key_up = False
        Input.p_key_up = False
        Input.q_key_up = False
        Input.r_key_up = False
        Input.s_key_up = False
        Input.t_key_up = False
        Input.u_key_up = False
        Input.v_key_up = False
        Input.w_key_up = False
        Input.x_key_up = False
        Input.y_key_up = False
        Input.z_key_up = False

        Input.delete_key_up = False
        Input.keypad0_key_up = False
        Input.keypad1_key_up = False
        Input.keypad2_key_up = False
        Input.keypad3_key_up = False
        Input.keypad4_key_up = False
        Input.keypad5_key_up = False
        Input.keypad6_key_up = False
        Input.keypad7_key_up = False
        Input.keypad8_key_up = False
        Input.keypad9_key_up = False
        Input.keypadPeriod_key_up = False
        Input.keypadDivide_key_up = False
        Input.keypadMultiply_key_up = False
        Input.keypadMinus_key_up = False
        Input.keypadPlus_key_up = False
        Input.keypadEnter_key_up = False
        Input.keypadEquals_key_up = False
        Input.keypadUp_key_up = False
        Input.keypadDown_key_up = False
        Input.keypadRight_key_up = False
        Input.keypadLeft_key_up = False
        Input.keypadInsert_key_up = False
        Input.keypadHome_key_up = False
        Input.keypadEnd_key_up = False
        Input.keypadPageUp_key_up = False
        Input.keypadPageDown_key_up = False
    
        Input.F1_key_up = False
        Input.F2_key_up = False
        Input.F3_key_up = False
        Input.F4_key_up = False
        Input.F5_key_up = False
        Input.F6_key_up = False
        Input.F7_key_up = False
        Input.F8_key_up = False
        Input.F9_key_up = False
        Input.F10_key_up = False
        Input.F11_key_up = False
        Input.F12_key_up = False
        Input.F13_key_up = False
        Input.F14_key_up = False
        Input.F15_key_up = False

        Input.lockNumber_key_up = False
        Input.capsLock_key_up = False
        Input.scrolLock_key_up = False
        Input.rightShift_key_up = False
        Input.leftShift_key_up = False
        Input.rightControl_key_up = False
        Input.leftControl_key_up = False
        Input.rightAlt_key_up = False
        Input.leftAlt_key_up = False
        Input.rightMeta_key_up = False
        Input.leftMeta_key_up = False
        Input.leftWindows_key_up = False
        Input.rightWindows_key_up = False
        Input.mode_key_up = False
        Input.help_key_up = False
        Input.print_key_up = False
        Input.sysreq_key_up = False
        Input.break_key_up = False
        Input.menu_key_up = False
        Input.power_key_up = False
        Input.euro_key_up = False
        Input.androidBack_button_up = False

        Input.left_mouseClick_up = False
        Input.right_mouseClick_up = False
        Input.middle_mouseClick_up = False
        Input.scrollUp_mouseWheel_up = False
        Input.scrollDown_mouseWheel_up = False
        
        Input.left_mouseClick_down = False
        Input.right_mouseClick_down = False
        Input.middle_mouseClick_down = False
        Input.scrollUp_mouseWheel_down = False
        Input.scrollDown_mouseWheel_down = False
        #endregion

class ColorRGB():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This class manages RGB colors (red, green, blue) and their values.
    There are some default colors you can access from their functions.

    NOTES:
    Defaults colors are functions because in this way are read-only.


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -r:             int or float        red channel. It represents the amount of red in the final color from 0 to 255.
    -g:             int or float        green channel. It represents the amount of green in the final color from 0 to 255.
    -b:             int or float        blue channel. It represents the amount of blue in the final color from 0 to 255.
    -color:         tuple               tuple representation of the color (r, g, b)     

    FUNCTIONS:

    STATIC:
    -light_red
    -red
    -dark_red
    -light_green
    -green
    -dark_green
    -light_blue
    -def blue
    -dark_blue
    -deep_blue
    -white
    -light_grey      
    -grey      
    -dark_grey      
    -black
    -light_yellow
    -yellow
    -dark_yellow
    -sand_yellow
    -light_orange
    -orange
    -dark_orange
    -salmon_orange
    -light_cyan
    -cyan
    -dark_cyan
    -light_pink
    -pink
    -magenta
    -dark_pink
    -light_brown
    -brown
    -dark_brown
    -light_purple
    -purple
    -dark_purple
    -soft_purple
    -ConvertToColorRGB
    -RandomColorRGB

    INSTANCE:
    -__init__

    SYSTEM:
    None

    """

    def __init__(self, r, g, b):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new color. The channels are clamped between 0 and 255.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -r:         int or float        red channel. It represents the amount of red in the final color from 0 to 255.
        -g:         int or float        green channel. It represents the amount of green in the final color from 0 to 255.
        -b:         int or float        blue channel. It represents the amount of blue in the final color from 0 to 255.

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
        """

        assert type(r) == int or type(r) == float, "'r' has to be a number!"
        assert type(g) == int or type(r) == float, "'g' has to be a number!"
        assert type(b) == int or type(r) == float, "'b' has to be a number!"

        self.r = Mathf.Clamp(r, 0, 255)
        self.g = Mathf.Clamp(g, 0, 255)
        self.b = Mathf.Clamp(b, 0, 255)
        self.color = (self.r, self.g, self.b)

    #Default Colors
    #region

    #Red
    #region
    def light_red():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(255, 77, 77).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 77, 77)

    def red():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns red ColorRGB(255, 0, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255,0,0)

    def dark_red():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark red ColorRGB(128, 0, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(128, 0, 0)
    #endregion

    #Green
    #region
    def light_green():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light green ColorRGB(102, 255, 51).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(102, 255, 51)

    def green():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns green ColorRGB(0, 255, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0,255,0)

    def dark_green():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(0, 102, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0, 102, 0)
    #endregion

    #Blue
    #region
    def light_blue():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(51, 102, 255).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(51, 102, 255)

    def blue():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(0, 0, 255).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0,0,255)

    def dark_blue():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(0, 0, 102).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0, 0, 102)

    def deep_blue():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(0, 51, 102).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0, 51, 102)
    #endregion

    #White, grey and black
    #region
    def white():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns white ColorRGB(255, 255, 255).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255,255,255)

    def light_grey():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light grey ColorRGB(217, 217, 217).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(217, 217, 217)

    def grey():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns grey ColorRGB(140, 140, 140).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(140, 140, 140)

    def dark_grey():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark grey ColorRGB(64, 64, 64).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(64, 64, 64)

    def black():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light red ColorRGB(0, 0, 0)

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0,0,0)
    #endregion

    #Yellow
    #region
    def light_yellow():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light yellow ColorRGB(255, 255, 102).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 255, 102)

    def yellow():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns yellow ColorRGB(255, 255, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 255, 0)

    def dark_yellow():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark yellow ColorRGB(204, 204, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(204, 204, 0)

    def sand_yellow():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns sand yellow ColorRGB(255, 204, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 204, 0)
    #endregion

    #Orange
    #region
    def light_orange():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light orange ColorRGB(255, 133, 51).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 133, 51)

    def orange():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns orange ColorRGB(255, 102, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 102, 0)

    def dark_orange():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark orange ColorRGB(179, 71, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(179, 71, 0)

    def salmon_orange():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns salmon orange ColorRGB(255, 153, 51).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 153, 51)
    #endregion

    #Cyan
    #region
    def light_cyan():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light cyan ColorRGB(77, 255, 255).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(77, 255, 255)

    def cyan():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns cyan ColorRGB(0, 255, 255).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0, 255, 255)

    def dark_cyan():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark cyan ColorRGB(0, 179, 179).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(0, 179, 179)
    #endregion

    #Pink
    #region
    def light_pink():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light pink ColorRGB(255, 102, 204).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 102, 204)

    def pink():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns pink ColorRGB(255, 51, 153).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 51, 153)

    def magenta():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns magenta ColorRGB(255, 0, 255).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(255, 0, 255)

    def dark_pink():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark pink ColorRGB(102, 0, 51).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(102, 0, 51)
    #endregion

    #Brown
    #region
    def light_brown():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light brown ColorRGB(153, 102, 51).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(153, 102, 51)

    def brown():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns brown ColorRGB(102, 51, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(102, 51, 0)

    def dark_brown():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark brown ColorRGB(51, 26, 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(51, 26, 0)
    #endregion

    #Purple
    #region
    def light_purple():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns light purple ColorRGB(153, 0, 204).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(153, 0, 204)

    def purple():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns purple ColorRGB(102, 0, 102).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(102, 0, 102)

    def dark_purple():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns dark purple ColorRGB(51, 0, 51).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(51, 0, 51)

    def soft_purple():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns soft purple ColorRGB(153, 51, 153).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(153, 51, 153)
    #endregion

    #endregion

    def ConvertToColorRGB(varToConvert):
        """
        STATIC FUNCTION

        DESCRIPTION: 
        Converts the parameter to ColorRGB.

        NOTES: 
        This is meant to convert rgb colors represented in tuples, lists, ecc. in ColorRGB.
        This function works with every indexable. The parameter has to have at least 3 indexes (first for red, second for green, third for blue, all others are ignored).

        PARAMETERS:
        REQUIRED:
        -varToConvert:          list or tuple (or another indexable)       the variable that holds the rgb color but in a different type of value.

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if type(varToConvert) == ColorRGB:
            return varToConvert
        else:
            try:
                return ColorRGB(varToConvert[0], varToConvert[1], varToConvert[2])
            except:
                assert 1 == 2, "Error: the parameter 'varToConvert' must be an indexable type!"
                

    def RandomColorRGB():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a random color.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return ColorRGB(random.randint(0,255),random.randint(0,255),random.randint(0,255))


    def HexToRGB(hex):
        """
        STATIC FUNCTION

        DESCRIPTION: 
        Converts the hex color to ColorRGB and returns it.

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        -hex:           string          the hex value of the color

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        hex = hex.lstrip('#')
        return ColorRGB.ConvertToColorRGB(tuple(int(hex[i:i+2], 16) for i in (0, 2, 4)))

class Palette():
    
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This class is used to organise your ColorRGBs in palettes, with names and descriptions.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -paletteName:           string          the name of your palette
    -paletteDescription:    string          the description of your palette
    -colorNames:            list            a list containing all the names of the colors in your palette
    -__colors__:            dictionary      the dictionary core of the class. It contains all the colors and their names  

    FUNCTIONS:

    STATIC:
    -ImportPalette

    INSTANCE:
    -__init__
    -GetColors
    -GetColor
    -SetColor
    -RemoveColor
    -ExportPalette
    -PaletteSpecs

    SYSTEM:
    -__str__

    """

    def __init__(self, paletteName, paletteDescription, nameColor, colorRGB):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new palette.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -paletteName:               string                              the name of your palette
        -paletteDescription:        string                              the description for your palette
        -nameColor:                 list                                name of your ColorRGB or list of names of ColorRGBs that compose your palette
        -colorRGB:                  list of ColorRGBs or ColorRGB       ColorRGB or list of ColorRGBs that compose your palette

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        assert type(paletteName) == str, "'paletteName' has to be type of 'str'!"
        assert type(paletteDescription) == int or type(paletteDescription) == str, "'paletteDescription' has to be type of 'str'!"

        self.paletteName = paletteName
        self.paletteDescription = paletteDescription
        self.__colors__ = {}

        for index in range (0, len(colorRGB)):
            try:
                color = colorRGB[index]
                if type(color) == tuple:
                    col = ColorRGB(color[0], color[1], color[2])
                    color = col

            except IndexError: 
                print("ColorError: couldn't add color to palette. Color of index ", index, "in colorRGB argument not found!", colorRGB)
            
            try:
                self.__colors__[nameColor[index]] = color
            except IndexError:
                print("ColorNameError: couldn't add color to palette. NameColor of index ", index, "in nameColor argument not found!", colorRGB)

        self.colorNames = nameColor

    def GetColors(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns the dictionary containing all of the colors of your palette.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return self.__colors__

    def GetColor(self, colorName):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns the ColorRGB associated with the colorName key.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -colorName:         var         the key associated to the color

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        try:
            return self.__colors__[colorName]
        except KeyError:
            print("KeyError: key ", colorName, " not found in palette ", self.paletteName, "!")

    def SetColor(self, colorName, colorRGB):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Adds a ColorRGB associated with the colorName to your palette.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -colorName:         var         the key associated to the color
        -colorRGB:          ColorRGB    the color you want to add to the palette

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.__colors__[colorName] = colorRGB
        self.colorNames.append(colorName)
    
    def RemoveColor(self, colorName):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Removes the ColorRGB associated with the colorName key from your palette.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -colorName:         var         the key associated to the color

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        try:
            self.__colors__.pop(colorName)
            self.colorNames.remove(colorName)
        except:
            print("Error: failed to remove color '", colorName, "' in the ", self.paletteName, "palette. The color name is probably wrong")

    def ExportPalette(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Exports the palette in a text file.

        NOTES:
        The name of the file of the palette is self.paletteName + '_palette.txt' suffix to make management of palettes name more clear.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        #We create a file and initilize the name and description of the palette
        paletteFile = open(self.paletteName + "_palette.txt", "w")
        fileContain = self.paletteName + "\n" + self.paletteDescription + "\n"

        #We subdivide each information of the palette in a new line
        for colorName in self.colorNames:
            fileContain += colorName + "\n"
            color = self.GetColor(colorName)
            fileContain += str(color.r) + "\n"
            fileContain += str(color.g) + "\n"
            fileContain += str(color.b) + "\n"

        #We write the informations on the file
        try:
            if paletteFile.write(fileContain) == len(fileContain):
                print("The palette ", self.paletteName, "was exported sucessfully")
            else:
                print("The palette ", self.paletteName, "WASN'T exported sucessfully")
        
        #We close the file whatever happens
        finally:
            paletteFile.close()
            
    def ImportPalette(fileName):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Imports the palette stored in a text file. 
        

        NOTES:
        To the fileName passed as argument is automatically added '_palette.txt' suffix to make management of palettes name more clear
        (you don't specify the file extension ecc. passing the argument).

        PARAMETERS:
        REQUIRED:
        -fileName:      string      the path to your file

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        #The text file containing the exported palette
        try:
            file = open(fileName + "_palette.txt", "r")
        except FileNotFoundError:
            print("FileNotFoundError: the file ", fileName, "was not found!")

        content = file.read()
        contentLines = content.split("\n")

        #The first two lines are the name of the palette and the description
        paletteName = contentLines[0]
        paletteDescription = contentLines[1]

        #Lists we use later to reassembly our palette
        colorList = []
        nameColorList = []

        #We use the while to go by 4 steps. 
        #We subtract 1 to the lenght of contentLines because 
        #at the last line there's a "\n" character
        index = 2
        while index < len(contentLines) - 1:
            #Every color occupies 4 lines: 
            #the first is the name of the color, 
            #the second the red channel
            #the third the green channel and the fourth the blue channel
            colorName = contentLines[index]
            colorR = float(contentLines[index+1])
            colorG = float(contentLines[index+2])
            colorB = float(contentLines[index+3])

            #We use the channel values obtained to create a new ColorRGB
            newColor = ColorRGB(colorR, colorG, colorB)

            colorList.append(newColor)
            nameColorList.append(colorName)
            index += 4

        importedPalette = Palette(paletteName, paletteDescription, nameColorList, colorList)
        
        file.close()
        return importedPalette

    def PaletteSpecs(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns a string containing the palette name and description.
        

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return "Palette " + self.paletteName + ": " + self.paletteDescription
    
    def __str__(self):
        """
        SYSTEM FUNCTION

        DESCRIPTION:
        Converts your palette in a string containing your palette name and description and all your palette colorNames associated with the ColorRGBs.
        

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        paletteString = self.PaletteSpecs() + "\n"
        for colorName in self.colorNames:
            paletteString += colorName +"\t"
            paletteString += str(self.GetColor(colorName).color)+ "\n"

        return paletteString

class Vector2():
    """
    STATIC CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This class is used to represent Vectors and points in a 2D space.


    NOTES:
    Note that the coordinates are (0,0) in the top left of the screen and (width of the screen, height of the screen) in the bottom right.
    In other words the origin is set in the top left corner.


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -x:         int or float        the x coordinate (horizontal)
    -y:         int or float        the y coordinate (vertical)


    FUNCTIONS:

    STATIC:
    -zero
    -one
    -left
    -right
    -up
    -down
    -screenCenter
    -CenterGameObjectInPosition
    -RandomIntegerVectorInScreen
    -RectToVector2
    -ConvertToVector2
    -DistanceBetweenTwoPoints
    

    INSTANCE:
    -__init__
    -DivideByNumber
    -MultiplyByNumber
    -Vector2ToRect
    -Vector2ToTuple

    SYSTEM:
    -__add__
    -__sub__
    -__mul__
    -__truediv__
    -__str__

    """
    
    def __init__(self, x = 0, y = 0):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new Vector2.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -x:         int or float        the x coordinate (horizontal)
        -y:         int or float        the y coordinate (vertical)

        DEFAULTS OF OPTIONAL VALUES:
        -x:         int or float        0
        -y:         int or float        0

        """
        

        #Make sure that both x and y are numbers
        assert type(x) == int or type(x) == float, "'x' component of the vector has to be a number!"
        assert type(y) == int or type(y) == float, "'y' component of the vector has to be a number!"
        self.x = x
        self.y = y

    def __add__(self, other):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Override that adds two Vector2.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -other:     Vector2     the Vector2 you want to add

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if type(other) == int or type(other) == float:
            newX = self.x + other
            newY = self.y + other
            return Vector2(newX, newY)
        elif type(other) == Vector2:
            newX = self.x + other.x
            newY = self.y + other.y
            return Vector2(newX, newY)
        elif type(other) == tuple:
            newX = self.x + other[0]
            newY = self.y + other[1]
            return Vector2(newX, newY)
        else:
            raise TypeError

    def __sub__(self, other):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Override that subtracts two Vector2.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -other:     Vector2     the Vector2 you want to subtract

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        newX = self.x - other.x
        newY = self.y - other.y
        return Vector2(newX, newY)

    def __mul__(self, other):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Multiplies both x and y of the Vector2 by the same number.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -other         int or float        the number you want to divide the Vector2 with

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if type(other) == int or type(other) == float:
            return Vector2.MultiplyByNumber(self, other)
        else:
            raise TypeError

    def __truediv__(self, other):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Divides both x and y of the Vector2 by the same number.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -other         int or float        the number you want to divide the Vector2 with

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if type(other) == int or type(other) == float:
            return Vector2.DivideByNumber(self, other)
        else:
            raise TypeError

    def __str__(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Converts the Vector2 to string.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return "(" + str(self.x) + "," + str(self.y) +")"

    def DivideByNumber(self, number):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Divides both x and y of the Vector2 by the same number.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -number         int or float        the number you want to divide the Vector2 with

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        newX = self.x/number
        newY = self.y/number
        return Vector2(newX, newY)

    def MultiplyByNumber(self, number):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Multiplies both x and y of the Vector2 by the same number.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -number         int or float        the number you want to divide the Vector2 with

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        newX = self.x*number
        newY = self.y*number
        return Vector2(newX, newY)

    def zero():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Shorthand to write Vector2(0,0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(0,0)

    def one():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Shorthand to write Vector2(1,1).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(1,1)

    def left():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Shorthand to write Vector2(-1,0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(-1,0)

    def right():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Shorthand to write Vector2(1,0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(1,0)

    def up():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Shorthand to write Vector2(0,1).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(0,1)

    def down():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Shorthand to write Vector2(0,-1).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(0,-1)

    def screenCenter():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns the center of the screen.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(Screen.width/2, Screen.height/2)

    def CenterGameObjectInPosition(position, gameObjectWidth, gameObjectHeight):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns the position considering the dimensions of a gameObject, so the center of the gameObject is in that position.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -position:          Vector2             the position you want to set the gameObject in
        -objectWidth:       int or float        the width of the gameObject
        -objectHeight:      int or float        the height of the gameObject

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(position.x - gameObjectWidth/2, position.y - gameObjectHeight/2)

    def CenterGameObjectInPosition(position, gameObjectDimension):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns the position considering the dimensions of a gameObject, so the center of the gameObject is in that position.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -position:                  Vector2             the position you want to set the gameObject in
        -gameObjectDimension:       Vector2             the dimensions of the gameObject

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(position.x - gameObjectDimension.x/2, position.y - gameObjectDimension.y/2)

    def RandomIntegerVectorInScreen():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a random Vector2 in screen.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Vector2(random.randint(0, Screen.width), random.randint(0, Screen.height))

    def RectToVector2(rect):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Converts the position of a pygame rect to a Vector2.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -rect:          pygame.rect.Rect        the rect you want to convert the position from

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        return Vector2(rect.x, rect.y)

    def Vector2ToRect(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns a rect with the x and y of the Vector2. Width and height are 0.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return pygame.rect.Rect(self.x, self.y, 0, 0)

    def ConvertToVector2(coordinates):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Converts the coordinates in Vector2 type. 
        

        NOTES:
        Supports conversion for everything that can be indexed (access the first and second elements), like tuples or lists.

        PARAMETERS:
        REQUIRED:
        -coordinates:          list or tuple (or another indexable)        the coordinates you want to convert

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        try:
            return Vector2(coordinates[0], coordinates[1])
        except:
            print("Invalid argument in conversion to 'Vector2' !")
            return None

    def Vector2ToTuple(self):

        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Converts the Vector2 in a tuple (x, y).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        try:
            return (self.x, self.y)
        except:
            print("Invalid argument in conversion to 'tuple' !")
            return None

    def DistanceBetweenTwoPoints(point1, point2):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns the distance between the points 'point1' and 'point2'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -point1:        Vector2         the first point
        -point2:        Vector2         the second point

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        dist = math.sqrt(pow((point1.x - point2.x), 2) + pow((point1.y - point2.y), 2))
        return dist

class Transform():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This class is used to manage the position, dimension and rotation of the gameObjects.


    NOTES:
    The origin of a gameObject is set in the upper left corner of the square created by its dimensions.
    Use functions as Vector2.CenterGameObjectInPosition() to set the center of the gameObjet in the position you want.


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -position:          Vector2             the position of the origin of the gameObject (upper left corner) 
    -dimension:         Vector2             the dimensions of the gameObject on the x and y axis
    -rotation:          int or float        the rotation of the gameObject (negative = clockwise, positive = counterclockwise)



    FUNCTIONS:

    STATIC:
    -DefaultValues
    -RandomTransform
    -GetCenter
    -TransformWithRandomPositionInScreen
    -TransformWithRandomDimensionInScreen
    -TransformWithRandomRotationIn360Degrees
    

    INSTANCE:
    -__init__
    -Copy

    SYSTEM:
    None

    """

    def __init__(self, position, dimension, rotation = 0):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Creates a new Transform.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -position:          Vector2             the position of the origin of the gameObject (upper left corner) 
        -dimension:         Vector2             the dimensions of the gameObject on the x and y axis

        OPTIONAL:
        -rotation:          int or float        the rotation of the gameObject (negative = clockwise, positive = counterclockwise)

        DEFAULTS OF OPTIONAL VALUES:
        -rotation:          int or float        0
         
        """
        
        assert type(position) == Vector2, "'Position' has to be type of 'Vector2'!"
        assert type(dimension) == Vector2, "'Dimension' has to be type of 'Vector2'!"
        assert type(rotation) == int or type(rotation) == float, "'Rotation' has to be a number!"
        
        self.position = position
        self.rotation = rotation
        self.dimension = dimension

    def DefaultValues():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns Transform(Vector2.zero(), Vector2.zero(), 0).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
         
        """
        return Transform(Vector2.zero(), Vector2.zero(), 0)

    def RandomTransform():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a Transform with random values (but clamped to the screen size).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
         
        """
        return Transform(Vector2.RandomIntegerVectorInScreen(), Vector2.RandomIntegerVectorInScreen(), Vector2.RandomIntegerVectorInScreen().x)

    def GetCenter(self):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns in a Vector2 the center of the gameObject.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
         
        """
        return Vector2(self.position.x + self.dimension.x//2, self.position.y + self.dimension.y//2)

    def TransformWithRandomPositionInScreen(dimension = Vector2.zero(), rotation = 0):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a Transform of the given dimension and rotation but with a random position on screen.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -dimension:         Vector2             the dimensions of the gameObject
        -rotation:          int or float        the rotation of the gameObject

        DEFAULTS OF OPTIONAL VALUES:
        -dimension:         Vector2             Vector2.zero()
        -rotation:          int or float        0
         
        """
        assert type(dimension) == Vector2, "'Dimension' has to be type of 'Vector2'!"
        assert type(rotation) == int or type(rotation) == float, "'Rotation' has to be a number!"
        return Transform(Vector2.RandomIntegerVectorInScreen(), dimension, rotation)

    def TransformWithRandomDimensionInScreen(position = Vector2.zero(), rotation = 0):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a Transform in the given position and rotation but with a random dimension (clamped to the screen size).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -position:          Vector2             the position of the gameObject
        -rotation:          int or float        the rotation of the gameObject

        DEFAULTS OF OPTIONAL VALUES:
        -position:          Vector2             Vector.zero()
        -rotation:          int or float        0
         
        """
        assert type(position) == Vector2, "'Position' has to be type of 'Vector2'!"
        assert type(rotation) == int or type(rotation) == float, "'Rotation' has to be a number!"
        return Transform(position, Vector2.RandomIntegerVectorInScreen(), rotation)

    def TransformWithRandomRotationIn360Degrees(position = Vector2.zero(), dimension = Vector2.zero()):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a Transform in the given position and dimensions but with a random rotation from -360 to 360 degrees.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -position:          Vector2             the position of the gameObject
        -dimension:         Vector2             the dimensions of the gameObject

        DEFAULTS OF OPTIONAL VALUES:
        -position:          Vector2             Vector.zero()
        -dimensions:        Vector2             Vector.zero()
         
        """
        return Transform(position, dimension, random.randint(-360, 360))

    def Copy(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns a copy of the Transform.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
         
        """
        return Transform(self.position, self.dimension, self.rotation)

class ComponentTransform():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Class used to manage the components' Transform.
    It holds the reference Transform (the Transform passed in the init method of the Component) and the personal Transform of the component.
    To update the personal Transform of the component to to the reference one, without altering it (so you can add an offset without moving the reference Transform) call the UpdateTransform method in the Component's Update().


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -selfTransform:             Transform           the private transform of the Component
    -referenceTransform:        Transform           the reference Transform of the Component
    -position_offset:           Vector2             the offset from the referenceTransform's position
    -dimension_offset:          Vector2             the offset from the referenceTransform's scale
    -rotation_offset:           int or float        the offset from the referenceTransform's rotation



    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -UpdateTransform
    -UpdatePositionX
    -UpdatePositionY
    -UpdateDimensionX
    -UpdateDimensionY
    -UpdatePosition
    -UpdateDimension
    -UpdateRotation

    SYSTEM:
    None

    """
    
    def __init__(self, referenceTransform, position_offset, dimension_offset, rotation_offset):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new ComponentTransform.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -referenceTransform:        Transform           the reference Transform of the Component
        -position_offset:           Vector2             the offset from the referenceTransform's position
        -dimension_offset:          Vector2             the offset from the referenceTransform's scale
        -rotation_offset:           int or float        the offset from the referenceTransform's rotation

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        self.selfTransform = referenceTransform.Copy()
        self.referenceTransform = referenceTransform
        self.position_offset = position_offset
        self.rotation_offset = rotation_offset
        self.dimension_offset = dimension_offset

    def UpdateTransform(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates the transform and adds the offsets.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.position = self.referenceTransform.position + self.position_offset
        self.selfTransform.dimension = self.referenceTransform.dimension + self.dimension_offset
        self.selfTransform.rotation = self.referenceTransform.rotation + self.rotation_offset

    def UpdatePositionX(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates only the x position of the transform and adds the offset.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.position.x = self.referenceTransform.position.x + self.position_offset.x
        
    def UpdatePositionY(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates only the y position of the transform and adds the offset.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.position.y = self.referenceTransform.position.y + self.position_offset.y
        
    def UpdateDimensionX(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates only the x dimension of the transform and adds the offset.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        
        self.selfTransform.dimension.x = self.referenceTransform.dimension.x + self.dimension_offset.x

    def UpdateDimensionY(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates only the y dimension of the transform and adds the offset.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.dimension.y = self.referenceTransform.dimension.y + self.dimension_offset.y

    def UpdatePosition(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates the position and adds the offsets.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.position = self.referenceTransform.position + self.position_offset
        
    def UpdateDimension(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates the dimension and adds the offsets.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.dimension = self.referenceTransform.dimension + self.dimension_offset
        
    def UpdateRotation(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates only the rotation of the transform and adds the offset.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.selfTransform.rotation = self.referenceTransform.rotation + self.rotation_offset

class AudioClip():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Create audioclips to play at runtime.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -path:              string                      the path of the audioclip. Make sure to include the file extension! 
    -loops:             int                         how many times the audioclip is played consecutively. -1 means it loops forever
    -audioclip:         pygame.mixer.Sound          the audioclip core


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -Play
    -SetVolume

    SYSTEM:
    None

    """

    def __init__(self, path, loops = 0):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new AudioClip.

        NOTES:
        Make sure to include the file extension in the path!
        loops = -1 means the clip loops forever (for example goood in background music).

        PARAMETERS:
        REQUIRED:
        -path:              string                      the path of the audioclip. Make sure to include the file extension! 

        OPTIONAL:
        -loops:             int                         how many times the audioclip is played consecutively. -1 means it loops forever
    
        DEFAULTS OF OPTIONAL VALUES:
        -loops:             int                         0

        """
        self.audioclip = pygame.mixer.Sound(path)
        self.loops = loops

    def Play(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Plays the audioClip with its loops.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None
    
        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.audioclip.play(loops = self.loops)

    def SetVolume(self, volume):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Sets the volume of the audioclip.

        NOTES:
        The volume you can set is a value between 0 and 1, like a multiplier of the original volume of the file.

        PARAMETERS:
        REQUIRED:
        -volume:        float       value between 0 and 1, like a multiplier of the original volume of the file

        OPTIONAL:
        None
    
        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.audioclip.set_volume(volume)

#==================== GAMEOBJECTS ====================

class GameObject():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This is the base class, from which all the others have to inherit (if the class is an object that, for example, needs to be rendered on screen).
    Contains methods to be overloaded in your derived class.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -name:                  string          the name of the object. Default is "GameObject"
    -transform:             Transform       the transform of the gameObject. All gameObjects must have a transform
    -dontDestroyOnLoad:     bool            True means the gameObject is not destroyed when a different scene is loaded from the SceneManager (if you want to learn more, see documentation for Scene and SceneManager classes) 
        

    FUNCTIONS:

    STATIC:
    -Instantiate
    -Destroy
    -ActiveGameObjectsNames_print
    -ActiveGameObjects_print
    -ActiveGameObjects
    -FindGameObjectOfType
    -FindGameObjectsOfType
    -FindGameObjectOfName
    -FindGameObjectsOfName
    


    INSTANCE:
    -__init__
    -Draw
    -Awake
    -Start
    -Update
    -OnInstantiate
    -Ondestroy
    -OnExit
    -OnCollisionEnter
    -OnCollisionStay
    -OnCollisionExit
    -CustomCallback
    -AddComponentByInstance
    -AddComponentByType
    -RemoveComponentByInstance
    -RemoveComponentByType
    -GetComponent
    -GetComponentForSure


    SYSTEM:
    -__str__
    """
    #Engine Methods
    def __init__(self, name = "GameObject", transform = Transform.DefaultValues(), autoInstantiate = False, dontDestroyOnLoad = False):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new GameObject.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -name:                  string          the name of the gameObject
        -transform:             Transform       the Transform of the GameObject
        -autoInstantiate:       bool            True means it automatically spawns the gameObject at the end of the init method, False means not
        -dontDestroyOnLoad:     bool            True means the gameObject is not destroyed when a different scene is loaded from the SceneManager (if you want to learn more, see documentation for Scene and SceneManager classes) 
        
        DEFAULTS OF OPTIONAL VALUES:
        -name:                  string          "GameObject"
        -transform:             Transform       Transform.DefaultValues()
        -autoInstantiate:       bool            False
        -dontDestroyOnLoad:     bool            False
        
        """
        
        assert type(name) == str, "'name' has to be type of 'str'!"
        assert type(transform) == Transform, "'transform' has to be type of 'Transform'!"
        self.name = name
        self.transform = transform
        self.dontDestroyOnLoad = dontDestroyOnLoad
        self.components = []
        if autoInstantiate == True:
            GameObject.Instantiate(self)
    
    def __str__(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Converts the gameObject to string (type of GameObject).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        name = str(type(self))
        name = name.split(".")[1]
        name = name.replace("'>", "")
        name = name.replace(" ", "")
        return name

    #Instances managing methods
    #region
    def Instantiate(gameObject, position = None):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Instantiates the GameObject gameObject in position passed by argument. If no position it's given, it's used the gameObject.transform.position.

        NOTES:
        Please note that creating a gameObject and instantiating it are two different thing: the first is when you create an instance of the class, the second is when you actually put it in the game.

        PARAMETERS:
        REQUIRED:
        -gameObject:     GameObject      the gameObject to instantiate (can be self)

        OPTIONAL:
        -position:       Vector2         where to instantiate the gameObject

        DEFAULTS OF OPTIONAL VALUES:
        -position:       Vector2         gameObject.transform.position

        """
        assert issubclass(type(gameObject), GameObject) , "Cannot instantiate an object that doesn't derivate from GameObject!"
        if (position == None):
            position = gameObject.transform.position
        gameObject.transform.position = position
        GameObjects.append(gameObject)
        gameObject.OnInstantiate()

    def Destroy(gameObject):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Destroys the gameObject.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -gameObject     GameObject      the gameObject to destroy (can be self)

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        assert issubclass(type(gameObject), GameObject) , "Cannot destroy an object that doesn't derivate from 'GameObject'!"
        gameObject.OnDestroy()

        #Destroys all its components
        for i in range(0, len(gameObject.components)):
            component = gameObject.components[0]    #always pick the first of the list as we shorten it
            gameObject.RemoveComponentByInstance(component)

        GameObjects.remove(gameObject)

    def ActiveGameObjectsNames_print():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Prints the names of all the GameObjects in the list 'GameObjects'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
            print(gameObject.name)

    def ActiveGameObjects_print():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Prints all the GameObjects in the list 'GameObjects'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for gameObject in GameObjects:
            print(gameObject)

    def ActiveGameObjects():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns the list 'GameObjects'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return GameObjects

    def FindGameObjectOfType(typeOfGameObject):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Search for the first occurence of a GameObject of type 'typeOfGameObject' and returns it.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -typeOfGameObject:      class       the type of the gameObject to find (for example a Player(GameObject) class would be of type 'Player')

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for obj in GameObjects:
            if type(obj) == typeOfGameObject:
                return obj
        return None

    def FindGameObjectsOfType(typeOfGameObjects):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Search for all occurrences of GameObjects of type 'typeOfGameObjects' and returns them in a list.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -typeOfGameObjects:      class       the type of the gameObjects to find (for example a Player(GameObject) class would be of type 'Player')

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        gameObjs = []
        for obj in GameObjects:
            if type(obj) == typeOfGameObjects:
                gameObjs.append(obj)
        return gameObjs

    def FindGameObjectOfName(nameOfGameObject):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Search for the first occurence of a GameObject named 'nameOfGameObject' and returns it.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -nameOfGameObject:      string       the name of the gameObject to find

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for obj in GameObjects:
            if obj.name == nameOfGameObject:
                return obj
        return None

    def FindGameObjectsOfName(nameOfGameObjects):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Search for all occurrences of GameObjects named 'nameOfGameObjects' and returns them in a list.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -nameOfGameObjects:      string       the name of the gameObjects to find

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        gameObjs = []
        for obj in GameObjects:
            if obj.name == nameOfGameObjects:
                gameObjs.append(obj)
        return gameObjs
            
    #endregion



    #Callbacks

    #Engine Callbacks
    #region
    def Draw(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Put the rendering logic here.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def Awake(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Awake is called once before Start and at the start of the game, before the first frame.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass
    
    def Start(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Start is called once at the start of the game, before the first frame.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def Update(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Update is called once per frame, after checking inputs and before rendering (gameObject.Draw() method).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def OnInstantiate(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        On Instantiate is called on the gameObject when it is being instantiated.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass
    
    def OnDestroy(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        On Destroy is called on the gameObject when it is being destroyed.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def OnExit(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        OnExit is called just before closing the application.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass
    #endregion

    #Collision Methods called by the SquareCollider Component
    #region
    def OnCollisionEnter(self, collider):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        This is called automatically by the SquareCollider Component when the collider enters a collision for the first time.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -collider       SquareCollider          the SquareCollider Component passes in this argument the collider that collided with the one on this gameObject

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def OnCollisionStay(self, collider):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        This is called automatically by the SquareCollider Component while the collider is in collision.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -collider       SquareCollider          the SquareCollider Component passes in this argument the collider that is colliding with the one on this gameObject

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def OnCollisionExit(self, collider):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        This is called automatically by the SquareCollider Component when the collider exits a collision.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -collider       SquareCollider          the SquareCollider Component passes in this argument the collider that stopped colliding with the one on this gameObject

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass
    
    #endregion

    #Custom Callback
    def CustomCallback(self, *args):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        This method is a custom callback.
        You have to call it manually. 
        It can be helpful in writing custom components.

        NOTES:
        You can pass as many arguments as you like.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -*args:         var         you can pass as many arguments as you like

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    #Components Managing
    #region
    def AddComponentByInstance(self, component):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Adds the component to the GameObject based on the instance (you can create the instance in the argument for simplicity) and returns it.

        NOTES:
        Is considered of type Component any class that derives from it.

        PARAMETERS:
        REQUIRED:
        -component:      Component       the component to add to the gameObject 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        assert issubclass(type(component), Component) , "Cannot add a component that doesn't derivate from 'Component'!"
        component.InitializeComponent(self)
        return component

    def AddComponentByType(self, componentType):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Adds the component to the GameObject based on the given type and returns it.

        NOTES:
        Is considered of type Component any class that derives from it.
        The component created has default values set in its __init__ method.

        PARAMETERS:
        REQUIRED:
        -componentType:      class       the type of component to add to the gameObject 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        assert issubclass(componentType, Component) , "Cannot add a component that doesn't derivate from 'Component'!"
        return self.AddComponentByInstance(componentType())
        
    def RemoveComponentByInstance(self, component):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Removes the component from the GameObject based on the instance of the component.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -component:      Component       the instance of the component to remove from the gameObject 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        assert issubclass(type(component), Component) , "Cannot remove a component that doesn't derivate from 'Component'!"
        try:
            component.DestroyComponent()  
        except:
            print("Component not found on the GameObject ", self)
        finally:
            return None

    def RemoveComponentByType(self, componentType):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Removes the first occurrence of a component of type 'componentType' from the gameObject.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -componentType      class       the type of the component to remove from the gameObject 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        assert issubclass(componentType, Component) , "Cannot remove a component that doesn't derivate from 'Component'!"
        try:
            component = self.GetComponent(componentType)
            component.DestroyComponent()  
        except:
            print("Component not found on the GameObject ", self)
        finally:
            return None

    def GetComponent(self, componentType):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Gets the first found component of type 'componentType' in the GameObject. If there isn't, returns 'None'. 

        NOTES:
        You don't need a 'GetComponent' method based on the instance because if you have reference to the instance to pass in the function, it means that you don't need to get it :)

        PARAMETERS:
        REQUIRED:
        -componentType      class       the type of the component to get from the gameObject 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        componentChosen = None
        for component in self.components:
            if type(component == componentType):
                componentChosen = component
                return componentChosen
        return None

    def GetComponentForSure(self, typeComponentToSearch):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Gets the component in the GameObject. If there isn't, it adds one by type and returns it. 

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -typeComponentToSearch      class       the type of the component to get from the gameObject or eventually add to it

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        componentChosen = self.GetComponent(typeComponentToSearch)
        if componentChosen == None:
            componentChosen = self.AddComponentByType(typeComponentToSearch)
        return componentChosen
    #endregion


class Console(GameObject):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    GameObject


    DESCRIPTION:
    Console gameObject is used for debugging.
    You can assign up to ten shortcuts and call them using TAB + number (ex. TAB+1). 
    Note that you can also assign a list of methods to a single shortcut.
    You can call Console.ToggleShortcuts to enable or disable the shortcuts.
    You can have text on screen to show variables.
    You can call Console.ToggleDebugText to render or not all the debug textes.
    You can call Console.ToggleConsole to toggle both the debugTextes and the shortcuts.

    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    -first_instance:                     Console                 used to determine which is the first created instance of the Console class (not the first Instantiated GameObject)

    INSTANCE:
    -shortcuts:                          dictionary              dictionary that keeps track of the shortcuts and relative methods
    -debugText_slots:                    int                     how many text slots you want
    -debugText_font:                     font                    the font used in the text slots
    -debugText_horizontalAlignement:     bool                    if True, the texts are placed horizontally from left to right. If False, they are placed vertically 
    -debugText_spacing:                  int or float            extra spacing between texts. It may be useful to adjust things if the font size gets in the way, or things like that
    -debugText_dimensions:               Vector2                 the dimensions of a single text slot
    -debugText_area:                     Transfom                transform from which depend all the texts. The dimension of the texts is calculated from the dimension of the text area and spacing. 
                                                                 You can change the position of the text area to change the position of all the texts
    -debugText_texts:                    list                    list containing the texts to write on the text slots
    -__shortcuts_enabled:                bool                    if True, Console shortcuts are enabled
    -__debugText_enabled:                bool                    if True, Console debug texts are enabled



    FUNCTIONS:

    STATIC:
    -SetDebugShortcut
    -ToggleShortcuts
    -ToggleDebugText
    -ToggleConsole

    INSTANCE:
    -__init__
    -WriteOnTextLog

    SYSTEM:
    -__InitializeShortcuts
    -__CheckShortcuts
    -__CallMethodShortcut
    -__InitializeLogArea
    -__CalculateOffsets
    -__CreateTexts

    """

    #Shortcuts
    #region
    def SetDebugShortcut(index, method, instance = "Console.first_instance"):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Assign the function 'method' to the relative shortcut (tab + number index).
        Note that you can also assign a list of methods to a single shortcut!

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -index:             int                 the index of the function (first position (index = 0) will be executed with TAB+1, ecc. till last with TAB+0)
        -method:            function            the function to execute when the shortcut is pressed

        OPTIONAL:
        -instance:          Console             the instance of the console class where to execute this method

        DEFAULTS OF OPTIONAL VALUES:
        -instance:          string              "Console.first_instance"

        """
        if instance == "Console.first_instance":
            instance = Console.first_instance
        if index in range (0,10):
            instance.shortcuts[index] = method

    def ToggleShortcuts(instance = "Console.first_instance"):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Toggle the shortcuts on or off.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -instance:          Console             the instance of the console class where to execute this method

        DEFAULTS OF OPTIONAL VALUES:
        -instance:          string              "Console.first_instance"

        """
        if instance == "Console.first_instance":
            instance = Console.first_instance

        instance.__shortcuts_enabled = not instance.__shortcuts_enabled

    def __InitializeShortcuts(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Sets up the shortcuts.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
    
        """
        self.shortcuts[0] = None
        self.shortcuts[1] = None
        self.shortcuts[2] = None
        self.shortcuts[3] = None
        self.shortcuts[4] = None
        self.shortcuts[5] = None
        self.shortcuts[6] = None
        self.shortcuts[7] = None
        self.shortcuts[8] = None
        self.shortcuts[9] = None

    def __CheckShortcuts(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Checks inputs for the shortcuts.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
    
        """
        if Input.tab_key_pressed:

                if Input.number0_key_down:
                    self.__CallMethodShortcut(0)

                if Input.number1_key_down:
                    self.__CallMethodShortcut(1)

                if Input.number2_key_down:
                    self.__CallMethodShortcut(2)

                if Input.number3_key_down:
                    self.__CallMethodShortcut(3)

                if Input.number4_key_down:
                    self.__CallMethodShortcut(4)

                if Input.number5_key_down:
                    self.__CallMethodShortcut(5)

                if Input.number6_key_down:
                    self.__CallMethodShortcut(6)

                if Input.number7_key_down:
                    self.__CallMethodShortcut(7)

                if Input.number8_key_down:
                    self.__CallMethodShortcut(8)

                if Input.number9_key_down:
                    self.__CallMethodShortcut(9)

    def __CallMethodShortcut(self, index):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the shortcut.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -index:         int         the index of the shortcut to call

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
    
        """ 
        try:
            methods = self.shortcuts[index]
        except:
            print("'Shortcut " + str(index) + "' is not assigned!")
            return

        if methods != None:
            if type(methods) == type(list):
                for i in methods:
                    i()
            else:
                methods()

        else:
            print("'Shortcut " + str(index) + "' is not assigned!")
    #endregion
    

    #Variable Exposer
    #region
    def __InitializeLogArea(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Setups the log area for texts.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
    
        """
        self.__CalculateOffsets()
        self.__CreateTexts()

    def __CalculateOffsets(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calculates the offsets for the text slots.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
    
        """
        self.debugText_dimensions = Vector2(round((self.debugText_area.dimension.x-(self.debugText_spacing*self.debugText_slots))/self.debugText_slots), round((self.debugText_area.dimension.y-(self.debugText_spacing*self.debugText_slots))/self.debugText_slots)) 

    def __CreateTexts(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Creates the texts.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None
    
        """
        alignement = Vector2(1,0)
        spacing = Vector2(self.debugText_spacing, 0)
        if self.debugText_horizontalAlignement == False:
            alignement = Vector2(0,1)
            spacing = Vector2(0, self.debugText_spacing)
        else:
            alignement = Vector2(1,0)
            spacing = Vector2(self.debugText_spacing,0)

        for x in range(self.debugText_slots):
            self.debugText_texts.append(self.AddComponentByInstance(Text("Console Write Index: "+str(x), self.debugText_font, self.debugText_area, alignement*50*x+spacing, renderToCamera = False)))

    def WriteOnTextLog(self, index, string):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Writes the string 'string' on the text at index 'index'. By default a text has its index shown so you can figure out quickly.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -index:             int             the index of the text where you want to write 
        -string:            string          the string you want to write on the text

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.debugText_texts[index].text = string

    def ToggleDebugText(instance = "Console.first_instance"):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Enables or disables the texts, and so the Console will render or not render them (by default they are enabled).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -instance:          Console             the instance of the console class where to execute this method

        DEFAULTS OF OPTIONAL VALUES:
        -instance:          string              "Console.first_instance"

        """
        if instance == "Console.first_instance":
            instance = Console.first_instance

        if instance.__debugText_enabled == True:
            instance.__debugText_enabled = False
        else:
            instance.__debugText_enabled = True

        for text in instance.debugText_texts:
            text.renderToScreen = instance.__debugText_enabled

    #endregion

    
    def ToggleConsole(instance = "Console.first_instance"):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Toggle on or off the shortcuts and the debug texts. 
        Note that this will toggle them separately, so if one is on and the other is off, then the first becomes off and the second on.
        

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -instance:          Console             the instance of the console class where to execute this method

        DEFAULTS OF OPTIONAL VALUES:
        -instance:          string              "Console.first_instance"

        """
        if instance == "Console.first_instance":
            instance = Console.first_instance

        instance.ToggleShortcuts()
        instance.ToggleDebugText()


    first_instance = None

    def __init__(self, textSlots = 5, textFont = 'FontManager.GetFont("black")', textHorizontalAlignement = False, textSpacing = 0, textDimensions = Vector2(200,75), textArea = 'Transform(Vector2(100,100), self.debugText_dimensions, 0)', dontDestroyOnLoad = True):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates the Console. You can have more than one.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -textSlots:                    int                     how many text slots you want
        -textFont:                     font                    the font used in the text slots
        -textHorizontalAlignement:     bool                    if True, the texts are placed horizontally from left to right. If False, they are placed vertically 
        -textSpacing:                  int or float            extra spacing between texts. It may be useful to adjust things if the font size gets in the way, or things like that
        -textDimensions:               Vector2                 the dimensions of a single text slot
        -textArea:                     Transform               transform from which depend all the texts. The dimension of the texts is calculated from the dimension of the text area and spacing. 
                                                               You can change the position of the text area to change the position of all the texts
        -dontDestroyOnLoad:            bool                    True means the Console is not destroyed when a different scene is loaded from the SceneManager (if you want to learn more, see documentation for Scene and SceneManager classes) 

        DEFAULTS OF OPTIONAL VALUES:
        -textSlots:                    int                     5
        -textFont:                     string                  'FontManager.GetFont("black")'
        -textHorizontalAlignement:     bool                    False
        -textSpacing:                  int                     0
        -textDimensions:               Vector2                 Vector2(200,75)
        -textArea:                     string                  'Transform(Vector2(100,100), self.debugText_dimensions, 0)'
        -dontDestroyOnLoad:            bool                    True

        """
        if Console.first_instance == None:
            Console.first_instance = self

        self.__shortcuts_enabled = True
        self.__debugText_enabled = True

        #Shortcuts
        self.shortcuts = {}

        #Variable Exposer
        self.debugText_slots = textSlots
        if textFont == 'FontManager.GetFont("black")':
            self.debugText_font = FontManager.GetFont("black")
        else:
            self.debugText_font = textFont
        self.debugText_horizontalAlignement = textHorizontalAlignement
        self.debugText_spacing = textSpacing
        self.debugText_dimensions = textDimensions
        if textArea == 'Transform(Vector2(100,100), self.debugText_dimensions, 0)':
            self.debugText_area = Transform(Vector2(100,100), self.debugText_dimensions, 0)
        else:
            self.debugText_area = textArea
        self.debugText_texts = []

        super().__init__(name = "Console", dontDestroyOnLoad = dontDestroyOnLoad)


    def OnInstantiate(self):
        self.__InitializeShortcuts()
        self.__InitializeLogArea() 

    def Draw(self):
        for text in self.debugText_texts:
            text.RenderToScreen()

    def Update(self):
        if self.__shortcuts_enabled:
            self.__CheckShortcuts()



#==================== COMPONENTS ====================

class Component():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This is the basic component class, from which all the other components have to inherit.


    NOTES:
    DON'T PUT REFERENCE TO THE COMPONENT'S GAMEOBJECT IN YOUR INIT METHODS, BECAUSE THE REFERENCE IS SET AFTER THE COMPONENT IS INITIALIZED (before it doesn't exist, so you create it --> init, and then you can set the reference).
    Contains methods to be overloaded in your derived class.
    NOTE THAT THE COMPONENTS' METHODS ARE CALLED AFTER THE GAMEOBJECTS' METHODS.


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -gameObject:            GameObject          the gameObject this component is attached to   


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -Draw
    -RenderToCamera
    -Awake
    -Start
    -Update
    -OnDestroy
    -OnExit
    

    SYSTEM:
    -InitializeComponent
    -DestroyComponent
    -__str__

    ‌"""

    def InitializeComponent(self, gameObject):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Sets the reference between the component and its gameObject.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -gameObject             GameObject              the gameObject to which this component belongs

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        #Reference al proprio gameObject
        self.gameObject = gameObject
        #Si aggiunge alla lista globale dei components
        Components.append(self)
        #Si aggiunge alla lista dei components del proprio gameObject
        self.gameObject.components.append(self)
    
    def Draw(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Put the rendering or debug to visualize logic here.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def RenderToCamera(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        The camera calls this method to get what it needs to be rendered.

        NOTES:
        This must return a tuple (surface, rect)!

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def Awake(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Awake is called once before Start and at the start of the game, before the first frame.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass
    
    def Start(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Start is called once at the start of the game, before the first frame.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def Update(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Update is called once per frame, after checking inputs and before rendering.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def OnDestroy(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        OnDestroy is called just before the component is destroyed.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def OnExit(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        OnExit is called just before closing the application.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        pass

    def DestroyComponent(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Destroys the component.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.OnDestroy()
        Components.remove(self)
        self.gameObject.components.remove(self)

    def __str__(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Converts the component to string (type of Component).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        name = str(type(self))
        name = name.split(".")[1]
        name = name.replace("'>", "")
        name = name.replace(" ", "")
        return name

class SquareCollider(Component):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    Component


    DESCRIPTION:
    Class for collision handling using pygame's rect. 
    

    NOTES:
    If you see compenetration between colliders, call the Move method for more reliability 
    (THIS DOESN'T RESOLVE TUNNELING, IT'S JUST THE COLLIDER CHECKS FOR COLLISION IN THE GAMEOBJECT'S UPDATE 
    (THAT'S WHERE YOU WANT TO CALL THIS FUNCTION) SO IT CHECKS COLLISION AS SOON AS YOU MOVE IT). 


    ATTRIBUTES:

    STATIC:
    -SquareColliders:                       list                            list containing all instances of active colliders

    INSTANCE:
    -isTrigger:                             bool                            a trigger collider is like a sensor: it calls the callbacks, but it doesn't collide
    -collideWithScreenBorder:               bool                            True means the collider can't exit the screen
    -transform:                             Transform                       the transform of the collider
    -callbackRect_dimension_offset:         int                             how many pixels the callback collider exceeds the collider. 
                                                                            you can see this as 'how sensitive' is your collider to callbacks. 
                                                                            You can call the 'drawcollidersquare' method to effectively see this collider. default is 1 pixel (recommended)
    -TransformManager:                      ComponentTransform              the TransformManager of the collider (it stores offsets, ecc. If you want to learn more read the docs for the ComponentTransform)
    -rect:                                  Pygame.Rect                     the rect of the collider
    -old_rect:                              Pygame.Rect                     a copy of the rect that stores the rect of the previous frame
    -callback_rect:                         Pygame.Rect                     rect used to check collisions to send in callbacks
    -colliding_dictionary:                  dictionary                      dictionary containing the data of collisions (collider with whom the component is colliding : [is colliding, was colliding previous frame])
    -isColliding:                           bool                            if True means that a collision is happening
    -wasCollidingPreviousFrame:             bool                            if True means that a collision was happening in the previous frame
    -other_colliders:                       list                            list containing all the other colliders except this one (so it doesn't collide with itself)


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -CheckCollisionWithPoint
    -CheckCollisionWithCollider
    -CheckCollisionWithCallbackCollider
    -Move
    -DrawToScreenColliderWireFrame
    -DrawToScreenColliderSquare
    

    SYSTEM:
    -__Collision
    -__ResolveX
    -__ResolveY
    -__CollisionWithScreenBorder
    -__UpdateWidthAndHeight
    -__Callbacks

    """

    SquareColliders = []
    
    def __init__(self, isTrigger = False, collideWithScreenBorder = False, transform = None, position_offset = Vector2.zero(), dimension_offset = Vector2.zero(), callbackRect_dimension_offset = 1):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new SquareCollider.

        NOTES: 
        position_offset and dimension_offset are used to create the TranformManager and are not stored in the SquareCollider.
        You can access their values from the TransformManager (if you want to learn more read the docs of the ComponentTransform).

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -isTrigger:                             bool                a trigger collider is like a sensor: it calls the callbacks, but it doesn't collide
        -collideWithScreenBorder:               bool                True means the collider can't exit the screen
        -transform:                             Transform           the transform of the collider
        -position_offset:                       Vector2             the position offset of the collider to the reference transform
        -dimension_offset:                      Vector2             the dimension offset of the collider to the reference transform
        -callbackRect_dimension_offset:         int                 how many pixels the callback collider exceeds the collider. You can see this as 'how sensitive' is your collider to callbacks. You can call the 'DrawColliderSquare' method to effectively see this collider. Default is 1 pixel (recommended)
        

        DEFAULTS OF OPTIONAL VALUES:
        -isTrigger:                             bool                False
        -collideWithScreenBorder:               bool                False
        -transform:                             None                None
        -position_offset:                       Vector2             Vector2.zero()
        -dimension_offset:                      Vector2             Vector2.zero()
        -callbackRect_dimension_offset:         int                 1

        """
        SquareCollider.SquareColliders.append(self)
        self.__other_colliders = []

        #Every collider has a list of all the colliders except itself (we need this to not collide with ourself)
        for i in SquareCollider.SquareColliders:
            for col in SquareCollider.SquareColliders:
                if col != i:
                    i.__other_colliders.append(col)
        
        self.TransformManager = ComponentTransform(transform, position_offset, dimension_offset, 0)

        self.rect = pygame.Rect(self.TransformManager.selfTransform.position.x + position_offset.x, self.TransformManager.selfTransform.position.y + position_offset.y, self.TransformManager.selfTransform.dimension.x + dimension_offset.x, self.TransformManager.selfTransform.dimension.y + dimension_offset.y)
        self.old_rect = self.rect.copy()   
        self.isTrigger = isTrigger
        self.callbackRect_dimension_offset = callbackRect_dimension_offset
        self.collideWithScreenBorder = collideWithScreenBorder

        self.callback_rect = pygame.Rect(self.rect.x - callbackRect_dimension_offset, self.rect.y - callbackRect_dimension_offset, self.rect.width + 2*callbackRect_dimension_offset, self.rect.height + 2*callbackRect_dimension_offset)
        self.colliding_dictionary = {}
        self.isColliding = False
        self.wasCollidingPreviousFrame = False

    #Methods that check the collision using pygame.rect.colliderect and collidepoint
    #region
    def CheckCollisionWithPoint(self, point):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Checks if the point is inside the collider and returns True if so, else returns False.

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        -point:             Vector2             point to check if it's inside the collider

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        posPoint = (point.x, point.y)
        return self.rect.collidepoint(posPoint) 

    def CheckCollisionWithCollider(self, collider):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Checks if the colliders are overlapping and returns True if so, else returns False.

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        -collider:             SquareCollider             collider to check if is overlapping

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return self.rect.colliderect(collider.rect)

    def CheckCollisionWithCallbackCollider(self, collider):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Checks if the callback_rect is colliding with the collider's callback_rect and returns True if so, else returns False.

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        -collider:             SquareCollider             collider to check if is overlapping

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return self.callback_rect.colliderect(collider.callback_rect)
    #endregion

    #Collision 
    #region
    def __Collision(self, direction):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Resolves a collision on the specified axis ('x' or 'y').

        NOTES:
        Value of direction has to be "y" or "x".

        PARAMETERS:
        REQUIRED:
        -direction:         string          the axis on which to solve the collision ("y" or "x")

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        collision_objects_index = self.rect.collidelistall(self.__other_colliders)
        objects_colliding = []
        for x in collision_objects_index:
            objects_colliding.append(self.__other_colliders[x])

        self.colliding_colliders = objects_colliding

        if objects_colliding and self.isTrigger == False:
            if direction == "x":
                    for collider in objects_colliding:
                        if collider.isTrigger == False:
                            #collision on the right
                            if self.rect.right >= collider.rect.left and self.old_rect.right <= collider.old_rect.left:
                                self.rect.right = collider.rect.left
                                self.TransformManager.referenceTransform.position.x = self.rect.x - self.TransformManager.position_offset.x

                            #collision on the left
                            if self.rect.left <= collider.rect.right and self.old_rect.left >= collider.old_rect.right:
                                self.rect.left = collider.rect.right
                                self.TransformManager.referenceTransform.position.x = self.rect.left - self.TransformManager.position_offset.x

            if direction == "y":  
                    for collider in objects_colliding:
                        if collider.isTrigger == False:
                            #collision on the bottom
                            if self.rect.bottom >= collider.rect.top and self.old_rect.bottom <= collider.old_rect.top:
                                self.rect.bottom = collider.rect.top
                                self.TransformManager.referenceTransform.position.y = self.rect.y - self.TransformManager.position_offset.y

                            #collision on the top
                            if self.rect.top <= collider.rect.bottom and self.old_rect.top >= collider.old_rect.bottom:
                                self.rect.top = collider.rect.bottom
                                self.TransformManager.referenceTransform.position.y = self.rect.y - self.TransformManager.position_offset.y
                                
    def __ResolveX(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Resolves the x axis.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.__Collision("x")
        if self.collideWithScreenBorder == True:
            self.__CollisionWithScreenBorder("x")

    def __ResolveY(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Resolves the y axis.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.__Collision("y")
        if self.collideWithScreenBorder == True:
            self.__CollisionWithScreenBorder("y")

    def Move(self, newPosition):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Updates the position of the collider and resolves the collisions.

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        -newPosistion:             Vector2             the new position of the collider

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.rect.x = round(newPosition.x)
        self.__ResolveX()

        self.rect.y = round(newPosition.y)
        self.__ResolveY()

    def __CollisionWithScreenBorder(self, direction):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Resolves a collision on the specified axis ('x' or 'y').

        NOTES:
        Value of direction has to be "y" or "x".

        PARAMETERS:
        REQUIRED:
        -direction:         string          the axis on which to solve the collision ("y" or "x")

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        if direction == "x":
            if self.rect.right >= Screen.width:
                self.rect.right = Screen.width
                self.TransformManager.referenceTransform.position.x = self.rect.x - self.TransformManager.position_offset.x
            if self.rect.left <= 0:
                self.rect.left = 0
                self.TransformManager.referenceTransform.position.x = self.rect.x - self.TransformManager.position_offset.x


        if direction == "y":
            if self.rect.bottom >= Screen.height:
                self.rect.bottom = Screen.height
                self.TransformManager.referenceTransform.position.y = self.rect.y - self.TransformManager.position_offset.y
            if self.rect.top <= 0:
                self.rect.top = 0
                self.TransformManager.referenceTransform.position.y = self.rect.y - self.TransformManager.position_offset.y
    #endregion

    #Update Mehtods
    #region
    def __UpdateWidthAndHeight(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Updates the width and height of the collider based on the dimensions.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.TransformManager.UpdateDimension()
        self.rect.width = self.TransformManager.selfTransform.dimension.x + self.TransformManager.dimension_offset.x
        self.rect.height = self.TransformManager.selfTransform.dimension.y + self.TransformManager.dimension_offset.y
        self.callback_rect = pygame.Rect(self.rect.x - self.callbackRect_dimension_offset, self.rect.y - self.callbackRect_dimension_offset, self.rect.width + 2*self.callbackRect_dimension_offset, self.rect.height + 2*self.callbackRect_dimension_offset)
        
    def Update(self):
        self.old_rect = self.rect.copy()

        self.__UpdateWidthAndHeight()

        self.__Callbacks()
       
    def ColliderUpdate(self):
        """A special Update specific to the colliders. It is called just after the gameObjects' Update but before all the other components"""
        self.Move(self.TransformManager.referenceTransform.position + self.TransformManager.position_offset)
        self.TransformManager.selfTransform.position.x = self.TransformManager.referenceTransform.position.x 
        self.TransformManager.selfTransform.position.y = self.TransformManager.referenceTransform.position.y 

        #We use the callback rect to manage callbacks (so the callback colliders are always overlapping)
        self.callback_rect.x = self.rect.x-self.callbackRect_dimension_offset
        self.callback_rect.y = self.rect.y-self.callbackRect_dimension_offset
    #endregion

    #Callbacks
    #region
    def __Callbacks(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Calls the callbacks for the colliders.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for collider in self.__other_colliders:

            #Makes sure that we have collision variables for every collider
            if collider in self.colliding_dictionary.keys():
                self.isColliding = self.colliding_dictionary[collider][0]
                self.wasCollidingPreviuosFrame = self.colliding_dictionary[collider][1]
            else:
                #Adds the collision variables for the new collider
                self.colliding_dictionary.update({collider: [False, False]})
                self.isColliding = False
                self.wasCollidingPreviuosFrame = False

            #Updates the collision variables
            self.wasCollidingPreviousFrame = self.isColliding

            if self.CheckCollisionWithCallbackCollider(collider):
                self.isColliding = True
            else:
                self.isColliding = False

            self.colliding_dictionary[collider] = [self.isColliding, self.wasCollidingPreviuosFrame]

            

            #Calls the callbacks
            if self.isColliding:
                if self.wasCollidingPreviousFrame:
                    self.gameObject.OnCollisionStay(collider)
                else:
                     self.gameObject.OnCollisionEnter(collider)

            else:
                if self.wasCollidingPreviousFrame:
                    self.gameObject.OnCollisionExit(collider) 
            

    #endregion

    #Draw Methods
    #region
    def DrawToScreenColliderWireFrame(self, colorRGB = ColorRGB.red(),  thicc = 2):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Draws the collider's edges with the colorRGB (default is red).

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -colorRGB:              ColorRGB            the color to draw the collider
        -thicc:                 int                 the thickness of the line

        DEFAULTS OF OPTIONAL VALUES:
        -colorRGB:              ColorRGB            ColorRGB.red()
        -thicc:                 int                 2

        """
        x_pos = self.TransformManager.selfTransform.position.x
        x_pos_dim = x_pos + self.TransformManager.selfTransform.dimension.x
        y_pos = self.TransformManager.selfTransform.position.y
        y_pos_dim = y_pos + self.TransformManager.selfTransform.dimension.y
        
        points = [(x_pos, y_pos), (x_pos_dim, y_pos), (x_pos_dim, y_pos_dim), (x_pos, y_pos_dim)]
        if colorRGB == None:
            colorRGB = self.colliderColor.color
        else:
            colorRGB = colorRGB.color
        pygame.draw.lines(Screen.screen, colorRGB, True, points, thicc)

    def DrawToScreenColliderSquare(self, collider_colorRGB = ColorRGB.red(), callback_collider_colorRGB = ColorRGB.yellow()):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Draws the collider square and the callback_collider with the colorRGB (default is red for the collider and yellow for the callback_rect).

        NOTES: 
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -collider_ccolorRGB:                      ColorRGB            the color to draw the collider
        -callback_collider_colorRGB:              ColorRGB            the color to draw the callback collider

        DEFAULTS OF OPTIONAL VALUES:
        -collider_ccolorRGB:                      ColorRGB            ColorRGB.red()
        -callback_collider_colorRGB:              ColorRGB            ColorRGB.yellow()

        """
        pygame.draw.rect(Screen.screen, callback_collider_colorRGB.color, self.callback_rect)
        pygame.draw.rect(Screen.screen, collider_colorRGB.color, self.rect)
 
    #endregion

    def OnDestroy(self):
        SquareCollider.SquareColliders.remove(self)
        for i in SquareCollider.SquareColliders:
            i.__other_colliders.remove(self)

class Image(Component):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    Component


    DESCRIPTION:
    Class used to render images and sprites.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -imagePath                  string                              the name / path of the image (ex.: "MyImage.png")
    -image                      Pygame.Surface                      the surface of the image
    -colorKey                   ColorRGB or convertible             the colorKey (which color is transparent) of the image
    -TransformManager           ComponentTransform                  the TransformManager of the image (it stores offsets, ecc. If you want to learn more read the docs for the ComponentTransform)
    -renderToCamera             bool                                set to True if you want to render the image with the camera
    -renderToScreen             bool                                set to True if you want to render the image directly on the screen


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -ScaleImage
    -SetAnimationImage
    -RenderToScreen

    SYSTEM:
    -__ScaleImageToTransform

    """
    
    def __init__(self, imagePath, transform = None, position_offset = Vector2.zero(), dimension_offset = Vector2.zero(), rotation_offset = 0, colorKey = ColorRGB.magenta(), convert_alpha = True, renderToCamera = True):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new Image.

        NOTES:
        position_offset, dimension_offset and rotation_offset are used to create the TranformManager and are not stored in the Image.
        You can access their values from the TransformManager (if you want to learn more read the docs of the ComponentTransform).

        PARAMETERS:
        REQUIRED:
        -imagePath:                 string                              the name / path of the image (ex.: "MyImage.png")

        OPTIONAL:
        -transform:                 Transform                           the transform of the image
        -position_offset:           Vector2                             the position offset from the Transform 'transform'
        -dimension_offset:          Vector2                             the dimension offset from the Transform 'transform'
        -rotation_offset:           int                                 the rotation offset from the Transform 'transform'
        -colorKey:                  ColorRGB or convertible             the colorKey (which color is transparent) of the image
        -convert_alpha:             bool                                if True calls the convert_alpha() method on the image when is loaded (recommended)
        -renderToCamera:            bool                                set to True if you want to render the image with the camera
        

        DEFAULTS OF OPTIONAL VALUES:
        -transform:                 None                None
        -position_offset:           Vector2             Vector2.zero()
        -dimension_offset:          Vector2             Vector2.zero()
        -rotation_offset:           int                 0
        -colorKey:                  ColorRGB            ColorRGB.magenta()
        -convert_alpha:             bool                True
        -renderToCamera:            bool                True

        """
        try:
            colorKey = ColorRGB.ConvertToColorRGB(colorKey)
        except:
            colorKey = None
        
        #Asserts data types
        assert type(imagePath) == str , "'Image' path has to be a string!"
        assert type(colorKey) == ColorRGB or colorKey == None, "'colorKey' has to be a color or an indexable data type or 'None'!"
        assert type(position_offset) == Vector2, "'position_offset' has to be type of 'Vector2'!"
        assert type(dimension_offset) == Vector2, "'dimension_offset' has to be type of 'Vector2'!"
        assert type(rotation_offset) == int or type(rotation_offset) == float, "'rotation_offset' has to be a number!"
        assert type(transform) == Transform, "'transform' has to be of type 'Transform'!"

        #Makes reference to self
        self.imagePath = imagePath
        self.image = pygame.image.load(self.imagePath).convert()
        if convert_alpha:
            self.image.convert_alpha()
        self.colorKey = colorKey
        if self.colorKey != None:
            self.image.set_colorkey(self.colorKey.color)
        else:
            self.image.set_colorkey(None)

        self.TransformManager = ComponentTransform(transform, position_offset, dimension_offset, rotation_offset)
        self.renderToCamera = renderToCamera
        self.renderToScreen = not renderToCamera
        Camera.generalRenderGroup.append(self)

    #If we override the image with the rotated one, over and over, it will shrink, don't know why (i think its due to like approximation of like radicals of the dimensions of the rotated object, but who cares)
    #So, we're just rotating the image when we're displaying it
    #The scale instead resizes the image, so we want to override it
    def __ScaleImageToTransform(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Scales the image accordingly to its TransformManager.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.image = pygame.transform.scale(self.image, self.TransformManager.selfTransform.dimension.Vector2ToTuple())

    def Update(self):
        self.TransformManager.UpdateTransform()
        self.__ScaleImageToTransform()


    def ScaleImage(self, dimension):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Scales the image to a new dimension.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -dimension:         Vector2         the dimension to scale the image

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.TransformManager.selfTransform.dimension = dimension
        self.__ScaleImageToTransform()

    def SetAnimationImage(self, image, colorKey = ColorRGB.magenta()):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Sets a new image with an optional colorKey. This is useful to set the frames for an animation (for example the AnimationPlayer.CycleInAListOfFrames() uses this method to display the current frame).

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -image:                      Surface              the surface of the image

        OPTIONAL:
        -colorKey:                   ColorRGB             the colorKey (which color is transparent) of the image

        DEFAULTS OF OPTIONAL VALUES:
        -colorKey:                   ColorRGB             ColorRGB.magenta()

        """
        self.image = image
        self.image.set_colorkey(colorKey.color)


    def RenderToScreen(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Renders the image to the screen at its position and rotation and with its dimensions. (if self.renderToScreen == True).

        NOTES:
        This works only if self.renderToScreen == True (in the __init__ method, self.renderToScreen = not renderToCamera).

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.renderToScreen == True:
            rotated_image = pygame.transform.rotate(self.image, self.TransformManager.selfTransform.rotation)

            #Keeps the rotated image at the same distance from the origin
            rotated_rect = rotated_image.get_rect(center = self.image.get_rect(topleft = self.TransformManager.selfTransform.position.Vector2ToTuple()).center)

            #Draws the image 
            Screen.screen.blit(rotated_image, rotated_rect)

    def RenderToCamera(self):
        if self.renderToCamera == True:
            rotated_image = pygame.transform.rotate(self.image, self.TransformManager.selfTransform.rotation)

            #Keeps the rotated image at the same distance from the origin
            rotated_rect = rotated_image.get_rect(center = self.image.get_rect(topleft = self.TransformManager.selfTransform.position.Vector2ToTuple()).center)

            #Returns the image 
            return(rotated_image, rotated_rect)

    def OnDestroy(self):
        Camera.generalRenderGroup.remove(self)

class Font():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Class used to create fonts.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -antiAliasing:              bool            True means anti-aliasing is on, False means it is off
    -color:                     ColorRGB        the color of the font
    -background:                ColorRGB        the font's background color. None means it has no background
    -isBold:                    bool            True means the font is in bold style, false means it is not
    -isItalic:                  bool            True means the font is in italic style, false means it is not
    -fileName:                  string          the font path
    -size:                      int             True means it is a system font, False means it is a custom one
    -isSystemFont:              bool            True means it is a system font, False means it is a custom one
    -font                       Pygame.Font     the font


    FUNCTIONS:

    STATIC:
    -DefaultFont

    INSTANCE:
    -__init__
    -Render
    -SetBold
    -SetItalic

    SYSTEM:
    -__LoadSystemFont
    -__LoadFileFont

    """

    def __init__(self, fileName, size = 11, color = ColorRGB.black(), systemFont = True, antiAliasing = True, bold = False, italic = False, background = None):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new font.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fileName:                  string          the font path

        OPTIONAL:
        -size:                      int             the size of the font
        -color:                     ColorRGB        the color of the font
        -systemFont:                bool            True means it is a system font, False means it is a custom one
        -antiAliasing:              bool            True means anti-aliasing is on, False means it is off
        -bold:                      bool            True means the font is in bold style, false means it is not
        -italic:                    bool            True means the font is in italic style, false means it is not
        -background:                ColorRGB        the font's background color. None means it has no background


        DEFAULTS OF OPTIONAL VALUES:
        -size:                      int             11
        -color:                     ColorRGB        ColorRGB.black()
        -systemFont:                bool            True
        -antiAliasing:              bool            True
        -bold:                      bool            False
        -italic:                    bool            False
        -background:                None            None

        """
        assert type(fileName) == str, "'nameFile' must be of type 'str'!"
        assert type(size) == int or type(size) == float, "'size' must be a number!"
        assert type(systemFont) == bool, "'systemFont' must be of type 'bool'!"
        assert type(bold) == bool, "'bold' must be of type 'bool'!"
        assert type(italic) == bool, "'italic' must be of type 'bool'!"

        assert background == None or type(background) == ColorRGB, "'background' must be of type 'None' or 'ColorRGB'!"

        self.antiAliasing = antiAliasing
        self.color = color
        self.background = background
        self.isBold = bold
        self.isItalic = italic
        self.fileName = fileName
        self.size = size

        if systemFont == True:
            Font.__LoadSystemFont(self, fileName, size, bold, italic)
            self.isSystemFont = True

        else:
            Font.__LoadFileFont(self, fileName, size)
            self.isSystemFont = False



    def __LoadSystemFont(self, name, size, bold, italic):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Loads a system font.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -name:              string          name of the system font you want to load (ex. "arial")
        -size:              int             the size of the font
        -bold:              bool            True means the font is in bold style, false means it is not
        -italic:            bool            True means the font is in italic style, false means it is not
        

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.font = pygame.font.SysFont(name, size, bold, italic)


    def __LoadFileFont(self, filePath, size):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Loads a custom font.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -filePath:          string          the font path
        -size:              int             the size of the font
        

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.font = pygame.font.Font(filePath, size)


    def DefaultFont():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns an arial font with the size of 100.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return Font("arial", 100)

    def Render(self, text, antiAliasing, color, background):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns a surface with the text rendered in this font on it.

        NOTES:
        Just calls the render method on the font (pygame's method), but converts the background color too.

        PARAMETERS:
        REQUIRED:
        -text:                  string              the text you want to render
        -antiAliasing:          bool                True means anti-aliasing is on, False means it is off
        -color:                 ColorRGB            the color of the font
        -background:            ColorRGB            the font's background color. None means it has no background

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if type(background) == ColorRGB:
            background = background.color
        return self.font.render(text, antiAliasing, color, background)

    def SetBold(self, bold):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Sets the font to bold or not based on the bool 'bold' in the parameters.

        NOTES:
        Note that custom fonts cannot be set to bold, only system fonts can.

        PARAMETERS:
        REQUIRED:
        -bold:              bool            True means the font is in bold style, false means it is not 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.isSystemFont == True:
            self.font.bold = bold
            self.isBold = bold
        else:
            self.isBold = False

    def SetItalic(self, italic):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Sets the font to italic or not based on the bool 'italic' in the parameters.

        NOTES:
        Note that custom fonts cannot be set to italic, only system fonts can.

        PARAMETERS:
        REQUIRED:
        -italic:              bool            True means the font is in italic style, false means it is not 

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.isSystemFont == True:
            self.font.italic = italic
            self.isItalic = italic
        else:
            self.isItalic = False

class FontManager():
    """
    STATIC CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    This class is used to organize your Fonts like for the palettes, with names and descriptions.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    -__fonts__:             dictionary              dictionary containing all the fonts and their names
    -fontNames:             list                    list containing all the fonts' names

    INSTANCE:
    None


    FUNCTIONS:

    STATIC:
    -SetFont
    -SetFonts
    -GetFont
    -GetFonts
    -RemoveFont
    -SetItalic
    -SetBold
    -ExportFonts
    -ImportFonts
    -StringFonts


    INSTANCE:
    None

    SYSTEM:
    None

    """

    __fonts__ = {}
    fontNames = []

    def SetFont(fontName, font):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Adds the font 'font' to the FontManager under the keyword 'fontName'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fontName:          string          how you want to call your font
        -font:              Font            the font you want to set in the FontManager

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        FontManager.__fonts__[fontName] = font
        FontManager.fontNames.append(fontName)

    def SetFonts(fontNames, fonts):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Adds the fonts in the list 'fonts' to the FontManager under the keywords at the same index in 'fontNames'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fontNames:          list           list of names for the fonts
        -fonts:              list           list of fonts you want to add

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        for index in range (0, len(fonts)):
            fontName = fontNames[index]
            font = fonts[index]
            FontManager.__fonts__[fontName] = font
            FontManager.fontNames.append(fontName)

    def GetFont(fontName):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns the font associated with the fontName key.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fontName:              string              the name of the font you want

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        try:
            return FontManager.__fonts__[fontName]
        except KeyError:
            print("KeyError: key ", fontName, " not found!")

    def GetFonts():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns the dictionary containing all of the fonts of your FontManager.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return FontManager.__fonts__ 
    
    def RemoveFont(fontName):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Removes the font associated with the fontName key from the FontManager.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fontName:              string              the name of the font you want to remove from the FontManager

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        try:
            FontManager.__fonts__.pop(fontName)
            FontManager.fontNames.remove(fontName)
        except:
            print("Error: failed to remove font '", fontName, "'. The font name is probably wrong")

    def SetItalic(fontName, italic):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Sets the font to italic or not based on the bool 'italic' in the parameters.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fontName:              string              the name of the font you want to change style
        -italic:                bool                True means the font is set in italic style, false means it isn't

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        font = FontManager.GetFont(fontName)
        font.Set_Italic(italic)
        FontManager.SetFont(fontName, font)

    def SetBold(fontName, bold):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Sets the font to bold or not based on the bool 'bold' in the parameters.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fontName:              string              the name of the font you want to change style
        -bold:                  bool                True means the font is set in bold style, false means it isn't

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        font = FontManager.GetFont(fontName)
        font.Set_Bold(bold)
        FontManager.SetFont(fontName, font)

    def ExportFonts(fileName):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Exports all the fonts in a text file called 'fileName'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fileName:              string              the name of the text file where the fonts are exported

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        #We create a file and initilize the name and description of the palette
        fontsFile = open(fileName + "_fontManager.txt", "w")
        fileContain = ""

        #We subdivide each information of the fonts in a new line
        for fontName in FontManager.fontNames:
            font = FontManager.GetFont(fontName)
            fileContain += fontName + "\n"
            fileContain += font.fileName + "\n"
            fileContain += str(font.size) + "\n"
            fileContain += str(font.isSystemFont) + "\n"
            fileContain += str(font.color.r) + "\n"
            fileContain += str(font.color.g) + "\n"
            fileContain += str(font.color.b) + "\n"
            fileContain += str(font.antiAliasing) + "\n"
            fileContain += str(font.isBold) + "\n"
            fileContain += str(font.isItalic) + "\n"
            if font.background == None:
                fileContain += "None" + "\n"
                fileContain += "None" + "\n"
                fileContain += "None" + "\n"
            else:
                fileContain += str(font.background.r) + "\n"
                fileContain += str(font.background.g) + "\n"
                fileContain += str(font.background.b) + "\n"

        #We write the informations on the file
        try:
            if fontsFile.write(fileContain) == len(fileContain):
                print("The fonts were exported sucessfully")
            else:
                print("The fonts WEREN'T exported sucessfully")
        
        #We close the file whatever happens
        finally:
            fontsFile.close()
            
    def ImportFonts(fileName):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Imports all the fonts from the text file called 'fileName'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -fileName:              string              the name of the text file from which you want to import the fonts

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """

        #The text file containing the exported fonts
        try:
            file = open(fileName + "_fontManager.txt", "r")
        except FileNotFoundError:
            print("FileNotFoundError: the file ", fileName, "was not found!")

        content = file.read()
        contentLines = content.split("\n")

        #Lists we use later to reassembly our FontManager
        fontList = []
        fontKeysList = []

        #We use the while to go by 6 steps. 
        #We subtract 1 to the lenght of contentLines because 
        #at the last line there's a "\n" character
        index = 0
        while index < len(contentLines) - 1:
            #Every font occupies 13 lines: 
            #the first is the name key of the font, 
            #the second is the fontPath
            #the third is the size
            #the fourth is the systemFont bool
            #the fifth is the red color of the font
            #the sixth is the green color of the font
            #the seventh is the blue color of the font
            #the eighth is the antiAliasing bool
            #the nineth is the bold bool
            #the tenth is the italic bool
            #the eleventh is the red background color
            #the twelveth is the green background color
            #the thirteenth is the blue background color
            fontName = contentLines[index]
            fontPath = contentLines[index+1]
            size = int(contentLines[index+2])
            systemFont = bool(contentLines[index+3])

            colorFont_red = float(contentLines[index+4])
            colorFont_green = float(contentLines[index+5])
            colorFont_blue = float(contentLines[index+6])
            colorFont = ColorRGB(colorFont_red, colorFont_green, colorFont_blue)
            
            antiAliasing = bool(contentLines[index+7])
            bold_str = contentLines[index+8]
            italic_str = contentLines[index+9]
            bold = False
            italic = False
            if bold_str == "True":
                bold = True

            if italic_str == "True":
                italic = True
            
            
            bckGround_red = contentLines[index+10]
            bckGround_green = contentLines[index+11]
            bckGround_blue = contentLines[index+12]

            if bckGround_red != "None":
                backGroundColor = ColorRGB(float(bckGround_red), float(bckGround_green), float(bckGround_blue))

            else:
                backGroundColor = None

            #We use the values obtained to recreate the font
            recreatedFont = Font(fontPath, size, colorFont, systemFont, antiAliasing, bold, italic, backGroundColor)

            fontList.append(recreatedFont)
            fontKeysList.append(fontName)
            index += 13

        importedFonts = FontManager.SetFonts(fontKeysList, fontList)
        
        file.close()
        print("The fonts were imported succesfully")
        return importedFonts

    def StringFonts():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Returns a string that contains all the information about the fonts in the Font Manager. It can be useful when printing in debugging.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        string = ""
        for fontName in FontManager.fontNames:
            font = FontManager.GetFont(fontName)
            string += "Font Name: " + fontName + "\n"
            string += "Path: " + font.fileName + "\n"
            string += "Size: " + str(font.size) + "\n"
            string += "System Font: " + str(font.isSystemFont) + "\n"
            string += "Color Font (RGB): " + str(font.color.color) + "\n"
            string += "AntiAliasing: " + str(font.antiAliasing) + "\n"
            string += "Bold: " + str(font.isBold) + "\n"
            string += "Italic: " + str(font.isItalic) + "\n"
            
            if font.background == None:
                string += "Background Color (RGB): " + "None" + "\n"
            else:
                string += "Background Color (RGB): " + str(font.background.color) + "\n"

        return string

class Text(Component):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    Component


    DESCRIPTION:
    Use this class to attach a text to your gameObject.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -text:                          string                  the string written in the text
    -font:                          Font                    the font in which the text is written
    -TransformManager:              ComponentTransform      the TransformManager of the image (it stores offsets, ecc. If you want to learn more read the docs of the ComponentTransform)
    -renderToCamera:                bool                    set to True if you want to render the image with the camera
    -renderToScreen:                bool                    set to True if you want to render the image directly on the screen


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -RenderToScreen

    SYSTEM:
    None

    """

    def __init__(self, text = "", font = Font.DefaultFont(), transform = None, position_offset = Vector2.zero(), dimension_offset = Vector2.zero(), rotation_offset = 0, renderToCamera = True):
       """
       INSTANCE FUNCTION

       DESCRIPTION:
       Creates a new Text.

       NOTES:
       position_offset, dimension_offset and rotation_offset are used to create the TranformManager and are not stored in the Text.
       You can access their values from the TransformManager (if you want to learn more read the docs of the ComponentTransform).

       PARAMETERS:
       REQUIRED:
       None

       OPTIONAL:
       -text:                       string                  the string written in the text
       -font:                       Font                    the font in which the text is written
       -transform:                  Transform               the transform of the text
       -position_offset:            Vector2                 the position offset from the Transform 'transform'
       -dimension_offset:           Vector2                 the dimension offset from the Transform 'transform'
       -rotation_offset:            int                     the rotation offset from the Transform 'transform'
       -renderToCamera:             bool                    set to True if you want to render the image with the camera

    
       DEFAULTS OF OPTIONAL VALUES:
       -text:                       string                  ""
       -font:                       Font                    Font.DefaultFont()
       -transform:                  None                    None
       -position_offset:            Vector2                 Vector2.zero()
       -dimension_offset:           Vector2                 Vector2.zero()
       -rotation_offset:            int                     0
       -renderToCamera:             bool                    True 

       """
       assert type(text) == str, "'text' must be of type 'str'!"
       assert type(font) == Font, "'font' must be of type 'Font'!"
       assert type(dimension_offset) == Vector2, "'dimension_offset' has to be type of 'Vector2'!"
       assert type(rotation_offset) == int or type(rotation_offset) == float, "'rotation_offset' has to be a number!"
       assert type(transform) == Transform, "'transform' has to be of type 'Transform'!"

       self.text = text
       self.font = font
       
       self.TransformManager = ComponentTransform(transform, position_offset, dimension_offset, rotation_offset)
       self.renderToCamera = renderToCamera
       self.renderToScreen = not renderToCamera
       Camera.generalRenderGroup.append(self)

    def Update(self):
        self.TransformManager.UpdateTransform()

            
    def RenderToScreen(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Renders the text to the screen with its position, dimension and rotation. (If self.renderToScreen == True).

        NOTES:
        This works only if self.renderToScreen == True (in the __init__ method, self.renderToScreen = not renderToCamera).

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None 

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.renderToScreen == True:
            rendered_text = self.font.Render(self.text, self.font.antiAliasing, self.font.color.color, self.font.background)
        
            scaled_text = pygame.transform.scale(rendered_text, self.TransformManager.selfTransform.dimension.Vector2ToTuple())
        
            rotated_text = pygame.transform.rotate(scaled_text, self.TransformManager.selfTransform.rotation)

            #Keeps the rotated image at the same distance from the origin
            rotated_rect = rotated_text.get_rect(center = scaled_text.get_rect(topleft = self.TransformManager.selfTransform.position.Vector2ToTuple()).center)

            #Draws the image 
            Screen.screen.blit(rotated_text, rotated_rect)

    def RenderToCamera(self):
        if self.renderToCamera == True:
            rendered_text = self.font.Render(self.text, self.font.antiAliasing, self.font.color.color, self.font.background)
        
            scaled_text = pygame.transform.scale(rendered_text, self.TransformManager.selfTransform.dimension.Vector2ToTuple())
        
            rotated_text = pygame.transform.rotate(scaled_text, self.TransformManager.selfTransform.rotation)

            #Keeps the rotated image at the same distance from the origin
            rotated_rect = rotated_text.get_rect(center = scaled_text.get_rect(topleft = self.TransformManager.selfTransform.position.Vector2ToTuple()).center)
 
            #Returns the image
            return(rotated_text, rotated_rect)

    def OnDestroy(self):
        Camera.generalRenderGroup.remove(self)

class Button(GameObject):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    GameObject


    DESCRIPTION:
    Create easily buttons: pass a function or a list of functions you want to be called when the button is pressed, parameters for image and text and voilà!
    

    NOTES:
    Remember that the image and text parameters are used to create the components, so you can always edit the button's Image and Text components after instantiating it!


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -pressedFunction:               function                the function to execute when the button is activated
    -imagePath:                     string                  the name / path of the image of the button (ex.: "MyButtonImage.png")
    -text:                          string                  the string written in the text over the button
    -font:                          Font                    the font in which the text of the button is written
    -renderToScreen:                bool                    set to True if you want to render the button (image and text) directly on the screen
    -activateOnClick:               bool                    set to True if you want to click on the button to activate it (for example UI buttons)
    -activateOnCollision:           bool                    set to True if you want to activate the button when it collides with something (for example in a game it could be a pressure pad that opens a door, but maybe I'm overthinking it, anyway the button uses a SquareCollider so adding this required only this variable.)

    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -ButtonPressed

    SYSTEM:
    None

    """
    def __init__(self, pressedFunction, imagePath = "Button_defaultImage.png", text = " button", font = Font.DefaultFont(), name = "Button (GameObject)", transform = Transform.DefaultValues(), autoInstantiate = False, renderToScreen = True, activateOnClick = True, activateOnCollision = False, dontDestroyOnLoad = False):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new Button.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -pressedFunction:               function or list        the function (of list of functions) to execute when the button is activated

        OPTIONAL:
        -imagePath:                     string                  the name / path of the image of the button (ex.: "MyButtonImage.png")
        -text:                          string                  the string written in the text over the button
        -font:                          Font                    the font in which the text of the button is written
        -name:                          string                  the name of the GameObject
        -renderToScreen:                bool                    set to True if you want to render the button (image and text) directly on the screen
        -activateOnClick:               bool                    set to True if you want to click on the button to activate it (for example UI buttons)
        -activateOnCollision:           bool                    set to True if you want to activate the button when it collides with something (for example in a game it could be a pressure pad that opens a door, but maybe I'm overthinking it, anyway the button uses a SquareCollider so adding this required only this variable.)
        -dontDestroyOnLoad:             bool                    True means the Console is not destroyed when a different scene is loaded from the SceneManager (if you want to learn more, see documentation for Scene and SceneManager classes) 

        DEFAULTS OF OPTIONAL VALUES:
        -imagePath:                     string                  "Button_defaultImage.png"
        -text:                          string                  "button"
        -font:                          Font                    Font.DefaultFont()
        -name:                          string                  "Button (GameObject)"
        -renderToScreen:                bool                    True
        -activateOnClick:               bool                    True
        -activateOnCollision:           bool                    False

        """
        self.pressedFunction = pressedFunction
        if imagePath == "Button_defaultImage.png":
            relative_path = os.path.join("Engine Default Assets", "Button_defaultImage.png")
            imagePath = os.path.join(os.path.dirname(__file__), relative_path)
        self.imagePath = imagePath
        self.text = text
        self.font = font
        self.renderToScreen = renderToScreen
        self.activateOnClick = activateOnClick
        self.activateOnCollision = activateOnCollision
        super(Button, self).__init__(name, transform, autoInstantiate, dontDestroyOnLoad)

    def OnInstantiate(self):
        self.textComponent = self.AddComponentByInstance(Text(self.text, self.font, transform = self.transform, renderToCamera= not self.renderToScreen))
        self.imageComponent = self.AddComponentByInstance(Image(self.imagePath, transform = self.transform, renderToCamera= not self.renderToScreen))
        self.colliderComponent = self.AddComponentByInstance(SquareCollider(isTrigger = True, transform = self.transform))

    def Draw(self):
        if self.renderToScreen == True:
            self.imageComponent.RenderToScreen()
            self.textComponent.RenderToScreen()

    def OnCollisionEnter(self, collider):
        if self.activateOnCollision == True:
            self.ButtonPressed()
        

    def Update(self):
        if Input.left_mouseClick_down and self.activateOnClick:
            mouse_over = self.colliderComponent.CheckCollisionWithPoint(Input.mouse_position)
            if mouse_over:
                self.ButtonPressed()
            
    def ButtonPressed(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Calls the functions that are executed when the button is activated.

        NOTES:
        This function is called automatically if you set activateOnClick or activateOnCollision to True. If they're both False, you have to call this manually.

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        try:
            for index in range(0, len(self.pressedFunction)):
                try:
                    self.pressedFunction[index]()
                except:
                    print("Error occurred from " + self.name + " button trying to call its funtion at index " + str(index))
        except:
            try:
                self.pressedFunction()
            except:
                    print("Error occurred from " + self.name + " button trying to call its funtion")

class FrameManager(Component):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    Component


    DESCRIPTION:
    Class that holds the frames for your animations.


    NOTES:
    You can pass anything you like as animationNames or in the list of frames, but if you want to load images (I suppose you want) I recommend the frames of the animation to be loaded images (pygame.image.load("MyImage.png") for example is ok).


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -__animations:              dictionary              dictionary holding the names of the animations as keys and lists of frames of the animations


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -AddAnimationFrames
    -GetAnimationFrames
    -GetFrameFromAnimation
    -GetAnimationsNames

    SYSTEM:
    None

    """
    def __init__(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Initialise the FrameManager.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.__animations = {}

    def AddAnimationFrames(self, animationName, framesList):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Adds an animation and its frames to the FrameManager.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -animationName:             string              the name of the animation
        -framesList:                list                list of frames of the animation

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.__animations[animationName] = framesList

    def GetAnimationFrames(self, animationName):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns the list containing the frames of the animation 'animationName'.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -animationName:             string              the name of the animation you want to get the frame from

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return self.__animations[animationName]

    def GetFrameFromAnimation(self, animationName, index):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns a specific frame at index 'index' from the animation 'animationName' list of frames.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -animationName:             string              the name of the animation you want to get the frame from
        -index:                     int                 the index of the frame you want to get

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return self.__animations[animationName][index]

    def GetAnimationsNames(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Returns a list containing all the names of the animations.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        return self.__animations.keys()

class AnimationClip():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Class that manages animation clips. They are methods (so you can do what you want: change sprite, scale ecc.)


    NOTES:
    About animationMethod --> it MUST have two arguments: 'self' and 'imageComponent', where is passed the reference to the gameObject's image component from the AnimationPlayer. 
    You can change animationComponent.SetAnimationImage to change the rendered image.

    About animationFrames and animationMethod --> your animation must have 'animationMehtod' if you want custom particular animation that you do in a method, 
    but if you want to just cycle in a list of frames, pass them in 'animationFrames' and use AnimationPlayer.CycleInAListOfFrames.
    You don't have to pass both, it just depends on what kind of animation you wanna make.

    If you use animationMethod, you can use frameStep_timer, index and animationLenght to keep track of the progress of the animation between the frames (Remember that the method is called every frame).
    Ex. from AnimationPlayer.CycleInAListOfFrames:

        if animationClip.alreadyPlayed == False:                                                                <-- check if we already played the animation in case it is set not to loop
            animationClip.frameStep_timer -= 1                                                                  <-- we subtract 1 frame from the counter of how many frame of the game a frame of the animation is displayed
            if animationClip.frameStep_timer < 0:                                                               <-- if it's 0 means it is time to update to the next frame
                animationClip.frameStep_timer = animationClip.frameStep                                         <-- we reset the timer of the frameStep_timer
                self.imageComponent.SetAnimationImage(animationClip.animationFrames[animationClip.index])       <-- we set the new frame on the image to be rendered (we set before we add something because index start at 0)
                animationClip.index += 1                                                                        <-- we prepare the index for the next frame
                if animationClip.index > animationClip.animationLength:                                         <-- if we are on the last frame of the animation it means the animation is ended 
                    if animationClip.canLoop == True:                                                           <-- if canLoop == True we follow the logic to restart the animation
                        animationClip.index = 0                                                                 <-- we set the index to 0 to restart from the first frame
                        animationClip.alreadyPlayed = False                                                     <-- we set alreadyPlayed to false just to be sure
                    else:                                                                                       <-- if the animation is set to NOT play in loop
                        animationClip.alreadyPlayed = True                                                      <-- we set alreadyPlayed to True. That stops the animation from restarting
                        animationClip.index = 0                                                                 <-- we reset the index to not cause possible errors if the user wants to recall the animation
                        animationClip.frameStep_timer = animationClip.frameStep                                 <-- same for the framestep


    ATTRIBUTES:

    STATIC:
    None
    
    INSTANCE:
    -animationMethod:           function            method called for custom animation
    -animationFrames:           list                list of frames of the animation
    -frameStep:                 int                 how many frames of the game each frame (sprite) of the animation lasts on the screen (Consider the FPS of the game too!)
    -frameStep_timer:           int                 used as a timer in AnimationPlayer.CycleInAListOfFrames. You can use it as a timer in your animationMethod
    -index:                     int                 used in AnimationPlayer.CycleInAListOfFrames to know what frame to display. You can use it in your animationMethod
    -animationLength:           int                 the length of the animation (can be how many frames, but if you use the animationMethod, can be the "how many steps" of your animation, which are basically frames)
                                                    If it is set to None in the __init__ method, it is automatically calculated with this formula: len(animationFrames)-1
    -canLoop:                   bool                if True means the animation can be played in loop
    -alreadyPlayed:             bool                if True means the animation has already been played. You can use this with canLoop to make animation play a single time

    
    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    None

    SYSTEM:
    None
    
    """
    def __init__(self, animationMethod = None, animationFrames = [], frameStep = 10, animationLength = None, canLoop = True):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Create a new AnimationClip.

        NOTES:
        You don't have to pass both animationMethod and animationFrames, it just depends on what kind of animation you wanna make.
        For example a simple squash and stretch doesn't require frames, so you could make a function that animates the transform and set it as the animation method.
        

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -animationMethod:           function            method called for custom animation
        -animationFrames:           list                list of frames of the animation
        -frameStep:                 int                 how many frames of the game each frame (sprite) of the animation lasts on the screen (Consider the FPS of the game too!)
        -animationLength:           int                 the lenght of the animation (can be how many frames, but if you use the animationMethod, can be the "how many steps" of your animation, which are basically frames)
                                                        If it is set to None, it is automatically calculated with this formula: len(animationFrames)-1
        -canLoop:                   bool                if True means the animation can be Played in loop

        DEFAULTS OF OPTIONAL VALUES:
        -animationMethod:           None                None
        -animationFrames:           list                []
        -frameStep:                 int                 10
        -animationLength:           None                None
        -canLoop                    bool                True

        """
        self.animationMethod = animationMethod
        self.animationFrames = animationFrames
        self.frameStep = frameStep
        self.frameStep_timer = frameStep
        self.index = 0
        if animationLength == None:
            self.animationLenght = len(animationFrames)-1
        else:
            self.animationLenght = animationLength

        self.canLoop = canLoop
        self.alreadyPlayed = False

class AnimationPlayer(Component): 
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    Component


    DESCRIPTION:
    Component that holds the logic for playing animation.
    It needs an Image component.
    It is provided a method of cycling through a list of frames.


    NOTES:
    Note that the AnimationPlayer doesn't affect the AnimationClip variables (except CycleInAListOfFrames), so you can use the variables provided in the animationClip as you need.
    
    REMEMBER YOU HAVE TO CALL THE ANIMATIONS EVERY FRAME SO THEY CAN PROGRESS!


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -imageComponent:            Image           the image used to render the frames of the animation


    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -PlayAnimation
    -CycleInAListOfFrames

    SYSTEM:
    None

    """

    def __init__(self, imageComponent = None):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new AnimationPlayer.


        NOTES:
        None


        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -imageComponent:            Image           the image used to render the frames of the animation
       
        DEFAULTS OF OPTIONAL VALUES:
        -imageComponent:            None            None
             
        """
        if imageComponent == None:
            print("Image is None! the animation will not be rendered!")
            #Can't use "GameObject.GetComponentForSure because the gameObejct reference is set after the component is created (initialized)"

        self.imageComponent = imageComponent
        
 
    def PlayAnimation(self, animationClip):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Plays the animationClip's animationMethod (use this for custom animations).

        NOTES:
        Note the requirements of the animation method! (see AnimationClip's docs).

        PARAMETERS:
        REQUIRED:
        -animationClip:             AnimationClip           the animation you want to play

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        animationClip.animationMethod(self.gameObject, self.imageComponent)


    def CycleInAListOfFrames(self, animationClip):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Takes an animationClip that contains a list of frames (in 'animationFrames' attribute) 
        and use them to do the animation using the frameStep set in the animationClip.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -animationClip:             AnimationClip           the animation you want to play

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if animationClip.alreadyPlayed == False:
            if self.imageComponent != None:
                animationClip.frameStep_timer -= 1
                if animationClip.frameStep_timer < 0:
                    animationClip.frameStep_timer = animationClip.frameStep
                    self.imageComponent.SetAnimationImage(animationClip.animationFrames[animationClip.index])
                    animationClip.index += 1
                    if animationClip.index > animationClip.animationLenght:
                        if animationClip.canLoop == True:
                            animationClip.index = 0
                            animationClip.alreadyPlayed = False
                        else:
                            animationClip.alreadyPlayed = True
                            animationClip.index = 0                  
                            animationClip.frameStep_timer = animationClip.frameStep
                            
class Camera(Component):
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    Component


    DESCRIPTION:
    A camera to render dynamically to the screen.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    -cameras:                           list                        list of all the active cameras
    -generalRenderGroup:                list                        list of all the things to render

    INSTANCE:
    -targetSurface:                     pygame.Surface              the target surface where the camera renders everything
    -backgroundSurface:                 pygame.Surface              the background surface
    -backgroundColor:                   ColorRGB or convertible     the color used to fill the screen when it is refreshed
    -y_sort_camera:                     bool                        if True means that objects with an lower y position are rendered behind the higher ones
    -center_target_camera:              bool                        if True means that the camera will keep in center of the screen the targeted transform
    -box_camera:                        bool                        if True means that the camera will stand still, and the targeted transform will be able to push it around from the borders
    -keyboardControl_camera:            bool                        if True means that the camera will be moved around with key inputs
    -mouseControl_camera:               bool                        if True means that the camera will be moved around with mouse inputs
    -cameraModeBackup:                  dictionary                  a dictionary containing all the bool values about every camera mode
    -offset:                            Vector2                     the displacement applied to the camera's viewport
    -halfWidth:                         int                         half the width of the target surface of the camera
    -halfHeight:                        int                         half the width of the target surface of the camera
    -trackingTransformTarget:           Transform                   the target that the camera follows or focus on, depending on the modes
    -camera_borders:                    dictionary                  dictionary containing the top, right, bottom and left of the camera box
    -camera_rect:                       pygame.Rect                 rect used in box camera mode, to keep the trackingTransformTarget inside this box
    -keyboard_speed:                    int                         the speed at which the camera is moved using the keyboards controls
    -mouse_speed:                       int                         the speed at which the camera is moved using the mouse controls
        
        
    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    -BackupCameraMode
    -Refresh
    -YSortGroup
    -Center_target_camera
    -Box_target_camera
    -KeyboardControl
    -MouseControl
    -ToggleKeyboardControl
    -ToggleMouseControl

    SYSTEM:
    None

    """
    cameras = []
    generalRenderGroup = []

    
    def __init__(self, targetSurface = None, backgroundSurface = None, backgroundColor = ColorRGB.black(), y_sort_camera = False, center_target_camera = False, box_camera = False, keyboardControl_camera = False, mouseControl_camera = False, trackingTransformTarget = None, boxCameraBorder_left = 20, boxCameraBorder_top = 20, boxCameraBorder_right = 20, boxCameraBorder_bottom = 20):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new camera.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        -targetSurface:                     pygame.Surface              the target surface where the camera renders everything
        -backgroundSurface:                 pygame.Surface              the backgorund surface
        -backgroundColor:                   ColorRGB or convertible     the color used to fill the screen when it is refreshed
        -y_sort_camera:                     bool                        if True means that objecs with an lower y position are rendered back the higher
        -center_target_camera:              bool                        if True means that the camera will keep in center of the screen the targeted transform
        -box_camera :                       bool                        if True means that the camera will stand still, and the targeted transform will be able to push it around from the borders
        -keyboardControl_camera:            bool                        if True means that the camera will be moved around with key inputs
        -mouseControl_camera:               bool                        if True means that the camera will be moved around with mouse inputs
        -trackingTransformTarget:           Transform                   the target that the camera follows or focus on, depending on the modes
        -boxCameraBorder_left:              int                         distance between the left edge of the screen and the left of the camera rect
        -boxCameraBorder_top:               int                         distance between the top edge of the screen and the top of the camera rect
        -boxCameraBorder_right:             int                         distance between the right edge of the screen and the right of the camera rect
        -boxCameraBorder_bottom:            int                         distance between the bottom edge of the screen and the bottom of the camera rect

        DEFAULTS OF OPTIONAL VALUES:
        -targetSurface:                     None                        None
        -backgroundSurface:                 None                        None
        -backgroundColor:                   ColorRGB                    ColorRGB.black()
        -y_sort_camera:                     bool                        False
        -center_target_camera:              bool                        False
        -box_camera :                       bool                        False
        -keyboardControl_camera:            bool                        False
        -mouseControl_camera:               bool                        False
        -trackingTransformTarget:           None                        None
        -boxCameraBorder_left:              int                         20
        -boxCameraBorder_top:               int                         20
        -boxCameraBorder_right:             int                         20
        -boxCameraBorder_bottom:            int                         20

        """
        Camera.cameras.append(self)

        if targetSurface == None:
            targetSurface = pygame.display.get_surface()

        self.targetSurface = targetSurface
        self.backgroundSurface = backgroundSurface
        self.backgroundColor = backgroundColor

        #Camera Types
        self.y_sort_camera = y_sort_camera
        self.center_target_camera = center_target_camera
        self.box_camera = box_camera
        self.keyboardControl_camera = keyboardControl_camera
        self.mouseControl_camera = mouseControl_camera 

        self.cameraModeBackup = {'y_sort_camera': self.y_sort_camera, 'center_target_camera': self.center_target_camera, 'box_camera': self.box_camera, 'keyboardControl_camera': self.keyboardControl_camera, 'mouseControl_camera': self.mouseControl_camera}
        

        #Variables for Camera Types

        #Target Center Camera
        self.offset = Vector2(0,0)
        self.halfWidth = self.targetSurface.get_size()[0] // 2
        self.halfHeight = self.targetSurface.get_size()[1] //2
        self.trackingTransformTarget = trackingTransformTarget

        #Box camera
        self.camera_borders = {'left': boxCameraBorder_left, 'right': boxCameraBorder_right, 'top': boxCameraBorder_top, 'bottom': boxCameraBorder_bottom}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.targetSurface.get_size()[0] -(self.camera_borders['left']+self.camera_borders['right'])
        h = self.targetSurface.get_size()[1] -(self.camera_borders['top']+self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l,t,w,h)

        #KeyboardControl
        self.keyboard_speed = 5

        #MouseControl
        self.mouse_speed = 0.4
        
    def Update(self):
        self.privateRenderGroup = Camera.generalRenderGroup

        if self.y_sort_camera:
            self.YSortGroup()

        if self.center_target_camera:
            self.Center_target_camera()

        if self.box_camera:
            self.Box_target_camera()

        if self.mouseControl_camera:
            self.MouseControl()

    def BackupCameraMode(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Saves the values of the camera modes in the dictionary self.cameraModeBackup.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.cameraModeBackup = {'y_sort_camera': self.y_sort_camera, 'center_target_camera': self.center_target_camera, 'box_camera': self.box_camera, 'keyboardControl_camera': self.keyboardControl_camera, 'mouseControl_camera': self.mouseControl_camera}

    def OnDestroy(self):
        Camera.cameras.remove(self)

    def Refresh(self):
        """
        SYSTEM FUNCTION
        DO NOT USE THIS FUNCTION IN YOUR CODE

        DESCRIPTION:
        Refreshes the screen.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if type(self.backgroundColor) == ColorRGB:
                self.targetSurface.fill(self.backgroundColor.color)
        else:
            self.backgroundColor = ColorRGB.ConvertToColorRGB(self.backgroundColor)
            if type(self.backgroundColor) == ColorRGB:
                self.targetSurface.fill(self.backgroundColor.color)
            else:
                assert 1 == 0, "self.backgroundColor has wrong value/type and was not able to be converted to ColorRGB!"


    def YSortGroup(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Applies the logic for the y_sort_camera mode.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        self.privateRenderGroup = sorted(self.privateRenderGroup, key = lambda x: x.TransformManager.selfTransform.position.y + x.TransformManager.selfTransform.dimension.y/2)
        
    def Center_target_camera(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Applies the logic for the center_target_camera mode.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.trackingTransformTarget != None:
            self.offset.x = self.trackingTransformTarget.GetCenter().x - self.halfWidth
            self.offset.y = self.trackingTransformTarget.GetCenter().y - self.halfHeight

    def Box_target_camera(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Applies the logic for the box_camera mode.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.trackingTransformTarget != None:
            if self.trackingTransformTarget.position.x < self.camera_rect.left:
                self.camera_rect.left = self.trackingTransformTarget.position.x

            if (self.trackingTransformTarget.position.x + self.trackingTransformTarget.dimension.x) > self.camera_rect.right:
                self.camera_rect.right = (self.trackingTransformTarget.position.x + self.trackingTransformTarget.dimension.x)

            if self.trackingTransformTarget.position.y < self.camera_rect.top:
                self.camera_rect.top = self.trackingTransformTarget.position.y

            if (self.trackingTransformTarget.position.y + self.trackingTransformTarget.dimension.y) > self.camera_rect.bottom:
                self.camera_rect.bottom = (self.trackingTransformTarget.position.y + self.trackingTransformTarget.dimension.y)

            self.offset.x = self.camera_rect.left - self.camera_borders['left']
            self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def KeyboardControl(self, left, up, right, down):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Applies the logic to move the camera using keyboard inputs.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -left:          bool            left input bool (You can directly set the Input class key bools here)
        -up:            bool            up input bool (You can directly set the Input class key bools here)
        -right:         bool            right input bool (You can directly set the Input class key bools here)
        -down:          bool            down input bool (You can directly set the Input class key bools here)

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.keyboardControl_camera:
            if left:
                self.offset.x -= self.keyboard_speed
            if up:
                self.offset.y -= self.keyboard_speed
            if right:
                self.offset.x += self.keyboard_speed
            if down:
                self.offset.y += self.keyboard_speed
        
    def MouseControl(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Applies the logic to move the camera using mouse position.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        mouse_pos_tuple = pygame.mouse.get_pos()
        mouse = Vector2(mouse_pos_tuple[0], mouse_pos_tuple[1])
        mouse_offset = Vector2()

        left_border = self.camera_borders['left']
        top_border = self.camera_borders['top']
        right_border = self.targetSurface.get_size()[0] - self.camera_borders['right']
        bottom_border = self.targetSurface.get_size()[1] - self.camera_borders['bottom']


        if top_border < mouse.y < bottom_border:
            if mouse.x < left_border:
                mouse_offset.x = mouse.x - left_border
                pygame.mouse.set_pos(left_border, mouse.y)
            if mouse.x > right_border:
                mouse_offset.x = mouse.x - right_border
                pygame.mouse.set_pos(right_border, mouse.y)

        elif mouse.y < top_border:
            if mouse.x < left_border:
                mouse_offset = mouse- Vector2(left_border, top_border)
                pygame.mouse.set_pos(left_border, top_border)
            if mouse.x > right_border:
                mouse_offset = mouse- Vector2(right_border, top_border)
                pygame.mouse.set_pos(right_border, top_border)

        elif mouse.y > bottom_border:
            if mouse.x < left_border:
                mouse_offset = mouse- Vector2(left_border, bottom_border)
                pygame.mouse.set_pos(left_border, bottom_border)
            if mouse.x > right_border:
                mouse_offset = mouse- Vector2(right_border, bottom_border)
                pygame.mouse.set_pos(right_border, bottom_border)

        if left_border < mouse.x < right_border:
            if mouse.y < top_border:
                mouse_offset.y = mouse.y - top_border
                pygame.mouse.set_pos(mouse.x, top_border)
            if mouse.y > bottom_border:
                mouse_offset.y = mouse.y - bottom_border
                pygame.mouse.set_pos(mouse.x, bottom_border)


        self.offset += mouse_offset * self.mouse_speed




    #Toggles (devo chiarire ancora come puoi usare le varie modalità. Probabilmente è meglio lasciarle indipendenti e se le combini che crei casini lo sai tu)
    #region
    def ToggleKeyboardControl(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Sets on or off the keyboard control on the camera.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.keyboardControl_camera == False:
            self.BackupCameraMode()
            self.keyboardControl_camera = True
            self.center_target_camera = False
            self.box_camera = False
         
        else:
            self.keyboardControl_camera = False
            self.center_target_camera = self.cameraModeBackup['center_target_camera']
            self.box_camera = self.cameraModeBackup['box_camera']
            self.BackupCameraMode()
    def ToggleMouseControl(self):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Sets on or off the mouse control on the camera.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        None

        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        if self.mouseControl_camera == False:
            self.BackupCameraMode()
            self.keyboardControl_camera = True
            self.center_target_camera = False
            self.box_camera = False
         
        else:
            self.mouseControl_camera = False
            self.center_target_camera = self.cameraModeBackup['center_target_camera']
            self.box_camera = self.cameraModeBackup['box_camera']
            self.BackupCameraMode()
    #endregion
            


    def Draw(self):

        if self.backgroundSurface != None:
            toRenderGroundPos = Vector2(0,0)
            toRenderGroundPos -= self.offset
            self.targetSurface.blit(self.backgroundSurface, toRenderGroundPos.Vector2ToTuple())

        for component in self.privateRenderGroup:
            toRender = component.RenderToCamera()
            if toRender != None:
                toRenderPosition = toRender[1]
                toRenderPosition.x -= self.offset.x 
                toRenderPosition.y -= self.offset.y 
                self.targetSurface.blit(toRender[0],  toRenderPosition)
        
        Screen.screen.blit(self.targetSurface, (0,0))



class Scene():
    """
    INSTANCEABLE CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    Class used to create scenes.


    NOTES:
    Scenes are loaded from the SceneManager.


    ATTRIBUTES:

    STATIC:
    None

    INSTANCE:
    -name:                     string               the name of the scene
    -gameObjects:              list                 the list of all the gameObjects that make up a scene
    

    FUNCTIONS:

    STATIC:
    None

    INSTANCE:
    -__init__
    
    SYSTEM:
    None

    """
    def __init__(self, name, gameObjects):
        """
        INSTANCE FUNCTION

        DESCRIPTION:
        Creates a new Scene.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -name:                     string               the name of the scene
        -gameObjects:              list                 the list of all the gameObjects that make up a scene
    
        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        SceneManager.scenes.append(self)
        self.name = name
        self.gameObjects = gameObjects

class SceneManager():
    """
    STATIC CLASS

    INHERIT FROM:
    None


    DESCRIPTION:
    The SceneManager loads the different scenes.


    NOTES:
    None


    ATTRIBUTES:

    STATIC:
    -currentScene:          Scene           the current active and loaded Scene
    -scenes:                list            list of all the scenes of the project
    

    INSTANCE:
    None


    FUNCTIONS:

    STATIC:
    -LoadScene
    -LoadSceneWithName
    -UnloadScene

    INSTANCE:
    None

    SYSTEM:
    None

    """
    currentScene = None
    scenes = []

    def LoadScene(scene, unloadCurrent = True):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Loads a scene given the instance.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -scene:             Scene           the scene to load
        
        OPTIONAL:
        -unloadCurrent:     bool            if True means that the current scene is unloaded (see UnloadScene for more documentation)

        DEFAULTS OF OPTIONAL VALUES:
        -unloadCurrent:     bool            True

        """
        if unloadCurrent:
            SceneManager.UnloadScene()
        for g in scene.gameObjects:
            g.Instantiate()
        activeScene = scene

    def LoadSceneWithName(name, unloadCurrent = True):
        """
        STATIC FUNCTION

        DESCRIPTION:
        Loads the first occurrence of a scene with name "name" in the scenes list.

        NOTES:
        None

        PARAMETERS:
        REQUIRED:
        -name:             string           the name of the scene to load
        
        OPTIONAL:
        -unloadCurrent:     bool            if True means that the current scene is unloaded (see "UnloadScene" function for more documentation)

        DEFAULTS OF OPTIONAL VALUES:
        -unloadCurrent:     bool            True

        """
        for scene in SceneManager.scenes:
            if scene.name == name:
                return SceneManager.LoadScene(scene, unloadCurrent)

    def UnloadScene():
        """
        STATIC FUNCTION

        DESCRIPTION:
        Unloads the current scene.

        NOTES:
        Unloading a scene means to destroy all active gameObjects.
        This is called automatically when you load a new Scene (if the unloadCurrent parameter is True, see "LoadScene" function for more documentation).

        PARAMETERS:
        REQUIRED:
        None
        
        OPTIONAL:
        None

        DEFAULTS OF OPTIONAL VALUES:
        None

        """
        activeGO = GameObject.ActiveGameObjects().copy()
        for g in activeGO:
            if g.dontDestroyOnLoad == False:
                g.Destroy()


