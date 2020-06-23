import numpy as np
import time
import pandas #to write csv file
import os  #to create folder
import matplotlib.pyplot as plt
import matplotlib

def find_nearest_index(array, a0):
    '''
    Return index of element in array closest to the scalar value a0

    Parameters
    ----------
    array : list
        A list of number
    a0 : flot
        The targeted value

    Return
    ------
    idx : integer
        The index of the closest value of a0
    '''
    array = np.asarray(array)
    idx = np.abs(array - a0).argmin()
    return idx

def find_nearest(array, a0):
    '''
    Return the element in an array closest to the scalar value a0

    Parameters
    ----------
    array : list
        A list of number
    a0 : flot
        The targeted value

    Return
    ------
    x : float
        The index of the closest value of a0
    '''
    x = min(array, key=lambda x:abs(x-a0))
    return x   


def save_FS(param,courbes):
    # save function deidcated to Frequency Sweep 
    today = time.strftime("%Y%m%d")
    name = param.dico['Save']['sample name']
    path_info = param.dico['Save']['path info']
    sample_info = param.dico['Save']['sample info']
    path = param.dico['Save']['path'] + '_'.join([today,name,path_info]) + '/'
    freq = '%2.0f-%2.0fkHz'%(param.dico['Acquisition']['freq min']/1e3,param.dico['Acquisition']['freq max']/1e3)   
    file_name = path + '_'.join([name,sample_info,freq]) 

    # if don't exist create the directory
    if not os.path.exists(path):
        os.makedirs(path)

    # save csv file with all the data
    data = pandas.DataFrame({'Frequency (Hz)': courbes.curves['curve 0']['data']['freq'],
                'x (Vrms)': courbes.curves['curve 0']['data']['X'],
                'y (Vrms)': courbes.curves['curve 0']['data']['Y'],
                'r (Vrms)': courbes.curves['curve 0']['data']['R'],
                'phase (deg)': courbes.curves['curve 0']['data']['Phi']})
    data.to_csv(file_name +'.csv', sep=' ', encoding='utf-8') 

    # save a txt file with all the parameter
    info = open(file_name+'.txt','w')
    info.write(time.strftime("%Y-%m-%d")+' '+time.strftime("%H:%M:%S")+ '\n')
    info.write('\n')   
    for k in param.dico:
        info.write(k+'\n')
        info.write(param.dico[k].child_list())
    info.close()

def save_PA(param,courbes):
    # save function deidcated to Frequency Sweep 
    today = time.strftime("%Y%m%d")
    name = param.dico['Save']['sample name']
    path_info = param.dico['Save']['path info']
    sample_info = param.dico['Save']['sample info']
    path = param.dico['Save']['path'] + '_'.join([today,name,path_info]) + '/'
    freq = '%.0f-%.0fmA'%(param.dico['Laser Driver']['current min']*1e3,param.dico['Laser Driver']['current max']*1e3)   
    file_name = path + '_'.join([name,sample_info,freq]) 

    # if don't exist create the directory
    if not os.path.exists(path):
        os.makedirs(path)

    # save csv file with all the data
    data = pandas.DataFrame({'current (mA)': courbes.curves['curve 0']['data']['Current'],
                'x (Vrms)': courbes.curves['curve 0']['data']['X'],
                'y (Vrms)': courbes.curves['curve 0']['data']['Y'],
                'r (Vrms)': courbes.curves['curve 0']['data']['R'],
                'phase (deg)': courbes.curves['curve 0']['data']['Phi']})
    data.to_csv(file_name +'.csv', sep=';', encoding='utf-8') 

    # save a txt file with all the parameter
    info = open(file_name+'.txt','w')
    info.write(time.strftime("%Y-%m-%d")+' '+time.strftime("%H:%M:%S")+ '\n')
    info.write('\n')   
    for k in param.dico:
        info.write(k+'\n')
        info.write(param.dico[k].child_list())
    info.close()
    
## Conversion of the current value in wavelenght (nm) for laser Eblana 2
def convert_wavelenght(current, temperature):
    if temperature == 15:
        return 1651.765+0.0145*current
    elif temperature == 20:
        return 1652.035+0.0155*current
    elif temperature == 25:
        return 1652.4075+0.01575*current
    else:
        return 1652.035+0.0155*current

# def save_figure(dico):
#     # save figure
#     fig, ax = plt.subplots(figsize=(12, 8),dpi=100) # = w*dpi, h*dpi
#     ax.plot(dico['Data']['FREQ']/1e3,dico['Data']['R']
#             ,marker='.',linewidth=2,label='magnitude',color='b')
#     ax.grid(b=True, which='major', color='#D3D3D3', linestyle='-')
#     formatter = matplotlib.ticker.FormatStrFormatter('%g')
#     ax.yaxis.set_major_formatter(formatter)
#     ax.tick_params(axis='both', which='major', labelsize=14)
#     ax.set_xlabel('Frequency (kHz)', labelpad=5, fontsize=18)
#     ax.set_ylabel('Amplitude (Vrms)', labelpad=5, fontsize=18)
#     ax.legend(loc=0)
#     plt.title(name + ' ' + sample_info)
#     fig.savefig(file_name+'.png', dpi=fig.dpi)
#     plt.show()
#     # ?? rajouter plt.close()



def create_frequency_list(dico):
    '''
    Create a array with all the frequency use for the frequency sweep
    It take into account if many sequences have been asked
    '''
    dico['Data']['FREQ'] = np.linspace(
            dico['Frequency sweep']['acquisition']['freq min'],
            dico['Frequency sweep']['acquisition']['freq max'],
            dico['Frequency sweep']['acquisition']['nbr pts'])
    if dico['Frequency sweep']['acquisition']['nbr seqs'] == 1:
        return dico
    else:
        temp = dico['Data']['FREQ']
        i=0
        while i < int(dico['Frequency sweep']['acquisition']['nbr seqs'])-1:
            i+=1
            dico['Data']['FREQ'] = np.append(dico['Data']['FREQ'],temp[::(-1)**i])
        return dico

def average(ARRAY,ns):
    '''
    Cut the long array list with all its sequence
    in array, one array by frequency sweep.
    And return only one array which is the average of all the array.
    --------
    ARRAY a list of number
    ns the number of sequence
    '''
    i=0
    nv = len(ARRAY)
    LIST_OF_ARRAY=[]
    while i <=ns-1:
        i+=1
        TEMP = ARRAY[int(nv/ns)*(i-1):int(nv/ns)*i]
        TEMP = TEMP[::(-1)**(i+1)]
        LIST_OF_ARRAY.append(TEMP)
    #print(LIST_OF_ARRAY)    
    MEAN = np.mean(LIST_OF_ARRAY,axis=0)
    #print(MEAN)
    return MEAN


# def sequence_average(dico):
#     '''
#     Cut the long array list with all its sequence
#     in array, one array by frequency sweep.
#     And return only one array which is the average of all the array.
#     '''
#     ns = dico['Frequency sweep']['acquisition']['nbr seqs']
#     def average(ARRAY):
#         i=0
#         nv = len(ARRAY)
#         LIST_OF_ARRAY=[]
#         while i <=ns-1:
#             i+=1
#             TEMP = ARRAY[int(nv/ns)*(i-1):int(nv/ns)*i]
#             TEMP = TEMP[::(-1)**(i+1)]
#             LIST_OF_ARRAY.append(TEMP)
#         #print(LIST_OF_ARRAY)    
#         MEAN = np.mean(LIST_OF_ARRAY,axis=0)
#         #print(MEAN)
#         return MEAN
#     for k in dico['Data']:
#         dico['Data'][k] = average(dico['Data'][k])
#     return dico



##############################################################################
###############  TESTING ZONE               ##################################
############################################################################## 
 
