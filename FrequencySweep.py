#!C:\\Users\\QEPAS\\.conda\\envs\\Interfero_Py37\\python.exe'
# -*- coding: utf-8 -*-
"""
GUI for uRes photoacoustic
"""

import os
from collections import namedtuple
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.dockarea import DockArea
from pyqtgraph.dockarea import Dock
from pyqtgraph.parametertree import Parameter
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph import GraphicsWindow
from pyqtgraph import PlotWidget
import numpy as np
import toolbox.instrument 
import toolbox.parameter_tree
import toolbox.function

import time



# only if you want a white background for your graph
# pg.setConfigOption('background', 'w')

class MainWindow(QtWidgets.QMainWindow): 
    def __init__(self):
        super().__init__()
        # the tuple version of a dictionary, use to store width and height of the screen 
        Screen = namedtuple('Screen', 'width height')
        # get screen's information (height and width)
        # CAUTION this attribut can be modified by other method like .show
        # it can put all the values at 0, even they were welle defined
        self.screen = Screen(width=1500,height=800) 
        # dictionary with all the graphic elements 
        self.obj_graph = {'plot': {'dock': None,
                                   'graph': None,
                                   'curve': None,
                                  },
                          'plot2': {'dock': None,
                                   'graph': None,
                                   'curve': None
                                   },         
                          'param': {'dock': None,
                                    'tree': None,
                                    'parameter': None}}                          

        self.on_init()       
        # change the size of the graphic interface
        self.resize(self.screen.width, self.screen.height)
        # my timer use for acquisition in real time
        self.my_timer = None
        self.period_timer = 50
        # create an attribute with all my instruments 
        self.instruments = MesInstrus(param_tree=self.parameters)
        # display the GUI
        self.show()

    def on_init(self):
        # for debug it is useful to separate the create         
        self.create_dock()
        self.create_contenu_dock_pg()
        self.create_contenu_dock_plot()


    def create_dock(self):
        area = DockArea()
        self.obj_graph['param']['dock'] = Dock("setting parameters")
        self.obj_graph['plot']['dock'] = Dock("graphic 1")
        self.obj_graph['plot2']['dock'] = Dock("graphic 2")
        area.addDock(self.obj_graph['param']['dock'], 'left')
        area.addDock(self.obj_graph['plot']['dock'],'right')
        area.addDock(self.obj_graph['plot2']['dock'],'bottom',self.obj_graph['plot']['dock'])
        self.setCentralWidget(area)


    def create_contenu_dock_plot(self):
        # creation of plot 1 (graph 1)
        # a place for this graph has been defined in create_dock()
        self.obj_graph['plot']['curve'] = MesCourbes()
        self.obj_graph['plot']['graph'] = self.obj_graph['plot']['curve'].plot_widget 
        self.obj_graph['plot']['dock'].addWidget(self.obj_graph['plot']['graph'])
        self.obj_graph['plot']['curve'].add_curve('curve 0',(0,200,200),markers_on=True)
               
        # creation of plot 2 (graph 2)
        # a place for this graph has been defined in create_dock()   
        self.obj_graph['plot2']['curve'] = MesCourbes()
        self.obj_graph['plot2']['graph'] = self.obj_graph['plot2']['curve'].plot_widget
        self.obj_graph['plot2']['dock'].addWidget(self.obj_graph['plot2']['graph']) 
        self.obj_graph['plot2']['curve'].add_curve('curve 0',(0,100,100),markers_on=True)

    def create_contenu_dock_pg(self):
        self.obj_graph['param']['tree'] = ParameterTree()
        self.create_parameter()
        self.obj_graph['param']['dock'].addWidget(self.obj_graph['param']
                                                  ['tree'])

    def create_parameter(self):
        # create a Class with all parameters use in the GUI
        self.parameters = MesParams()
        # build the GUI
        (self.obj_graph['param']
         ['parameter']) = Parameter.create(name='params',
                                           type='group',
                                           children=self.parameters.tree)
        (self.obj_graph['param']
         ['parameter'].sigTreeStateChanged.connect(self.catch_param_change))

        """
        setParameters
        Set the top-level :class:`Parameter <pyqtgraph.parametertree.Parameter>`
        to be displayed in this ParameterTree.

        If *showTop* is False, then the top-level parameter is hidden and only 
        its children will be visible. This is a convenience method equivalent 
        to::
        
            tree.clear()
            tree.addParameters(param, showTop)
        """
        self.obj_graph['param']['tree'].setParameters((self.obj_graph['param']
                                                       ['parameter']),
                                                      showTop=False)
        self.obj_graph['param']['tree'].setWindowTitle('Parameter Tree')


    def catch_param_change(self, _, changes):
        # call in create_parameter()
        for param, _, data in changes:
            path = self.obj_graph['param']['parameter'].childPath(param)
            if path is not None: 
                # print(path) -> ['Input- Zurich', 'time constant']
                child_name = '.'.join(path)
                # print(child_name) -> Input- Zurich.time constant
            else:
                child_name = param.name()
            print('  parameter: %s' % child_name)
            print('  change:    %s' % _)
            print('  data:      %s (%s)' % (str(data),type(data)))

            # who is the name of the parameter tree
            # what the name of the paramater of the parameter tree
            try:
                who, what = child_name.split('.')
            except:
                who = child_name
                what = child_name

            graph_1 = self.obj_graph['plot']['curve']
            graph_2 = self.obj_graph['plot2']['curve']


            ## INSTRUMENT CHANGE
            # CAUTION check it always in first
            if what in ['instrument']:
                # in this case data == name of the instrument
                self.instruments.update(who,data)

            ## CHANGE VALUES ASKED ON THE INSTRUMENT
            if who in ['Input','Generator']:
                if what in ['time constant','sensitivity','amplitude','on','frequency']:
                    # get the nam of instrument asked in the parameter tree 
                    instru = self.parameters.give_inst(who)
                    self.instruments.set_value(instru,what,data)

            ## REMANING TIME
            if who in ['Input','Acquisition']:
                # eval remaning time
                self.parameters.remaning_time()


            ## START ACQUISITION
            if (who+'.'+what) in 'Acquisition.start':
                # earase data
                graph_1.clear_data('curve 0')
                graph_2.clear_data('curve 0')
                # create frequency list
                graph_1.create_frequency_list(
                    curve_id='curve 0',
                    param_tree=self.parameters)
                graph_2.create_frequency_list(
                    curve_id='curve 0',
                    param_tree=self.parameters)
                # on lance un timer qui appelera 'timerEvent' toutes les period_timer
                if self.my_timer is None:
                    self.my_timer = self.startTimer(self.period_timer) #c une methode heritée
                # the method timeEvent will be executed each period_timer

            ## AVERAGE ACQUISITION
            if (who+'.'+what) in 'Acquisition.average':
                # average data
                graph_1.average(
                    curve_id='curve 0',
                    param_tree=self.parameters)
                graph_2.average(
                    curve_id='curve 0',
                    param_tree=self.parameters)  
                # display graphs
                graph_1.display('curve 0','R')
                graph_2.display('curve 0','Phi')


            ## ERASE ACQUISITION
            if (who+'.'+what) in 'Acquisition.clear all':
                # earase data
                graph_1.clear_data('curve 0')
                graph_2.clear_data('curve 0')
                # display graphs
                graph_1.display('curve 0','R')
                graph_2.display('curve 0','Phi')  

            ## SAVE ACQUISITION
            if (who+'.'+what) in 'Save.save':
                toolbox.function.save_FS(
                    self.parameters,
                    self.obj_graph['plot']['curve'])
        

    def stop_timer(self):
        """
        methode pour arrêter le timer s'il est en route
        """
        # si l'attribut 'my_timer' n'est pas None
        if self.my_timer is not None:
            # alors on arrête le timer
            self.killTimer(self.my_timer)
            self.my_timer = None

    def timerEvent(self, _):
        """
        code exécuté toutes les "period_timer"
        """
        graph_1 = self.obj_graph['plot']['curve']
        graph_2 = self.obj_graph['plot2']['curve']
        # test to stop the timer i.e. the acquisition
        if len(graph_1.curves['curve 0']['data']['R']) == len(graph_1.curves['curve 0']['data']['Freq']):
            self.stop_timer()
            return
        # change frequency on the instrument to freq
        index = len(graph_1.curves['curve 0']['data']['R'])
        freq_i = graph_1.curves['curve 0']['data']['Freq'][index]
        instru = self.parameters.give_inst('Generator')
        self.instruments.set_value(instru,'frequency',freq_i)
        # wait
        time.sleep(self.parameters.waiting_time())
        # get X Y R and Phi from instrument
        recording_time = self.parameters.give('Input','recording time')
        temp = self.instruments.get_X_Y_R_Phi(instru,recording_time)
        # update data
        graph_1.update_X_Y_R_Phi('curve 0',temp)
        graph_2.update_X_Y_R_Phi('curve 0',temp)
        # plot data
        graph_1.display('curve 0','R')
        graph_2.display('curve 0','Phi')



    def closeEvent(self, event):
        # result = QtWidgets.QMessageBox.question(self,
        #                                         "Confirm Exit...",
        #                                         "Do you want to exit ?",
        #                                         (QtWidgets.QMessageBox.Yes |
        #                                          QtWidgets.QMessageBox.No))
        # if result == QtWidgets.QMessageBox.Yes:
        #     # permet d'ajouter du code pour fermer proprement
        #     # close all instrument
        #     toolbox.instrument.close_all_inst()
        #     event.accept()
        # else:
        #     event.ignore()
        pass

class MesInstrus():
    def __init__(self,param_tree):
        self.param_tree = param_tree
        # attribut with all the instrument created
        self.connected = ['Virtual']
        # dico with instru which can be called
        self.use = {
            'Virtual':toolbox.instrument.Instrument(name='Virtual'),
            'Zurich-MFLI_dev4199':None}

    def set_value(self,inst,what,value):
        self.use[inst].set_value(what,value)

    def connect_inst(self,inst):
        # check if the instrument is already connected if not connect it
        if inst not in self.connected:
            print('%s has not been created'%inst)
            # create instrument
            self.use[inst] = toolbox.instrument.Instrument(name=inst)
            # add its named in the list of created instrument
            self.connected.append(inst)
            print('Instrument connected :%s'%(self.connected))

    def update(self,who,inst):
        # update value from the parameter tree to the instrument
        self.connect_inst(inst)
        A = self.param_tree.give_all_inst_value(who)
        for k in A:
            self.set_value(inst,k[0],k[1])
        pass

    def get_X_Y_R_Phi(self,inst,poll_length):
        return self.use[inst].poll(poll_length=poll_length)        

class MesParams():
    def __init__(self):
        # dictionary of parameter tree used
        self.dico = {
            'Laser Doppler Vibrometer':toolbox.parameter_tree.LaserDopplerVibrometer(name='Laser Doppler Vibrometer'),
            'Input':toolbox.parameter_tree.Input(name='Input'),
            'Generator':toolbox.parameter_tree.Generator(name='Generator'),
            'Acquisition':toolbox.parameter_tree.Acquisition(name='Acquisition'),
            'Save':toolbox.parameter_tree.Save(name='Save'),
            'Graph':toolbox.parameter_tree.AllPlotScalableGroup(name='Graph')}
        # use the self.dico to build a list required for the GUI
        self.tree = []       
        for k in self.dico:
            self.tree.append(self.dico[k]) 

    def give(self,who,what):
        # return the value of 'what' from 'who' in the parameter tree
        return self.dico[who].param(what).value()

    def give_inst(self,who):
        # return the name of the instrument selected in the parameter tree
        return self.dico[who].param('instrument').value()

    def give_all_inst_value(self,who):
        # returns all the parameters necessary for updating the instrument 
        # (amplitude, frequency , etc.)
        A = []
        if who in 'Input':
            for k in ['time constant','sensitivity']: 
                A.append([k,self.dico[who].param(k).value()])
        if who in 'Generator':
            for k in ['amplitude','on']: 
                A.append([k,self.dico[who].param(k).value()])
        return A

    def remaning_time(self):
        nbr_p = self.dico['Acquisition'].param('nbr pts').value()
        nbr_s = self.dico['Acquisition'].param('nbr seqs').value()
        wt = self.waiting_time()
        rt = (wt)*nbr_p*nbr_s
        self.dico['Acquisition'].remaning_time(rt)  

    def waiting_time(self):
        tc = self.dico['Input'].param('time constant').value()
        wt = self.dico['Acquisition'].param('waiting time').value()
        return tc*wt


class MesCourbes():
    def __init__(self):
        self.plot_widget = PlotWidget()
        self.plot_widget.showGrid(x=True,y=True)
        # self.plot_widget.getPlotItem().addLegend()
        self.plot_widget.setBackground((0, 0, 0))
        #  dictionary with all the curve and their data 
        # curve 0 is dedicated to the live/acquisition plot
        self.curves = {}

    def add_curve(self, curve_id, curve_color, markers_on=False):
        curve_name = curve_id
        pen = pg.mkPen(curve_color, width=3)
        symbol = "o"
        symbolPen = pg.mkPen(0,0,0)
        symbolBrush = curve_color
        symbolSize = 8
        # this adds the item to the plot and legend
        if markers_on:
            plot = self.plot_widget.plot(
                name=curve_name, pen=pen, symbol=symbol, symbolPen=symbolPen, 
                symbolBrush=symbolBrush, symbolSize=symbolSize
            )
        else:
            plot = self.plot_widget.plot(name=curve_name, pen=pen)
        self.curves[curve_id] = {
                    'plot':plot,
                    'data':{'Freq':[],'X':[],'Y':[],'R':[],'Phi':[]}
                        }

    def average(self,curve_id,param_tree):
        nbr_seqs = param_tree.give('Acquisition','nbr seqs')
        for k in ['X','Y','R','Phi']:
            temp = self.curves[curve_id]['data'][k]
            self.curves[curve_id]['data'][k] = toolbox.function.average(temp,nbr_seqs)

    def clear_data(self,curve_id):
        for k in ['Freq','X','Y','R','Phi']:
            self.curves[curve_id]['data'][k] = []       

    def create_frequency_list(self,curve_id,param_tree):
        '''
        Create a array with all the frequency use for the frequency sweep
        It take into account if many sequences have been asked
        '''
        freq_min = param_tree.give('Acquisition','freq min')
        freq_max = param_tree.give('Acquisition','freq max')
        nbr_pts = param_tree.give('Acquisition','nbr pts')
        nbr_seqs = param_tree.give('Acquisition','nbr seqs')
        freq_list = np.linspace(freq_min,freq_max,nbr_pts)
        if nbr_seqs > 1:
            temp = freq_list
            i=0
            while i < int(nbr_seqs)-1:
                i+=1
                freq_list = np.append(freq_list,temp[::(-1)**i])
        self.curves[curve_id]['data']['Freq'] = freq_list

    def display(self,curve_id,what):
        X = self.curves[curve_id]['data']['Freq']
        Y = self.curves[curve_id]['data'][what]
        # during acquisition freq is longer than the others datas
        # so it is useful to reduce it
        if len(X) != len(Y):
            X = self.curves[curve_id]['data']['Freq'][0:len(Y)]
        self.set_values(curve_id,X,Y)

    def remove_curve(self, curve_id):
        curve_id = str(curve_id)
        if curve_id in self.curves:
            self.plot_widget.removeItem(self.curves[curve_id]['plot'])
            del self.curves[curve_id]

    def set_values(self, curve_id, data_x, data_y):
        curve = self.curves[curve_id]['plot']
        curve.setData(data_x, data_y)

    def update_X_Y_R_Phi(self,curve_id,A):
        self.curves[curve_id]['data']['X'] = np.append(self.curves[curve_id]['data']['X'],A[0])
        self.curves[curve_id]['data']['Y'] = np.append(self.curves[curve_id]['data']['Y'],A[1])
        self.curves[curve_id]['data']['R'] = np.append(self.curves[curve_id]['data']['R'],A[2])
        self.curves[curve_id]['data']['Phi'] = np.append(self.curves[curve_id]['data']['Phi'],A[3]) 

if __name__ == '__main__': # permet d'executer que avec le run 
    import sys
    APP = pg.mkQApp() # fabriquer fenetre, ligne obligatoire
    WIN = MainWindow() # cree instance à ma class
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'): # fait moi tourner cette fenetre tant 
       QtWidgets.QApplication.instance().exec_()
    # le IF fait tourner la fenetre tant qu'elle n'est pas fermée ou que la fonction close est apellé