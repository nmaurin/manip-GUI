# 20200130 - Correction dico beug for the class ZurichMFLIdev4199

import numpy as np
import zhinst.ziPython
import pyvisa


def close_all_inst():
    # close all the instrument
    pass

def noisy_lorentzian_function(freq, amp, freq0, Q):
    '''
    Allow to draw calculted a Lorentzian profil. 
    Return the amplitude of dispacement of a forced excitation,
    and the phase between the resonator displacement and actuation force  
    And add noise on the frequency
    
    Prarameters
    -----------
    freq : Pulsation of the excitation
    amp : Amplitude      
    freq0 : Resonance frequency
    Q : quality factor      

    Return
    ------
    Return the amplitude of dispacement of a forced excitation,
    and the phase between the resonator displacement and actuation force       

    '''
    # add noise on the frequency
    freq = freq*(1+np.random.normal(0,2e-4,1))
    omega = 2*np.pi*freq
    omega0 = 2*np.pi*freq0
    xi=1/2/Q
    # Calculate amplitude and phase
    R = amp / np.sqrt((omega0**2 - omega**2)**2 
            + (2 * xi * omega * omega0)**2)
    Phi = np.arctan((omega/omega0/Q)/(1-(omega/omega0)**2)) # in radians
    return R, Phi

class Instrument():

    def __init__(self,name=None):
        # name of the instrument
        self.name = name
        # object from the specific class of the instrument
        self.inst_obj = None
        if self.name == 'Virtual':
            self.inst_obj = Virtual()
        if self.name == 'Zurich-MFLI_dev4199':
            self.inst_obj = ZurichMFLIdev4199()
        if self.name == 'Thorlabs_ITC4002QCL':
            self.inst_obj = ThorlabsITC4002QCL()

    def set_value(self,what,value):
        '''
        Give the value 'value' to the parameter 'what' on the instrument
        '''
        self.inst_obj.set_value(what,value)

    def poll(self,poll_length=0.01):
        # poll_length = recording time
        return self.inst_obj.poll(poll_length=0.01)
        
    def disconnect(self):
        pass


class ThorlabsITC4002QCL():
    # laser Driver with USB connection
    def __init__(self):
        self.daq = self.connect() 

    def connect(self):
        #identification de l'instrument
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        inst = rm.open_resource('USB0::0x1313::0x804A::M00560075::INSTR')
        print('Device Thorlabs-ITC4002QCL IDN is %s'%(self.IDN()))
        return inst

    def IDN(self):
        time.sleep(0.1)
        self.daq.write("*CLS")
        return self.daq.query("*IDN?")

    def set_value(self,what,value):
        inst = self.daq
        if 'on' in what:
            if value == True:
                inst.write("LAS:OUTPUT ON")
            if value == False:
                inst.write("LAS:OUTPUT OFF")
        if 'current' in what:
            inst.write("SOUR:CURR "+str(value))
            inst.write("SOUR:CURR "+str(value))
            
    def poll(self):
        inst = self.daq
        #inst.write("SOUR:CURR?")
        time.sleep(0.1)
        a = float(inst.query("SOUR:CURR?"))*1000
        return int(a)

class Virtual():

    def __init__(self):
        self.daq = self.connect()
        self.freq = None
        self.current = None

    def connect(self):
        daq = None
        return daq

    def set_value(self,what,value):
        '''
        Give the value 'value' to the parameter 'what' on the instrument
        '''
        # print('Virtual instrument : %s has been changed to %s' %(what,str(value)))
        if what in 'frequency':
            self.freq = value
        if what in 'current':
            self.freq = value

    def poll(self,poll_length=0.01):
        # poll_length = recording time
        R = np.random.normal(0,1,1)
        Phi = np.random.normal(-90,90,1)
        # R, Phi = noisy_lorentzian_function(self.freq,1,32e3,1000)
        X = R*np.cos(Phi)
        Y = R*np.sin(Phi)
        Phi = Phi*180/np.pi # convert phi in degre
        return [X,Y,R,Phi]


class ZurichMFLIdev4199():
    def __init__(self):
        self.daq = None
        self.connect()

    def connect(self):
        '''
        Use Device Discovery to find the ip adress and the port 
        of the device called dev
        '''
        dev = 'dev4199' #name of the device
        d = zhinst.ziPython.ziDiscovery()
        d.find(dev)
        devProp = d.get(dev)
        #print (devProp)
        print('Device Zurich-%s adress is %s'%(dev,devProp['serveraddress']))
        print('Device Zurich-%s port is %s'%(dev,devProp['serverport']))
        # Create a connection to the data server
        apilevel = 6 # allow timestamp support in poll (cf LabOneProgrammingManual page 16)
        #daq = data acquistion system adress
        self.daq = zhinst.ziPython.ziDAQServer(devProp['serveraddress'],devProp['serverport'], apilevel)
        # switch on the output signal 
        self.daq.setInt('/dev4199/sigouts/0/on', 1)
        # get ready for data acquisition
        self.poll_subscribe()


    def disconnect(self):
        self.poll_unsubscribe()

    def poll_subscribe(self):
        # Subscribe to the demodulator's sample node path.
        # If not done the poll function return a empty data
        # Unsubscribe from all paths.
        self.daq.unsubscribe('*')
        dev = 'dev4199'
        demod_index = 0
        path = '/%s/demods/%d/sample' % (dev, demod_index)
        self.daq.subscribe(path)

    def poll_unsubscribe(self):
        self.daq.unsubscribe('*')  

    def set_value(self,what,value):
        '''
        change value on zurich
        '''
        if 'frequency' in what:
            self.daq.setDouble('/dev4199/oscs/0/freq', value)
        if 'amplitude' in what:
            self.daq.setDouble('/dev4199/sigouts/0/amplitudes/1', value)
        if 'on' in what:
            if value == True:
                self.daq.setInt('/dev4199/sigouts/0/enables/1', 1)
            if value == False:
                self.daq.setInt('/dev4199/sigouts/0/enables/1', 0)        
        if 'sensitivity' in what:  
            self.daq.setDouble('/dev4199/sigins/0/range', value)
        if 'time constant' in what:
            self.daq.setDouble('/dev4199/demods/0/timeconstant', value)         

    def poll(self,poll_length = 0.01,poll_timeout = 500):
        ##############################################################################
        #-                   Get data  - POLL function                              -#
        ##############################################################################
        # POLL Continuously check for value changes (by calling pollEvent) in all
        # subscribed nodes for the specified duration and return the data. If
        # no value change occurs in subscribed nodes before duration + timeout,
        # poll returns no data.
        # poll_length = 0.1 # recording time in [s]. The function will block during that time
        # poll_timeout = 500 # Timeout in [ms]. Recommanded 500 ms. The timeout parameter is only
               # relevant when communicating in a slow network. In this case it may be
               # set to a value larger than the expected round-trip time in the
               # network.

        # don't forget to use the function poll_subscribe() before
        # if not done the poll function return a empty data
        dev = 'dev4199'
        demod_index = 0
        data = self.daq.poll(poll_length, poll_timeout)
        x = data[dev]['demods'][str(demod_index)]['sample']['x']
        y = data[dev]['demods'][str(demod_index)]['sample']['y']
        r = np.abs(x + 1j*y)
        phi = np.angle(x + 1j*y,deg=True)
        return [np.mean(x),np.mean(y),np.mean(r),np.mean(phi)]

# x = Instrument('Virtual')
# print(x.name)    
# print(x.inst_obj)   
if __name__ == "__main__":
    ma_thorlabs = ThorlabsITC4002QCL()
    ma_thorlabs.set_value('on', True)
    start = 1
    end = 30
    step = 1
    for i in range (start, end, step): 
        ma_thorlabs.set_value('current', i)
        print("Current : {} mA".format(ma_thorlabs.poll()))

    for j in range (end, start, step):
        ma_thorlabs.set_value('current', j)
        print("Current : {} mA".format(ma_thorlabs.poll())) 
    pass
