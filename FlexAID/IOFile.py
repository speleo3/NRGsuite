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

import functools
import math
import os
import tkFileDialog
import General
import Constants
import ProcessLigand

if __debug__:
    from pymol import cmd
    import General_cmd


'''
@title: FlexAID - IOFile tab - Interface

@summary: This is the IOFile tab interface of FlexAID application

@organization: Najmanovich Research Group
@creation date:  Nov. 24 2011
'''

class IOFile:

    def __init__(self, top, PyMOL):

        #print "New instance of IOFile"

        self.PyMOL = PyMOL

        self.top = top
        self.Tab = self.top.Btn_IOFiles
        self.FrameName = 'IOFile'

        self.font_Text = self.top.font_Text
        self.font_Title = self.top.font_Title

        self.Color_Black = self.top.Color_Black
        self.Color_White = self.top.Color_White

        self.DisplayMessage = self.top.DisplayMessage

        self.Def_Vars()
        self.Init_Vars()

        self.Frame()
        self.Trace()

    def Def_Vars(self):

        self.listConn = list()
        self.StateList = list()

        self.defaultOption = StringVar()
        self.FetchPDB = StringVar()
        self.ProtName = StringVar()
        self.LigandName = StringVar()
        self.AtomTypes = StringVar()
        self.TargetRNA = IntVar()

        self.Validator = list()

    def Init_Vars(self):

        #print("Init Vars for IOFile")
        self.ProtPath = ''
        self.LigandPath = ''
        self.ReferencePath = ''

        self.NbListAtom = 0
        self.ResSeq = 0

        self.listConn = []

        self.defaultOption.set('')
        self.FetchPDB.set('')
        self.ProtName.set('')
        self.LigandName.set('')
        self.AtomTypes.set('Sybyl')
        self.TargetRNA.set(0)

        self.fProcessLigand = False
        self.ProcessError = False

        self.fStoreInfo = False
        self.fLoadProcessed = False

        self.LIGAND = 'NRG_LIGAND__'
        self.PROTEIN = 'NRG_TARGET__'
        
    ''' ==================================================================================
    FUNCTION Kill_Frame: Kills the main frame window
    =================================================================================  '''    
    def Kill_Frame(self):
        
        self.ProcessError = False
        
        # Process ligand
        if not self.fProcessLigand:

            AtomIndex = General.store_Residues(self.top.Config1.listResidues, self.top.IOFile.ProtPath, 0)
            if AtomIndex == -1:
                return False

            self.ProcessLigand(True, AtomIndex + 1)

            if self.ProcessError:
                return False

        # Store content of ligand input files
        if not self.fStoreInfo:
            if self.store_InpFile():
                return False

        # Loads the PDB of the processed ligand
        if not self.fLoadProcessed:
            if self.Load_ProcessedLigand():
                return False

        self.fIOFile.pack_forget()
        #self.fIOFile.destroy()

        return True

    ''' ==================================================================================
    FUNCTION Validator_Fail: Triggers visual events upon validation failure
    =================================================================================  '''    
    def Validator_Fail(self):

        return

    ''' ==================================================================================
    FUNCTION ProcessLigand: Processes ligand PDB file using lig_extractor
    ================================================================================== '''    
    def ProcessLigand(self, boolRun, StartAtomIndex):

        if boolRun:

            self.StateList = []

            General.saveState(self.fIOFile, self.StateList)
            General.setState(self.fIOFile)

            self.top.ProcessRunning = True
            p = ProcessLigand.ProcLig(self, StartAtomIndex, self.AtomTypes.get())

        else:

            General.backState(self.fIOFile, self.StateList)


    ''' ==================================================================================
                         ENABLE / DISABLE - Buttons
    ================================================================================== '''             
    def ValidateLigProt(self,*args):

        if len(self.ProtName.get()) > 0 and len(self.LigandName.get()) > 0:
            self.top.Go_Step2()
        else:
            self.top.Go_Step1()

        self.fProcessLigand = False
        self.top.Reset_Step2()


    ''' ==================================================================================
    FUNCTION Show: Displays the frame onto the middle main frame
    ==================================================================================  '''  
    def Show(self):
        
        self.LoadMessage()
        
        #Show the list of selection/objects in case the user already worked in PyMOL
        self.Btn_RefreshOptMenu_Clicked()

        self.fIOFile.pack(fill=BOTH, expand=True)
        
    ''' ==================================================================================
    FUNCTION Trace: Adds a callback function to StringVars
    ==================================================================================  '''  
    def Trace(self):

        self.ProtNameTrace = self.ProtName.trace('w',self.ValidateLigProt)
        self.LigandNameTrace = self.LigandName.trace('w',self.ValidateLigProt)

    ''' ==================================================================================
    FUNCTION Del_Trace: Deletes observer callbacks
    ==================================================================================  '''  
    def Del_Trace(self):

        self.ProtName.trace_vdelete('w',self.ProtNameTrace)
        self.LigandName.trace_vdelete('w',self.LigandNameTrace)

    ''' ==================================================================================
    FUNCTION Frame: Generate the Input / Output Files frame in the the middle 
                    frame section    
    ==================================================================================  '''  
    def Frame(self):
        
        self.fIOFile = Frame(self.top.fMiddle)

        #==================================================================================
        #                              PDB Options
        #==================================================================================
        fPDB_options = Frame(self.fIOFile)#, border=1, relief=SUNKEN)
        fPDB_options.pack(fill=X, side=TOP, padx=5, pady=5)

        fPDB_optionsLine1 = Frame(fPDB_options)#, border=1, relief=SUNKEN)
        fPDB_optionsLine1.pack(side=TOP, fill=X)
        fPDB_optionsLine2 = Frame(fPDB_options)#, border=1, relief=SUNKEN)
        fPDB_optionsLine2.pack(side=TOP, fill=X)

        # Header Get PDB
        Label(fPDB_optionsLine1, text='Selection of the target', font=self.font_Title).pack(side=LEFT)
        
        # Get a PDB File from a file on your harddrive
        Button(fPDB_optionsLine2, text='Open file', command=self.Btn_OpenPDB_Clicked, font=self.font_Text).pack(side=LEFT, padx=20)
        
        # Download a PDB File from the internet
        Label(fPDB_optionsLine2, text='Enter the PDB code:', font=self.font_Text, justify=CENTER).pack(side=LEFT, padx=5)
        Entry(fPDB_optionsLine2, textvariable=self.FetchPDB, width=10, background='white', font=self.font_Text, justify=CENTER).pack(side=LEFT)
        Button(fPDB_optionsLine2, text='Download', command=self.Btn_DownloadPDB_Clicked, font=self.font_Text).pack(side=LEFT, padx=5)
        
        
        #==================================================================================
        #                                 Object/selections
        #==================================================================================
        fPDBsel = Frame(self.fIOFile)#, border=1, relief=SUNKEN)
        fPDBsel.pack(fill=X, expand=True, side=TOP, padx=5, pady=5)

        fPDBselLine1 = Frame(fPDBsel)#, border=1, relief=SUNKEN)
        fPDBselLine1.pack(side=TOP, fill=X)
        fPDBselLine2 = Frame(fPDBsel)#, border=1, relief=SUNKEN)
        fPDBselLine2.pack(side=TOP, fill=X)

        # List of selections
        Label(fPDBselLine2, text='PyMOL objects/selections:', width=25, justify=RIGHT, font=self.font_Text).pack(side=LEFT, anchor=E)

        optionTuple = ('',)
        self.optionMenuWidget = apply(OptionMenu, (fPDBselLine2, self.defaultOption) + optionTuple)
        self.optionMenuWidget.config(bg=self.Color_White, width=15, font=self.font_Text)
        self.optionMenuWidget.pack(side=LEFT)
        
        # Refresh the list with the selections in Pymol
        Button(fPDBselLine2, text='Refresh', command=self.Btn_RefreshOptMenu_Clicked, font=self.font_Text).pack(side=LEFT)
        Button(fPDBselLine2, text='Save as target', command=self.Btn_SaveProt_Clicked, font=self.font_Text).pack(side=LEFT)
        Button(fPDBselLine2, text='Save as ligand', command=self.Btn_SaveLigand_Clicked, font=self.font_Text).pack(side=LEFT)
 

        #==================================================================================
        #                                 Processing of molecules
        #==================================================================================

        fProcessing = Frame(self.fIOFile)
        fProcessing.pack(side=TOP, fill=X, pady=5, padx=5)

        fProcessingLine1 = Frame(fProcessing)#, border=1, relief=SUNKEN)
        fProcessingLine1.pack(side=TOP, fill=X)
        fProcessingLine2 = Frame(fProcessing)#, border=1, relief=SUNKEN)
        fProcessingLine2.pack(side=TOP, fill=X)
        
        Label(fProcessingLine1, text='Processing of molecules', font=self.font_Title).pack(side=LEFT)

        Label(fProcessingLine2, text='Atom typing:', width=30, justify=RIGHT, font=self.font_Text).pack(side=LEFT, anchor=E)

        Radiobutton(fProcessingLine2, text='Sobolev', variable=self.AtomTypes, value="Sobolev", font=self.font_Text).pack(side=LEFT)
        Radiobutton(fProcessingLine2, text='Gaudreault', variable=self.AtomTypes, value="Gaudreault", font=self.font_Text).pack(side=LEFT, padx=10)
        Radiobutton(fProcessingLine2, text='Sybyl', variable=self.AtomTypes, value="Sybyl", font=self.font_Text).pack(side=LEFT)
               
        #==================================================================================
        #                                SET TARGET
        #==================================================================================                
        fPDBprotein = Frame(self.fIOFile, border=1, relief=RAISED)
        fPDBprotein.pack(side=TOP, pady=5)

        fPDBproteinLine1 = Frame(fPDBprotein)
        fPDBproteinLine1.pack(side=TOP, fill=X, padx=3, pady=3)

        fPDBproteinLine2 = Frame(fPDBprotein)
        fPDBproteinLine2.pack(side=TOP, fill=X, padx=3, pady=3)

        # First line
        Label(fPDBproteinLine1, width=30, text='SET TARGET', font=self.font_Title).pack(side=LEFT)
        Button(fPDBproteinLine1, text='Load', command=self.Btn_LoadProt_Clicked, font=self.font_Text).pack(side=LEFT)
        Button(fPDBproteinLine1, text='Display', command=self.Btn_DisplayProtein_Clicked, font=self.font_Text).pack(side=LEFT)
        Button(fPDBproteinLine1, text='Reset', command=self.Btn_ResetProt_Clicked, font=self.font_Text).pack(side=LEFT)

        # Second line
        Label(fPDBproteinLine2, width=30, text='', font=self.font_Title).pack(side=LEFT)
        EntProtein = Entry(fPDBproteinLine2, textvariable=self.ProtName, disabledbackground=self.Color_White, disabledforeground=self.Color_Black, font=self.font_Text)
        EntProtein.pack(side=LEFT, fill=X)
        EntProtein.config(state='disabled')
        Checkbutton(fPDBproteinLine2, variable=self.TargetRNA, width=10, text='RNA', font=self.font_Text, justify=LEFT).pack(side=LEFT)
        
        #==================================================================================
        #                               SET LIGAND
        #==================================================================================   

        fPDBligand = Frame(self.fIOFile, border=1, relief=RAISED)
        fPDBligand.pack(side=TOP, pady=5)

        fPDBligandLine1 = Frame(fPDBligand)
        fPDBligandLine1.pack(side=TOP, fill=X, padx=3, pady=3)

        fPDBligandLine2 = Frame(fPDBligand)
        fPDBligandLine2.pack(side=TOP, fill=X, padx=3, pady=3)

        # First line
        Label(fPDBligandLine1, width=30, text='SET LIGAND', font=self.font_Title).pack(side=LEFT)
        Button(fPDBligandLine1, text='Load', command=self.Btn_LoadLigand_Clicked, font=self.font_Text).pack(side=LEFT)
        Button(fPDBligandLine1, text='Display', command=self.Btn_DisplayLigand_Clicked,font=self.font_Text).pack(side=LEFT)
        Button(fPDBligandLine1, text='Reset', command=self.Btn_ResetLigand_Clicked, font=self.font_Text).pack(side=LEFT)
        
        # Second line
        Label(fPDBligandLine2, width=30, text='', font=self.font_Title).pack(side=LEFT)
        EntLigand = Entry(fPDBligandLine2, disabledbackground=self.Color_White, disabledforeground=self.Color_Black, textvariable=self.LigandName, font=self.font_Text)
        EntLigand.pack(side=LEFT, fill=X)
        EntLigand.config(state='disabled')      
        Label(fPDBligandLine2, width=10, text='', font=self.font_Text).pack(side=LEFT)

    ''' ==================================================================================
    FUNCTIONS Reset Ligand and Protein textbox fields
    ================================================================================== '''
    def Btn_ResetProt_Clicked(self):     
        self.ProtPath = ''
        self.ProtName.set('')

    def Btn_ResetLigand_Clicked(self):
        self.LigandPath = ''
        self.LigandName.set('')

    ''' ==================================================================================
    FUNCTION Btn_Save : Ligand and Protein
    ==================================================================================  '''    
    def Btn_SaveLigand_Clicked(self):
        
        if not self.PyMOL:
            return

        # Get the Drop Down List Selection Name
        ddlSelection = self.defaultOption.get()

        if ddlSelection == '':
            return

        try:
            state = cmd.get_state()
            n = cmd.count_atoms(ddlSelection, state=state)

            if n < 2:
                self.DisplayMessage("  ERROR for object/selection '" + ddlSelection + "': The ligand must have at least (3) atoms)", 1)
                return

            elif n > Constants.MAX_LIGAND_ATOMS:
                self.DisplayMessage("  ERROR for object/selection '" + ddlSelection + "': The ligand must have a maximum of (" + 
                                    Constants.MAX_LIGAND_ATOMS + ') atoms', 1)
                return

        except:
            self.DisplayMessage("  ERROR: object/selection '" + ddlSelection + "' does not exist on current state", 1)
            return

        self.LigandPath = tkFileDialog.asksaveasfilename(initialdir=self.top.FlexAIDLigandProject_Dir, title='Save the PDB File', initialfile=ddlSelection, filetypes=[('PDB File','*.pdb')])

        if len(self.LigandPath) > 0:
            
            if self.LigandPath.find('.pdb') == -1:
                self.LigandPath = self.LigandPath + '.pdb'

            cmd.save(self.LigandPath, ddlSelection, state, 'pdb') # Save the Selection

            self.LigandName.set(os.path.basename(os.path.splitext(self.LigandPath)[0]))
            self.DisplayMessage('  Successfully saved and loaded the ligand:  ' + self.LigandName.get() + "'", 0)                            
    

    def Btn_SaveProt_Clicked(self):
        
        if not self.PyMOL:
            return

        # Get the Drop Down List Selection Name
        ddlSelection = self.defaultOption.get()

        if ddlSelection == '':
            return

        try:
            state = cmd.get_state()
            n = cmd.count_atoms(ddlSelection, state=state)

            if n < 2:
                self.DisplayMessage("  ERROR for object/selection '" + ddlSelection + "': The protein must have at least (3) atoms)", 1)
                return
        except:
            self.DisplayMessage(  "The object/selection '" + ddlSelection + "' does not exist on current state", 1)
            return
                    
        self.ProtPath = tkFileDialog.asksaveasfilename(initialdir=self.top.ProteinProject_Dir, title='Save the PDB File', initialfile=ddlSelection, filetypes=[('PDB File','*.pdb')])

        if len(self.ProtPath) > 0:

            if self.ProtPath.find('.pdb') == -1:
                self.ProtPath = self.ProtPath + '.pdb'

            cmd.save(self.ProtPath, ddlSelection, state, 'pdb') # Save the Selection
            self.ProtName.set(os.path.basename(os.path.splitext(self.ProtPath)[0]))
            self.DisplayMessage('  Successfully saved and loaded the target: ' + self.ProtName.get(), 0)                                    
                

    ''' ==================================================================================
    FUNCTIONS Load Ligand and Protein and display the filename in the textbox
    ================================================================================== '''        
    def Btn_LoadLigand_Clicked(self):        
        
        LigandPath = tkFileDialog.askopenfilename(filetypes=[('PDB File','*.pdb')], initialdir=self.top.FlexAIDLigandProject_Dir, title='Select a Ligand File to Load')
        
        if len(LigandPath) > 0 and LigandPath != self.LigandPath:
            
            self.LigandPath = LigandPath

            try:

                Name = os.path.basename(os.path.splitext(self.LigandPath)[0])

                if self.PyMOL:
                    cmd.load(self.LigandPath, Name, state=1)
                    n = cmd.count_atoms(Name, state=1)
                else:
                    # For testing purposes only
                    n = 50

                if n < 2:
                    self.DisplayMessage("  ERROR for object '" + Name + "': The ligand must have at least (3) atoms)", 1)
                    return

                elif n > Constants.MAX_LIGAND_ATOMS:
                    self.DisplayMessage("  ERROR for object '" + Name + "': The ligand must have a maximum of (" + 
                                        Constants.MAX_LIGAND_ATOMS + ') atoms', 1)
                    return

            except:
                self.DisplayMessage("  ERROR for file '" + LigandPath + "': Could not load the ligand file", 1)
                return
                
            self.LigandName.set(Name)
            self.DisplayMessage("  Successfully loaded the ligand: '" + self.LigandName.get() + "'", 0)


    def Load_ProcessedLigand(self):
        
        try:
            if self.PyMOL:
                cmd.load(self.ReferencePath, self.LigandName.get(), state=1)
        except:
            self.DisplayMessage('  ERROR: Could not load the PDB of the processed ligand', 1)
            return 1
        
        self.fLoadProcessed = True

        return 0

           
    def Btn_LoadProt_Clicked(self):
        
        ProtPath = tkFileDialog.askopenfilename(filetypes=[('PDB File','*.pdb')], initialdir=self.top.ProteinProject_Dir, title='Select a Target File to Load')
        
        if len(ProtPath) > 0 and ProtPath != self.ProtPath:
            self.ProtPath = ProtPath            
            
            try:
                Name = os.path.basename(os.path.splitext(self.ProtPath)[0])
                if self.PyMOL:
                    cmd.load(self.ProtPath, Name, state=1)

            except:
                self.top.DisplayMessage("  ERROR for object '" + ProtPath + "': Could not load the target file", 1)
                return

            self.ProtName.set(Name)
            self.DisplayMessage("  Successfully loaded the target: '" + self.ProtName.get() + "'", 0)

    ''' ==================================================================================
    FUNCTION openPDB: Import PDB file
    ================================================================================== '''
    def Btn_OpenPDB_Clicked(self):
        
        FilePath = tkFileDialog.askopenfilename(filetypes=[('PDB File','*.pdb')], initialdir=self.top.Project_Dir, title='Select a PDB File to Import')
        
        if len(FilePath) > 0:
            if self.PyMOL:
                cmd.load(FilePath, state=1)

                
    ''' ==================================================================================
    FUNCTION Btn_DownloadPDB_Clicked: Download a PDB from the internet and display the
                                      result in Pymol 
    ==================================================================================  '''    
    def Btn_DownloadPDB_Clicked(self):       

        PdbCode = self.FetchPDB.get()
        
        try:            
            if self.PyMOL:
                cmd.fetch(PdbCode, async=0)

        except:
            self.DisplayMessage('You entered an invalid pdb code.', 1)
            
        self.FetchPDB.set('')        

    ''' ==================================================================================
    FUNCTION Btn_RefreshOptMenu_Clicked: Refresh the selections list in the application
                                         with the selections in Pymol 
    ==================================================================================  '''                
    def Btn_RefreshOptMenu_Clicked(self): 
        
        if self.PyMOL:
            exc = []
            General_cmd.Refresh_DDL(self.optionMenuWidget, self.defaultOption, exc, None)
   
    ''' ==================================================================================
    FUNCTIONS Display Ligand and Protein in pymol
    ================================================================================== '''        
    def Btn_DisplayLigand_Clicked(self):
        
        if not self.PyMOL:
            return

        if self.LigandName.get() != '':

            if not General_cmd.object_Exists(self.LigandName.get()):
                cmd.load(self.LigandPath, state=1)                      # Load the pdb file in Pymol                     
            else:
                cmd.center(self.LigandName.get())
                cmd.zoom(self.LigandName.get())    
    
        
    def Btn_DisplayProtein_Clicked(self):
        
        if not self.PyMOL:
            return

        if self.ProtName.get() != '':

            if not General_cmd.object_Exists(self.ProtName.get()):
                cmd.load(self.ProtPath, state=1)                        # Load the pdb file in Pymol                     
            else:
                cmd.center(self.ProtName.get())
                cmd.zoom(self.ProtName.get())        
            

    # Welcome menu message
    def LoadMessage(self):

	self.DisplayMessage('' ,0)
        self.DisplayMessage('  FlexAID < Input Files > Menu', 2)
        self.DisplayMessage('  INFO:   Select a < TARGET > and a < LIGAND > by:', 2)
        self.DisplayMessage('          1) Saving a PyMOL object/selection to your project directory', 2)
        self.DisplayMessage('          2) Loading an existing object file from your project directory', 2)

    #=======================================================================
    ''' Store inp file information (flexible bonds, atom types)  '''
    #=======================================================================   
    def store_InpFile(self):
                
        inpFilePath = os.path.join(self.top.FlexAIDSimulationProject_Dir,'LIG.inp')

        inpInfo = dict()
        flexInfo = dict()

        #Read the inp file and get the flexible bonds
        try:
            file = open(inpFilePath)
            inpFile = file.readlines()
            file.close()

            nbLines = len(inpFile)      
            for line in range(0, nbLines):

                #HETTYP  902 1  N1  m   909  910  903    0
                if inpFile[line].startswith('HETTYP'):
                    
                    ATOM = inpFile[line][7:11].strip()

                    list = []
                    list.append(inpFile[line][11:13].strip()) # Type
                    list.append(inpFile[line][22:26].strip()) # Neighbour 1
                    list.append(inpFile[line][27:31].strip()) #           2
                    list.append(inpFile[line][32:36].strip()) #           3
                    inpInfo[ATOM] = list

                #FLEDIH  4   916  917   
                elif inpFile[line].startswith('FLEDIH'):

                    INDEX = inpFile[line][7:9].strip()

                    list = []
                    for i in range(0,len(inpFile[line][10:])/5):
                        list.append(inpFile[line][(10+i*5):(10+5+i*5)].strip())
                    flexInfo[INDEX] = list
                    
        except:
            self.top.DisplayMessage('  ERROR: Could not retrieve ligand input file', 1)
            return 1

        self.store_Neighbours(inpInfo)
        self.store_AtomTypes(inpInfo)
        self.store_FlexBonds(flexInfo)

        self.fStoreInfo = True

        return 0

    #=======================================================================
    ''' Store Neighbours Dictionary'''
    #=======================================================================   
    def store_Neighbours(self, inpInfo):
        
        self.top.Config2.dictNeighbours.clear()

        for atom in iter(inpInfo):

            self.top.Config2.dictNeighbours[atom] = inpInfo[atom][1:]

    #=======================================================================
    ''' Store Flexible Bonds Dictionary'''
    #=======================================================================   
    def store_FlexBonds(self, flexInfo):
        
        self.top.Config2.dictFlexBonds.clear()

        for index in iter(flexInfo):
            
            ''' [ Selected as flexible,
                  Forced as flexible,
                  Number of atoms defining the bond,
                  Atom list defining bond ] '''

            dictList = [ 0, 0, len(flexInfo[index]) ]
            for i in range(0, len(flexInfo[index])):
                dictList.append(flexInfo[index][i])
                
            self.top.Config2.dictFlexBonds[index] = dictList

    #=======================================================================
    ''' Store Atom Types Dictionary'''
    #=======================================================================   
    def store_AtomTypes(self, inpInfo):
        
        self.top.Config2.dictAtomTypes.clear()

        for atom in iter(inpInfo):

            self.top.Config2.dictAtomTypes[atom] = [inpInfo[atom][0], inpInfo[atom][0]]
