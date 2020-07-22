import numpy as np
import configparser
from os.path import join, basename, dirname, splitext, abspath
from os import walk, listdir


class ConfigParameters:
    
    def __init__(self, filename):
        self.config = configparser.ConfigParser()
        self.read_config(filename)
    

    def read_config(self, filename):
        self.config.read(filename)
        parameters = {}
        
        for mainkey in self.config.sections():
            for subkey in self.config[mainkey]:
                parameters.update({subkey:self.config[mainkey][subkey]})
                print(subkey,':',self.config[mainkey][subkey])
        
        
        self.set_config(parameters)
        
    
    
    def set_config(self, parameters):
        # Setting
        self.mbcomport = parameters['mbcomport']
        self.baudrate = int(parameters['baudrate'])
        self.databit = int(parameters['databit'])
        self.parity = parameters['parity']
        self.stopbit = int(parameters['stopbit'])
        self.mbtimeout = int(parameters['mbtimeout'])
        self.mbid = int(parameters['mbid'])
        
        #Control
        self.angles = [int(ang) for ang in parameters['angles'].split(',')]
        self.motor_rot_speed = int(parameters['motor_rot_speed'])
        
        
        
        

if __name__ == "__main__":
    param = ConfigParameters('plc.ini')
    print(param.angles)
    
    
