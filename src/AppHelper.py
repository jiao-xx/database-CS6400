import sys
from flaskext.mysql import MySQL

class AppHelper:

  def get_manufacturers(mysql):

    query = 'SELECT ManufacturerName FROM Manufacturer;'
    cursor = mysql.get_db().cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()

    return results
  
  def is_email_available(mysql, email):

    query = '''
      SELECT COUNT(email) FROM Household WHERE email = %s;
    '''

    cursor = mysql.get_db().cursor()
    cursor.execute(query, [email])
    resultCount = cursor.fetchone()[0]
    cursor.close()

    return True if resultCount == 0 else False

  def is_postalcode_valid(mysql, postalCode):

    query = '''
      SELECT COUNT(PostalCode) FROM PostalCode WHERE PostalCode = %s;
    '''

    cursor = mysql.get_db().cursor()
    cursor.execute(query, [postalCode])
    resultCount = cursor.fetchone()[0]
    cursor.close()

    print('is_postalcode_valid: ' + str(postalCode), file=sys.stdout)
    print('is_postalcode_valid: ' + str(cursor.rowcount), file=sys.stdout)

    return True if resultCount == 1 else False

  def get_appliance_next_order_number(mysql, householdID):

    query = """
      SELECT COALESCE(Max(orderNumber) + 1, 1) FROM Appliance where HouseHoldId = %s  
    """
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [householdID])
    
    next_order_num = cursor.fetchone()[0]
    cursor.close()

    return next_order_num

  def insert_appliance(mysql, householdID, orderNumber, manufacturerName, modelName, btuRating):

    #insert appliance and get ID
    query ='''
    INSERT INTO Appliance (HouseholdID, OrderNumber, ManufacturerName, ModelName, BtuRating) VALUES (%s, %s, %s, %s, %s);
    '''

    cursor = mysql.get_db().cursor()
    values = (
      householdID,
      orderNumber,
      manufacturerName,
      modelName,
      btuRating
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      applianceID = cursor.lastrowid
      return applianceID
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False
    
  def is_household_otg(mysql, householdID):

    query='''
    SELECT count(UtilityName) FROM PublicUtility WHERE HouseholdID = %s
    '''

    cursor = mysql.get_db().cursor()
    cursor.execute(query, [householdID])
    
    total_utilities = cursor.fetchone()[0]
    print(f"total_utilities: '{total_utilities}'",file=sys.stdout)
    cursor.close()

    return True if total_utilities == 0 else False


  def household_has_power_generators(mysql, householdID):

    query='''
    SELECT COUNT(PowerGeneratorID) FROM PowerGenerator WHERE HouseholdID =%s
    '''

    cursor = mysql.get_db().cursor()
    cursor.execute(query, [householdID])
    
    power_generators = cursor.fetchone()[0]
    print(f"power_generators: '{power_generators}'",file=sys.stdout)
    cursor.close()

    return True if power_generators > 0 else False
  
  def get_power_generator_next_order_number(mysql, householdID):

    query = """
      SELECT COALESCE(Max(orderNumber) + 1, 1) FROM PowerGenerator where HouseHoldId = %s  
    """
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [householdID])
    
    next_order_num = cursor.fetchone()[0]
    cursor.close()

    return next_order_num
  
  def insert_power_generator(mysql, householdID, avgKwh, batteryStorageCapacity, generationType, orderNumber=None):

    if orderNumber == None:
      orderNumber = AppHelper.get_power_generator_next_order_number(mysql, householdID)

    query ='''
    INSERT INTO PowerGenerator (HouseholdID, OrderNumber, BatteryStorageCapacity, AvgMonthlyKwHours, GenerationType) VALUES (%s, %s, %s, %s, %s);
    '''

    cursor = mysql.get_db().cursor()
    values = (
      householdID,
      orderNumber,
      batteryStorageCapacity,
      avgKwh,
      generationType
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      applianceID = cursor.lastrowid
      return applianceID
    
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
      return False
    

  def get_household_power_generation(mysql, householdID):
    
    query = """
    SELECT OrderNumber as Num, GenerationType as Type, AvgMonthlyKwHours as 'Monthly kWh', BatteryStorageCapacity as 'Battery kWh', PowerGeneratorID as ID
    FROM PowerGenerator
    WHERE HouseholdID = %s
    ORDER BY Num ASC
    """
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [householdID])
    
    results = cursor.fetchall()
    cursor.close()

    return results

  def delete_power_generator(mysql, powerGeneratorID):

    query ='''
    DELETE FROM PowerGenerator WHERE PowerGeneratorID = %s;
    '''

    cursor = mysql.get_db().cursor()

    cursor.execute(query, [powerGeneratorID])
    mysql.get_db().commit()
    
    return True if cursor.rowcount == 1 else False