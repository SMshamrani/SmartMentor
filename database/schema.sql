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

-- Devices table (stores Arduino boards and similar devices)
CREATE TABLE Devices (
    DeviceID SERIAL PRIMARY KEY,
    DeviceName VARCHAR(255) NOT NULL,
    DeviceType VARCHAR(100),
    ImageURL TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Components table (stores components related to each device)
CREATE TABLE Components (
    ComponentID SERIAL PRIMARY KEY,
    DeviceID INTEGER REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    ComponentName VARCHAR(255) NOT NULL,
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Guides table (tutorials or guides for each device)
CREATE TABLE Guides (
    GuideID SERIAL PRIMARY KEY,
    DeviceID INTEGER REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    Title VARCHAR(500) NOT NULL,
    DateCreated DATE,
    GuideURL TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Steps table (detailed steps inside each guide)
CREATE TABLE Steps (
    StepID SERIAL PRIMARY KEY,
    GuideID INTEGER REFERENCES Guides(GuideID) ON DELETE CASCADE,
    StepNumber INTEGER NOT NULL,
    Description TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- UserProgress table (tracks user progress through guides and steps)
CREATE TABLE UserProgress (
    ProgressID SERIAL PRIMARY KEY,
    UserID INTEGER REFERENCES Users(UserID) ON DELETE CASCADE,
    DeviceID INTEGER REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    StepID INTEGER REFERENCES Steps(StepID) ON DELETE CASCADE,
    ProgressPercent INT DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'started',
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table (stores user feedback on guides)
CREATE TABLE Feedback (
    FeedbackID SERIAL PRIMARY KEY,                -- Unique feedback ID
    UserID INTEGER REFERENCES Users(UserID) ON DELETE CASCADE,     -- User who gave the feedback
    GuideID INTEGER REFERENCES Guides(GuideID) ON DELETE CASCADE,  -- Guide being reviewed
    Rating INT CHECK (Rating BETWEEN 1 AND 5),   -- Rating from 1 to 5
    Comment TEXT,                                 -- Optional text comment
    DateSubmitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When feedback was submitted
);

-- Indexes for better performance on foreign keys and lookups
CREATE INDEX idx_components_device_id ON Components(DeviceID);
CREATE INDEX idx_guides_device_id ON Guides(DeviceID);
CREATE INDEX idx_steps_guide_id ON Steps(GuideID);
CREATE INDEX idx_steps_step_number ON Steps(GuideID, StepNumber);

CREATE INDEX idx_userprogress_user_id ON UserProgress(UserID);
CREATE INDEX idx_userprogress_device_id ON UserProgress(DeviceID);
CREATE INDEX idx_userprogress_step_id ON UserProgress(StepID);

CREATE INDEX idx_feedback_user_id ON Feedback(UserID);
CREATE INDEX idx_feedback_guide_id ON Feedback(GuideID);
CREATE INDEX idx_feedback_rating ON Feedback(Rating);

-- Sample data insertion (optional examples for devices)
INSERT INTO Devices (DeviceName, DeviceType, ImageURL) VALUES 
('Arduino Uno', 'Microcontroller Board', 'https://example.com/arduino-uno.jpg'),
('Arduino Nano', 'Microcontroller Board', 'https://example.com/arduino-nano.jpg');
