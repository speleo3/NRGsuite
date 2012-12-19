'''
    NRGsuite: PyMOL molecular tools interface
    Copyright (C) 2011 Gaudreault, F., Morin, E. & Najmanovich, R.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

'''
@title: GetCleft - Interface

@summary: This is the interface of GetCleft application accessible via the
          PyMOL menu (NRGsuite).

@organization: Najmanovich Research Group
@creation date:  Oct. 19, 2010
'''

from Tkinter import *

import tkFileDialog, tkMessageBox
import tkFont, os

import General
import Color
import Prefs
import CleftObj
import ManageFiles2
import Default
import AdvOptions
#import CropCleft
import Volume

#=========================================================================================
'''                           ---   PARENT WINDOW  ---                                 '''
#========================================================================================= 

class displayGetCleft:
    
    ''' ==================================================================================
    FUNCTION __init__ : Initialization of the variables of the interface
    ================================================================================== '''
    def __init__(self, top, ActiveWizard, Project_Dir, Install_Dir, AlreadyRunning_Dir, OSid, PyMOL):
        
        self.PyMOL = PyMOL
        if self.PyMOL:
            from pymol import cmd
            import General_cmd

        self.OSid = OSid
        
        self.WINDOWWIDTH = 500
        self.WINDOWHEIGHT = 550

        #================================================================================== 
        ''' ROOT PATH TO THE FLEXAID DIRECTORY  '''
        self.AlreadyRunning_Dir = AlreadyRunning_Dir
        
        self.Install_Dir = Install_Dir
        self.Project_Dir = Project_Dir

        self.GetCleftInstall_Dir = os.path.join(self.Install_Dir,'GetCleft')

        self.BindingSiteProject_Dir = os.path.join(self.Project_Dir,'Binding_Site')

        if self.OSid == 'WIN':
            self.GetCleftExecutable = os.path.join(self.GetCleftInstall_Dir,'WRK','GetCleft.exe')
        else:
            self.GetCleftExecutable = os.path.join(self.GetCleftInstall_Dir,'WRK','GetCleft')

        self.Project_Dir = Project_Dir
        self.GetCleftProject_Dir = os.path.join(self.Project_Dir,'GetCleft')
        self.ProteinProject_Dir = os.path.join(self.Project_Dir,'Protein')

        self.GetCleftSaveProject_Dir = os.path.join(self.GetCleftProject_Dir,'Save')
        self.GetCleftTempProject_Dir = os.path.join(self.GetCleftProject_Dir,'Temp')

        #self.GetCleftTempCleftsProject_Dir = os.path.join(self.GetCleftTempProject_Dir,'Clefts')
        #self.GetCleftTempAtomsProject_Dir = os.path.join(self.GetCleftTempProject_Dir,'Atoms')

        # Create the folders if the arent exist
        self.ValidateFolders()
               
        self.GetCleftIsRunning()

        #self.MsgLineCounter = 2
        
        self.Color_Green = '#CCFFCC'
        self.Color_Grey = '#EDEDED'
        self.Color_Blue = '#6699FF'
        self.Color_Red = '#FF9999'
        self.Color_White = '#FFFFFF'
	self.Color_Black = 'black'

        self.top = top
        self.top.title('GetCleft')

        General.CenterWindow(self.top,self.WINDOWWIDTH,self.WINDOWHEIGHT)

        #self.top.geometry()   # Interface DIMENSIONS
        #self.top.maxsize(self.WINDOWWIDTH,self.WINDOWHEIGHT)
        #self.top.minsize(self.WINDOWWIDTH,self.WINDOWHEIGHT)
        self.top.protocol('WM_DELETE_WINDOW', self.Btn_Quit_Clicked)       

        #================================================================================== 
        #                 SET the default fonts of the interface
        #==================================================================================
        FontType = Prefs.GetFontType()
        FontSize = Prefs.GetFontSize()
        
        self.font_Title = tkFont.Font(family=FontType,size=FontSize, weight=tkFont.BOLD)        
        self.font_Text = tkFont.Font(family=FontType,size=FontSize)
        self.font_Text_I = tkFont.Font(family=FontType,size=FontSize, slant=tkFont.ITALIC)
        self.font_Text_U = tkFont.Font(family=FontType,size=FontSize, underline=True)       
        
        #================================================================================== 
        #                       FRAMES Settings and startup
        #==================================================================================
        self.fMain = Frame(self.top)  # Main frame
        self.fMain.pack(expand=True)

        self.ActiveFrame = None
        self.ActiveWizard = ActiveWizard
        self.WizardError = False
        self.WizardResult = 0

        self.ProcessRunning = False
        self.Run = None

        self.Frame_Main()

        # Build class objects of each tab
        self.Default = Default.Default(self, self.PyMOL)
        self.Manage = ManageFiles2.Manage(self)
        self.AdvOptions = AdvOptions.AdvOptions(self)        
        #self.Crop = CropCleft.CropCleft(self, self.PyMOL)        
        self.Volume = Volume.EstimateVolume(self)        
        
        self.listBtnTabs = [self.Btn_Config,self.Btn_Volume,self.Btn_CropCleft]

        # Default view
        self.Btn_Config_Clicked()
        
        # For testing purposes only
        Button(self.fMiddle, command=self.Default.Btn_Save_Clefts, text='Save clefts').pack(side=TOP)
        #Button(self.fMiddle, command=self.Default.Btn_Load_Clefts, text='Load clefts').pack(side=TOP)
        Button(self.fMiddle, command=self.Default.Btn_Save_BindingSite, text='Save binding-site').pack(side=TOP)
        #Button(self.fMiddle, command=self.Default.Btn_Load_BindingSite, text='Load binding-site').pack(side=TOP)
        #Button(self.fMiddle, command=self.Btn_EstimateVolume, text='Show Volume').pack(side=TOP)

    ''' ==================================================================================
    FUNCTION Frame_Main: Generate the Main interface containing ALL the Frames    
    ==================================================================================  '''        
    def Frame_Main(self):
        
        #==================================================================================
        '''                  --- TOP MENU OF THE INTERFACE ---                          '''
        #==================================================================================

        fTop = Frame(self.fMain, relief=RIDGE, border=4, height=50)
        fTop.pack(fill=BOTH, expand=True)#, padx=10, pady=10, ipady=10, ipadx=10, side=TOP)
	fTop.pack_propagate(0)
        
        self.Btn_Config = Button(fTop, text='Config', bg=self.Color_White, command=self.Btn_Config_Clicked, font=self.font_Text)
        self.Btn_Config.pack(side=LEFT, fill=BOTH, expand=True)
        self.Btn_Config.config(state='normal')

        self.Btn_CropCleft = Button(fTop, text='Cropping', bg=self.Color_Grey, command=self.Btn_CropCleft_Clicked, font=self.font_Text)
        self.Btn_CropCleft.pack(side=LEFT, fill=BOTH, expand=True)
        self.Btn_CropCleft.config(state='disabled')

        self.Btn_Volume = Button(fTop, text='Volume', bg=self.Color_Grey, command=self.Btn_Volume_Clicked, font=self.font_Text)
        self.Btn_Volume.pack(side=LEFT, fill=BOTH, expand=True)
        self.Btn_Volume.config(state='disabled')

        #==================================================================================
        '''                  --- MIDDLE FRAME OF THE INTERFACE ---                      '''
        #==================================================================================
        
        self.fMiddle = Frame(self.fMain, relief=RIDGE)
        self.fMiddle.pack(fill=X, expand=True, padx=10, pady=10)
        self.fMiddle.bind('<FocusIn>', lambda e: None)
        
        #==================================================================================
        '''                 BOTTOM DISPLAY SECTION OF THE INTERFACE                     '''
        #==================================================================================
 
        fBottom = Frame(self.fMain, border=1, relief=SUNKEN)
        fBottom.pack(fill=BOTH, expand=True, padx=10, pady=5, ipadx=10, ipady=5, side=TOP)

        fBottomRight = Frame(fBottom)
        fBottomRight.pack(fill=Y, side=RIGHT)

        Btn_Default = Button(fBottomRight, text='Default', command=self.Btn_Default_Clicked, font=self.font_Text)
        Btn_Default.pack(side=TOP, fill=X)

        Btn_SaveDefault = Button(fBottomRight, text='Save as default', command=self.Btn_SaveDefault_Clicked, font=self.font_Text)
        Btn_SaveDefault.pack(side=TOP, fill=X)

        Btn_Restore = Button(fBottomRight, text='Restore', command=self.Btn_Restore_Clicked, font=self.font_Text)
        Btn_Restore.pack(side=TOP, fill=X)

        Btn_Quit = Button(fBottomRight, text='Close', command=self.Btn_Quit_Clicked, font=self.font_Text)

        Btn_Quit.pack(side=BOTTOM, fill=X)

        fBottomLeft = Frame(fBottom)
        fBottomLeft.pack(side=LEFT, fill=Y)

	#self.MessageBox = MessageBox.scrollableContainer(fBottomLeft, bd=2, bg="black")
	#self.MessageBox.pack(fill=BOTH, expand=True)

        scrollBar = Scrollbar(fBottomLeft)
        scrollBar.pack(side=RIGHT, fill=Y)

        self.TextMessage = Text(fBottomLeft, border=1, background=self.Color_Grey, font=self.font_Text)
        self.TextMessage.pack(side=RIGHT, fill=BOTH, expand=True)

        scrollBar.config(command=self.TextMessage.yview)
        self.TextMessage.config(state='disabled', yscrollcommand=scrollBar.set)                                       
    
    ''' ==================================================================================
    FUNCTION Btn_Config_Clicked: Default configuration view
    ==================================================================================  '''                 
    def Btn_Config_Clicked(self):
        
        self.SetActiveFrame(self.Default)

    ''' ==================================================================================
    FUNCTION Btn_Volume_Clicked: Estimates the volume of the loaded Clefts
    ==================================================================================  '''                 
    def Btn_Volume_Clicked(self):
        
        self.SetActiveFrame(self.Volume)
        
    ''' ==================================================================================
    FUNCTION Btn_CropCleft_Clicked: Opens the crop cleft menu 
    ==================================================================================  '''                 
    def Btn_CropCleft_Clicked(self):
        
        self.SetActiveFrame(self.Crop)

    ''' ==================================================================================
    FUNCTION Go_Step1: Enables/Disables buttons for step 1
    ================================================================================== '''    
    def Go_Step1(self):

        #print "Setting Tab buttons to Step 1"        
        for Btn in self.listBtnTabs:
            Btn.config(state='disabled', bg=self.Color_Grey)

        self.Btn_Config.config(state='normal')
        self.Btn_Config.config(bg=self.Color_Blue)

    ''' ==================================================================================
    FUNCTION Go_Step2: Enables/Disables buttons for step 2
    ================================================================================== '''    
    def Go_Step2(self):
        
        #print "Setting Tab buttons to Step 2"
        for Btn in self.listBtnTabs:
            Btn.config(state='normal',bg=self.Color_White)

    ''' ==================================================================================
    FUNCTION ValidateFolders: Be sure the folders Exists 
    ==================================================================================  '''    
    def ValidateFolders(self):
        
        if not os.path.isdir(self.GetCleftProject_Dir):
            os.makedirs(self.GetCleftProject_Dir)
            
        if not os.path.isdir(self.ProteinProject_Dir):
            os.makedirs(self.ProteinProject_Dir)

        if not os.path.isdir(self.BindingSiteProject_Dir):
            os.makedirs(self.BindingSiteProject_Dir)
        
        if not os.path.isdir(self.GetCleftSaveProject_Dir):
            os.makedirs(self.GetCleftSaveProject_Dir)

        if not os.path.isdir(self.GetCleftTempProject_Dir):
            os.makedirs(self.GetCleftTempProject_Dir)
            
        #if not os.path.isdir(self.GetCleftTempCleftsProject_Dir):
        #    os.makedirs(self.GetCleftTempCleftsProject_Dir)
            
        #if not os.path.isdir(self.GetCleftTempAtomsProject_Dir):
        #    os.makedirs(self.GetCleftTempAtomsProject_Dir)

    
    ''' ==================================================================================
    FUNCTION DisplayMessage: Display the message  
    ==================================================================================  '''    
    def DisplayMessage(self, msg, priority):
        
        self.TextMessage.config(state='normal', font=self.font_Text) 
        self.TextMessage.insert(INSERT, '\n' + msg)

        if priority == 1:
            #self.TextMessage.tag_add('warn', lineNo + '.0', lineNo + '.' + str(NbChar))
            self.TextMessage.tag_config('warn', foreground='red')
        elif priority == 2:
            #self.TextMessage.tag_add('notice', lineNo + '.0', lineNo + '.' + str(NbChar))
            self.TextMessage.tag_config('notice', foreground='blue')   

        self.TextMessage.yview(INSERT)
        
        
    ''' ==================================================================================
    FUNCTION Btn_Quit_Clicked: Exit the application 
    ==================================================================================  '''
    def Btn_Quit_Clicked(self):
        
        #Delete the .run file
        RunPath = os.path.join(self.AlreadyRunning_Dir,'.grun')
        if os.path.isfile(RunPath):
            try:
                os.remove(RunPath)
            except OSError:
                time.sleep(0.1)
                os.remove(RunPath)
                    
        self.top.destroy()        

        print('   Closed GetCleft.')
        

    ''' ==================================================================================
    FUNCTION GetCleftIsRunning: Update or Create the Running File to BLOCK multiple GUI 
    ==================================================================================  '''       
    def GetCleftIsRunning(self):
        
        #Create the .run file
        RunPath = os.path.join(self.AlreadyRunning_Dir,'.grun')
        RunFile = open(RunPath, 'w')
        RunFile.write(str(os.getpid()))
        RunFile.close()

    ''' ==================================================================================
    FUNCTION Lost_Focus: Draws a red square in box if field was not validated
    ==================================================================================  '''    
    def Lost_Focus(self, event, args):

        self.Validate_Field(args)

        Entry = args[0]
        Validator = args[5]
        
        if not Validator[0]:
            Entry.config(bg=self.Color_Red)

        return "break"

    ''' ==================================================================================
    FUNCTION Validate_Field: Validates an Entry Field in the GetCleft interface
    ==================================================================================  '''    
    def Validate_Field(self, args):

        Entry = args[0]
        StringVar = args[1]
        Min = args[2]
        Max = args[3]
        nDec = args[4]
        Validator = args[5]
        Label = args[6]
        Type = args[7]

        rv = -1

        if Type == 'float':
            # If the min-max value depends on another Widget Entry value
            if type(Min) != float:
                try:
                    Min = float(Min.get())
                except:
                    Min = 0.0

            if type(Max) != float:
                try:
                    Max = float(Max.get())
                except:
                    Max = 1.0

            rv = General.validate_Float(StringVar.get(), Min, Max, nDec)

        elif Type == 'int':
            # If the min-max value depends on another Widget Entry value
            if type(Min) != int:
                try:
                    Min = int(Min.get())
                except: 
                    Min = 1

            if type(Max) != int:
                try:
                    Max = int(Max.get())
                except:
                    Max = 100
        
            rv = General.validate_Integer(StringVar.get(), Min, Max)

        elif Type == 'str':
            rv = General.validate_String(StringVar.get())

        # Return-value testing
        if rv == 0:
            Entry.config(bg=self.Color_White)
            Validator[0] = True
 
        elif rv == 1:
            self.DisplayMessage("Value has erroneus format for field " + Label, 1)
            Validator[0] = False

        elif rv == 2:
            self.DisplayMessage("The number of decimals cannot exceed (" + str(nDec) + ") for field " + Label, 1)
            Validator[0] = False

        elif rv == 3:
            self.DisplayMessage("Value must be within the range[" + str(Min) + "," + str(Max) + "] for field " + Label, 1)
            Validator[0] = False

        elif rv == -1:
            print "Unknown data format"


    ''' ==================================================================================
    FUNCTION Validate_Entries: Validate all entries of a frame before switching
    ==================================================================================  '''    
    def Validate_Entries(self, list):
        
        #print list
        for valid in list:
            if not valid[2] and valid[0] == False:

                if valid[3] != None:
                    valid[3].config(bg=self.Color_Red)

                return valid[1]

        return 0


    ''' ==================================================================================
    FUNCTION SetActiveFrame: Switch up tabs in the uppper menu
    ================================================================================== '''    
    def SetActiveFrame(self, Frame):

        if not self.ActiveWizard is None:
            self.DisplayMessage("Cannot switch tab: A wizard is currently running...", 2)
            return

        if self.ProcessRunning:
            self.DisplayMessage("Cannot switch tab: A process is currently running...", 2)
            return

        if self.ActiveFrame != Frame:

            if not self.ActiveFrame is None:

                # Trigger lost_focus event for validation
                self.fMiddle.focus_set()
                self.fMiddle.update_idletasks()

                rv = self.Validate_Entries(self.ActiveFrame.Validator)
                if rv > 0:
                    if rv == 1:
                        self.DisplayMessage("Cannot switch tab: Not all fields are validated", 2)
                    elif rv == 2:
                        self.ActiveFrame.Validator_Fail()
                    return

                if not self.ActiveFrame.Kill_Frame():
                    self.DisplayMessage("Cannot switch tab: Not all fields are validated", 2)
                    return

                self.fMiddle.update_idletasks()

                #print "Killed Frame " + self.ActiveFrame.FrameName
                #self.ActiveFrame.Del_Trace()

            self.ActiveFrame = Frame
            #print "New active frame " + self.ActiveFrame.FrameName

            self.ActiveFrame.Show()
            self.ActiveFrame.Tab.config(bg=self.Color_Blue)

            self.fMiddle.update_idletasks()

        return


    ''' ==================================================================================
    FUNCTION Btn_Restore_Clicked: Restore the original default configuration
    ================================================================================== '''    
    def Btn_Restore_Clicked(self):

	    return

    ''' ==================================================================================
    FUNCTION Btn_SaveDefault_Clicked: Saves the current configuration as default
    ================================================================================== '''    
    def Btn_SaveDefault_Clicked(self):

	    return

    ''' ==================================================================================
    FUNCTION Btn_Default_Clicked: Sets back the default config
    ================================================================================== '''    
    def Btn_Default_Clicked(self):
        
        if self.ActiveWizard != None:
            self.DisplayMessage("Cannot reset values while a Wizard is active", 2)
            return

        if self.ProcessRunning is True:
            self.DisplayMessage("Cannot reset values while a Process is running", 2)
            return
            
        self.ActiveFrame.Init_Vars()