
CREATE TABLE PostalCode (
  PostalCode VARCHAR(5) NOT NULL,
  City VARCHAR(50) NOT NULL,
  State VARCHAR(50) NOT NULL,
  Latitude decimal(8,6) NOT NULL,
  Longitude decimal(8,6) NOT NULL,
  PRIMARY KEY (PostalCode),
  UNIQUE KEY PostalCode (PostalCode)
);

CREATE TABLE Manufacturer (
  ManufacturerName VARCHAR(50) NOT NULL,
  PRIMARY KEY (ManufacturerName),
  UNIQUE KEY ManufacturerName (ManufacturerName)
);

CREATE TABLE Household (
  HouseholdID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Email VARCHAR(100) NOT NULL,
  SquareFootage INT NOT NULL,
  HouseholdType VARCHAR(50) NOT NULL,
  HeatingSetting INT,
  CoolingSetting INT,
  PostalCode VARCHAR(5) NOT NULL,
  PRIMARY KEY (HouseholdID),
  UNIQUE KEY Email (Email),
  FOREIGN KEY (PostalCode) REFERENCES `PostalCode`(PostalCode)

);

CREATE TABLE PublicUtility (
  PublicUtilityId INT UNSIGNED NOT NULL AUTO_INCREMENT,
  HouseholdID INT UNSIGNED NOT NULL,
  UtilityName VARCHAR(50) NOT NULL,
  PRIMARY KEY (PublicUtilityId),
  UNIQUE KEY (HouseholdID, UtilityName),
  FOREIGN KEY (HouseholdID) REFERENCES `Household`(HouseholdID)
);

CREATE TABLE PowerGenerator (
  PowerGeneratorID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  HouseholdID INT UNSIGNED NOT NULL,
  OrderNumber INT UNSIGNED NOT NULL,
  BatteryStorageCapacity INT UNSIGNED,
  AvgMonthlyKwHours INT UNSIGNED NOT NULL,
  GenerationType VARCHAR(50) NOT NULL,
  PRIMARY KEY (PowerGeneratorID),
  UNIQUE KEY (HouseholdID, OrderNumber),
  FOREIGN KEY (HouseholdID) REFERENCES `Household`(HouseholdID)
);

CREATE TABLE Appliance (
  ApplianceID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  HouseholdID INT UNSIGNED NOT NULL,
  OrderNumber INT UNSIGNED NOT NULL,
  ManufacturerName VARCHAR(50) NOT NULL,
  ModelName VARCHAR(50) DEFAULT NULL,
  BtuRating INT UNSIGNED NOT NULL,
  PRIMARY KEY (ApplianceID),
  UNIQUE KEY (HouseholdID, OrderNumber),
  FOREIGN KEY (HouseholdID) REFERENCES `Household`(HouseholdID),
  FOREIGN KEY (ManufacturerName) REFERENCES `Manufacturer`(ManufacturerName)
);

CREATE TABLE WaterHeater (
  WaterHeaterID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ApplianceID INT UNSIGNED NOT NULL,
  TankSize DECIMAL(20,10) NOT NULL,
  CurrentTempSetting INT,
  EnergySource VARCHAR(50) NOT NULL,
  PRIMARY KEY (WaterHeaterID),
  FOREIGN KEY (ApplianceID) REFERENCES `Appliance`(ApplianceID)
  ON DELETE CASCADE
);

CREATE TABLE AirHandler (
  AirHandlerID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Rpm INT UNSIGNED NOT NULL,
  ApplianceID INT UNSIGNED NOT NULL,
  PRIMARY KEY (AirHandlerID),
  FOREIGN KEY (ApplianceID) REFERENCES `Appliance`(ApplianceID)
  ON DELETE CASCADE
);

CREATE TABLE AirConditioner (
  AirConditionerID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  EER DECIMAL(20,10) NOT NULL,
  AirHandlerID INT UNSIGNED NOT NULL,
  PRIMARY KEY (AirConditionerID),
  FOREIGN KEY (AirHandlerID) REFERENCES `AirHandler`(AirHandlerID)
  ON DELETE CASCADE
);

CREATE TABLE Heater (
  HeaterID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  EnergySource VARCHAR(50) NOT NULL,
  AirHandlerID INT UNSIGNED NOT NULL,
  PRIMARY KEY (HeaterID),
  FOREIGN KEY (AirHandlerID) REFERENCES `AirHandler`(AirHandlerID)
  ON DELETE CASCADE
);

CREATE TABLE HeatPump (
  HeatPumpID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  SEER DECIMAL(20,10) NOT NULL,
  HSPF DECIMAL(20,10) NOT NULL,
  AirHandlerID INT UNSIGNED NOT NULL,
  PRIMARY KEY (HeatPumpID),
  FOREIGN KEY (AirHandlerID) REFERENCES `AirHandler`(AirHandlerID)
  ON DELETE CASCADE
);

-- updates
ALTER TABLE PostalCode MODIFY COLUMN Latitude decimal(12,8) NOT NULL;
ALTER TABLE PostalCode MODIFY COLUMN Longitude decimal(12,8) NOT NULL;