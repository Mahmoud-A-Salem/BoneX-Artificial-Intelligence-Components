from db import get_connection
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

conn = get_connection()

def get_doctors():
    query = ''' SELECT [DoctorID]
      ,[FullName]
      ,[ExperienceYears]
      ,[Latitude]
      ,[Longitude]
      ,[Rating]
      ,[NumberOfReviews] FROM Doctors 
    '''
    return pd.read_sql(query, conn)

# def get_patients():
#     query = ''' SELECT [PatientID]
#                  ,CASE WHEN Gender = 'Female' THEN 0 ELSE 1 END AS Gender
#                  ,DATEDIFF(YEAR, [DateOfBirth], GETDATE()) AS Age
#                FROM Patients
#     '''
#     return pd.read_sql(query, conn)

def get_ratings():
    query = ''' SELECT * FROM Ratings'''
    return pd.read_sql(query, conn)

def get_all_conditions():
    query = '''
    SELECT DISTINCT ConditionName
    FROM MedicalHistory
    '''
    return pd.read_sql(query, conn)

def get_patients_medical_history():
    # Get all condition names
    conditions_df = get_all_conditions()
    conditions = conditions_df['ConditionName'].tolist()  # List of condition names

    # Get patients with their medical history
    query = '''
    SELECT p.PatientID, mh.ConditionName
    FROM Patients p
    JOIN PatientMedicalHistory pmh ON p.PatientID = pmh.PatientID
    JOIN MedicalHistory mh ON pmh.MedicalHistoryID = mh.MedicalHistoryID
    '''
    patient_conditions_df = pd.read_sql(query, conn)

    # Initialize the binary matrix with zeros
    patient_condition_matrix = pd.DataFrame(0, index=patient_conditions_df['PatientID'].unique(), columns=conditions)

    # Define a function to apply to each row
    def populate_condition(row):
        # Set the corresponding condition for the patient to 1
        patient_condition_matrix.at[row['PatientID'], row['ConditionName']] = 1

    # Apply the function to each row of the patient_conditions_df
    patient_conditions_df.apply(populate_condition, axis=1)

    patient_condition_matrix.reset_index(inplace=True)
    patient_condition_matrix.rename(columns={'index': 'PatientID'}, inplace=True)

    return patient_condition_matrix


