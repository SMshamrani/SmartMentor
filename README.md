# SmartMentor

## AI-Powered Device Guidance Platform

SmartMentor is an intelligent mobile application designed to bridge the gap between traditional device manuals and practical hands-on guidance using Artificial Intelligence (AI), Computer Vision, and Large Language Models (LLMs).

The system enables users to scan electronic devices using their mobile camera, automatically recognize the device model, and generate interactive setup and troubleshooting guides in real time.

SmartMentor aims to simplify device usage, reduce user frustration, and provide accessible step-by-step assistance without requiring technical expertise.

---

# Project Overview

Traditional user manuals and online tutorials are often difficult to follow, time-consuming, and not personalized to the user's exact device or current problem.

SmartMentor solves this challenge by combining:

- Computer Vision for device recognition
- AI-generated troubleshooting and setup guides
- Cloud database integration
- Personalized user progress tracking
- Mobile-first interactive experience

The platform is designed to support multiple device categories such as:

- Printers
- Smartphones
- Laptops
- Routers
- Cameras
- Smart devices
- Future IoT devices

---

# Features

- AI-powered device recognition using images
- Automatic guide generation using LLMs
- Real-time device scanning
- Cloud PostgreSQL database
- Personalized recent devices history
- User progress tracking
- Feedback and rating system
- Smart search functionality
- Notifications system
- Cloud image upload support
- Multi-device scalable architecture
- Flutter mobile application
- Node.js backend API
- Secure cloud-based storage

---

# Technologies Used

## Frontend
- Flutter
- Dart

## Backend
- Node.js
- Express.js

## Database
- PostgreSQL
- Supabase

## Artificial Intelligence
- OpenAI API
- Computer Vision
- Large Language Models (LLMs)

## Cloud Services
- Cloudinary

## Other Technologies
- REST APIs
- JSON
- Git & GitHub

---

# System Architecture

```text
Flutter Mobile App
        ↓
Node.js Backend API
        ↓
PostgreSQL Cloud Database
        ↓
OpenAI API (AI + Vision)
        ↓
Cloudinary Image Storage
```

---

# Main Functionalities

## 1. User Authentication

Users can:
- Create accounts
- Login securely
- Access personalized device history

---

## 2. Device Scanning

Users can scan devices using the mobile camera.

The system:
- Detects the device model
- Searches the database
- Generates AI-based guides if the device does not exist

---

## 3. AI Guide Generation

If a device is not available in the database:

- AI automatically generates:
  - Device information
  - Components
  - Troubleshooting steps
  - Setup instructions

The generated guide is then stored permanently in the database.

---

## 4. Personalized User Experience

The system tracks:
- Recent devices
- User progress
- Completed guides
- Incomplete guides
- User feedback

---

# Database Tables

The system database contains the following main tables:

- Users
- Devices
- DeviceImages
- Components
- Guides
- Steps
- UserProgress
- Feedback

---

# Installation

## Clone Repository

```bash
git clone https://github.com/SMshamrani/SmartMentor.git
cd SmartMentor
```

---

# Backend Setup

## Navigate to backend

```bash
cd src/Phase2_Runtime/backend
```

## Install dependencies

```bash
npm install
```

## Create `.env` file

```env
OPENAI_API_KEY=your_openai_key

DATABASE_URL=your_postgresql_connection

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## Run backend server

```bash
node server.js
```

Server runs on:

```text
http://localhost:3000
```

---

# Flutter Setup

## Navigate to Flutter application

```bash
cd ui-designs/flutter_application_1
```

## Install Flutter packages

```bash
flutter pub get
```

## Run application

```bash
flutter run
```

---

# API Endpoints

## Authentication
- `POST /users`
- `POST /login`

## Device Scanning
- `POST /scan-printer`

## Device Guides
- `GET /devices/:id/guide`

## Search
- `GET /devices/search`

## User Progress
- `POST /user-progress/open-device`
- `POST /user-progress/update`

## Notifications
- `GET /users/:userId/notifications`

## Feedback
- `POST /feedback`

## AI Device Generation
- `POST /generate-device-guide`

---

# Security Features

- Password hashing using bcrypt
- Environment variable protection using `.env`
- Cloud database security
- Row Level Security (RLS)
- API key protection
- Secure backend architecture

---

# Future Enhancements

- Multi-language support
- Voice assistant integration
- Augmented Reality (AR) guidance
- Advanced AI troubleshooting
- Device recommendation system
- Analytics dashboard
- Admin control panel
- Real-time notifications
- Expanded IoT device support

---

# Contributors

- Sarah Mohammad Alshamrani — 444003567
- Waad Mohammad Al luhaybi — 444001927
- Shahad Hassan Altalhi — 444001817
- Reem Ahmad Alharbi — 444003905

---

# Supervisor

Dr. Daren FadolAlkarim

---

# License

This project is developed for academic and educational purposes as part of a graduation project.

---
