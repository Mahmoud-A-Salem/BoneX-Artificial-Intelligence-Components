CREATE DATABASE BoneXRecommendationSystem
GO

USE BoneXRecommendationSystem
GO

CREATE TABLE Doctors (
    DoctorID INT PRIMARY KEY IDENTITY,         
    FullName NVARCHAR(100) NOT NULL,                    
    ExperienceYears INT CHECK (ExperienceYears >= 0) NOT NULL,                       
    Latitude FLOAT NOT NULL,                            
    Longitude FLOAT NOT NULL,                           
    Rating FLOAT CHECK (Rating BETWEEN 0 AND 5) DEFAULT 0,
    NumberOfReviews INT DEFAULT 0,             
    SumOfRatings FLOAT DEFAULT 0	-- Sum of All Normalized Ratings
);

CREATE TABLE Patients (
    PatientID INT PRIMARY KEY IDENTITY,         
    FullName NVARCHAR(100) NOT NULL,                     
    Gender NVARCHAR(10) NOT NULL,                        
    DateOfBirth DATE NOT NULL                        
);

CREATE TABLE Ratings (
	DoctorID INT FOREIGN KEY REFERENCES Doctors(DoctorID) ON DELETE CASCADE,
	PatientID INT FOREIGN KEY REFERENCES Patients(PatientID) ON DELETE CASCADE,
	NormalizedRating FLOAT CHECK (NormalizedRating BETWEEN 0 AND 5) NOT NULL,
	PRIMARY KEY (DoctorID, PatientID) -- Composite Primary Key
);

CREATE TABLE MedicalHistory (
	MedicalHistoryID INT PRIMARY KEY IDENTITY,	-- Unique ID for each medical condition
	ConditionName NVARCHAR(100) NOT NULL,				-- Name of the medical condition (Ex: Diabetes or Hypertension)
);

CREATE TABLE PatientMedicalHistory (
	PatientID INT FOREIGN KEY REFERENCES Patients(PatientID) ON DELETE CASCADE,
	MedicalHistoryID INT FOREIGN KEY REFERENCES MedicalHistory(MedicalHistoryID),
	PRIMARY KEY (PatientID, MedicalHistoryID) -- Composite Primary Key
);

CREATE TRIGGER UpdateDoctorRatingOnInsert
ON Ratings
AFTER INSERT
AS
BEGIN
	UPDATE d
	SET
		NumberOfReviews = d.NumberOfReviews + i.CountInserted,
		SumOfRatings = d.SumOfRatings + i.TotalInserted,
		Rating = CASE
					WHEN (d.NumberOfReviews + i.CountInserted) = 0
					THEN 0
					ELSE (d.SumOfRatings + i.TotalInserted) / (d.NumberOfReviews + i.CountInserted)
				END
	FROM Doctors d
	JOIN (
		SELECT DoctorID, ISNULL(COUNT(*), 0) AS CountInserted, ISNULL(SUM(NormalizedRating), 0) AS TotalInserted
		FROM inserted
		GROUP BY DoctorID
	) i ON d.DoctorID = i.DoctorID
END;

CREATE TRIGGER UpdateDoctorRatingOnUpdate
ON Ratings
AFTER UPDATE
AS
BEGIN
	UPDATE d
	SET
		SumOfRatings = d.SumOfRatings - upd.OldRating + upd.NewRating,
		Rating = CASE 
					WHEN d.NumberOfReviews = 0 THEN 0 
					ELSE (d.SumOfRatings - upd.OldRating + upd.NewRating) / d.NumberOfReviews
				END
	FROM Doctors d
	JOIN (
		SELECT i.DoctorID,
		       ISNULL(SUM(i.NormalizedRating), 0) AS NewRating,
		       ISNULL(SUM(d.NormalizedRating), 0) AS OldRating
		FROM inserted i
		JOIN deleted d ON i.DoctorID = d.DoctorID AND i.PatientID = d.PatientID
		GROUP BY i.DoctorID
	) upd ON d.DoctorID = upd.DoctorID
END;


CREATE TRIGGER UpdateDoctorRatingOnDelete
ON Ratings
AFTER DELETE
AS
BEGIN
	UPDATE d
	SET
		NumberOfReviews = d.NumberOfReviews - del.CountDeleted,
		SumOfRatings = d.SumOfRatings - del.TotalDeleted,
		Rating = CASE 
					WHEN d.NumberOfReviews - del.CountDeleted = 0 THEN 0
					ELSE (d.SumOfRatings - del.TotalDeleted) / (d.NumberOfReviews - del.CountDeleted)
				END
	FROM Doctors d
	JOIN (
		SELECT DoctorID, ISNULL(COUNT(*), 0) AS CountDeleted, ISNULL(SUM(NormalizedRating), 0) AS TotalDeleted
		FROM deleted
		GROUP BY DoctorID
	) del ON d.DoctorID = del.DoctorID
END;


-- 1. Insert 10 Doctors
INSERT INTO Doctors (FullName, ExperienceYears, Latitude, Longitude)
VALUES
('Dr. Sarah Mahmoud', 5, 30.05, 31.25),
('Dr. Ahmed Zaki', 10, 30.08, 31.22),
('Dr. Mona ElShamy', 7, 29.95, 31.20),
('Dr. Karim Farouk', 15, 30.10, 31.30),
('Dr. Layla Samir', 3, 30.02, 31.18),
('Dr. Tarek Hossam', 20, 29.98, 31.40),
('Dr. Heba Said', 12, 30.00, 31.15),
('Dr. Mostafa Nabil', 8, 30.03, 31.35),
('Dr. Mariam Adel', 6, 30.04, 31.27),
('Dr. Osama Ehab', 9, 30.07, 31.24);

-- 2. Insert 30 Patients
DECLARE @i INT = 1;
WHILE @i <= 30
BEGIN
    INSERT INTO Patients (FullName, Gender, DateOfBirth)
    VALUES (
        CONCAT('Patient_', @i),
        CASE WHEN @i % 2 = 0 THEN 'Male' ELSE 'Female' END,
        DATEADD(DAY, -365 * (20 + (@i % 30)), GETDATE())
    );
    SET @i += 1;
END;

-- 3. Insert Medical Conditions
INSERT INTO MedicalHistory (ConditionName)
VALUES
('Asthma'),
('Diabetes'),
('Hypertension'),
('Heart Disease'),
('Arthritis'),
('Cancer'),
('Chronic Pain'),
('Epilepsy'),
('Multiple Sclerosis'),
('COPD (Chronic Obstructive Pulmonary Disease)'),
('Stroke'),
('Depression'),
('Anxiety Disorders'),
('Osteoporosis'),
('Ulcerative Colitis'),
('Crohn''s Disease'),
('Parkinson''s Disease'),
('AIDS/HIV'),
('Obesity'),
('Hyperthyroidism'),
('Hypothyroidism'),
('Chronic Kidney Disease');

-- 4. Assign 1–3 Random Conditions to Each Patient
DECLARE @pid INT, @totalConditions INT, @p INT;
SELECT @totalConditions = COUNT(*) FROM MedicalHistory;

SET @p = 1;
WHILE @p <= 30
BEGIN
    DECLARE @numConditions INT = 1 + ABS(CHECKSUM(NEWID())) % 3;
    DECLARE @j INT = 1;
    WHILE @j <= @numConditions
    BEGIN
        DECLARE @conditionID INT = 1 + ABS(CHECKSUM(NEWID())) % @totalConditions;
        IF NOT EXISTS (
            SELECT 1 FROM PatientMedicalHistory WHERE PatientID = @p AND MedicalHistoryID = @conditionID
        )
        BEGIN
            INSERT INTO PatientMedicalHistory (PatientID, MedicalHistoryID)
            VALUES (@p, @conditionID);
        END
        SET @j += 1;
    END
    SET @p += 1;
END;


-- 5. Assign Random Ratings to Doctors from Patients
-- Each patient gives 1 to 3 ratings
DECLARE @r INT;
SET @r = 1;
WHILE @r <= 30
BEGIN
    DECLARE @numRatings INT = 1 + ABS(CHECKSUM(NEWID())) % 3, @l INT;
    SET @l = 1;
    WHILE @l <= @numRatings
    BEGIN
        DECLARE @doctorID INT = 1 + ABS(CHECKSUM(NEWID())) % 10;
        DECLARE @rating FLOAT = CAST((ABS(CHECKSUM(NEWID())) % 50) AS FLOAT) / 10.0; -- from 0.0 to 5.0

        IF NOT EXISTS (
            SELECT 1 FROM Ratings WHERE PatientID = @r AND DoctorID = @doctorID
        )
        BEGIN
            INSERT INTO Ratings (PatientID, DoctorID, NormalizedRating)
            VALUES (@r, @doctorID, @rating);
        END

        SET @l += 1;
    END
    SET @r += 1;
END;

SELECT p.PatientID, mh.ConditionName
    FROM Patients p
    JOIN PatientMedicalHistory pmh ON p.PatientID = pmh.PatientID
    JOIN MedicalHistory mh ON pmh.MedicalHistoryID = mh.MedicalHistoryID
	WHERE p.PatientID = 2


INSERT INTO Doctors (FullName, ExperienceYears, Latitude, Longitude)
VALUES
('Dr. Mahmoud Ali', 10, 30.05, 31.25)

--DELETE FROM Doctors
--WHERE DoctorID = 13