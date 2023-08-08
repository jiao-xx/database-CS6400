-- Tables 

CREATE TABLE Household (
  Email VARCHAR(255) NOT NULL,
  SquareFootage INT NOT NULL,
  Household_type VARCHAR(50) NOT NULL,
  Degrees_for_heating INT,
  Degrees_for_cooling INT,
  PRIMARY KEY (Email)
  UNIQUE KEY Email (Email)
);

CREATE TABLE PostalCode (
  Email VARCHAR(255) NOT NULL,
  PostalCode INT NOT NULL,
  City VARCHAR(50) NOT NULL,
  State VARCHAR(50) NOT NULL,
  Latitude FLOAT NOT NULL,
  Longitude FLOAT NOT NULL,
  PRIMARY KEY (Email),
  FOREIGN KEY (Email) REFERENCES Household(Email)
);

CREATE TABLE PublicUtilities (
  Email VARCHAR(255) NOT NULL,
  PublicUtilities VARCHAR(50) NULL,
  PRIMARY KEY (Email,PublicUtilities)
  FOREIGN KEY (Email) REFERENCES Household(Email)
);

CREATE TABLE PowerGeneration (
  Email VARCHAR(255) NOT NULL,
  PGOrderNumber INT NOT NULL,
  BatteryStorageCapacity INT, Null,
  AvgMonthlyKwhours INT NOT NULL,
  GenerationType VARCHAR(50) NOT NULL,
  PRIMARY KEY (Email, PGOrderNumber),
  FOREIGN KEY (Email) REFERENCES Household(Email)
);

CREATE TABLE Appliance (
  APOrderNum INT NOT NULL,
  Email VARCHAR(255) NOT NULL,
  ManufacturerName VARCHAR(100) Null,
  BtuRating INT NOT NULL,
  ModelName VARCHAR(100) Null,
  PRIMARY KEY (APOrderNum),
  FOREIGN KEY (Email) REFERENCES Household(Email),
  FOREIGN KEY (ManufacturerName) REFERENCES Manufacturer(ManufacturerName)
);

CREATE TABLE Manufacturer (
  ManufacturerName VARCHAR(200) NOT NULL,
  PRIMARY KEY (ManufacturerName)
);

CREATE TABLE WaterHeater (
  APOrderNum INT NOT NULL,
  Email VARCHAR(255) NOT NULL,
  TankSize FLOAT NOT NULL,
  EnergySource VARCHAR(50) NOT NULL,
  CurrentTempSetting INT NOT NULL,
  PRIMARY KEY (APOrderNum),
  FOREIGN KEY (APOrderNum) REFERENCES Appliance(APOrderNum),
  FOREIGN KEY (Email) REFERENCES Household(Email)
);

CREATE TABLE AirHandler (
  APOrderNum INT NOT NULL,
  Email VARCHAR(255) NOT NULL,
  Rpm INT NOT NULL,
  PRIMARY KEY (APOrderNum),
  FOREIGN KEY (APOrderNum) REFERENCES Appliance(APOrderNum),
  FOREIGN KEY (Email) REFERENCES Household(Email)
);

CREATE TABLE HeatingCoolingMethods (
  APOrderNum INT NOT NULL,
  Email VARCHAR(255) NOT NULL,
  EER FLOAT NOT NULL,
  EnergySource VARCHAR(50) NOT NULL,
  SEER FLOAT NOT NULL,
  HSPF FLOAT NOT NULL,
  PRIMARY KEY (APOrderNum),
  FOREIGN KEY (APOrderNum) REFERENCES Appliance(APOrderNum),
  FOREIGN KEY (Email) REFERENCES Household(Email)
);


