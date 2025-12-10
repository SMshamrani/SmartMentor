-- ==================== DEVICES ====================

INSERT INTO Devices (DeviceName, DeviceType, ImageURL) 
VALUES ('Arduino UNO R3', 'Microcontroller Board', NULL);

-- ==================== COMPONENTS ====================

INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'Digital I/O Pins', 'General purpose digital input/output');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'Analog Input Pins', 'Read analog sensors');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, '5V Power Supply', 'Provides power to components');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'Ground', 'Common return path for circuits');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'USB Port', 'For programming and power');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'Serial Communication', 'For data transfer');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'SPI Interface', 'Serial Peripheral Interface');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'I2C Interface', 'Two-wire communication');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'Built-in LED', 'Connected to digital pin 13');
INSERT INTO Components (DeviceID, ComponentName, Description) 
VALUES (1, 'Reset Button', 'To reset the microcontroller');

-- ==================== GUIDES ====================

INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL) 
VALUES (1, 'Getting Started with Arduino UNO', '2025-12-10', 'https://docs.arduino.cc/tutorials/uno-rev3/getting-started/');
INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL) 
VALUES (1, 'Digital I/O Tutorial', '2025-12-10', NULL);
INSERT INTO Guides (DeviceID, Title, DateCreated, GuideURL) 
VALUES (1, 'Analog Input and Sensors', '2025-12-10', NULL);

-- ==================== STEPS ====================

INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 1, 'Connect the USB cable to your Arduino UNO board');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 2, 'Download and install the Arduino IDE from arduino.cc');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 3, 'Open the Arduino IDE and select your board type');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 4, 'Select the correct COM port from Tools menu');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 5, 'Load the Blink example from File > Examples > 01.Basics');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 6, 'Click the Upload button to program your board');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (1, 7, 'Observe the LED blinking on the board');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 1, 'Understand digital pins (0-13) as INPUT or OUTPUT');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 2, 'Use pinMode() to configure a pin');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 3, 'Use digitalWrite() to set HIGH (5V) or LOW (0V)');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 4, 'Use digitalRead() to read pin state');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 5, 'Create a simple LED on/off circuit');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 6, 'Test with a pushbutton as input');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (2, 7, 'Build a simple LED control with button');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 1, 'Connect an analog sensor to pin A0');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 2, 'Use analogRead() to read the sensor value (0-1023)');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 3, 'Map sensor values to useful ranges');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 4, 'Use Serial.print() to view the values');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 5, 'Open Serial Monitor to see data');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 6, 'Create a light sensor application');
INSERT INTO Steps (GuideID, StepNumber, Description) 
VALUES (3, 7, 'Calibrate sensors for accuracy');