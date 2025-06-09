import pandas as pd
from geopy.distance import geodesic
from sklearn.metrics.pairwise import cosine_similarity
from surprise import Reader, Dataset, SVD

def get_user_medical_history(user_id, patients_medical_history_df):
    patient_conditions = patients_medical_history_df[patients_medical_history_df['PatientID'] == user_id]

    if patient_conditions.empty:
        condition_columns = patients_medical_history_df.columns[patients_medical_history_df.columns != 'PatientID']
        empty_data = pd.DataFrame([[0] * len(condition_columns)], columns=condition_columns)
        patient_conditions = pd.concat([pd.DataFrame({'PatientID': [user_id]}), empty_data], axis=1)

    return patient_conditions.drop(columns='PatientID').values.flatten()


def build_doctor_condition_matrix(doctors_df, patients_to_doctors_ratings_df, patients_medical_history_df):
    # Step 1: Merge all doctors with patients_to_doctors_ratings
    all_doctor_even_if_without_patient_yet = pd.merge(
        doctors_df[['DoctorID']],
        patients_to_doctors_ratings_df[['DoctorID', 'PatientID']],
        on='DoctorID', how='left'
    )

    # Step 2: Fill missing PatientIDs with -1 to mark doctor who has no patient
    doctor_patient_data = all_doctor_even_if_without_patient_yet.fillna({'PatientID': -1})

    # Step 3: Merge with patients' medical history
    doctor_patient_data = pd.merge(
        doctor_patient_data,
        patients_medical_history_df,
        on='PatientID',
        how='left'
    )

    # Step 4: Fill missing medical history with 0 (patients with no medical history)
    doctor_patient_data = doctor_patient_data.fillna(0)

    # Step 5: Calculate the total number of patients each doctor has treated (even if medical history is missing)
    patient_counts = doctor_patient_data.groupby('DoctorID')['PatientID'].count()

    # Step 6: Drop PatientID before performing the division
    doctor_patient_data.drop(columns=['PatientID'], inplace=True)

    # Step 7: Group by DoctorID and sum condition counts
    doctor_condition_counts = doctor_patient_data.groupby('DoctorID').sum()

    # Step 8: Normalize using total number of patients treated (even if medical history is missing)
    normalized_condition_counts = doctor_condition_counts.div(patient_counts, axis=0)

    return normalized_condition_counts


def calculate_similarity(patient_conditions, doctor_conditions_matrix):
    # Reshape the user conditions to a 2D array (1, n_features)
    patient_conditions = patient_conditions.reshape(1, -1)

    # Calculate cosine similarity between user conditions and doctor conditions
    similarity_scores = cosine_similarity(patient_conditions, doctor_conditions_matrix)

    # Flatten the similarity scores into a 1D array
    similarity_scores = similarity_scores.flatten()

    return similarity_scores

def calculate_distance(user_location, doctor_location):
    return geodesic(user_location, doctor_location).km  # Returns distance in kilometers

def collaborative_filtering(ratings_df):
    # Initialize the reader to specify the scale of the ratings
    reader = Reader(rating_scale=(1, 5))
    # Load the ratings data into Surprise's Dataset object
    data = Dataset.load_from_df(ratings_df[["PatientID", "DoctorID", "NormalizedRating"]], reader)

    # Use SVD (Singular Value Decomposition) algorithm
    algo = SVD()

    # Fit the model on the full dataset
    trainset = data.build_full_trainset()
    algo.fit(trainset)

    return algo

