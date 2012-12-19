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
@title: FlexAID - FlexSideChain.py

@summary: Permit to select the residu in the protein that will be used for the 
          Flexible Side Chain option.

@organization: Najmanovich Research Group
@creation date:  March 30, 2010
'''

from pymol.wizard import Wizard
from pymol import cmd

import pymol
import General_cmd

class flexSC(Wizard):
    
    #=======================================================================
    ''' Initialization of the interface '''
    #=======================================================================
    def __init__(self, top):
        
        #print "New instance of FlexSC Wizard"

        Wizard.__init__(self)

        self.top = top
        self.FlexAID = self.top.top

        self.FlexAID.WizardError = False

        self.ProtName = self.FlexAID.IOFile.ProtName.get()
        self.TargetFlex = self.top.TargetFlex

        self.ResidueName = '...'
        self.PanelResidue = '   Residue: '
        
        self.FlexSCDisplay = 'FLEXIBLE_SIDE_CHAINS__'   
        self.ResidueDisplay = 'HIGHLIGHT_RESIDUE__'   
        self.BackboneDisplay = 'BACKBONE_ATOMS__'

        # for get_prompt
        self.error = 0
        
        # for Quit_Wizard
        self.ErrorCode = 1
                  
    #=======================================================================
    ''' Button Done selected '''
    #=======================================================================
    def btn_Done(self):
        
        self.Quit_Wizard()
        
    #=======================================================================
    ''' Executes the first steps of the Wizard'''
    #=======================================================================    
    def Start(self):
        
        cmd.refresh_wizard()

        # Initial view
        self.View = cmd.get_view()
        self.State = cmd.get_state()

        # Display all Selected Flexible Bonds
        if self.show_SelectedSC():
            self.FlexAID.DisplayMessage("  ERROR: Could not display selected flexible side-chains", 1)
            self.Quit_Wizard()
            return

        #self.selection_mode = cmd.get_setting_legacy("mouse_selection_mode")
        self.selection_mode = cmd.get("mouse_selection_mode")
        cmd.set("mouse_selection_mode", 1) # set selection mode to residue

        # Mask objects
        self.exc = [ self.ProtName ]
        General_cmd.mask_Objects(self.exc)

        # remove any possible selection before selecting atoms
        cmd.deselect()
              
        self.ErrorCode += 1

    #=======================================================================
        ''' update_SelectedSC : updates the view of selected flexible sc. ''' 
    #=======================================================================       
    def show_SelectedSC(self):
        
        selString = ''

        for sc in self.TargetFlex.listSideChain:
            
            resn = sc[0:3]
            resi = sc[3:3+len(sc)-4]
            chain = sc[len(sc)-1:len(sc)]

            if selString != '':
                selString += ' or '

            selString += ' ! n. C+O+N '
            selString += ' & resn ' + str(resn)
            selString += ' & resi ' + str(resi)
            
            if chain != '-':
                selString += ' & c. ' + str(chain)

            selString += ' & ' + self.ProtName
            
            
        cmd.delete(self.FlexSCDisplay)

        if selString != '' and self.highlight_FlexibleSC(selString):
            return 1

        return 0

    #=======================================================================
    ''' Button Add Residue Clicked: Add the residue in the Flexible Side-Chains
                                   DDL in FlexAID '''
    #=======================================================================       
    def btn_AddResidue(self):
        
        self.TargetFlex.Add_SideChain(self.ResidueName)

        self.ResidueName = '...'
        self.show_SelectedSC()

        cmd.delete(self.ResidueDisplay)
        cmd.refresh_wizard()
            
                
    #=======================================================================
    ''' Button Add Residue Clicked: Add the residue in the Flexible Side-Chains
                                   DDL in FlexAID '''
    #=======================================================================       
    def btn_DelResidue(self):
        
        self.TargetFlex.Remove_SideChain(self.ResidueName)

        self.ResidueName = '...'
        self.show_SelectedSC()

        cmd.delete(self.ResidueDisplay)
        cmd.refresh_wizard()
     
    #=======================================================================
    ''' Display a message in the interface '''
    #=======================================================================
    def get_prompt(self):
     
        if self.error == 0:
            return ['Click on a side-chain of the protein object']
        elif self.error == 1:
            return ['Invalid side-chain selected. Please try again.']

    #=======================================================================
    ''' Residue selection, then display the information related to it '''
    #=======================================================================
    def do_select(self, name):

        self.atom = self.get_Atom(name)

        if self.atom:

            resn = self.atom[1]
            resi = self.atom[2]
            chain = self.atom[3]

            if chain == '':
                chain = '-'

            if resn != 'VAL' and resn != 'LEU' and resn != 'MET' and resn != 'ILE' and \
               resn != 'ASN' and resn != 'CYS' and resn != 'SER' and resn != 'THR' and \
               resn != 'GLN' and resn != 'ASP' and resn != 'GLU' and resn != 'LYS' and \
               resn != 'ARG' and resn != 'HIS' and resn != 'PHE' and resn != 'TYR' and \
               resn != 'TRP':
                
                self.error = 1
                
            else:

                self.highlight_Residue(name)
                self.ResidueName = resn + str(resi) + chain
                
                self.error = 0

        cmd.deselect()
        cmd.refresh_wizard()

    #=======================================================================
    ''' Panel displayed in the right side of the Pymol interface '''
    #=======================================================================
    def get_panel(self):

        return [
         [ 1, '* Flexible Side-Chains *',''],
         [ 3, self.PanelResidue + self.ResidueName,''],
         [ 2, 'Add the Residue','cmd.get_wizard().btn_AddResidue()'],
         [ 2, 'Delete the Residue','cmd.get_wizard().btn_DelResidue()'],       
         [ 2, 'Done','cmd.get_wizard().btn_Done()'],         
         ]


    #=======================================================================
    ''' Quits the wizard '''
    #=======================================================================    
    def Quit_Wizard(self):
        
        try:

            #Delete the Residue objects
            cmd.delete(self.FlexSCDisplay)
            cmd.delete(self.ResidueDisplay)
            cmd.delete(self.BackboneDisplay)

            if self.ErrorCode != 1:
                General_cmd.unmask_Objects(self.exc)
                cmd.set('mouse_selection_mode', self.selection_mode)
                #cmd.config_mouse('three_button_editing', 1)

            if self.ErrorCode > 0:
                self.FlexAID.WizardError = True

            self.FlexAID.ActiveWizard = None

            cmd.set_wizard()
            #cmd.set_view(self.View)
            
        except:
            pass

        self.top.FlexSCRunning(False)

     #=======================================================================   
    ''' gets atom information (coordinates and index)'''
    #=======================================================================    
    def get_Atom(self, name):

        info = []

        try:
            # test if the click is on the protein
            list = cmd.index(name + " & " + self.ProtName)

            if len(list) > 0:
                atoms = cmd.get_model(name, state=1)
                for at in atoms.atom:
                    info.extend([ at.index, at.resn, at.resi, at.chain, at.name,
                                  at.coord[0], at.coord[1], at.coord[2] ])

                    break

            else:
                self.FlexAID.DisplayMessage("  You must click in the protein object '" + self.ProtName + "'", 2)
                return info

            cmd.deselect()

        except:
            self.FlexAID.DisplayMessage("  ERROR: Could not retrieve atom info", 1)
            self.Quit_Wizard()
        
        return info

    #=======================================================================   
    ''' highlight_Residue: Highlight residue upon selection '''
    #=======================================================================    
    def highlight_Residue(self, name):

        try:
            View = cmd.get_view()
            
            cmd.delete(self.ResidueDisplay)
            
            # Create new object from selection
            cmd.create(self.ResidueDisplay, name + ' & ! n. C+O+N', target_state=self.State)

            # Visual appearance
            cmd.hide('lines', self.ResidueDisplay)
            cmd.show('sticks', self.ResidueDisplay)
            cmd.color('orange', self.ResidueDisplay)

            cmd.mask(self.ResidueDisplay)

            # Toggle FlexSC obj to overlap ResidueDisplay
            cmd.disable(self.FlexSCDisplay)
            cmd.enable(self.FlexSCDisplay)
            cmd.disable('TOP_*__')
            cmd.enable('TOP_*__')

            cmd.set_view(View)

        except:
            self.FlexAID.DisplayMessage("  ERROR: Could not highlight residue upon selection", 2)

    #=======================================================================   
    ''' highlight_FlexibleSC: Highlight flexible side-chains '''
    #=======================================================================    
    def highlight_FlexibleSC(self, selString):

        try:
            View = cmd.get_view()

            # Create new object from selection
            #cmd.select('TEMP_SELECTION__', selString)
            cmd.create(self.FlexSCDisplay, selString, target_state=self.State)

            # Visual appearance
            cmd.hide('lines', self.FlexSCDisplay)
            cmd.show('sticks', self.FlexSCDisplay)
            cmd.color('white', self.FlexSCDisplay)
                
            cmd.mask(self.FlexSCDisplay)

            cmd.disable('TOP_*__')
            cmd.enable('TOP_*__')

            cmd.set_view(View)

        except:
            return 1

        return 0