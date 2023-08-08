import sys
from flaskext.mysql import MySQL
from AppHelper import AppHelper

class ApplianceFormHelper:
    
  def get_manufacturers(mysql):

    query = 'SELECT ManufacturerName FROM Manufacturer;'
    cursor = mysql.get_db().cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results

  def get_household_appliances(mysql, householdID):
    query = """
          SELECT a.ApplianceID, 'Water Heater' as Type, a.ManufacturerName, a.ModelName, a.OrderNumber FROM WaterHeater w, Appliance a
          WHERE w.ApplianceID = a.ApplianceID and a.HouseholdID = %s
          UNION
          SELECT a.ApplianceID, 'Air Handler' as Type, a.ManufacturerName, a.ModelName, a.OrderNumber FROM AirHandler ah, Appliance a
          WHERE ah.ApplianceID = a.ApplianceID and a.HouseholdID = %s
          
        """
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [householdID,householdID])
    
    results = cursor.fetchall()
    cursor.close()

    return results

  def insert_water_heater(mysql, householdID, manufacturerName, btus, modelName, energySource, tankSize, currentTempSetting, orderNumber=None):

    if orderNumber == None:
      orderNumber = AppHelper.get_appliance_next_order_number(mysql, householdID)

    # insert appliance and get the ID
    applianceID = AppHelper.insert_appliance(mysql, householdID, orderNumber, manufacturerName, modelName, btus)
    
    query ='''
    INSERT INTO WaterHeater (ApplianceID, TankSize, CurrentTempSetting, EnergySource) 
    VALUES (%s,%s,%s,%s)
    '''

    cursor = mysql.get_db().cursor()
    values = (
      applianceID,
      tankSize,
      currentTempSetting,
      energySource
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      return True
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False
    
  def insert_air_handler(mysql, householdID, manufacturerName, btus, modelName, fanRpms, eer, heaterEnergySource, seer, hspf, heatingCoolingTypes, orderNumber=None):

    if orderNumber == None:
      orderNumber = AppHelper.get_appliance_next_order_number(mysql, householdID)

    # insert appliance and get the ID
    applianceID = AppHelper.insert_appliance(mysql, householdID, orderNumber, manufacturerName, modelName, btus)
    
    query ='''
    INSERT INTO AirHandler (Rpm, ApplianceID) VALUES (%s,%s);
    '''

    cursor = mysql.get_db().cursor()
    values = (
      fanRpms,
      applianceID
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      airhandlerID = cursor.lastrowid

      # insert heater
      if 'Heater' in heatingCoolingTypes or 'heater' in heatingCoolingTypes:
        ApplianceFormHelper.insert_heater(mysql, heaterEnergySource, airhandlerID)
      
      # insert air conditioner
      if 'Air conditioner' in heatingCoolingTypes or 'air_conditioner' in heatingCoolingTypes:
        ApplianceFormHelper.insert_air_conditioner(mysql, eer, airhandlerID)

      # insert heat pump
      if 'Heat pump' in heatingCoolingTypes or 'heatpump' in heatingCoolingTypes:
        ApplianceFormHelper.insert_heatpump(mysql, seer, hspf, airhandlerID)

      return True
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False

  def insert_heater(mysql, heaterEnergySource, airhandlerID):

    query ='''
    INSERT INTO Heater (EnergySource, AirHandlerID) VALUES (%s, %s);
    '''

    cursor = mysql.get_db().cursor()
    values = (
      heaterEnergySource,
      airhandlerID
    )

    test="""
    test %s
    """
    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      return True
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False


  def insert_heatpump(mysql, seer, hspf, airhandlerID):

    query ='''
    INSERT INTO HeatPump (SEER, HSPF, AirHandlerID) VALUES (%s, %s, %s);
    '''

    cursor = mysql.get_db().cursor()
    values = (
      seer,
      hspf,
      airhandlerID
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      return True
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False
    
  def insert_air_conditioner(mysql, eer, airhandlerID):

    query ='''
    INSERT INTO AirConditioner (EER, AirHandlerID) VALUES (%s, %s);
    '''

    cursor = mysql.get_db().cursor()
    values = (
      eer,
      airhandlerID
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      return True
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False

  def delete_appliance(mysql, applianceID):

    query ='''
    DELETE FROM Appliance WHERE ApplianceID = %s;
    '''

    cursor = mysql.get_db().cursor()

    cursor.execute(query, [applianceID])
    mysql.get_db().commit()
    
    return True if cursor.rowcount == 1 else False