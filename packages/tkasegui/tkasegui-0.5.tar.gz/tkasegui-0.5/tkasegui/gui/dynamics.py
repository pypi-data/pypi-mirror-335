''' Module for performing energy minimization
'''

import tkasegui.gui.ui as ui
from tkasegui.gui.simulation import Simulation
# import ase
from ase import units
from ase.gui.i18n import _


class Dynamics(Simulation):
    ''' Window for performing molecular dynamics simulations '''

    md_styles = ('VelocityVerlet', 'Langevin', 'NVTBerendsen', 'NVT',
                 'NPT', 'NPTBerendsen')

    def __init__(self, gui):
        super().__init__(gui)
        self.title = _('Molecular dynamics')
        self.win.add(ui.Label(
            _('Move atoms according to forces acting on them.')))
        self.win.add(ui.Label(''))

        self.packimageselection()
        self.win.add(ui.Label(''))

        self.make_dynamics_gui()
        self.win.add(ui.Label(''))

        self.status_label = ui.Label('')
        self.win.add(self.status_label)

        self.makebutbox()

    def make_dynamics_gui(self):
        self.style_cb = ui.ComboBox(labels=self.md_styles,
                                    callback=self.dyn_style_selected)
        self.win.add([ui.Label(_('MD style: ')), self.style_cb])
        self.nsteps_spin = ui.SpinBox(value=100, start=0,
                                    end=1e6, step=1)
        self.win.add([ui.Label(_('Number of time steps: ')), self.nsteps_spin])
        self.timestep_spin = ui.SpinBox(value=0.5, start=0.0, end=10.0, step=0.1)
        self.win.add([ui.Label(_('Time step [fs]: ')), self.timestep_spin])
        self.taut_spin = ui.SpinBox(value=50, start=10, end=1000, step=10)
        self.win.add([ui.Label(_('Thermostat coupling [fs]: ')), self.taut_spin])
        self.temp_spin = ui.SpinBox(value=300, start=0, end=30000, step=100)
        self.win.add([ui.Label(_('Thermostat temperature [K]: ')), self.temp_spin])
        self.taup_spin = ui.SpinBox(value=200, start=10, end=1000, step=10)
        self.win.add([ui.Label(_('Barostat coupling [fs]: ')), self.taup_spin])
        self.pres_spin = ui.SpinBox(value=1, start=0, end=10, step=1)
        self.win.add([ui.Label(_('Barostat pressure [GPa]: ')), self.pres_spin])

        self.dyn_style_selected()

    def dyn_style_selected(self, *args):
        ''' Show or hide thermo/barostats widgets '''
        style = self.md_styles[self.style_cb.value]
        flag_temp = style in ['Langevin', 'NVTBerendsen', 'NVT',
                              'NPT', 'NPTBerendsen']
        flag_pres = style in ['NPT', 'NPTBerendsen']
        self.taut_spin.active = flag_temp
        self.temp_spin.active = flag_temp
        self.taup_spin.active = flag_pres
        self.pres_spin.active = flag_pres

    def run(self, *args):
        ''' run the dynamics '''
        if not self.setup_atoms():
            return
        nsteps = self.nsteps_spin.value
        timestep = self.timestep_spin.value
        tauT = self.taut_spin.value
        tauP = self.taup_spin.value
        T = self.temp_spin.value
        P = self.pres_spin.value
        self.begin(mode='dyn', nsteps=nsteps, dt=timestep)
        style = self.md_styles[self.style_cb.value]
        try:
            logger_func = self.gui.simulation['progress'].get_logger_stream
        except (KeyError, AttributeError):
            logger = '-'  # None
        else:
            logger = logger_func()  # Don't catch errors in the function.
        # algo = getattr(ase.md, backend)
        if style == 'VelocityVerlet':
            from ase.md.verlet import VelocityVerlet
            dyn = VelocityVerlet(self.atoms, timestep=timestep*units.fs,
                                 logfile=logger)
        elif style == 'Langevin':
            from ase.md.langevin import Langevin
            dyn = Langevin(self.atoms, timestep=timestep*units.fs,
                           friction=1/(tauT*units.fs), temperature_K=T,
                           logfile=logger)
        elif style == 'NVTBerendsen':
            from ase.md.nvtberendsen import NVTBerendsen
            dyn = NVTBerendsen(self.atoms, timestep=timestep*units.fs,
                           taut=tauT*units.fs, temperature_K=T,
                           logfile=logger)
        elif style == 'NVT':  # Nose with disabled barostat
            from ase.md.npt import NPT
            dyn = NPT(self.atoms, timestep=timestep*units.fs,
                      ttime=tauT*units.fs, temperature_K=T,
                      pfactor=None, externalstress=0,
                      logfile=logger)
        elif style == 'NPT':  # Nose
            from ase.md.npt import NPT
            dyn = NPT(self.atoms, timestep=timestep*units.fs,
                      ttime=tauT*units.fs, temperature_K=T,
                      pfactor=0.6*(tauP*units.fs)**2, externalstress=0.006*P,
                      logfile=logger)
        elif style == 'NPTBerendsen':
            from  ase.md.nptberendsen import NPTBerendsen
            dyn = NPTBerendsen(self.atoms, timestep=timestep*units.fs,
                               taut=tauT*units.fs, temperature_K=T,
                               taup=tauP*units.fs, pressure_au=0.006*P,
                               compressibility_au=4.57e-5/units.bar,  # needed?
                               logfile=logger)
        else:
            raise Exception('MD stlye %s is not implemented' % style)
        # Display status message
        self.count_steps = 0
        self.status_label.text = _('Step %i of %i') \
                                 % (self.count_steps, nsteps)
        self.win.update()

        self.prepare_store_atoms()
        dyn.attach(self.step_performed, interval=1)
        try:
           dyn.run(nsteps)
        # except AseGuiCancelException:
        # # Update display to reflect cancellation of simulation.
        #     self.status_label.set_text(_('Minimization CANCELLED after %i steps.')
        #                                % self.count_steps)
        except MemoryError:
            self.status_label.text = _('Out of memory!')
        else:
            self.status_label.text = _('Dynamics performed for %i steps (%f ps)') \
                                     % (self.count_steps,
                                        self.count_steps*timestep/1000)
        self.end()
        if self.count_steps:
            self.gui.notify_vulnerable()

        # Open movie window and energy graph
        # XXX disabled 2018-10-19.  --askhl
        #if self.gui.images.nimages > 1:
        #    self.gui.movie()
        #    assert not np.isnan(self.gui.images.E[0])
        #    if not self.gui.plot_graphs_newatoms():
        #        expr = 'i, e - E[-1]'
        #        self.gui.plot_graphs(expr=expr)

    def step_performed(self):
        ''' called after each step '''
        self.status_label.text = _('Running step %i of %i') \
                                 % (self.count_steps,
                                    self.nsteps_spin.value)
        self.win.update()
        self.store_atoms()
        self.gui.set_frame(len(self.gui.images)-1)
