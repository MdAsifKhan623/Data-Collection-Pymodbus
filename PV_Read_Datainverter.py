# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 12:09:05 2020

@author: mdasi
"""
import time,os,csv
from datetime import datetime
from pytz import timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.constants import Defaults
from firebase import firebase
Defaults.RetryOnEmpty=True
Defaults.Timeout=5
Defaults.Retries=5
energyToday=0
# firebaseConn=firebase.FirebaseApplication('https://pvinverterdata.firebaseio.com/',None)
data={
    'Name':'PvInverterData',
    'batteryTemperature':0,
    'chargedVoltage':0,
    'inverterTemp':0
}
eastern=timezone('US/Eastern')
fmt='%Y-%m-%d %H:%M:%S %Z%z'
local_time=eastern.localize(datetime.now())
current_time=local_time.strftime(fmt)
PVinverterData={"AmbientTemperature":"","EnergyToday":"","GridCurrent":"","DcModuleTemperature":"",
                "InverterModuleTemperature":"","PVVoltage":"","PVcurrent":"","PVPower":"", "Timestamp":""}

#result=firebaseConn.post('/DataOfPV/',data)
#print(result)
def getPvData():
    
    client=ModbusClient(method='rtu',port='COM1',timeout=2,stopbits=1,bytesize=8,parity='N',baudrate=9600,strict= False)
    client.connect()
    

    while True:
        try:
            hh = client.read_holding_registers(address=245, count=8, unit=1);
            fterm=1
            inverterTemp = hh.registers[7] / 10
            batteryTemp = hh.registers[0] / 10
            hd = client.read_holding_registers(address=223, count=1, unit=1);
            chargedVoltage = hd.registers[0] / 10
            energy=client.read_holding_registers(address=42052,count=2, unit=1)
            energyToday=energy.registers[0]/10
            PVinverterData["EnergyToday"]=str(energyToday)
            
            ambTmpReg=client.read_holding_registers(address=45889, count=1,unit=1)
            ambTemperature=ambTmpReg.registers[0]/10
            PVinverterData["AmbientTemperature"]=str(ambTemperature)
            
            gridCurrentReg=client.read_holding_registers(address=45893, count=1,unit=1)
            gridcurrent=gridCurrentReg.registers[0]/10
            PVinverterData["GridCurrent"]=str(gridcurrent)
            
            dcModuleTemperatureReg=client.read_holding_registers(address=45890, count=1,unit=1)
            dcmoduleTemp=dcModuleTemperatureReg.registers[0]/10
            PVinverterData["DcModuleTemperature"]=str(dcmoduleTemp)
            
            inverterModuleTempReg=client.read_holding_registers(address=45894, count=1,unit=1)
            inverterTemp=inverterModuleTempReg.registers[0]/10
            PVinverterData["InverterModuleTemperature"]=str(inverterTemp)
            
            pvVoltageReg=client.read_holding_registers(address=56143, count=1,unit=1)
            pvVoltage=pvVoltageReg.registers[0]/10
            PVinverterData["PVVoltage"]=str(pvVoltage)
            
            pvCurrentReg=client.read_holding_registers(address=56144, count=1,unit=1)
            pvCurrent=pvCurrentReg.registers[0]/10
            PVinverterData["PVcurrent"]=str(pvCurrent)
            
            pvPowerReg=client.read_holding_registers(address=56145, count=1,unit=1)
            pvPower=pvPowerReg.registers[0]/10
            PVinverterData["PVPower"]=str(pvPower)
            
            PVinverterData["Timestamp"]=str(current_time)     
        except Exception as e:
            print(e)
def getCSVData(csv_file,dict_data_list,csv_columns):
    exists=os.path.isfile(os.getcwd()+"InverterData.csv") 
    global filecsv
    if exists:
        with open(os.getcwd()+"InverterData.csv") as f:
            filecsv=csv.reader(f)
            count=0
            for line in filecsv:
                #print(line)
                if len(line)==0:
                    continue
                else:
                    if count>0:
                        new_dict={"AmbientTemperature":"","EnergyToday":"","GridCurrent":"","DcModuleTemperature":"",
                "InverterModuleTemperature":"","PVVoltage":"","PVcurrent":"","PVPower":"", "Timestamp":""}
                        new_dict["AmbientTemperature"]=line[0]
                        new_dict["EnergyToday"]=line[1]
                        new_dict["GridCurrent"]=line[2]
                        new_dict["DcModuleTemperature"]=line[3]
                        new_dict["InverterModuleTemperature"]=line[4]
                        new_dict["PVVoltage"]=line[5]
                        new_dict["PVcurrent"]=line[6]
                        new_dict["PVPower"]=line[7]
                        new_dict["Timestamp"]=line[8]
                        dict_data_list.append(new_dict)
            try:
                '''writing the current as well as previous datas to csv file'''
                
                with open(csv_file, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    #writer=csv.writer(csvfile)
                    
                    writer.writeheader()
                    for data in dict_data_list:
                        #print(data)
                        writer.writerow(data)
                    
            
            except (IOError,OSError) :
                print("IOError/OSError")
    else:
        
        try:
            with open(csv_file,'w') as csvfile:
                writer=csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for data in dict_data_list:
                    writer.writerow(data)
        except(IOError,OSError):
            print("IOError/OSError")
    return 
                    
current_path=os.getcwd()
csv_file=current_path+"InverterData.csv"
dict_data_list=[PVinverterData]
csv_columns=["AmbientTemperature","EnergyToday","GridCurrent","DcModuleTemperature",
                "InverterModuleTemperature","PVVoltage","PVcurrent","PVPower", "Timestamp"]
getPvData()
getCSVData(csv_file,dict_data_list,csv_columns)

    


