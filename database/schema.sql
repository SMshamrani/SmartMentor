-- =========================================================
-- database/schema.sql
-- Updated PostgreSQL schema for SmartMentor Printer Guide App
-- =========================================================

-- =========================
-- DROP TABLES (optional for clean reset)
-- =========================
DROP TABLE IF EXISTS Feedback CASCADE;
DROP TABLE IF EXISTS UserProgress CASCADE;
DROP TABLE IF EXISTS Steps CASCADE;
DROP TABLE IF EXISTS Guides CASCADE;
DROP TABLE IF EXISTS Components CASCADE;
DROP TABLE IF EXISTS DeviceImages CASCADE;
DROP TABLE IF EXISTS Devices CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

-- =========================
-- Users table
-- For future authentication and tracking user activity
-- =========================
CREATE TABLE Users (
    UserID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- Devices table
-- Stores printer devices imported from dataset
-- SourceID = Printer ID from dataset
-- =========================
CREATE TABLE Devices (
    DeviceID SERIAL PRIMARY KEY,
    SourceID INT UNIQUE,
    DeviceName VARCHAR(255) NOT NULL,
    DeviceType VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- DeviceImages table
-- Stores multiple images for each printer
-- =========================
CREATE TABLE DeviceImages (
    ImageID SERIAL PRIMARY KEY,
    DeviceID INTEGER NOT NULL REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    ImageURL TEXT,
    ImageNumber INTEGER,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- Components table
-- Stores components related to each device
-- =========================
CREATE TABLE Components (
    ComponentID SERIAL PRIMARY KEY,
    DeviceID INTEGER NOT NULL REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    ComponentName VARCHAR(255) NOT NULL,
    Description TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- Guides table
-- Stores generated guide for each device
-- =========================
CREATE TABLE Guides (
    GuideID SERIAL PRIMARY KEY,
    DeviceID INTEGER NOT NULL REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    Title VARCHAR(500) NOT NULL,
    DateCreated DATE,
    GuideURL TEXT,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- Steps table
-- Stores ordered guide steps
-- =========================
CREATE TABLE Steps (
    StepID SERIAL PRIMARY KEY,
    GuideID INTEGER NOT NULL REFERENCES Guides(GuideID) ON DELETE CASCADE,
    StepNumber INTEGER NOT NULL,
    Description TEXT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- UserProgress table
-- Tracks user progress through guides and steps
-- Kept for future app functionality
-- =========================
CREATE TABLE UserProgress (
    ProgressID SERIAL PRIMARY KEY,
    UserID INTEGER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    DeviceID INTEGER NOT NULL REFERENCES Devices(DeviceID) ON DELETE CASCADE,
    StepID INTEGER REFERENCES Steps(StepID) ON DELETE CASCADE,
    ProgressPercent INT DEFAULT 0 CHECK (ProgressPercent BETWEEN 0 AND 100),
    Status VARCHAR(20) DEFAULT 'started',
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- Feedback table
-- Stores user ratings and comments on guides
-- =========================
CREATE TABLE Feedback (
    FeedbackID SERIAL PRIMARY KEY,
    UserID INTEGER NOT NULL REFERENCES Users(UserID) ON DELETE CASCADE,
    GuideID INTEGER NOT NULL REFERENCES Guides(GuideID) ON DELETE CASCADE,
    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    Comment TEXT,
    DateSubmitted TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- UNIQUE CONSTRAINTS / INDEXES
-- =========================

-- Prevent duplicate image numbers for same device
CREATE UNIQUE INDEX deviceimages_deviceid_imagenumber_unique
ON DeviceImages (DeviceID, ImageNumber);

-- Prevent duplicate step numbers inside same guide
CREATE UNIQUE INDEX steps_guideid_stepnumber_unique
ON Steps (GuideID, StepNumber);

-- =========================
-- PERFORMANCE INDEXES
-- =========================
CREATE INDEX idx_devices_source_id ON Devices(SourceID);
CREATE INDEX idx_devices_name ON Devices(DeviceName);

CREATE INDEX idx_deviceimages_device_id ON DeviceImages(DeviceID);
CREATE INDEX idx_components_device_id ON Components(DeviceID);
CREATE INDEX idx_guides_device_id ON Guides(DeviceID);
CREATE INDEX idx_steps_guide_id ON Steps(GuideID);

CREATE INDEX idx_userprogress_user_id ON UserProgress(UserID);
CREATE INDEX idx_userprogress_device_id ON UserProgress(DeviceID);
CREATE INDEX idx_userprogress_step_id ON UserProgress(StepID);

CREATE INDEX idx_feedback_user_id ON Feedback(UserID);
CREATE INDEX idx_feedback_guide_id ON Feedback(GuideID);
CREATE INDEX idx_feedback_rating ON Feedback(Rating);