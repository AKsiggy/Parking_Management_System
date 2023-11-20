-- Create database
CREATE DATABASE IF NOT EXISTS Parking_Management_System;
USE Parking_Management_System;

-- Table info
CREATE TABLE ParkingSpot (
    SpotID INT PRIMARY KEY AUTO_INCREMENT,
    SpotNumber INT,
    IsOccupied BOOLEAN,
    EntryTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    ExitTime DATETIME DEFAULT NULL
);

-- vehicles
CREATE TABLE Vehicle (
    VehicleID INT PRIMARY KEY AUTO_INCREMENT,
    LicensePlate VARCHAR(20),
    OwnerName VARCHAR(50),
    VehicleType VARCHAR(20)
);

-- users
CREATE TABLE User (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    UserName VARCHAR(50),
    Email VARCHAR(100)
);

-- reservations
CREATE TABLE Reservation (
    ReservationID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    SpotID INT,
    ReservationTime DATETIME,
    FOREIGN KEY (UserID) REFERENCES User(UserID),
    FOREIGN KEY (SpotID) REFERENCES ParkingSpot(SpotID)
);

-- payments
CREATE TABLE Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    ReservationID INT,
    Amount DECIMAL(10, 2),
    PaymentTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ReservationID) REFERENCES Reservation(ReservationID)
);

CREATE TABLE UserActivity (
    ActivityID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    ActivityType VARCHAR(50),
    ActivityTime DATETIME,
    FOREIGN KEY (UserID) REFERENCES User(UserID)
);

-- Function to check if a parking spot is available
DELIMITER //
CREATE FUNCTION IsSpotAvailable(pSpotNumber INT) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE available BOOLEAN;

    SELECT IFNULL(SUM(1), 0) = 0 INTO available
    FROM ParkingSpot
    WHERE SpotNumber = pSpotNumber AND IsOccupied = TRUE;

    RETURN available;
END //
DELIMITER ;

-- Trigger to automatically update the exit time when a vehicle exits a spot
DELIMITER //
CREATE TRIGGER UpdateExitTime
BEFORE UPDATE ON ParkingSpot
FOR EACH ROW
BEGIN
    IF NEW.IsOccupied = 0 THEN
        SET NEW.ExitTime = NOW();
    END IF;
END //
DELIMITER ;


-- trigger to log user activity when a reservation is made
DELIMITER //
CREATE TRIGGER LogReservation
AFTER INSERT ON Reservation
FOR EACH ROW
BEGIN
    INSERT INTO UserActivity (UserID, ActivityType, ActivityTime)
    VALUES (NEW.UserID, 'Reservation Made', NOW());
END //
DELIMITER ;

ALTER TABLE ParkingSpot
ADD CONSTRAINT unique_parking_spot
UNIQUE (SpotNumber);

DELIMITER //
CREATE PROCEDURE MakeReservation(
    IN pUserID INT,
    IN pSpotNumber INT
)
BEGIN
    DECLARE spotAvailable BOOLEAN;
    DECLARE spotID INT;

    -- Check if the parking spot is available
    SELECT IFNULL(SUM(1), 0) = 0 INTO spotAvailable
    FROM ParkingSpot
    WHERE SpotNumber = pSpotNumber AND IsOccupied = TRUE;

    IF spotAvailable THEN
        -- Update IsOccupied to TRUE
        UPDATE ParkingSpot SET IsOccupied = FALSE, EntryTime = NOW() WHERE SpotID = spotID;

        -- Insert a new reservation record
        INSERT INTO Reservation (UserID, SpotID, ReservationTime)
        VALUES (pUserID, spotID, NOW());

        -- Log the reservation activity
        INSERT INTO UserActivity (UserID, ActivityType, ActivityTime)
        VALUES (pUserID, 'Reservation Made', NOW());

        SELECT 'Reservation made successfully.' AS Result;
    ELSE
        SELECT 'The selected parking spot is not available.' AS Result;
    END IF;
END //
DELIMITER ;

