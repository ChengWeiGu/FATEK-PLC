#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
import numpy as np
import time
import sys

from ConfigReader import ConfigParameters



class FATEK_PLC():
    
    def __init__(self):
        
        self.config_params = ConfigParameters("plc.ini")
        
        self.M100_addr = 100 + 2000 # calibration button
        self.M201_addr = 201 + 2000 # calibration state
        self.D500_addr = 500 + 6000 # plc memory for angles
        self.D501_addr = 501 + 6000 # plc memory for angles
        self.M500_addr = 500 + 2000 # rotation button
        self.M237_addr = 237 + 2000 # rotation state
        self.R20_addr = 20 # plc memory for mortor speed
        
        
    def connect_plc(self):
        
        self.mb_port = serial.Serial(port=self.config_params.mbcomport, baudrate=self.config_params.baudrate, bytesize=self.config_params.databit, 
                                     parity=self.config_params.parity, stopbits=self.config_params.stopbit)
        
        self.master = modbus_rtu.RtuMaster(self.mb_port)
        self.master.set_timeout(self.config_params.mbtimeout/1000.0)
        self.master.set_verbose(True)
        
        self.motor_speed = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_REGISTER , self.R20_addr , output_value=self.config_params.motor_rot_speed)
        
    
        
    def start_calibration(self):
        
        self.connect_plc()
        
        try:
            
            zero_end = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_COIL , self.M201_addr, output_value = 0)
            
            start = self.master.execute(slave = self.config_params.mbid, function_code = cst.WRITE_SINGLE_COIL , 
                                        starting_address = self.M100_addr, output_value = 1)
            print("M100 calibration state = ", start)

            time.sleep(1)
            
            zero_start = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_COIL , self.M100_addr , output_value = 0)
            print("M100 calibration state = ", zero_start)

            while True:
                end = self.master.execute(self.config_params.mbid, cst.READ_COILS , self.M201_addr, 1)
                print("M201 calibration state = ",  end)
                time.sleep(1)
                if end[0] == 1:
                    print("calibration finished!")
                    break
        
        except Exception as e:
            print("modbus test Error: " + str(e))


        self.master._do_close()
        
    
        
    def start_multirot(self):
        
        self.connect_plc()
        
        val_D500 = 0
        val_D501 = 0
        
        print("start multi-rotation...")
        for angle in self.config_params.angles:
            time.sleep(0.5)
            
            if angle >= 0: # positive angle >= 0
                val_D500 = 100*angle
                val_D501 = 0
        
            else: # negative angle < 0
                val_D500 = 65535 + 100*angle
                val_D501 = 65535
                      
            try:
                angle_write_D500 = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_REGISTER  , self.D500_addr , output_value=val_D500)
                angle_write_D501 = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_REGISTER  , self.D501_addr , output_value=val_D501)
                
                start = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_COIL  , self.M500_addr , output_value=1)
                
                # angle_read = self.master.execute(self.config_params.mbid, cst.READ_HOLDING_REGISTERS , self.D500_addr , 1)
                # print("D500_addr value= ",  angle_read)
                
                # start = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_COIL  , self.M500_addr , output_value=1)
                # print("M500_addr value= ",  start)
                
                while True:

                    state = self.master.execute(self.config_params.mbid, cst.READ_COILS  , self.M237_addr, 1)
                    if state[0] == 1:
                        print("Now at {} degrees".format(angle))
                        break
            
            except Exception as e:
                print("modbus test Error: " + str(e))

        
        self.master._do_close()
        print("end of multi-rotation")
        
    
    
    
    def start_single_rot(self, angle):
        
        self.connect_plc()
        
        val_D500 = 0
        val_D501 = 0
        
        if angle >= 0: # positive angle >= 0
            val_D500 = 100*angle
            val_D501 = 0
        
        else: # negative angle < 0
            val_D500 = 65535 + 100*angle
            val_D501 = 65535
        
        try:
            angle_write_D500 = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_REGISTER  , self.D500_addr , output_value=val_D500)
            angle_write_D501 = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_REGISTER  , self.D501_addr , output_value=val_D501)
            
            start = self.master.execute(self.config_params.mbid, cst.WRITE_SINGLE_COIL  , self.M500_addr , output_value=1)

            while True:

                state = self.master.execute(self.config_params.mbid, cst.READ_COILS  , self.M237_addr, 1)
                if state[0] == 1:
                    print("Now at {} degrees".format(angle))
                    break
                    
            
        except Exception as e:
            print("modbus test Error: " + str(e))
            
        
        self.master._do_close()
        
        if state[0] == 1:
            return True
        else:
            return False
        
    

def main():
    # create plc and do calibration
    plc = FATEK_PLC()
    plc.start_calibration()
    # plc.start_calibration() # second time of calibration which is unnecessary
    
    # change angles\mortor-speed and do multi-rotation
    plc.config_params.set_config({'mbcomport': 'COM4', 'baudrate': '19200', 'databit': '8', 'parity': 'E', 'stopbit': '1', 
                                  'mbtimeout': '100', 'mbid': '2', 'angles': '-180,-30,30,0', 'motor_rot_speed': '5000'})
    
    plc.start_multirot()
    
    # change the mortor-speed only and do twice rotation
    plc.config_params.motor_rot_speed = 2000
    res = plc.start_single_rot(-60)
    plc.config_params.motor_rot_speed = 4000
    res = plc.start_single_rot(0)
    print(res)



if __name__ == "__main__":
    main()
    
    
    
