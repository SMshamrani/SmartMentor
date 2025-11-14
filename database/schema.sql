-- database/schema.sql
-- Database schema for Arduino Guide Application

-- Users table (for future authentication)
CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices table
CREATE TABLE Devices (
    DeviceID SERIAL PRIMARY KEY,
    DeviceName VARCHAR(255) NOT NULL,
    DeviceType VARCHAR(100),
    ImageURL TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Components table
CREATE TABLE Components (
    ComponentID SERIAL PRIMARY KEY,
    DeviceID INTEGER REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    ComponentName VARCHAR(255) NOT NULL,
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guides table
CREATE TABLE Guides (
    GuideID SERIAL PRIMARY KEY,
    DeviceID INTEGER REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    Title VARCHAR(500) NOT NULL,
    DateCreated DATE,
    GuideURL TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Steps table
CREATE TABLE Steps (
    StepID SERIAL PRIMARY KEY,
    GuideID INTEGER REFERENCES Guides(GuideID) ON DELETE CASCADE,
    StepNumber INTEGER NOT NULL,
    Description TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_components_device_id ON Components(DeviceID);
CREATE INDEX idx_guides_device_id ON Guides(DeviceID);
CREATE INDEX idx_steps_guide_id ON Steps(GuideID);
CREATE INDEX idx_steps_step_number ON Steps(GuideID, StepNumber);

-- Sample data insertion (optional)
INSERT INTO Devices (DeviceName, DeviceType, ImageURL) VALUES 
('Arduino Uno', 'Microcontroller Board', 'https://example.com/arduino-uno.jpg'),
('Arduino Nano', 'Microcontroller Board', 'https://example.com/arduino-nano.jpg');

-- UserProgress table (track user progress per step per device)
CREATE TABLE UserProgress (
    ProgressID SERIAL PRIMARY KEY,
    UserID INTEGER REFERENCES Users(UserID) ON DELETE CASCADE,
    DeviceID INTEGER REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    StepID INTEGER REFERENCES Steps(StepID) ON DELETE CASCADE,
    ProgressPercent INT DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'started',
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_userprogress_user_id ON UserProgress(UserID);
CREATE INDEX idx_userprogress_device_id ON UserProgress(DeviceID);
CREATE INDEX idx_userprogress_step_id ON UserProgress(StepID);
