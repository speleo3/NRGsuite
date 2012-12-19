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

from Tkinter import *

import os
import functools
import tkFileDialog
import General
import SphereObj
import CleftObj
import BindingSite
import TargetFlex
import pickle

if __debug__:
    from pymol import cmd
    from pymol.wizard import Wizard

    import Sphere
    import FlexSideChain
    import General_cmd
            

class Config1:

    def __init__(self,top,PyMOL):
        
        #print "New instance of Config1"
        self.PyMOL = PyMOL

        self.top = top
        self.Tab = self.top.Btn_Config1
        self.FrameName = 'Config1'

        self.DisplayMessage = self.top.DisplayMessage

        self.Def_Vars()
        self.Init_Vars()

        self.Frame()
        self.Trace()

    def Def_Vars(self):
        
        self.RngOpt = StringVar()

        self.ResiduValue = StringVar()
        self.defOptSphere = StringVar()
        self.defOptCleft = StringVar()
        self.defOptResidue = StringVar()
        self.SphereSize = DoubleVar()

        self.StateList = list()
        self.listResidues = list()

        self.TargetFlexName = StringVar()
        self.BindingSiteName = StringVar()

        self.BindingSite = BindingSite.BindingSite()
        self.TargetFlex = TargetFlex.TargetFlex()

        self.ValidCleft = list()
        self.Validator = list()


    def Init_Vars(self):

        self.RngOpt.set('')

        self.defOptSphere.set('')
        self.defOptCleft.set('')
        self.defOptResidue.set('')
        self.SphereSize.set(0.0)
                
        self.ProcessError = False
        self.BindingSiteDisplay = 'BINDINGSITE_AREA__'
        self.SphereDisplay = 'SPHERE__'
        self.ScaleResolution = 0.25
        
        self.HIGHLIGHT_RELIEF = RAISED
        self.HIGHLIGHT_RELIEF = SUNKEN
        self.HIGHLIGHT_WIDTH = 2
        
        self.FlexSideChainPath = ''        
        self.ResiduValue.set('')

        self.CleftPath = os.path.join(self.top.BindingSiteProject_Dir,'tmp.pdb')
        self.TargetFlexName.set('')
        self.BindingSiteName.set('')

        self.TargetFlex.Clear_SideChain()
        self.BindingSite.Clear()

        self.ValidCleft = [True, 2, 0, None]
        self.ValidGridDistance = [True, 1, 0, None]
        self.Validator = [self.ValidCleft]

    ''' ==================================================================================
    FUNCTION Trace: Adds a callback to StringVars
    =================================================================================  '''    
    def Trace(self):

        self.RngOptTrace = self.RngOpt.trace('w',self.RngOpt_Toggle)
        self.defOptCleftTrace = self.defOptCleft.trace('w',self.defOptCleft_Toggle)
        #self.BindingSiteNameTrace = self.BindingSiteName.trace('w',self.BindingSiteName_Toggle)

    ''' ==================================================================================
    FUNCTION Del_Trace: Deletes observer callbacks
    =================================================================================  '''    
    def Del_Trace(self):

        self.RngOpt.trace_vdelete('w',self.RngOptTrace)
        self.defOptCleft.trace_vdelete('w',self.defOptCleftTrace)
        #self.BindingSiteName.trace_vdelete('w',self.BindingSiteNameTrace)

    ''' ==================================================================================
    FUNCTION Kill_Frame: Kills the main frame window
    =================================================================================  '''    
    def Kill_Frame(self):
        
        self.fConfig.pack_forget()
        self.Highlight_SelectedCleft('')

        return True

    ''' ==================================================================================
    FUNCTION Validator_Fail: Triggers visual events upon validation failure
    =================================================================================  '''    
    def Validator_Fail(self):
        
        if self.BindingSite.Type == 2 and self.BindingSite.Count_Cleft() == 0:

            self.Btn_Import_Cleft.flash()
            self.Btn_Import_Cleft.flash()

            self.top.DisplayMessage("  You cannot proceed further until you:", 2)
            self.top.DisplayMessage("          1) Import clefts generated from GetCleft", 2)
            self.top.DisplayMessage("          2) Load a previously configured binding-site", 2)

    ''' ==================================================================================
    FUNCTION Show: Displays the frame onto the middle main frame
    ==================================================================================  '''  
    def Show(self):
        
        self.LoadMessage()
        
        self.fConfig.pack(fill=BOTH, expand=True)

        self.Btn_OptSphRefresh_Clicked()

        self.Update_FlexSideChain_DDL()
        self.Update_Clefts_DDL()

        #self.Highlight_RngOpt()

    ''' ==================================================================================
    FUNCTION Frame: Generate the Configuration Options frame in the the middle 
                    frame section
    =================================================================================  '''    
    def Frame(self):
           
        self.fConfig = Frame(self.top.fMiddle)

        #==================================================================================
        '''                        ---  FRAME -  TOP   SIDE  ---                        '''
        #==================================================================================      

        self.fBindingSite = Frame(self.fConfig, border=2, relief=RAISED)
        self.fBindingSite.pack(fill=BOTH, side=TOP, padx=5, pady=5)

        Label(self.fBindingSite, text='Binding-site definition', font=self.top.font_Title).pack(side=TOP, fill=X)

        fConfBS = Frame(self.fBindingSite)
        fConfBS.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)

        Label(fConfBS, text='Pre-configured binding-site:', width=30, font=self.top.font_Text).pack(side=LEFT)
        Button(fConfBS, text='Load', command=self.Btn_LoadConfBS_Clicked, font=self.top.font_Text).pack(side=LEFT)
        Button(fConfBS, text='Save', command=self.Btn_SaveConfBS_Clicked, font=self.top.font_Text).pack(side=LEFT)
        Entry(fConfBS, textvariable=self.BindingSiteName, font=self.top.font_Text, state='disabled', disabledbackground=self.top.Color_White, disabledforeground=self.top.Color_Black).pack(side=LEFT, fill=X, expand=True)
        
        #=================================================================================
        # Range Optimization fields
        #==================================================================================
        fRangeOpt = Frame(self.fBindingSite)
        fRangeOpt.pack(fill=BOTH, expand=True, padx=5, pady=5)

        Label(fRangeOpt, text='Choose binding-site type', font=self.top.font_Title).pack(side=TOP, fill=X)

        self.fRangeOptLeft = Frame(fRangeOpt)
        self.fRangeOptLeft.pack(side=LEFT, padx=3, expand=True, fill=BOTH)

        fRangeOptLeftLine1 = Frame(self.fRangeOptLeft)
        fRangeOptLeftLine1.pack(side=TOP, fill=X)
        fRangeOptLeftLine2 = Frame(self.fRangeOptLeft)
        fRangeOptLeftLine2.pack(side=TOP, fill=X)
        fRangeOptLeftLine3 = Frame(self.fRangeOptLeft)
        fRangeOptLeftLine3.pack(side=TOP, fill=X)

        self.fRangeOptRight = Frame(fRangeOpt)
        self.fRangeOptRight.pack(side=LEFT, padx=3, expand=True, fill=BOTH)

        fRangeOptRightLine1 = Frame(self.fRangeOptRight)
        fRangeOptRightLine1.pack(side=TOP, fill=X)
        fRangeOptRightLine2 = Frame(self.fRangeOptRight)
        fRangeOptRightLine2.pack(side=TOP, fill=X)
        fRangeOptRightLine3 = Frame(self.fRangeOptRight)
        fRangeOptRightLine3.pack(side=TOP, fill=X)

        #=====================================================================================
        #SPHERE Section        
        self.RadioBtn_Sphere = Radiobutton(fRangeOptLeftLine1, text='SPHERE', variable=self.RngOpt, value='LOCCEN', font=self.top.font_Text, disabledforeground=self.top.Color_White)
        self.RadioBtn_Sphere.pack(side=TOP, anchor=N)

        Label(fRangeOptLeftLine2, text='Radius:', width=10, font=self.top.font_Text).pack(side=LEFT, anchor=SE)
        
        self.sclResizeSphere = Scale(fRangeOptLeftLine2, from_ = 0.0, to = 0.0, orient=HORIZONTAL, length=150, resolution=self.ScaleResolution, command=self.ResizeSphere, variable=self.SphereSize)
        self.sclResizeSphere.pack(side=LEFT)
        self.sclResizeSphere.config(state='disabled')

        self.Btn_EditSphere = Button(fRangeOptLeftLine2, text='Edit', command=self.Btn_EditSphere_Clicked, font=self.top.font_Text)
        self.Btn_EditSphere.pack(side=LEFT)
        self.Btn_EditSphere.config(state='disabled')            
        
        Label(fRangeOptLeftLine3, text='Center with:', width=10, font=self.top.font_Text).pack(side=LEFT)
        optionTuple = '',
        self.OptMenuSphere = apply(OptionMenu, (fRangeOptLeftLine3, self.defOptSphere) + optionTuple)
        self.OptMenuSphere.config(state='disabled', width=15)
        self.OptMenuSphere.pack(side=LEFT)

        self.Btn_OptSphRefresh = Button(fRangeOptLeftLine3, text='Refresh', command=self.Btn_OptSphRefresh_Clicked, font=self.top.font_Text)
        self.Btn_OptSphRefresh.pack(side=LEFT)
        self.Btn_OptSphRefresh.config(state='disabled')            
                        
        #=====================================================================================
        # CLEFT Section
        #=====================================================================================        
        self.RadioBtn_Cleft = Radiobutton(fRangeOptRightLine1, text='CLEFT', variable=self.RngOpt, value='LOCCLF', font=self.top.font_Text, disabledforeground=self.top.Color_White)
        self.RadioBtn_Cleft.pack(side=TOP, anchor=N)
                
        #Label(fRangeOptRightLine2, text='Clefts:', width=10, font=self.top.font_Text).pack(side=LEFT)
        
        self.Btn_ImportCleft = Button(fRangeOptRightLine2, text='Import clefts', command=self.Btn_Import_Clefts, font=self.top.font_Text)
        self.Btn_ImportCleft.pack(side=RIGHT)
        self.Btn_ImportCleft.config(state='disabled')

        self.Btn_ClearCleft = Button(fRangeOptRightLine3, text='Clear', command=self.Btn_ClearCleft_Clicked, font=self.top.font_Text)
        self.Btn_ClearCleft.pack(side=RIGHT)
        self.Btn_ClearCleft.config(state='disabled')

        self.Btn_DeleteCleft = Button(fRangeOptRightLine3, text='Delete', command=self.Btn_DeleteCleft_Clicked, font=self.top.font_Text)
        self.Btn_DeleteCleft.pack(side=RIGHT)
        self.Btn_DeleteCleft.config(state='disabled')

        optionTuple = '',
        self.OptMenuCleft = apply(OptionMenu, (fRangeOptRightLine3, self.defOptCleft) + optionTuple)
        self.OptMenuCleft.config(state='disabled', width=15)
        self.OptMenuCleft.pack(side=RIGHT)
     
        #==================================================================================
        '''                        ---  FRAME - BOTTOM SIDE  ---                        '''
        #==================================================================================      

        fProtFlex = Frame(self.fConfig, border=2, relief=RAISED)
        fProtFlex.pack(fill=BOTH, side=TOP, padx=5, pady=5)

        Label(fProtFlex, text='Target flexibility', font=self.top.font_Title).pack(side=TOP, fill=X)

        #==================================================================================
        # Pre-configured protein flexibility
        #==================================================================================
        fConfFlex = Frame(fProtFlex)
        fConfFlex.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)

        Label(fConfFlex, text='Pre-configured target flexibility:', width=30, font=self.top.font_Text).pack(side=LEFT)
        Button(fConfFlex, text='Load', command=self.Btn_LoadConfFlex_Clicked, font=self.top.font_Text).pack(side=LEFT)
        Button(fConfFlex, text='Save', command=self.Btn_SaveConfFlex_Clicked, font=self.top.font_Text).pack(side=LEFT)
        Entry(fConfFlex, textvariable=self.TargetFlexName, font=self.top.font_Text, state='disabled', disabledbackground=self.top.Color_White, disabledforeground=self.top.Color_Black).pack(side=LEFT, fill=X, expand=True)

        #==================================================================================
        # Flexible Side-Chains
        #==================================================================================
        self.fFlexSC = Frame(fProtFlex)
        self.fFlexSC.pack(side=TOP, fill=X, padx=5, pady=5)
        
        fFlexSCLine1 = Frame(self.fFlexSC)
        fFlexSCLine1.pack(fill=X, side=TOP)

        fFlexSCLine2 = Frame(self.fFlexSC)
        fFlexSCLine2.pack(fill=X, side=TOP)

        fFlexSCLine3 = Frame(self.fFlexSC)
        fFlexSCLine3.pack(fill=X, side=TOP)

        Label(fFlexSCLine1, text='Flexible Side-Chains', font=self.top.font_Title).pack(side=LEFT)
        Label(fFlexSCLine2, text='Enter residue name (e.g. ALA21A):', width=30, font=self.top.font_Text, justify=LEFT).pack(side=LEFT, anchor=W)
        self.EntryResidu = Entry(fFlexSCLine2, textvariable=self.ResiduValue, background='white', width=10, justify=CENTER, font=self.top.font_Text)
        self.EntryResidu.pack(side=LEFT, anchor=E)

        Button(fFlexSCLine2, text='Add', command=self.Btn_AddResidu_Clicked, font=self.top.font_Text).pack(side=LEFT)        
        Button(fFlexSCLine2, text='Add from PyMOL', command=self.SelectFlexibleSideChains, font=self.top.font_Text).pack(side=LEFT)

        Label(fFlexSCLine3, text='', width=30, font=self.top.font_Text).pack(side=LEFT, anchor=W)                
        optionTuple = '',
        self.optMenuWidgetRES = apply(OptionMenu, (fFlexSCLine3, self.defOptResidue) + optionTuple)
        self.optMenuWidgetRES.config(width=10, bg='white', font=self.top.font_Text)
        self.optMenuWidgetRES.pack(side=LEFT, anchor=NE, padx=4)
        Button(fFlexSCLine3, text='Delete', command=self.Btn_DelResidu_Clicked, font=self.top.font_Text).pack(side=LEFT)
        Button(fFlexSCLine3, text='Clear', command=self.Btn_DelAllResidu_Clicked, font=self.top.font_Text).pack(side=LEFT)
                    
        #==================================================================================
        # Normal-modes
        #==================================================================================
        fNormalModes = Frame(fProtFlex)
        fNormalModes.pack(fill=X, side=TOP, padx=5, pady=5)

        fNMrow1 = Frame(fNormalModes)
        fNMrow1.pack(fill=X, side=TOP)

        fNMrow2 = Frame(fNormalModes)
        fNMrow2.pack(fill=X, side=TOP)
        
        Label(fNMrow1, text='Normal Modes', font=self.top.font_Title).pack(side=LEFT)
        Label(fNMrow2, text='Upcoming feature...', width=30, font=self.top.font_Text_I).pack(side=LEFT, anchor=W)
                           
    ''' ==================================================================================
    FUNCTION Get_TargetFlexPath: Returns the default path of target flexibility
    =================================================================================  '''    
    def Get_TargetFlexPath(self):

        PROTNAME = self.top.IOFile.ProtName.get().upper()
        TargetFlexPath = os.path.join(self.top.FlexAIDTargetFlexProject_Dir,PROTNAME)
        
        return TargetFlexPath

    ''' ==================================================================================
    FUNCTION Highlight_SelectedCleft: Highlights the selected cleft
    =================================================================================  '''                            
    def Highlight_SelectedCleft(self, CleftName):

        if self.BindingSite.Type == 2:
            
            cmd.color('purpleblue', self.BindingSiteDisplay)
            
            if CleftName != '':
                Cleft = self.BindingSite.Get_CleftName(CleftName)
                cmd.color('oxygen', self.BindingSiteDisplay + ' & resi ' + str(Cleft.Index))
                self.defOptCleft.set(CleftName)

    ''' ==================================================================================
    FUNCTION defOptCleft_Toggle: Highlights the selected cleft
    =================================================================================  '''    
    def defOptCleft_Toggle(self,*args):

        self.Highlight_SelectedCleft(self.defOptCleft.get())

    ''' ==================================================================================
    FUNCTION RngOpt_Toggle: Changes the optimization range
    =================================================================================  '''    
    def RngOpt_Toggle(self,*args):
        
        if self.RngOpt.get() == 'LOCCLF':
            self.Btn_ImportCleft.config(state='normal')
            self.Btn_DeleteCleft.config(state='normal')        
            self.Btn_ClearCleft.config(state='normal')        
            self.OptMenuCleft.config(state='normal')

            self.Btn_EditSphere.config(state='disabled')

            self.BindingSite.Set_Cleft()
            self.Display_BindingSite()

        elif self.RngOpt.get() == 'LOCCEN':
            self.Btn_ImportCleft.config(state='disabled')
            self.Btn_DeleteCleft.config(state='disabled')
            self.Btn_ClearCleft.config(state='disabled')
            self.OptMenuCleft.config(state='disabled')

            self.Btn_EditSphere.config(state='normal')
                    
            if self.BindingSite.Sphere == None:
                self.Create_NewSphere()

            self.BindingSite.Set_Sphere()
            self.Display_BindingSite()

        else:
            self.Btn_ImportCleft.config(state='disabled')
            self.Btn_DeleteCleft.config(state='disabled')        
            self.Btn_ClearCleft.config(state='disabled')        
            self.OptMenuCleft.config(state='disabled')
                    
            self.Btn_EditSphere.config(state='disabled')
            
            self.BindingSite.Unset()
            self.Delete_BindingSite()
                
        self.Highlight_RngOpt()
        self.top.fMiddle.update_idletasks()
        
    ''' ==================================================================================
    FUNCTION Create_NewSphere: Creates a new sphere using the target as center of geometry
    ==================================================================================  '''               
    def Create_NewSphere(self):
        
        if not self.PyMOL:
            return
        
        Center = General_cmd.Get_CenterOfMass2(self.top.IOFile.ProtName.get())
        Width = General_cmd.Get_MaxWidth(self.top.IOFile.ProtName.get())

        if len(Center) > 0 and Width != -1:
            self.BindingSite.Sphere = SphereObj.SphereObj(Width/4.0,Width/2.0,Center)
            self.sclResizeSphere.config(from_=1.0,to=self.BindingSite.Sphere.MaxRadius)
            self.SphereSize.set(self.BindingSite.Sphere.Radius)
        else:
            self.DisplayMessage("  ERROR: Could not display the default sphere", 1)
            self.RngOpt.set('')

    ''' ==================================================================================
    FUNCTION SelectFlexibleSideChains: Starts the flexible side-chain wizard
    ==================================================================================  '''               
    def SelectFlexibleSideChains(self):

        if not self.PyMOL:
            return

        if self.top.ActiveWizard is None:
            self.FlexSCRunning(True)
            self.top.ActiveWizard = FlexSideChain.flexSC(self)
            cmd.set_wizard(self.top.ActiveWizard)

            self.top.ActiveWizard.Start()
            
        else:
            self.top.DisplayMessage("  ERROR: Could not open Wizard because one is already active", 2)

    ''' ==================================================================================
    FUNCTION FlexSCRunning: Disables/Enables controls related to Flexible side-chains
    ==================================================================================  '''               
    def FlexSCRunning(self, boolRun):
        
        if boolRun:
            del self.StateList[:]
            General.saveState(self.fFlexSC, self.StateList)
            General.setState(self.fFlexSC)
        else:
            General.backState(self.fFlexSC, self.StateList)
            self.Update_FlexSideChain_DDL()

    ''' ==================================================================================
    FUNCTION Update_FlexSideChain_DDL: Updates the drop-down-list meny of flex sc.
    ==================================================================================  '''           
    def Update_FlexSideChain_DDL(self):

        self.optMenuWidgetRES["menu"].delete(0, END)

        Residue = ''
        for res in sorted(self.TargetFlex.listSideChain):
            self.optMenuWidgetRES["menu"].add_command(label=res, command=lambda temp = res: self.optMenuWidgetRES.setvar(self.optMenuWidgetRES.cget("textvariable"), value = temp))
            Residue = res

        self.defOptResidue.set(Residue)

    ''' ==================================================================================
    FUNCTION Update_Clefts_DDL: Updates the drop-down-list of clefts
    ==================================================================================  '''           
    def Update_Clefts_DDL(self):

        self.OptMenuCleft["menu"].delete(0, END)

        CleftName = ''
        for clf in self.BindingSite.Get_SortedCleftNames():
            self.OptMenuCleft["menu"].add_command(label=clf, command=lambda temp = clf: self.Highlight_SelectedCleft(temp))
            CleftName = clf

        self.defOptCleft.set(CleftName)

    ''' ==================================================================================
    FUNCTION Btn_LoadConfFlex_Clicked: Loads a preconfigured protein flexibility
    ==================================================================================  '''           
    def Btn_LoadConfFlex_Clicked(self):

        TargetFlexPath = self.Get_TargetFlexPath()

        if not os.path.isdir(TargetFlexPath):
            self.DisplayMessage("  Could not find a TargetFlex folder for your target:", 2)
            self.DisplayMessage("  The default TargetFlex folder is used.", 2)

            TargetFlexPath = self.top.FlexAIDTargetFlexProject_Dir
            
        LoadPath = tkFileDialog.askopenfilename(filetypes=[('NRG TargetFlex file','*.nrgtf')],
                                                initialdir=TargetFlexPath, title='Load a TargetFlex file')

        if len(LoadPath) > 0:
            try:
                in_ = open(LoadPath, 'r')
                TargetFlex = pickle.load(in_)
                in_.close()

                TargetFlex.listSideChain[:] = [ res for res in TargetFlex.listSideChain if self.listResidues.count(res) ]

                if TargetFlex.Count_SideChain() > 0: # or normal modes
                    self.TargetFlex = TargetFlex
                    self.Update_FlexSideChain_DDL()

                    self.TargetFlexName.set(os.path.basename(os.path.splitext(LoadPath)[0]))
                else:
                    self.DisplayMessage("  ERROR: The TargetFlex '" + LoadPath + "' does not match the selected target", 2)

            except:
                self.DisplayMessage("  ERROR: Could not read the TargetFlex", 2)

    ''' ==================================================================================
    FUNCTION Btn_SaveConfFlex_Clicked: Saves the current protein flexibility
    ==================================================================================  '''           
    def Btn_SaveConfFlex_Clicked(self):

        TargetFlexPath = self.Get_TargetFlexPath()
        #DefaultName = self.Test

        if self.TargetFlex.Count_SideChain() > 0:
            
            if not os.path.isdir(TargetFlexPath):
                os.makedirs(TargetFlexPath)

            SaveFile = tkFileDialog.asksaveasfilename(initialdir=TargetFlexPath,
                                                      title='Save the TargetFlex file', initialfile='def_targetflex',
                                                      filetypes=[('NRG TargetFlex','*.nrgtf')])
                
            if len(SaveFile) > 0:
                
                if SaveFile.find('.nrgtf') == -1:
                    SaveFile = SaveFile + '.nrgtf'

                try:
                    out = open(SaveFile, 'w')
                    pickle.dump(self.TargetFlex, out)
                    out.close()

                    self.TargetFlexName.set(os.path.basename(os.path.splitext(SaveFile)[0]))

                    self.top.DisplayMessage("  Successfully saved '" + SaveFile + "'", 0)
                except:
                    self.top.DisplayMessage("  Could not save target flexibility configuration", 0)

    ''' ==================================================================================
    FUNCTION Btn_LoadConfBS_Clicked: Asks for user to load binding-site
    ==================================================================================  '''        
    def Btn_LoadConfBS_Clicked(self):

        if self.top.ActiveWizard != None:
            self.DisplayMessage("  Cannot load a binding-site while the 'Sphere' Wizard is currently active", 2)
            return

        BindingSitePath = self.Get_BindingSitePath()

        if not os.path.isdir(BindingSitePath):
            self.DisplayMessage("  Could not find a BindingSite folder for your target:", 2)
            self.DisplayMessage("  The default BindingSite folder is used.", 2)
            
            BindingSitePath = self.top.BindingSiteProject_Dir
        
        LoadPath = tkFileDialog.askopenfilename(filetypes=[('NRG BindingSite','*.nrgbs')],
                                                initialdir=BindingSitePath, title='Select a BindingSite file to load')
        
        if len(LoadPath) > 0:
            try:
                in_ = open(LoadPath, 'r')
                BindingSite = pickle.load(in_)
                in_.close()
                
                if BindingSite.Type != 0 and (BindingSite.Count_Cleft() > 0 or BindingSite.Sphere != None):
                    self.BindingSite = BindingSite

                    if self.BindingSite.Type == 1:
                        self.sclResizeSphere.config(from_=1.0,to=self.BindingSite.Sphere.MaxRadius)
                        self.SphereSize.set(self.BindingSite.Sphere.Radius)
                        self.RngOpt.set('LOCCEN')
                    elif self.BindingSite.Type == 2:
                        self.RngOpt.set('LOCCLF')
                
                    self.Update_Clefts_DDL()
                
                    self.BindingSiteName.set(os.path.basename(os.path.splitext(LoadPath)[0]))

                else:
                    self.DisplayMessage("  ERROR: The BindingSite file has unknown format", 2)
                
            except:
                self.DisplayMessage("  ERROR: Could not read the BindingSite file", 2)

    ''' ==================================================================================
    FUNCTION Btn_SaveConfBS_Clicked: Asks for user to save binding-site
    ==================================================================================  '''        
    def Btn_SaveConfBS_Clicked(self):

        if self.top.ActiveWizard != None:
            self.DisplayMessage("  Cannot save a binding-site while the 'Sphere' Wizard is currently active", 2)
            return

        BindingSitePath = self.Get_BindingSitePath()

        if self.BindingSite.Type == 1 or (self.BindingSite.Type == 2 and self.BindingSite.Count_Cleft() > 0):
            
            if not os.path.isdir(BindingSitePath):
                os.makedirs(BindingSitePath)

            SaveFile = tkFileDialog.asksaveasfilename(initialdir=BindingSitePath,
                                                      title='Save the BindingSite file', initialfile='my_default_bindingsite',
                                                      filetypes=[('NRG BindingSite','*.nrgbs')])
            
            if len(SaveFile) > 0:
                
                if SaveFile.find('.nrgbs') == -1:
                    SaveFile = SaveFile + '.nrgbs'

                try:
                    out = open(SaveFile, 'w')
                    pickle.dump(self.BindingSite, out)
                    out.close()

                    self.BindingSiteName.set(os.path.basename(os.path.splitext(SaveFile)[0]))

                    self.top.DisplayMessage("  Successfully saved '" + SaveFile + "'", 0)

                except:
                    self.top.DisplayMessage("  ERROR: Could not save binding-site configuration", 1)

        else:
            self.top.DisplayMessage("  No clefts or sphere to save as 'binding-site'", 2)

    ''' ==================================================================================
    FUNCTION Btn_AddResidu_Clicked: Add a residue name in the Flexible side chain ddl.
    ==================================================================================  '''           
    def Btn_AddResidu_Clicked(self):
        
        res = self.ResiduValue.get()
        resn = res[0:3]

        # Verify if the residue is in the list of residues and already in the ddl
        if self.listResidues.count(res) != 0:

            if resn != 'ALA' and resn != 'GLY' and resn != 'PRO':

                self.TargetFlex.Add_SideChain(res)
                self.Update_FlexSideChain_DDL()
                self.ResiduValue.set('')
                self.EntryResidu.config(bg=self.top.Color_White)

            else:
                self.top.DisplayMessage("Invalid residue entered (ALA/GLY/PRO do not have flexible bonds)", 2)
                self.EntryResidu.config(bg=self.top.Color_Red)                

        else:
            self.top.DisplayMessage("Invalid residue entered (you need a '-' chain identifier when no chain is provided)", 2)
            self.EntryResidu.config(bg=self.top.Color_Red)
        
    
    ''' ==================================================================================
    FUNCTION Btn_DelResidu_Clicked: Delete a residue name in the drop-down-list of flex. sc.
    ==================================================================================  '''        
    def Btn_DelResidu_Clicked(self):
        
        OptResidue = self.defOptResidue.get()

        if OptResidue != '':

            Index = self.optMenuWidgetRES["menu"].index(OptResidue)
            self.optMenuWidgetRES["menu"].delete(Index)

            self.TargetFlex.Remove_SideChain(OptResidue)
            self.Update_FlexSideChain_DDL()

    ''' ==================================================================================
    FUNCTION Btn_DelAllResidu_Clicked: Delete all residues in the DDL
    ==================================================================================  '''        
    def Btn_DelAllResidu_Clicked(self):
        
        self.TargetFlex.Clear_SideChain()
        self.Update_FlexSideChain_DDL()
        
    ''' ==================================================================================
    FUNCTION Highlight_RngOpt: Highlight with a grey bar the RngOpt selected
    ==================================================================================  '''       
    def Highlight_RngOpt(self):

        if self.RngOpt.get() == 'LOCCEN':
            self.fRangeOptRight.config(bd=0)
            self.fRangeOptLeft.config(bd=self.HIGHLIGHT_WIDTH, relief=self.HIGHLIGHT_RELIEF)

        elif self.RngOpt.get() == 'LOCCLF':
            self.fRangeOptLeft.config(bd=0)
            self.fRangeOptRight.config(bd=self.HIGHLIGHT_WIDTH, relief=self.HIGHLIGHT_RELIEF)
            
        else:
            self.fRangeOptRight.config(bd=0)
            self.fRangeOptLeft.config(bd=0)

    ''' ==================================================================================
    FUNCTION Btn_DeleteCleft_Clicked: Deletes the selected item in the DDL
    ==================================================================================  '''   
    def Btn_DeleteCleft_Clicked(self):

        if self.defOptCleft.get() != '':
            self.BindingSite.Remove_CleftName(self.defOptCleft.get())

            self.Display_BindingSite()
            self.Update_Clefts_DDL()

    ''' ==================================================================================
    FUNCTION Btn_ClearCleft_Clicked: Clears the DDL of the clefts
    ==================================================================================  '''   
    def Btn_ClearCleft_Clicked(self):

        self.BindingSite.Clear_Cleft()
        self.Display_BindingSite()
        self.Update_Clefts_DDL()

    ''' ==================================================================================
                                  Edit Sphere radius-center
    ================================================================================== '''          
    def Btn_EditSphere_Clicked(self):

        self.Sphere_Clicked()

    ''' ==================================================================================
                                  Sphere binding-site: Starts the wizard
    ================================================================================== '''          
    def Sphere_Clicked(self):

        if not self.PyMOL:
            return

        if self.top.ActiveWizard is None:

            self.SphereRunning(True)

            self.top.ActiveWizard = Sphere.Sphere(self, self.BindingSite.Sphere, self.SphereDisplay, self.SphereSize)
            cmd.set_wizard(self.top.ActiveWizard)
            self.top.ActiveWizard.Start()

        else:
            self.top.DisplayMessage("  ERROR: Could not open Wizard because one is already active", 1)

    # Deletes the binding-site object
    def Delete_BindingSite(self):
        try:
            cmd.delete(self.BindingSiteDisplay)
        except:
            pass

    # Disable/Enable widgets
    def SphereRunning(self, boolRun):

        if boolRun:
            self.RadioBtn_Sphere.config(state='disabled')
            self.RadioBtn_Cleft.config(state='disabled')

            self.sclResizeSphere.config(state='normal')
            self.OptMenuSphere.config(state='normal')
            self.Btn_OptSphRefresh.config(state='normal')

            self.Delete_BindingSite()

        else:
            
            self.RadioBtn_Sphere.config(state='normal')
            self.RadioBtn_Cleft.config(state='normal')

            self.sclResizeSphere.config(state='disabled')
            self.OptMenuSphere.config(state='disabled')
            self.Btn_OptSphRefresh.config(state='disabled')

            # Reset RngOpt to None if there was an error
            if self.top.WizardError:
                self.RngOpt.set('')

            self.SphereSize.set(self.BindingSite.Sphere.Radius)
            self.Display_BindingSite()
            
    
    # ResizeSphere = Get the scale value, then resize the sphere          
    def ResizeSphere(self, *args):

        if self.top.ActiveWizard is not None:
            self.top.ActiveWizard.ResizeSphere()

    # Center the sphere based on the selection
    def CenterSphere(self, sel):

        if not self.PyMOL:
            return

        if self.top.ActiveWizard is not None:
            Center = General_cmd.Get_CenterOfMass2(sel)
            
            if len(Center) > 0:
                self.top.ActiveWizard.SphereView.Set_Center(Center)
                self.top.ActiveWizard.DisplaySphere()
                self.defOptSphere.set(sel)
        else:
            self.top.DisplayMessage(  "ERROR: Could not open Wizard because one is already active", 1)
     
    # Listbox Menu Refresh values  
    def Btn_OptSphRefresh_Clicked(self):

        if not self.PyMOL:
            return

        exc = [ self.BindingSiteDisplay, self.SphereDisplay ]
        General_cmd.Refresh_DDL(self.OptMenuSphere,self.defOptSphere,exc,self.CenterSphere)

    ''' ==================================================================================
    FUNCTION Get_BindingSitePath: Retrieves the default path of the bindingsite
    ==================================================================================  '''        
    def Get_BindingSitePath(self):

        TARGETNAME = self.top.IOFile.ProtName.get().upper()
        BindingSitePath = os.path.join(self.top.BindingSiteProject_Dir,TARGETNAME)
        
        return BindingSitePath

    ''' ==================================================================================
    FUNCTION Get_BindingSitePath: Retrieves the default path of clefts
    ==================================================================================  '''        
    def Get_CleftPath(self):

        TARGETNAME = self.top.IOFile.ProtName.get().upper()
        CleftPath = os.path.join(self.top.GetCleftSaveProject_Dir,TARGETNAME)
        
        return CleftPath

    ''' ==================================================================================
    FUNCTION Btn_Import_Clefts: Asks for user to load clefts
    ==================================================================================  '''        
    def Btn_Import_Clefts(self):

        CleftPath = self.Get_CleftPath()
        
        if not os.path.isdir(CleftPath):
            self.DisplayMessage("  Could not find a Cleft folder for your target:", 2)
            self.DisplayMessage("  The default Cleft folder is used.", 2)
        
            CleftPath = self.top.GetCleftSaveProject_Dir

        LoadFiles = tkFileDialog.askopenfilename(filetypes=[('PDB Cleft file','*.pdb')],
                                                 initialdir=CleftPath, title='Select cleft file(s) to load',
                                                 multiple=1)
        
        if len(LoadFiles) > 0:
            
            for LoadFile in iter(LoadFiles):
                CleftName = os.path.splitext(os.path.basename(LoadFile))[0]

                Cleft = CleftObj.CleftObj()
                Cleft.CleftFile = LoadFile
                Cleft.CleftName = CleftName
                Cleft.Set_CleftMD5()

                self.BindingSite.Add_Cleft(Cleft)
                
            self.Display_BindingSite()
            self.Update_Clefts_DDL()

    ''' ==================================================================================
    FUNCTION Display_BindingSite: Displays the binding-site of the target
    ================================================================================== '''        
    def Display_BindingSite(self):

        if not self.PyMOL:
            return

        View = cmd.get_view()
        
        self.Delete_BindingSite()

        try:
            if self.BindingSite.Type == 1:

                cmd.pseudoatom(self.BindingSiteDisplay,
                               pos=self.BindingSite.Sphere.Center,
                               vdw=self.BindingSite.Sphere.Radius,
                               state=1)

                cmd.hide('everything', self.BindingSiteDisplay)
                cmd.show('spheres', self.BindingSiteDisplay)
                cmd.set('sphere_transparency', 0.7, self.BindingSiteDisplay)

            elif self.BindingSite.Type == 2:
                
                self.Generate_CleftBindingSite()

                cmd.load(self.CleftPath, self.BindingSiteDisplay, state=1)
                cmd.hide('everything', self.BindingSiteDisplay)
                cmd.show('surface', self.BindingSiteDisplay)
                cmd.set('transparency', 0.7, self.BindingSiteDisplay)

            cmd.color('purpleblue', self.BindingSiteDisplay)

            # reset view
            cmd.set_view(View)

        except:
            self.top.DisplayMessage("  ERROR: while displaying the binding-site", 2)


    ''' ==================================================================================
    FUNCTION Generate_CleftBindingSite: Generate a file combining all clefts together
    ================================================================================== '''        
    def Generate_CleftBindingSite(self):
        
        out = file(self.CleftPath, 'w')

        for Cleft in iter(self.BindingSite.listClefts):
            in_ = open(Cleft.CleftFile, 'r')
            lines = in_.readlines()
            in_.close()

            for line in lines:
                out.write(line[0:22])
                out.write('%4d' % Cleft.Index)
                out.write(line[26:])
            
        out.close()

    ''' ==================================================================================
    FUNCTION MenuLoadMessage: Display the message based on the menu selected
    ================================================================================== '''        
    def LoadMessage(self):
        
        self.top.DisplayMessage('', 0)
        self.top.DisplayMessage('  FlexAID < Target Cfg > Menu.', 2)
        self.top.DisplayMessage('  INFO: Configure the target molecule', 2)
        self.top.DisplayMessage('          1) Define the binding-site using a sphere or one or more cleft(s)', 2)
        self.top.DisplayMessage('          2) Include flexibility in the target, if necessary', 2)
