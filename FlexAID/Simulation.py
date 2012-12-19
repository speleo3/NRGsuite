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
@title: FlexAID - Simulation.py

@summary: Class that handle the flexAID simulation.

@contain: dictAdjAtom, dictDisAngDih, CreateTempPDB, progressBarHandler
          getVarAtoms, buildcc

@organization: Najmanovich Research Group
@creation date:  Sept. 24, 2010
'''

from collections import defaultdict
from pymol import cmd
from subprocess import Popen, PIPE, STDOUT

import math, os, time, re
import threading
import Color
import Geometry
import UpdateScreen

# Start the simulation with FlexAID      
class Start(threading.Thread):

    def __init__(self, top,commandline):

        #print "New instance of Start Class"

        threading.Thread.__init__(self)

        self.commandline = commandline
        #self.commandline += ' > /Users/francisgaudreault/test.log'

        self.top = top
        self.FlexAID = self.top.top

        self.top.ProcessError = False
        self.start()

    # Start FlexAID on a side thread
    def run(self):        
        
        try:

            self.FlexAID.ProcessRunning = True
            if self.FlexAID.OSid == 'WIN':
                self.FlexAID.Run = Popen(self.commandline, shell=False, bufsize=1, stdout=PIPE, stderr=STDOUT)
            else:
                self.FlexAID.Run = Popen(self.commandline, shell=True,  bufsize=1, stdout=PIPE, stderr=STDOUT)
                
            self.FlexAID.Run.wait()

        except:

            self.FlexAID.DisplayMessage('   Fatal error: Could not execute FlexAID', 1)
            self.FlexAID.DisplayMessage('   Make sure you downloaded NRGsuite for the right platform', 1)

            self.FlexAID.ProcessRunning = False
            self.top.ProcessError = True

        self.FlexAID.Run = None
        


class Parse(threading.Thread):
#class Parse():

    def __init__(self, top):
        threading.Thread.__init__(self)
        
        #print "New instance of Parse Class"

        self.top = top
        self.FlexAID = self.top.top

        self.FlexStatus = self.FlexAID.Config2.FlexStatus.get()
        self.OSid = self.FlexAID.OSid

        self.LOGFILE = self.top.Manage.LOGFILE
                
        self.NbTopChrom = int(self.FlexAID.GAParam.NbTopChrom.get())
        
        self.dictFlexBonds = self.FlexAID.Config2.dictFlexBonds

        self.RngOpt = self.FlexAID.Config1.RngOpt.get()  # Possibility: GLOBAL, LOCCEN, LOCCLF
        
        self.NbTotalGen = int(self.FlexAID.GAParam.NbGen.get())
        self.DefaultDisplay = self.top.SimDefDisplay.get()
        
        self.LOGFILE = self.top.Manage.LOGFILE     
        self.LOGFILETMP = self.top.Manage.LOGFILE + '.tmp'

        self.Generation = -1
        self.Best = ''
        self.TOP = -1

        #self.Updating = 0

        self.State = 0
        self.CurrentState = 0

        self.PrevTextValue = 0
        self.StrCount = '   0'
        self.NbGen = ' / ' + str(self.FlexAID.GAParam.NbGen.get())
        self.FloatNbGen = float(self.FlexAID.GAParam.NbGen.get())
        self.ParseGA = False
        self.FixedAngle = {}

        # Rotamers data
        self.dictRotamers = defaultdict(list)         # Contains the list of all dihedral for a residue
                                                      # dictRotamers['ALA'] = [1.000, 2.000, 3.100, 2.900, ...]
        self.dictRotamersIndex = defaultdict(list)    # Contains the list of indexes to map in Rotamers dict
                                                      # dictRotamersIndex['ALA36A'] = [0, 5, 18, 56, ...]
        self.dictNumberRotamers = {}                  # Corresponds to the number of Rotamers for a residue
                                                      # dictNumberRotamers['ALA'] = Xn

        self.ReferencePath = self.FlexAID.IOFile.ReferencePath

        self.listFlexSideChainNRot = list()
        self.listFlexSideChain = self.FlexAID.Config1.TargetFlex.listSideChain

        self.dictSimData = self.top.dictSimData

        self.ModuloGEN = int(self.FlexAID.GAParam.NbGenFreq.get())     # Draw every XX generation        
        self.NBLineGEN = int(self.FlexAID.GAParam.NbTopChrom.get())    # Number of Lines READ per Generation        

        self.listTmpPDB = list()
        self.dictCoordRef = dict()

        self.CreateTempPDB(self.FlexAID.FlexAIDSimulationProject_Dir)

        # Set the Colors
        self.NBCOLOR = Color.NBCOLOR
        self.PymolColorList = Color.GetHeatColorList(self.NBLineGEN, False)

        #Creation of the dictionaries
        self.RecAtom = self.dictRecAtom(self.top.Manage.INPFlexAIDRunSimulationProject_Dir)        # 3 Neighbors that lead to the middle atoms
        self.DisAngDih = self.dictDisAngDih(self.top.Manage.ICFlexAIDRunSimulationProject_Dir)     # Distance, Angle, Dihedral angle

        self.Ori = [0.0, 0.0, 0.0]    # Origin coordinate
        self.OriX = [0.0, 0.0, 0.0]   # Origin coordinate with X+1
        self.OriY = [0.0, 0.0, 0.0]   # Origin coordinate with Y+1
        
        self.ListAtom = []           # List of the atoms of the ligand

        # In order, atoms that need their values to be modified
        self.VarAtoms = self.getVarAtoms(self.top.Manage.INPFlexAIDRunSimulationProject_Dir)    # 1st = 3 positions, 2nd = 2 positions, 3rd = 1 position
         
        print('STEP 5: Start the thread...')
        self.start()
        
    '''
    @summary: SUBROUTINE run: Start the simulation
    '''    
    def run(self):
    #def start(self):
        
        # 20 msec
        INTERVAL = 0.05


        # Number of ligand atoms
        nbAtoms = len(self.DisAngDih)

        # Always print docking results in frame range (1...Xn)
        self.State = 1

        try:
            file = open(self.ReferencePath,'r')
            self.ReferenceFile = file.readlines()
            file.close()

            if self.FlexAID.Config2.UseReference.get():
                self.dictCoordRef = self.Get_CoordRef()

        except:
            print "Could not read ligand PDB File"
            return

    
        print "Waiting for the simulation to start..."

        # Wait for the simulation to start...
        while (1):
            if not self.FlexAID.Run is None:
                print "FlexAID is running..."
                break
            elif self.top.ProcessError:
                print "An error occured while trying to run FlexAID"
                return

            time.sleep(INTERVAL)

        
        self.top.progressBarHandler(0,self.NbTotalGen)
        self.top.Init_Table()
        
        # Set the auto_zoom to off
        cmd.set("auto_zoom", 0)
        cmd.delete("TOP_*__")
        cmd.frame(1)
        
        while self.FlexAID.Run is not None: # and self.FlexAID.Run.poll() is None:

            while (1):
                # Parsing output
                try:
                    Line = self.FlexAID.Run.stdout.readline()
                except:
                    break

                # stop reading from stdout buffer
                if Line == '':
                    break
                
                if self.ParseGA:
                             
                    '''
                    Generation:   0
                    best by energy
                     0 (   16.819   128.976    15.591   154.488   171.496  -137.480 )  value= -406.907 fitnes=  100.000
                     1 (   17.286   -58.110   -43.937  -148.819   -26.929   -83.622 )  value= -494.421 fitnes=   99.000
                     2 (   19.386    -1.417    63.780   120.472   -15.591    29.764 )  value= -498.632 fitnes=   98.000
                     3 (   22.186   -38.268    72.283  -106.299   157.323    52.441 )  value= -515.372 fitnes=   97.000
                     4 (   22.653    -1.417    38.268  -109.134    89.291  -126.142 )  value= -533.335 fitnes=   96.000
                    best by fitnes
                     0 (   16.819   128.976    15.591   154.488   171.496  -137.480 )  value= -406.907 fitnes=  100.000
                     1 (   17.286   -58.110   -43.937  -148.819   -26.929   -83.622 )  value= -494.421 fitnes=   99.000
                     2 (   19.386    -1.417    63.780   120.472   -15.591    29.764 )  value= -498.632 fitnes=   98.000
                     3 (   22.186   -38.268    72.283  -106.299   157.323    52.441 )  value= -515.372 fitnes=   97.000
                     4 (   22.653    -1.417    38.268  -109.134    89.291  -126.142 )  value= -533.335 fitnes=   96.000
                    '''

                    m = re.match("(\s*(\d+) \()", Line)
                    if m:
                        self.TOP = int(m.group(2))

                        # Find starting index where to parse column values
                        colNo = len(m.group(1))

                        if self.Best == 'energy' and self.Generation != -1 and self.TOP != -1:

                            # Reading the values calculated for the generation
                            if (self.Generation % self.ModuloGEN) == 0 or self.Generation == self.NbTotalGen:

                                #self.Updating += 1

                                ID = str(self.Generation) + '.' + str(self.TOP)
                                #print("updating " + ID)

                                #print Line
                                Update = UpdateScreen.UpdateScreen(self, ID, colNo, Line, self.CurrentState, self.TOP)

                                    
                                #Update.join()

                                #while(self.Updating):
                                    #print "is already updating..."
                                #    time.sleep(INTERVAL)
                                
                                    
                                #    while(self.Updating):
                                #        time.sleep(INTERVAL)

                                if (self.TOP+1) == self.NBLineGEN:
                                    self.State = self.CurrentState

                                    # Range of optimization
                                    RngOpt = self.FlexAID.Config1.RngOpt.get()

                                    try:
                                        # append range object to next state
                                        if RngOpt == 'LOCCEN':
                                            cmd.create(self.FlexAID.Config1.SphereDisplay, self.FlexAID.Config1.SphereDisplay, 
                                                       1, self.CurrentState)
                                        elif RngOpt == 'LOCCLF':
                                            cmd.create(self.FlexAID.Config1.GridDisplay, self.FlexAID.Config1.GridDisplay,
                                                       1, self.CurrentState)

                                    except:
                                        self.FlexAID.DisplayMessage("Could not display range of optimization: Object no longer exists", 1)

                                    # Update energy/fitness table
                                    self.top.update_DataList()

                        continue


                    m = re.match("best by (\w+)\s+", Line)
                    if m:
                        self.Best = m.group(1)
                        #print "Best by " + self.Best
                        continue

                    m = re.match("Generation:\s*(\d+)\s+", Line)
                    if m:

                        self.Generation = int(m.group(1))
                        #print("Generation " + str(self.Generation))
                        self.CurrentState = self.State + 1

                        #print "will update progressbar"
                        # ProgressionBar Handler
                        try:
                            self.top.progressBarHandler(self.Generation, self.NbTotalGen)
                        except:
                            pass

                        continue
                    

                else:
    
                    # track errors
                    if Line.startswith('ERROR'):
                        self.FlexAID.DisplayMessage(str("A critical error occured\nFlexAID :: " + Line), 1)
                        self.FlexAID.Run.terminate()
                        self.FlexAID.Run = None
                        break
                    
                    # parse output
                    m = re.match("\d+ possible rotamer", Line)
                    if m:

                        words = Line.split()
                        residue = words[5] + words[6] + words[7]
                        
                        # If the residue is found in the list
                        if self.listFlexSideChain.count(residue) > 0: # and residue not in self.dictRotamersIndex:

                            for i in range(0,int(words[0])):
                                self.dictRotamersIndex[residue].append(int(words[9+i]))
                            
                            #print str(self.dictRotamersIndex[residue])

                            if int(words[0]) > 0 and words[5] not in self.dictRotamers:
                                if self.AddToRotamers(words[5]) == 0:
                                    print "No rotamers found for residue " + words[5]
                            
                            self.listFlexSideChainNRot.append(int(words[0]))
                            
                            #print str(self.listFlexSideChain)
                            #print str(self.listFlexSideChainNRot)
                            
                            
                            if len(self.listFlexSideChain) == len(self.listFlexSideChainNRot):
                                break

                        else:
                            print "Residue " + residue + " was not found in Flexible Side-Chains list."

                        continue



                    m = re.match("shiftval=", Line)
                    if m and self.FlexStatus != '':

                        # Shift values for fixed dihedrals between pair-triplets of atoms
                        fields = Line.split()

                        MergeAtomsAB = fields[1] + fields[2]
                        
                        self.FixedAngle[MergeAtomsAB] = fields[5]                   
                                                    
                        continue

                    m = re.match("lout\[\d+\]=\s*(\d+)\s+", Line)
                    if m:

                        self.ListAtom.append(int(m.group(1)))

                        if len(self.ListAtom) == nbAtoms:
                        
                            # Order the FLEDIH based on the atoms occurences
                            self.OrderFledih()
                        
                        continue

                    m = re.match("the protein center of coordinates is:\s+(\S+)\s+(\S+)\s+(\S+)\s+", Line)
                    if m:
                        
                        self.Ori[0] = float(m.group(1))
                        self.Ori[1] = float(m.group(2))
                        self.Ori[2] = float(m.group(3))

                        if self.RngOpt == 'LOCCLF':

                            self.OriX[0] = self.Ori[0] + 1  # X
                            self.OriX[1] = self.Ori[1]      # Y
                            self.OriX[2] = self.Ori[2]      # Z 
                            
                            self.OriY[0] = self.Ori[0]      # X
                            self.OriY[1] = self.Ori[1] + 1  # Y
                            self.OriY[2] = self.Ori[2]      # Z                        
                        
                            fileGrd = open(self.GridPath)
                            self.GridLines = fileGrd.readlines()
                            fileGrd.close() 

                        continue            


                    m = re.match("SIGMA_SHARE", Line)
                    if m:
                        self.ParseGA = True
                        continue
                                
            time.sleep(INTERVAL)


        print "FlexAID ended."

        self.FlexAID.ProcessRunning = False

        # Empty rotamers data
        self.dictRotamers.clear()
        self.dictRotamersIndex.clear()
        self.dictNumberRotamers.clear()
        del self.listFlexSideChainNRot[:]

        # Re-enable buttons
        self.top.Btn_Start.config(state='normal') 
        self.top.Btn_PauseResume.config(state='disabled')
        self.top.Btn_Stop.config(state='disabled')
        self.top.Btn_Abort.config(state='disabled')
        self.top.SimulationSTATUS = ''

        # Put back the auto_zoom to on
        cmd.set("auto_zoom", -1)


    '''
    @summary: SUBROUTINE OrderFledih: Order the FLEDIH atoms number based on
                                      the ligand construction (lout) if REQUIRED!                
    '''
    def OrderFledih(self):

        # Flexible bond(s) selected?
        # LOOK for ALL the EXTRA column (1 par Flexbond SELECTED)
        if self.FlexStatus != '':
            
            # Find occurrence order
            tot = len(self.ListAtom)
            
            # Get all the keys in the Dictionary (ALL the Atoms)
            order = self.dictFlexBonds.keys()
            order.sort()
        
            for k in order:
        
                if (self.dictFlexBonds[k][2] > 1):                                                        
                                                                
                    # Get the Atoms LIST
                    AtList = list()
                    AtList = self.dictFlexBonds[k][3:]
                    
                    AtListSorted = list()
                    
                    counter = 0
                    totalAtom = self.dictFlexBonds[k][2]                    
                            
                    for an in range(0, tot):
                        NoAtom = str(self.ListAtom[an])
                        
                        for noAt in range(0, totalAtom):                            
                        
                            if NoAtom == AtList[noAt]:
                                AtListSorted.append(NoAtom)
                                AtList[noAt] = 0
                                counter += 1
                                break
                            
                        if counter == totalAtom:
                            break

                    elemTot = len(self.dictFlexBonds[k])

                    for elem in range(3, elemTot):
                        self.dictFlexBonds[k][elem] = AtListSorted[elem-3]            
        
    '''
    @summary: SUBROUTINE AddToRotamers: Add the residue name to list of rotamers (from file rotobs)
    '''
    def AddToRotamers(self, ResName):
        
        # Try opening file 'rotobs.lst'
        f = open(os.path.join(self.FlexAID.RootDir,'WRK','deps','rotobs.lst'),'r')
        lines = f.readlines()
        f.close()

        self.dictNumberRotamers[ResName] = 0

        for line in lines:

            if line[0:3] == ResName:

                columns = str(line).split()
                
                for i in range(1,len(columns)):
                    self.dictRotamers[ResName].append(float(str(columns[i]).strip()))
                    
                self.dictNumberRotamers[ResName] += 1


        #print str(self.dictRotamers[ResName])

        return self.dictNumberRotamers[ResName] 
             
            
    '''
    @summary: SUBROUTINE getVarAtoms: Get the atoms that need their values to be modified                  
    @return: listAtVar - list
    '''
    def getVarAtoms(self, inpPath):
        
        NoAtom3 = 0
        NoAtom2 = 0
        NoAtom1 = 0

        file = open(inpPath)
        inpFile = file.readlines()
        file.close()
        
        # Creation of a dictionary containing the 3 neighbors of each atoms
        for line in inpFile:
            if line.startswith('HETTYP'):
                noLine = int(line[7:11])
                if (int(line[32:36]) == 0):
                    if (int(line[27:31]) == 0):
                        if (int(line[22:26]) == 0):
                            NoAtom3 = noLine
                        else:
                            NoAtom2 = noLine
                    else:
                        NoAtom1 = noLine
                        
                
        return [NoAtom3, NoAtom2, NoAtom1]
    

    '''
    @summary: SUBROUTINE Get_CoordRef: Get the list of initial coordinates of the reference
    '''
    def Get_CoordRef(self):

        dictCoordRef = {}

        for Line in self.ReferenceFile:
            
            if Line.startswith('HETATM'):
                index = int(Line[6:11].strip())
                CoordX = float(Line[30:38].strip())
                CoordY = float(Line[38:46].strip())
                CoordZ = float(Line[46:54].strip())

                dictCoordRef[index] = [ CoordX, CoordY, CoordZ ]

        return dictCoordRef
    
    '''
    @summary: SUBROUTINE dictRecAtom: Create a dictionary containing the neighbors of
              each atoms for the reconstruction.                  
    @param inpPath: Path to the inp file
    @return: RecAtom - dictionary
    '''
    def dictRecAtom(self, inpPath):
        RecAtom = {}

        file = open(inpPath)
        inpFile = file.readlines()
        file.close()
        
        # Creation of a dictionary containing the 3 neighbors of each atoms
        for line in inpFile:
            if line.startswith('HETTYP'):
                noLine = int(line[7:11])
                RecAtom[noLine] = [int(line[22:26]), int(line[27:31]), int(line[32:36])]
                
        return RecAtom


    def printDictDisAngDih(self):
        
        print("******************************************")
        for k, v in self.DisAngDih.items():
            print("ATOM: " + str(k) + "  " + str(self.DisAngDih[k][0]) + " " + str(self.DisAngDih[k][1]) + " " + str(self.DisAngDih[k][2]))

    '''
    @summary: SUBROUTINE dictRecAtom: Create a dictionary containing the neighbors of
              each atoms.                  
    @param icPath: Path to the ic file
    @return: DisAngDih - dictionary
    '''
    def dictDisAngDih(self, icPath):

        DisAngDih = {}        
                
        file = open(icPath)
        icFile = file.readlines()
        file.close()
        
        # Creation of a dictionary containing the 3 neighbors of each atoms
        for line in icFile:
            if line[0:6] != 'REFPCG':
                noLine = int(line[1:5])
                DisAngDih[noLine] = [float(line[7:15]), float(line[16:24]), float(line[25:33])]
                    
        return DisAngDih
    
    '''
    @summary: SUBROUTINE CreateTempPDB: Create X copy of the ligand PDB file                  
    '''   
    def CreateTempPDB(self, Path):
        
        # Create the custom path for the temporary pdb files
        for i in range (self.NBLineGEN + 1):
            self.listTmpPDB.append(os.path.join(Path,'LIG' + str(i) + '.pdb'))
            #print Path + "/LIG" + str(i) + '.pdb'