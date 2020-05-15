# 20200130 Creation of AcquisitionRD for RingDown interface

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

app = QtGui.QApplication([])
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

path_WINDOWS = 'C:\\Users\\QEPAS\\Documents\\DATA\\'
path_MACOS = '/Users/michaelbahriz/Recherche/Python/data/'
path = path_MACOS

class MonParametre():
    # mother class use to transfert method to other class

    def child_list(self):
        # return a list with the name and value of all the children
        A = ''
        for i in self.children():
            A = A+i.name()+' : '+str(i.value())+'\n'
        return A

class Acquisition(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        freq_min = 32.76e3
        freq_max = 32.78e3
        self.addChild({'name': 'remaning time', 'type': 'float', 'value': 'NaN', 'siPrefix': True, 'suffix': 's', 'readonly': True})
        self.addChild({'name': 'freq min', 'type': 'float','value': freq_min, 'step': 10e3, 'limits': (1, 500e3),'siPrefix': True, 'suffix': 'Hz','decimals':6})
        self.addChild({'name': 'freq max', 'type': 'float','value': freq_max, 'step': 10e3, 'limits': (1, 500e3),'siPrefix': True, 'suffix': 'Hz','decimals':6})
        self.addChild({'name': 'nbr pts', 'type': 'int','value': 100, 'step': 100, 'limits': (10, 100e3),'siPrefix': False, 'tip':'number of points use for the frequecy sweep'})
        self.addChild({'name': 'nbr seqs', 'type': 'list','values':[1,2,3,4,5,6,7,8,9,10],'value': 1, 'tip':'number of sequences, number of time frequecy sweep is running'})
        self.addChild({'name': 'waiting time', 'type': 'list','values':[1,2,3,4,5,6,7,8,9,10],'value': 3, 'tip':'Time time between two measurements. It is equal to time cosntant multiply by this factor'})
        self.addChild({'name': 'start', 'type': 'action'})
        self.addChild({'name': 'average', 'type': 'action'})
        self.addChild({'name': 'clear all', 'type': 'action'})


    def remaning_time(self,value):
        self.param('remaning time').setValue(value)

class AcquisitionRD(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        freq_min = 30e3 #32.76e3
        freq_max = 34e3 # 32.78e3
        self.addChild({'name': 'excitation time', 'type': 'float','value': 100e-3, 'step': 10e3, 'limits': (100e-3, 10),'siPrefix': True, 'suffix': 's','decimals':3})
        self.addChild({'name': 'de-excitation time', 'type': 'float','value': 100e-3, 'step': 10e3, 'limits': (100e-3, 10),'siPrefix': True, 'suffix': 's','decimals':3})
        self.addChild({'name': 'nbr points', 'type': 'int','value': 100, 'step': 100, 'limits': (100, 100e3)})
        self.addChild({'name': 'start', 'type': 'action'})
        self.addChild({'name': 'clear all', 'type': 'action'})



class AllPlotScalableGroup(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        opts['type'] = 'group'
        opts['addText'] = "Add"
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChild({'name': 'path', 'type': 'str', 'value': path})

    def addNew(self):
        new = OneCurve(name="Curve_%d" % (len(self.childs)))
        new.param('file name').setValue("Curve %d.csv" % (len(self.childs)))
        self.addChild(new,dict(removable=True))

class FitRD(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        MonParametre.__init__(self) # get method from MonParametre
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild({'name': 'exponential fit', 'type': 'bool', 'value': False})
        self.addChild({'name': 'sinusoidal fit', 'type': 'bool', 'value': False})

class Generator(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        MonParametre.__init__(self) # get method from MonParametre
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild({'name': 'instrument', 'type': 'list', 'values': ['Virtual','Zurich-MFLI_dev4199'], 'value': 'Virtual'})
        self.addChild({'name': 'frequency', 'type': 'float','value': 10e3, 'step': 1e3, 'limits': (1, 500e3),'siPrefix': True, 'suffix': 'Hz','decimals':6})        
        self.addChild({'name': 'amplitude', 'type': 'float','value': 1e-3, 'step': 50e-3, 'limits': (0, 1),'siPrefix': True, 'suffix': 'V'})
        self.addChild({'name': 'on', 'type': 'bool', 'value': False, 'tip': "ON when it is checked"})

class Input(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):       
        MonParametre.__init__(self) # get method from MonParametre
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        time_cst = 50e-3 #100e-3 # time cst use for the acquisition
        self.addChild({'name': 'instrument', 'type': 'list', 'values': ['Virtual','Zurich-MFLI_dev4199'], 'value': 'Virtual'})
        self.addChild({'name': 'time constant', 'type': 'float','value': time_cst, 'step': 100e-3, 'limits': (time_cst, 10),'siPrefix': True, 'suffix': 's'})
        self.addChild({'name': 'recording time', 'type': 'float','value': 10e-3, 'step': 10e-3, 'limits': (10e-3, time_cst),'siPrefix': True, 'suffix': 's','tip':'data acquisition time, then averaged'})
        self.addChild({'name': 'sensitivity', 'type': 'list', 'values': [1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3], 'value': 1})

class LaserDopplerVibrometer(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):       
        MonParametre.__init__(self) # get method from MonParametre
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        self.addChild({'name': 'decoder', 'type': 'list','values':['Unknow','VD02','VD06'],'value': 'Unknow'})
        self.addChild({'name': 'sensitivity', 'type': 'list','values':['Unknow','2mm/s/V','10mm/s/V'],'value': 'Unknow'})

class LaserDriver(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):       
        MonParametre.__init__(self) # get method from MonParametre
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild({'name': 'instrument', 'type': 'list', 'values': ['Virtual','Thorlabs_LDC4005'], 'value': 'Virtual'})
        self.addChild({'name': 'remaning time', 'type': 'float', 'value': 'NaN', 'siPrefix': True, 'suffix': 's', 'readonly': True})
        self.addChild({'name': 'on', 'type': 'bool', 'value': False, 'tip': "ON when it is checked"})
        self.addChild({'name': 'current', 'type': 'float','value': 1e-3, 'step': 1e-3, 'limits': (1e-4, 50e-3),'siPrefix': True, 'suffix': 'A','decimals':6})
        self.addChild({'name': 'current min', 'type': 'float','value': 1e-3, 'step': 1e-3, 'limits': (1e-4, 50e-3),'siPrefix': True, 'suffix': 'A','decimals':6})
        self.addChild({'name': 'current max', 'type': 'float','value': 5e-3, 'step': 1e-3, 'limits': (1e-4, 50e-3),'siPrefix': True, 'suffix': 'A','decimals':6})
        self.addChild({'name': 'nbr pts', 'type': 'int','value': 100, 'step': 100, 'limits': (10, 100e3),'siPrefix': False, 'tip':'number of points use for the frequecy sweep'})
        self.addChild({'name': 'nbr seqs', 'type': 'list','values':[1,2,3,4,5,6,7,8,9,10],'value': 1, 'tip':'number of sequences, number of time frequecy sweep is running'})
        self.addChild({'name': 'waiting time', 'type': 'list','values':[1,2,3,4,5,6,7,8,9,10],'value': 3, 'tip':'Time time between two measurements. It is equal to time cosntant multiply by this factor'})
        self.addChild({'name': 'start', 'type': 'action'})
        self.addChild({'name': 'average', 'type': 'action'})
        self.addChild({'name': 'clear all', 'type': 'action'})

    def remaning_time(self,value):
        self.param('remaning time').setValue(value)

class OneCurve(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        opts['removable'] = True
        opts['renamable'] = True
        pTypes.GroupParameter.__init__(self, **opts)
        self.addChild({'name': 'file name', 'type': 'str', 'value': 'curve 1'})
        self.addChild({'name': 'color', 'type': 'color', 'value': "FF0", 'tip': "This is a color button"})

class Save(pTypes.GroupParameter,MonParametre):
    def __init__(self, **opts):
        opts['type'] = 'bool'
        opts['value'] = True
        pTypes.GroupParameter.__init__(self, **opts)

        path_info = 'test python code'
        sample_name = 'QTF'
        sample_info = 'vacuum'
        self.addChild({'name': 'path', 'type': 'str', 'value': path})
        self.addChild({'name': 'path info', 'type': 'str', 'value': path_info})
        self.addChild({'name': 'sample name', 'type': 'str', 'value': sample_name})
        self.addChild({'name': 'sample info', 'type': 'str', 'value': sample_info})
        self.addChild({'name': 'other information', 'type': 'text', 'value': 'Some text...'})
        self.addChild({'name': 'save', 'type': 'action'})    

##############################################################################
##############################################################################
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    ## Create tree of Parameter objects
    params = [Input(name='Input'),
              Generator(name='Generator'),
              AllPlotScalableGroup(name='Graph')]

    p = Parameter.create(name='params', type='group', children=params)

    ## Create two ParameterTree widgets, both accessing the same data
    t = ParameterTree()
    t.setParameters(p, showTop=False)
    t.setWindowTitle('pyqtgraph example: Parameter Tree')

    win = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    win.setLayout(layout)
    layout.addWidget(t, 1, 0, 1, 1)
    win.show()
    win.resize(800,800)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

##############################################################################
##############################################################################


#### OLD VERSION #########

# def build_dico(dico):

#   '''
#   This dictionary define all the parametre tree use for the GUI 
#   (graphic utilisator interface)
#   The dico here is use for the inital value
#   '''


#   p_global = [{'name': 'Input', 'type': 'group',
#                'children': [{'name': 'instrument', 'type': 'list', 'values': ['Virtual','Zurich-MFLI_dev4199'], 'value': dico['Input']['instrument']},
#                             {'name': 'time constant', 'type': 'float',
#                              'value': dico['Input']['time constant'], 'step': 100e-3, 'limits': (400e-9, 10),
#                              'siPrefix': True, 'suffix': 's'},
#                              {'name': 'recording time', 'type': 'float',
#                              'value': dico['Input']['recording time'], 'step': 10e-3, 'limits': (10e-3, dico['Input']['time constant']),
#                              'siPrefix': True, 'suffix': 's','tip':'data acquisition time, then averaged'},
#                              {'name': 'sensitivity', 'type': 'list', 'values': [1e-3,3e-3,1e-2,3e-2,1e-1,3e-1,1,3], 'value': dico['Input']['sensitivity']},
#                             ]},
#               {'name': 'Frequency sweep', 'type': 'group',
#                'children': [{'name': 'generator', 'type': 'group', 'children': [
#                             {'name': 'instrument', 'type': 'list', 'values': ['Virtual','Zurich-MFLI_dev4199'], 'value': dico['Frequency sweep']['generator']['instrument']},
#                             {'name': 'amplitude', 'type': 'float','value': dico['Frequency sweep']['generator']['amplitude'], 'step': 50e-3, 'limits': (0, 1),'siPrefix': True, 'suffix': 'V'},
#                             {'name': 'on', 'type': 'bool', 'value': dico['Frequency sweep']['generator']['on'], 'tip': "ON when it is checked"},
#                             ]},
#                             {'name': 'acquisition', 'type': 'group', 'children': [
#                             {'name': 'freq min', 'type': 'float',
#                              'value': dico['Frequency sweep']['acquisition']['freq min'], 'step': 10e3, 'limits': (1, 500e3),
#                              'siPrefix': True, 'suffix': 'Hz','decimals':6},
#                              {'name': 'freq max', 'type': 'float',
#                              'value': dico['Frequency sweep']['acquisition']['freq max'], 'step': 10e3, 'limits': (1, 500e3),
#                              'siPrefix': True, 'suffix': 'Hz','decimals':6},
#                              {'name': 'nbr pts', 'type': 'int',
#                              'value': dico['Frequency sweep']['acquisition']['nbr pts'], 'step': 100, 'limits': (10, 100e3),
#                              'siPrefix': False, 'tip':'number of points use for the frequecy sweep'},
#                              {'name': 'nbr seqs', 'type': 'list','values':[1,2,3,4,5,6,7,8,9,10],
#                              'value': dico['Frequency sweep']['acquisition']['nbr seqs'], 'tip':'number of sequences, number of time frequecy sweep is running'},
#                              {'name': 'waiting time', 'type': 'list','values':[1,2,3,4,5,6,7,8,9,10],
#                              'value': dico['Frequency sweep']['acquisition']['waiting time'], 'tip':'Time time between two measurements. It is equal to time cosntant multiply by this factor'},
#                              {'name': 'start', 'type': 'action'},
#                              {'name': 'average', 'type': 'action'},
#                              {'name': 'clear all', 'type': 'action'}
#                              ]}
#                           ]},
#               {'name': 'Save', 'type': 'group',
#                'children': [{'name': 'path', 'type': 'str', 'value': dico['Save']['path']},
#                             {'name': 'path info', 'type': 'str', 'value': dico['Save']['path info']},
#                             {'name': 'sample name', 'type': 'str', 'value': dico['Save']['sample name']},
#                             {'name': 'sample info', 'type': 'str', 'value': dico['Save']['sample info']},
#                             {'name': 'save', 'type': 'action'}                 
#                           ]}
#               ]
#   return p_global