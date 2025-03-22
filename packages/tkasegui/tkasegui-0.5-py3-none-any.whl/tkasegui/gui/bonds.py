''' Statistics for valence bonds:
    average bond lengths, anlges,
    coordination numbers
'''

from ase.gui.i18n import _
import tkasegui.gui.ui as ui
from tkasegui.gui.simulation import Simulation
from ase.geometry.analysis import Analysis

import numpy as np

class BondsStat:
    def __init__(self, gui):
        self.gui = gui
        self.gui.register_vulnerable(self)
        self.win = ui.Window(_('Bonds statistics'))
        self.win.add(ui.Label(
            _('Calculate *average* bond lengths, angles and '
            'number of neighbors')))
        self.win.add(ui.Label(''))
        # self.chems = ['*']  # chemical symbols, * - any symbol
        # self.chems.extend(set(gui.atoms.get_chemical_symbols()))
        self.chems = list(set(gui.atoms.get_chemical_symbols()))
        self.win.add(ui.Label(_('atom types')))
        self.cbA = ui.ComboBox(labels=self.chems, width=5)
        self.cbB = ui.ComboBox(labels=self.chems, width=5)
        self.cbC = ui.ComboBox(labels=self.chems, width=5)
        self.win.add([ui.Label('A: '), self.cbA])
        self.win.add([ui.Label('B: '), self.cbB])
        self.cbAngles = ui.CheckButton(_('angles info'))
        self.win.add(self.cbAngles)
        self.win.add([ui.Label('C: '), self.cbC])
        self.win.add(ui.Label(''))
        self.btCalc = ui.Button('Calculate', self.run)
        self.win.add(self.btCalc)
        self.output = ui.Text(12 * '\n')
        self.savebutton = ui.Button('Save', self.saveoutput)
        self.win.add(ui.Label(_('Output:')))
        self.win.add([self.output, self.savebutton])
        self.savebutton.active = False
        self.win.add(ui.Button(_('Close'), self.close))

    def saveoutput(self):
        chooser = ui.SaveFileDialog(self.win.win)
        filename = chooser.go()
        if filename:
            with open(filename, 'w') as f:
                for line in self.output.text:
                    f.write(line)

    def run(self, *args):
        atoms = self.gui.atoms
        ana = Analysis(atoms)

        A = self.chems[self.cbA.value]
        B = self.chems[self.cbB.value]
        # if (A == '*') and (B == '*'):
        #     bonds = ana.all_bonds
        # else:
        bonds = ana.get_bonds(A, B, unique=True)
        bond_lengths = ana.get_values(bonds)
        chems = np.array(atoms.get_chemical_symbols())
        nA = len(chems[chems == A])
        nB = len(chems[chems == B])
        txt = _(f'Count of {A} atoms: {nA}\n')
        if A != B:
            txt += _(f'Count of {B} atoms: {nB}\n')
        txt += _(f'Number of {A}-{B} bonds: {len(bonds[0])}\n')
        txt += _(f'average: {np.average(bond_lengths):.3f} Angstr.\n')
        txt += _(f'    std: {np.std(bond_lengths):.3f} Angstr.\n')
        if A == B:
            txt += _(f'Number of neighbors: {2*len(bonds[0])/nA:.2f}\n')
        else:  # A != B
            txt += _(f'Number of {B} neighbors around {A}: {len(bonds[0])/nA:.2f}\n')
            txt += _(f'Number of {A} neighbors around {B}: {len(bonds[0])/nB:.2f}\n')
        del bond_lengths

        if self.cbAngles.value:
            C = self.chems[self.cbC.value]
            # if (A == '*') and (B == '*') and (C == '*'):
            #    angles = ana.all_angles
            # else:
            angles = ana.get_angles(A, B, C, unique=True)
            angles_values = ana.get_values(angles)
            # nC = len(chems[chems == C])
            # txt += _(f'Count of {C} atoms: {nC}\n')
            txt += _(f'\nNumber of {A}-{B}-{C} angles: {len(angles[0])}\n')
            txt += _(f'average: {np.average(angles_values):.3f} deg.\n')
            txt += _(f'    std: {np.std(angles_values):.3f} deg.\n')
            del angles_values

        self.output.text = txt
        self.savebutton.active = True

    def notify_atoms_changed(self):
        pass

    def close(self):
        self.gui.unregister_vulnerable(self)
        self.win.close()
