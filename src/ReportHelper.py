import sys
from flaskext.mysql import MySQL

class ReportHelper:

  def get_top_manufacturers(mysql):

    query = """
            SELECT ManufacturerName, count(ManufacturerName) as TotalAppliances 
            FROM Appliance
            GROUP BY ManufacturerName
            ORDER BY TotalAppliances DESC
            LIMIT 25;
        """

    cursor = mysql.get_db().cursor()
    cursor.execute(query)

    results = cursor.fetchall()
    cursor.close()

    return results
  
  def get_top_manufacturers_drilldown(mysql, manufacturerName):

    query = """
            SELECT 'Water Heater' as Type, COUNT(*) as Total
            FROM WaterHeater w, Appliance a
            WHERE a.ManufacturerName = %s
                AND w.ApplianceID = a.ApplianceID
            UNION
            SELECT 'Air Handler' as Type, COUNT(*) as Total
            FROM AirHandler ah, Appliance a
            WHERE a.ManufacturerName = %s
                AND ah.ApplianceID = a.ApplianceID
        """
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [manufacturerName, manufacturerName])
    
    results = cursor.fetchall()
    cursor.close()

    return results
  
  def manufacturer_model_search(mysql, searchParam):

    query = """
            SELECT distinct(ManufacturerName), COALESCE(ModelName, '-') as ModelName
            FROM Appliance
            WHERE LOWER(ManufacturerName) LIKE CONCAT('%%', LOWER(%s), '%%')
            OR LOWER(ModelName) LIKE CONCAT('%%', LOWER(%s), '%%') 
            ORDER BY ManufacturerName ASC, ModelName ASC;
          """
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [searchParam, searchParam])
    
    results = cursor.fetchall()
    cursor.close()

    return results
  
  def get_heating_cooling_methods(mysql):
    
    query1 = """
            SELECT h.HouseholdType,
            COUNT(DISTINCT ac.AirConditionerID) AS AirConditionerCount, 
            ROUND(AVG(a.BtuRating)) AS AvgAirConditionerBTU, 
            ROUND(AVG(ah.Rpm), 1) AS AvgAirHandlerRPM, 
            ROUND(AVG(ac.EER), 1) AS AvgAirConditionerEER
            FROM Household h 
            LEFT JOIN Appliance a ON h.HouseholdID = a.HouseholdID 
            LEFT JOIN AirHandler ah ON a.ApplianceID = ah.ApplianceID
            LEFT JOIN AirConditioner ac ON ah.AirHandlerID = ac.AirHandlerID 
            GROUP BY h.HouseholdType 
            ORDER BY h.HouseholdType ASC;
        """
    query2 = """
          SELECT h.HouseholdType,
          COUNT(DISTINCT he.HeaterID) AS HeaterCount,
          ROUND(AVG(a.BtuRating)) AS AvgHeaterBTU,
          ROUND(AVG(ah.Rpm), 1) AS AvgHeaterRPM,
          (SELECT EnergySource FROM Heater 
          WHERE AirHandlerID = ah.AirHandlerID
          GROUP BY EnergySource 
          ORDER BY COUNT(*) DESC LIMIT 1) AS MostCommonEnergySource
          FROM Household h
          LEFT JOIN Appliance a ON h.HouseholdID = a.HouseholdID 
          LEFT JOIN AirHandler ah ON a.ApplianceID = ah.ApplianceID 
          LEFT JOIN Heater he ON ah.AirHandlerID = he.AirHandlerID 
          GROUP BY h.HouseholdType
          ORDER BY h.HouseholdType ASC;
        """
    query3 = """
        SELECT h.HouseholdType,
        COUNT(DISTINCT hp.HeatPumpID) AS HeatPumpCount, 
        ROUND(AVG(a.BtuRating)) AS AvgHeatPumpBTU, 
        ROUND(AVG(ah.Rpm), 1) AS AvgHeatPumpRPM, 
        ROUND(AVG(hp.SEER), 1) AS AvgHeatPumpSEER, 
        ROUND(AVG(hp.HSPF), 1) AS AvgHeatPumpHSPF 
        FROM Household h
        LEFT JOIN Appliance a ON h.HouseholdID = a.HouseholdID 
        LEFT JOIN AirHandler ah ON a.ApplianceID = ah.ApplianceID
        LEFT JOIN HeatPump hp ON ah.AirHandlerID = hp.AirHandlerID 
        GROUP BY h.HouseholdType 
        ORDER BY h.HouseholdType ASC;
        """ 
      
    cursor = mysql.get_db().cursor()
    
    cursor.execute("SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
    cursor.execute(query1)
    result1 = cursor.fetchall()
    
    cursor.execute("SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
    cursor.execute(query2)
    result2 = cursor.fetchall()

    cursor.execute("SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));")
    cursor.execute(query3)
    result3 = cursor.fetchall()

    cursor.close()

    return result1, result2, result3

  def get_waterheater_statistics(mysql):
    
    query = """
              SELECT pc.State,
              ROUND(AVG(wh.TankSize)) AS AvgTankSize,
              ROUND(AVG(a.BtuRating)) AS AvgWaterHeaterBTU, 
              ROUND(AVG(wh.CurrentTempSetting), 1) AS AvgTemperatureSetting, 
              COUNT(CASE WHEN wh.CurrentTempSetting IS NOT NULL THEN 1 END)
              AS TempSettingProvidedCount,
              COUNT(CASE WHEN wh.CurrentTempSetting IS NULL THEN 1 END) AS
              TempSettingNotProvidedCount 
              FROM WaterHeater wh
              JOIN Appliance a ON wh.ApplianceID = a.ApplianceID 
              JOIN Household hh ON a.HouseholdID = hh.HouseholdID 
              JOIN PostalCode pc ON hh.PostalCode = pc.PostalCode
              GROUP BY pc.State ORDER BY pc.State;
            """ 
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query)
    
    results = cursor.fetchall()
    cursor.close()

    return results

  def get_waterheater_statistics_drilldown(mysql, state):
    
    query = """
              SELECT
              wh.EnergySource,
              ROUND(MIN(wh.TankSize)) AS MinTankSize, 
              ROUND(AVG(wh.TankSize)) AS AvgTankSize, 
              ROUND(MAX(wh.TankSize)) AS MaxTankSize, 
              MIN(wh.CurrentTempSetting) AS MinTempSeJng, 
              ROUND(AVG(wh.CurrentTempSetting),1) AS AvgTempSeJng,
              MAX(wh.CurrentTempSetting) AS MaxTempSeJng
              FROM WaterHeater wh
              JOIN Appliance a ON wh.ApplianceID = a.ApplianceID 
              JOIN Household hh ON a.HouseholdID = hh.HouseholdID 
              JOIN PostalCode pc ON hh.PostalCode = pc.PostalCode
              WHERE pc.State = %s 
              GROUP BY 1
              ORDER BY EnergySource
            """
    
    cursor = mysql.get_db().cursor()
    cursor.execute(query, [state])
    
    results = cursor.fetchall()
    cursor.close()

    return results

  def get_otg_household_dashboard(mysql):
    
    query1 = """
        SELECT pc.State,
        COUNT(DISTINCT hh.HouseholdID) AS OffGridHouseholds 
        FROM Household AS hh
        JOIN PostalCode AS pc ON hh.PostalCode = pc.PostalCode 
        WHERE hh.HouseholdID 
        NOT IN (
          SELECT pu.HouseholdID
          FROM PublicUtility AS pu)
        GROUP BY pc.State
        ORDER BY OffGridHouseholds DESC LIMIT 1;
        """
    
    query2 = """
        SELECT ROUND(AVG(pg.BatteryStorageCapacity), 0) as AverageBatteryStorageCapacity
        FROM PowerGenerator pg
        WHERE pg.HouseholdID 
        IN (
          SELECT HouseholdID 
          FROM Household 
          WHERE HouseholdID 
        NOT IN (
          SELECT HouseholdID 
          FROM PublicUtility
          ))
    """

    query3 = """
            SELECT gt.GenerationType,
            COALESCE( NULLIF(ROUND(100 * (COUNT(pg.GenerationType) * 1.0 /
            (SELECT COUNT(GenerationType) FROM PowerGenerator) * 1.0)
            ,1),0), '0%' ) as '%%'
            
            FROM 
              (select 'Solar' as GenerationType 
              union all 
              select 'Wind-turbine' 
              union all
              select 'Mixed') gt
            LEFT OUTER JOIN PowerGenerator pg
            ON LOWER(pg.GenerationType) = LOWER(gt.GenerationType)
            GROUP BY gt.GenerationType
        """
    
    query4 = """
              SELECT ht.HouseholdType,
              COALESCE( NULLIF(ROUND(100 * (COUNT(hh.HouseholdType) * 1.0 /
              (SELECT COUNT(HouseholdType) FROM Household) * 1.0)
              ,1), 0), '0%' ) as '%%'
              FROM (
                select 'House' as HouseholdType 
                union all 
                select 'Apartment' 
                union all
                select 'Townhome' 
                union all 
                select 'Condominium' 
                union all 
                select 'Modular home' 
                union all select 'Mixed') ht
              LEFT OUTER JOIN Household hh
              ON LOWER(hh.HouseholdType) = LOWER(ht.HouseholdType) 
              GROUP BY ht.HouseholdType
            """

    query5 = """
            SELECT
              ROUND(AVG(wh1.TankSize),1) asAvgOffGridTankSize, 
                ROUND(AVG(wh2.TankSize),1) asAvgOnGridTankSize
            FROM Appliance ap1, WaterHeater wh1, Appliance ap2, WaterHeater wh2
            WHERE ap1.ApplianceID = wh1.ApplianceID AND ap2.ApplianceID = wh2.ApplianceID AND ap1.HouseholdID IN 
            (
              SELECT HouseholdID FROM Household WHERE HouseholdID NOT IN (SELECT DISTINCT(HouseholdID) FROM PublicUtility)
            )
            AND ap2.HouseholdID NOT IN (
              SELECT HouseholdID FROM Household WHERE HouseholdID NOT IN (SELECT HouseholdID FROM PublicUtility)
            )
        """
    
    query6 = """
            SELECT
            'Water Heater' as ApplianceType,
            IFNULL( ROUND(MIN(a.BtuRating), 0), 0) as MinBTU, 
            IFNULL(ROUND(MAX(a.BtuRating), 0), 0) as MaxBTU, 
            IFNULL(ROUND(AVG(a.BtuRating), 0), 0) as AvgBTU
            FROM Appliance a, WaterHeater w 
            WHERE a.ApplianceID = w.ApplianceID 
            GROUP BY ApplianceType
            UNION
            SELECT
            'Air Handler' as ApplianceType, 
            IFNULL(ROUND(MIN(a2.BtuRating), 0), 0) as MinBTU, 
            IFNULL(ROUND(MAX(a2.BtuRating), 0), 0) as MaxBTU, 
            IFNULL(ROUND(AVG(a2.BtuRating), 0), 0) as AvgBTU
            FROM Appliance a2, AirHandler ah 
            WHERE a2.ApplianceID = ah.ApplianceID 
            GROUP BY ApplianceType
         """
    
    cursor = mysql.get_db().cursor()
    
    cursor.execute(query1)
    result1 = cursor.fetchall()

    cursor.execute(query2)
    result2 = cursor.fetchall()    

    cursor.execute(query3)
    result3 = cursor.fetchall()

    cursor.execute(query4)
    result4 = cursor.fetchall()    

    cursor.execute(query5)
    result5 = cursor.fetchall()

    cursor.execute(query6)
    result6 = cursor.fetchall()    

    cursor.close()

    return result1, result2, result3, result4, result5, result6 

  def get_household_avg_radius(mysql, postalCode, searchRadius):
      query = '''
              with val as (
              select 
                  p.PostalCode, 
                  p.City,
                  p.State,
                  (t.Latitude* pi() / 180 - p.Latitude * pi() / 180) as d_lat, 
                  (t.Longitude* pi() / 180 - p.Longitude * pi() / 180) as d_lon, 
                  t.Latitude* pi() / 180 as lat_2, 
                  p.Latitude * pi() / 180 as lat_1, 
                  t.Longitude* pi() / 180 as lon_2, 
                  p.Longitude * pi() / 180 as lon_1
              from PostalCode p, PostalCode t
              where t.PostalCode = %s
              ),
              
              a as (
              select 
                  PostalCode, 
                  City, 
                  State, 
                  power(sin(d_lat/2), 2) + cos(lat_1)*cos(lat_2)  * power(sin(d_lon/2),2) as a_value -- calculate a value 
              from val),
              
              c as (
              select 
                  PostalCode, 
                  City, 
                  State, 
                  2*atan2(sqrt(a_value), sqrt(1-a_value)) as c_value
              from a
              ),
              
              zipcode_in_radius as (
              select 
                  PostalCode, 
                  City, 
                  State, 
                  c_value * 3598.75 as radius 
              from c
              where c_value * 3598.75  <= %s
              order by radius asc
              )

              SELECT
              h.PostalCode,
              UPPER(h.HouseholdType),
              COUNT(h.HouseholdID),
              COALESCE(AVG(h.HeatingSetting), 0) as AvgHeatingSetting,
              COALESCE(AVG(h.CoolingSetting), 0) as AvgCoolingSetting
              FROM Household h
              WHERE h.PostalCode IN (
                  select PostalCode
                  from zipcode_in_radius
              )
              GROUP BY h.PostalCode, h.HouseholdType
              ORDER BY h.PostalCode
          '''
      cursor = mysql.get_db().cursor()
      cursor.execute(query, [postalCode, searchRadius])

      results = cursor.fetchall()
      cursor.close()

      hh_tuple = ReportHelper.get_households_in_radius(mysql, postalCode, searchRadius)
      households_in_radius = [item for sublist in hh_tuple for item in sublist]

      household_type_count = []
      household_avgs = []
      household_avg_power = []

      if len(households_in_radius) > 0:
        household_type_count = ReportHelper.get_household_type_count(mysql, households_in_radius)
        household_avgs = ReportHelper.get_household_avgs(mysql, households_in_radius)
        household_avg_power = ReportHelper.get_avg_power_per_household(mysql, households_in_radius)

      print('#' * 22,file=sys.stdout)
      print(f"household_type_count: '{household_type_count}'",file=sys.stdout)
      print(f"household_avgs: '{household_avgs}'",file=sys.stdout)
      print(f"household_avg_power: '{household_avg_power}'",file=sys.stdout)
      print('#' * 22,file=sys.stdout)
      return results, household_type_count, household_avgs, household_avg_power
  
  def get_households_in_radius(mysql, postalCode, searchRadius):
        results = []
        query = '''
                with val as (
                select 
                    p.PostalCode, 
                    p.City,
                    p.State,
                    (t.Latitude* pi() / 180 - p.Latitude * pi() / 180) as d_lat, 
                    (t.Longitude* pi() / 180 - p.Longitude * pi() / 180) as d_lon, 
                    t.Latitude* pi() / 180 as lat_2, 
                    p.Latitude * pi() / 180 as lat_1, 
                    t.Longitude* pi() / 180 as lon_2, 
                    p.Longitude * pi() / 180 as lon_1
                from PostalCode p, PostalCode t
                where t.PostalCode = %s
                ),
                
                a as (
                select 
                    PostalCode, 
                    City, 
                    State, 
                    power(sin(d_lat/2), 2) + cos(lat_1)*cos(lat_2)  * power(sin(d_lon/2),2) as a_value -- calculate a value 
                from val),
                
                c as (
                select 
                    PostalCode, 
                    City, 
                    State, 
                    2*atan2(sqrt(a_value), sqrt(1-a_value)) as c_value
                from a
                ),
                
                zipcode_in_radius as (
                select 
                    PostalCode, 
                    City, 
                    State, 
                    c_value * 3598.75 as radius 
                from c
                where c_value * 3598.75  <= %s
                order by radius asc
                )

                SELECT
                h.HouseholdID
                FROM Household h
                WHERE h.PostalCode IN (
                    select PostalCode
                    from zipcode_in_radius
                )
            '''
        
        print(f"get_households_in_radius: '{postalCode}:{searchRadius}'",file=sys.stdout)
    
      
        cursor = mysql.get_db().cursor()
        cursor.execute(query, [postalCode, searchRadius])

        results = cursor.fetchall()
        cursor.close()
        print(f"results: '{results}'\n\n",file=sys.stdout)
        return results
  
  def get_household_type_count(mysql, households):

    results = []
    ids = tuple(households) if len(households) > 0 else tuple([0,-1])
    query = """
            with matching_hh as (
            SELECT HouseHoldID
              FROM Household
              where HouseholdID in {}
          )

          select UPPER(HouseholdType) as HouseholdType, 
          Count(HouseholdType) as HouseholdCount,
          (select COUNT(HouseHoldID) from matching_hh) as TotalHouseHolds,
          (SELECT GROUP_CONCAT(distinct(UtilityName) SEPARATOR ', ') from PublicUtility ) as UtilitiesInUse,
          (select COUNT(HouseHoldID) from matching_hh  where HouseHoldID not in (SELECT DISTINCT(HouseHoldID) from PublicUtility)) as OffTheGridHouseHolds,
          (select COUNT(HouseHoldID) from matching_hh  where HouseHoldID  in (SELECT DISTINCT(HouseHoldID) from PowerGenerator)) as HomesWithPowerGeneration,
          (
				    SELECT GenerationType FROM cs6400.PowerGenerator
            WHERE HouseHoldID  in (SELECT DISTINCT(HouseHoldID) from PowerGenerator)
				    GROUP BY GenerationType
				    ORDER BY Count(generationType)   DESC
            LIMIT 1
            ) as MostCommonGenerationMethod,
          (select COUNT(HouseHoldID) from matching_hh  where HouseHoldID in (SELECT DISTINCT(HouseHoldID) from PowerGenerator WHERE BatteryStorageCapacity is not null) ) as HomesWithBatteryStorage

          from Household
          where HouseholdID in (select HouseHoldID from matching_hh)
          group by HouseholdType
          order by HouseholdCount DESC
        """.format(ids)
    
    print(f"ids: '{ids}'",file=sys.stdout)
    print(f"query: '{query}'",file=sys.stdout)

    try:
      cursor = mysql.get_db().cursor()
      cursor.execute(query)
      results = cursor.fetchall()
      cursor.close()
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)
    return results
  
  def get_household_avgs(mysql, households):

    ids = tuple(households) if len(households) > 0 else tuple([0])
    results = []
    query = """
            with matching_hh as (
            SELECT HouseHoldID
              FROM Household
              where HouseholdID in {}
          )

          select 
            ROUND(AVG(SquareFootage)),
            ROUND(AVG(HeatingSetting), 1),
            ROUND(AVG(CoolingSetting), 1) 
            from Household where HouseholdID in (select HouseHoldID from matching_hh)
        """.format(ids)
    
    #f"query: '{query}'",file=sys.stdout)
    try:
      cursor = mysql.get_db().cursor()
      cursor.execute(query)
      results = cursor.fetchall()
      cursor.close()

    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout)  

    return results
  
  def get_avg_power_per_household(mysql, households):

    ids = tuple(households) if len(households) > 0 else tuple([0])
    results = []

    query = """
            with matching_hh as (
            SELECT HouseHoldID
              FROM Household
              where HouseholdID in {}
          )
          SELECT HouseholdID, ROUND(Avg(AvgMonthlyKwHours), 0) 
          FROM PowerGenerator where HouseholdID in (select HouseHoldID from matching_hh)
          GROUP BY HouseholdID
        """.format(ids)
    
    print(f"query: '{query}'",file=sys.stdout)
    
    try:
      cursor = mysql.get_db().cursor()
      cursor.execute(query)
      
      results = cursor.fetchall()
      cursor.close()
    except Exception as err:
      print(f"Error: '{err}'",file=sys.stdout) 
    return results