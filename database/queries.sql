SELECT COUNT(*) FROM Devices;
SELECT COUNT(*) FROM DeviceImages;
SELECT COUNT(*) FROM Guides;
SELECT COUNT(*) FROM Steps;
SELECT COUNT(*) FROM Components;

SELECT DeviceName
FROM Devices
ORDER BY DeviceName;

SELECT d.DeviceName
FROM Devices d
LEFT JOIN DeviceImages di ON d.DeviceID = di.DeviceID
WHERE di.DeviceID IS NULL
ORDER BY d.DeviceName;

SELECT 
    d.SourceID,
    d.DeviceName,
    g.Title AS GuideTitle,
    s.StepNumber,
    s.Description AS StepDescription
FROM Devices d
JOIN Guides g ON d.DeviceID = g.DeviceID
JOIN Steps s ON g.GuideID = s.GuideID
ORDER BY d.SourceID, s.StepNumber;

SELECT *
FROM DeviceImages
ORDER BY DeviceID, ImageNumber;