
from ase.gui.i18n import _
import tkasegui.gui.ui as ui
from tkasegui.geometry import prdf
from tkasegui.gui.widgets import pybutton
import numpy as np

# delayed import
# import matplotlib.pyplot as plt

class Rdf:
    ''' Window for obtaining Radial Distribution Function
        of atoms
    '''
    def __init__(self, gui):
        self.gui = gui
        self.gui.register_vulnerable(self)

        self.result_r = []
        self.result_rdf = []

        atoms = self.gui.atoms
        nImages = len(self.gui.images)

        self.win = ui.Window(_('RDF'))
        self.win.add(ui.Label(_(
            '''Compute radial distribution
            function between atoms

            Note: partial RDFs under construction
            '''
        )))

        self.win.add(ui.Label(_('Distance grid')))
        self.enRmax = ui.Entry(value=10, width=8)
        self.enRstep = ui.Entry(value=0.1, width=5)
        self.win.add([ui.Label(_('Rmax: ')),
                      self.enRmax, ui.Label('Å'),
                      ui.Label(_(' Rstep: ')),
                      self.enRstep, ui.Label('Å')])
        self.win.add(ui.Label(''))
        self.win.add(ui.Label(_('Average over configurations')))

        self.sbFrom = ui.SpinBox(value=1, start=1, end=nImages, step=1)
        self.sbTo = ui.SpinBox(value=nImages, start=1, end=nImages, step=1)
        self.sbStep = ui.SpinBox(value=1, start=1, end=nImages, step=1)

        self.win.add([ui.Label(_('from: ')), self.sbFrom,
                      ui.Label(_(' to: ')), self.sbTo,
                      ui.Label(_(' every: ')), self.sbStep])
        self.win.add(ui.Label(''))
        self.chems = ['*']  # chemical symbols, * - any symbol
        self.chems.extend(set(atoms.get_chemical_symbols()))
        self.cbA = ui.ComboBox(labels=self.chems, width=5)
        self.cbB = ui.ComboBox(labels=self.chems, width=5)
        self.win.add(ui.Label(_('Atom types (* - any)')))
        self.win.add([_('A: '), self.cbA])
        self.win.add([_('B: '), self.cbB])
        self.win.add(ui.Label(''))
        self.win.add([pybutton('Python', self.pybutton_click),
                      ui.Button(_('Compute RDF'), self.compute),
                      ui.Button(_('Plot'), self.plot_rdf),
                      ui.Button(_('Save data'), self.save_rdf),
                      ui.Button(_('Close'), self.close)])

    def close(self):
        self.gui.unregister_vulnerable(self)
        self.win.close()

    def compute(self):
        rmax = float(self.enRmax.value)
        dR = float(self.enRstep.value)
        A = self.chems[self.cbA.value]
        B = self.chems[self.cbB.value]
        nconf = (self.sbTo.value - self.sbFrom.value + 1) / self.sbStep.value
        print(f'Computing RDF for {nconf:.0f} configurations')

        R, rdf, rdf_AA, rdf_AB, rdf_BA, rdf_BB = \
            prdf.get_mean_rdf(list(self.gui.images),
                              A=A, B=B, Rmax=rmax, dR=dR, mic=True,
                              imageIdx=slice(self.sbFrom.value-1,
                                             self.sbTo.value,
                                             self.sbStep.value))
        self.result_r = R
        self.result_rdf = rdf
        self.result_rdf_AA = rdf_AA
        self.result_rdf_AB = rdf_AB
        self.result_rdf_BA = rdf_BA
        self.result_rdf_BB = rdf_BB
        print('RDF computation finished')
        return

    def plot_rdf(self):
        import matplotlib.pyplot as plt
        A = self.chems[self.cbA.value]
        B = self.chems[self.cbB.value]
        plt.figure(figsize=(4 * 2.5**0.5, 4))
        plt.plot(self.result_r, self.result_rdf, color='black', label='tot')
        if (A != '*') and (B != '*'):
            plt.plot(self.result_r, self.result_rdf_AA, label=f'{A}-{A}')
            if A != B:
                plt.plot(self.result_r, self.result_rdf_AB, label=f'{A}-{B}')
                plt.plot(self.result_r, self.result_rdf_BA, label=f'{B}-{A}')
                plt.plot(self.result_r, self.result_rdf_BB, label=f'{B}-{B}')
        plt.xlabel(r'$R$, Å')
        plt.ylabel(r'RDF, Å$^{-1}$')
        plt.legend()
        plt.show()
        return

    def save_rdf(self):
        A = self.chems[self.cbA.value]
        B = self.chems[self.cbB.value]
        chooser = ui.SaveFileDialog(self.win.win)
        filename = chooser.go()
        if filename:
            np.savetxt(filename,
                       np.transpose(np.stack([self.result_r,
                                              self.result_rdf,
                                              self.result_rdf_AA,
                                              self.result_rdf_AB,
                                              self.result_rdf_BA,
                                              self.result_rdf_BB])),
                       header=f'R,Angstr\ttotal\t{A}-{A}\t{A}-{B}\t{B}-{A}\t{B}-{B}')
        return

    def pybutton_click(self):
        rmax = float(self.enRmax.value)
        dR = float(self.enRstep.value)
        A = self.chems[self.cbA.value]
        B = self.chems[self.cbB.value]
        s = 'from tkasegui.geometry import prdf\n\n'
        s += 'ana = Analysis(images)\n'
        s += 'R, rdf, rdf_AA, rdf_AB, rdf_BA, rdf_BB = \n'
        s += '    prdf.get_mean_rdf(images,\n'
        s += f'         A=\'{A}\', B=\'{B}\',\n'
        s += f'         Rmax={rmax}, dR={dR}, mic=True,\n'
        s += f'         imageIdx=slice({self.sbFrom.value-1},'
        s += f'{self.sbTo.value},{self.sbStep.value}))'
        return s

    def notify_atoms_changed(self):
        nImages = len(self.gui.images)
        # if self.scale.value > n:
        #     self.scale.value = n
        # self.scale.set_end(n)
