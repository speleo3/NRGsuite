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

# coding: utf-8 
'''
@title: CfgIsoCleft.py

@summary: Module that define the configuration of the NRG suite applications.

@organization: Najmanovich Research Group
@creation date:  feb. 18, 2011
'''

# FONT SETTINGS

def GetFontType():
    #Possibility:
    #    'helvetica'
    #    'courrier'
    FontType = 'helvetica'
    return FontType

def GetFontSize():
    FontSize = 12
    return FontSize