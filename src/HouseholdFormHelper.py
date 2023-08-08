import sys
from flaskext.mysql import MySQL

class HouseholdFormHelper:
    
  def insert_household(mysql, email, squareFootage, householdType, heatingSetting, coolingSetting, postalCode):

    query ='''
    INSERT INTO Household (Email, SquareFootage, HouseholdType, HeatingSetting, CoolingSetting, PostalCode)
    VALUES (%s, %s, %s, %s, %s, %s)
    '''

    cursor = mysql.get_db().cursor()
    values = (
      email,
      squareFootage,
      householdType,
      heatingSetting,
      coolingSetting,
      postalCode
    )

    try:
      cursor.execute(query, values)
      mysql.get_db().commit()
      resultCount = cursor.fetchone()[0]
      return True if resultCount == 0 else False
    
    except Exception as err:
      # print(f"insert_household::Error: {email} ->'{err}'",file=sys.stdout)
      # print(f'email: {email}')
      # print(f'squareFootage: {squareFootage}')
      # print(f'householdType: {householdType}')
      # print(f'heatingSetting: {heatingSetting}')
      # print(f'coolingSetting: {coolingSetting}')
      # print(f'postalCode: {postalCode}')
      return False
    

  def get_household_id(mysql, email):

    query = '''
    SELECT householdID FROM Household where email = %s;
    '''

    cursor = mysql.get_db().cursor()
    cursor.execute(query, [email])
    id = cursor.fetchone()
    cursor.close()

    return id

  def insert_household_utilities(mysql, householdID, utilities):

    query ='''
    INSERT INTO PublicUtility (HouseholdID, UtilityName)
    VALUES (%s, %s)
    '''
    insertCount = 0
    try:

      cursor = mysql.get_db().cursor()
      rowsToInsert = []
      print(utilities,file=sys.stdout)
      for u in utilities:
        if u and len(u) > 0:
          rowsToInsert.append((householdID, u))

      cursor.executemany(query, rowsToInsert)
      mysql.get_db().commit()
      insertCount = insertCount + cursor.fetchone()[0]

      return True if insertCount == len(utilities) else False
    
    except Exception as err:
      #print(f"insert_household_utilities::Error: '{err}', {householdID}",file=sys.stdout)
      return False
    
    cursor.close()