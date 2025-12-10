-- DEVICES

INSERT INTO Devices (DeviceName, DeviceType, ImageURL) 
VALUES ('Arduino UNO R3', 'Microcontroller Board', NULL);

-- COMPONENTS


-- GUIDES

INSERT INTO Guides (DeviceID, Title, DateCreated) 
VALUES (1, 'Getting Started with Arduino UNO', '2025-12-10');

-- STEPS

INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 1, 'Connect the USB cable to your Arduino UNO');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 2, 'Install the Arduino IDE on your computer');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 3, 'Select your board in the Tools menu');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 4, 'Upload the first sketch');