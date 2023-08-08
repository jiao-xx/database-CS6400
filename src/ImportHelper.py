import sys
from flaskext.mysql import MySQL
from AppHelper import AppHelper
from HouseholdFormHelper import HouseholdFormHelper
from ApplianceFormHelper import ApplianceFormHelper

class ImportHelper:
    
  def import_household(mysql, filePath):
    line_count = 1
    with open(filePath) as file:
      for line in file:

        if line_count == 1:
            line_count = line_count +1
            continue

        h = line.split('\t')
        print("-" *22)
        #email	household_type	footage	heating_temp	cooling_temp	postal_code	utilities
        #INSERT INTO Household (Email, SquareFootage, HouseholdType, HeatingSetting, CoolingSetting, PostalCode)

        email = h[0]
        householdType = h[1]
        squareFootage = h[2]
        heatingSetting = None if not h[3] else h[3]
        coolingSetting = None if not h[4] else h[4]
        postalCode = h[5]
        publicUtilities = [x.strip() for x in h[6].split(',')]
        
        HouseholdFormHelper.insert_household(mysql,
        email,
        squareFootage,
        householdType,
        heatingSetting,
        coolingSetting,
        postalCode
        )
        
        householdID = HouseholdFormHelper.get_household_id(mysql, email)
        if publicUtilities and len(publicUtilities) > 0:
            HouseholdFormHelper.insert_household_utilities(mysql, householdID, publicUtilities)

     
  #household_email	power_number	energy_source	kilowatt_hours	battery
  def import_power(mysql, filePath):
    line_count = 1

    with open(filePath) as file:
      for line in file:

          if line_count == 1:
              line_count = line_count +1
              continue

          h = line.split('\t')

          email = h[0]
          orderNumber = h[1]
          generationType = h[2]
          avgKwh = h[3]
          batteryStorageCapacity = None if not h[4].strip() else h[4]

          householdID = HouseholdFormHelper.get_household_id(mysql, email)
          AppHelper.insert_power_generator(mysql, householdID, avgKwh, batteryStorageCapacity, generationType, orderNumber)

  #household_email	appliance_number	manufacturer_name	model	appliance_type	energy_source	air_handler_types	rpm	eer	hspf	seer	tank_size	temperature	btu
  def import_appliance(mysql, filePath):
    line_count = 1
    with open(filePath) as file:
      for line in file:

        if line_count == 1:
            line_count = line_count +1
            continue
        
        h = line.split('\t')

        email = h[0]
        appliance_number = h[1]
        manufacturer_name = h[2]
        model= None if not h[3].strip() else h[3]
        appliance_type= h[4]
        energy_source = None if not h[5].strip() else h[5]
        air_handler_types = None if not h[6].strip() else h[6]
        air_handler_rpm	= None if not h[7].strip() else h[7]
        air_conditioner_eer	= None if not h[8].strip() else h[8]
        heat_pump_hspf	= None if not h[9].strip() else h[9]
        heat_pump_seer	= None if not h[10].strip() else h[10]
        water_heater_tank_size	= None if not h[11].strip() else h[11]
        water_heater_temperature= None if not h[12].strip() else h[12]
        appliance_btu= h[13].strip()

        householdID = HouseholdFormHelper.get_household_id(mysql, email)

        if appliance_type == 'air_handler':
          ApplianceFormHelper.insert_air_handler(
              mysql, 
              householdID, 
              manufacturer_name, 
              appliance_btu, 
              model, 
              air_handler_rpm, 
              air_conditioner_eer, 
              energy_source,
              heat_pump_seer,
              heat_pump_hspf,
              air_handler_types,
              appliance_number
              )
    
        elif appliance_type == 'water_heater':

          ApplianceFormHelper.insert_water_heater(
              mysql, 
              householdID, 
              manufacturer_name, 
              appliance_btu, 
              model, 
              energy_source, 
              water_heater_tank_size, 
              water_heater_temperature,
              appliance_number)

        print(f'h: {h}', file=sys.stdout) 
        #publicUtilities = [x.strip() for x in h[6].split(',')]