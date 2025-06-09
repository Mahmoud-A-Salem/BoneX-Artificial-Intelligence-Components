import threading
import time
import pandas as pd
from data_fetching_functions import get_doctors, get_ratings, get_patients_medical_history
import numpy as np
from helper_functions import get_user_medical_history, build_doctor_condition_matrix, calculate_similarity, \
    calculate_distance, collaborative_filtering


doctors_df = pd.DataFrame()
patients_to_doctors_ratings_df = pd.DataFrame()
patients_medical_history_df = pd.DataFrame()

data_lock = threading.Lock()


def fetch_latest_data():
    with data_lock:
        global doctors_df, patients_to_doctors_ratings_df, patients_medical_history_df
        doctors_df = get_doctors()
        patients_to_doctors_ratings_df = get_ratings()
        patients_medical_history_df = get_patients_medical_history()
        print("Data refreshed! at: " + str(time.time()))


def recommend_doctors(user_id, user_location):
    patient_conditions = get_user_medical_history(user_id, patients_medical_history_df)

    doctor_treated_conditions_matrix = build_doctor_condition_matrix(doctors_df, patients_to_doctors_ratings_df, patients_medical_history_df)


    # Step 1: Calculate condition-based similarity
    doctor_similarity = calculate_similarity(patient_conditions, doctor_treated_conditions_matrix)


    # Step 2: Calculate proximity scores
    proximity_scores = []
    distances = []

    for doctor_id in doctors_df['DoctorID'].tolist():
        doctor_location = doctors_df[doctors_df['DoctorID'] == doctor_id][['Latitude', 'Longitude']].values.flatten()
        distance = calculate_distance(user_location, doctor_location)
        distances.append(distance)

    threshold_distance = 1

    for distance in distances:
        if distance == 0:
            # If the distance is zero, assign the highest proximity score (1)
            proximity_scores.append(1)
        elif distance < threshold_distance:
            # If the distance is less than 1 km, assign a high proximity score (1)
            proximity_scores.append(1)
        else:
            # Otherwise, calculate the inverse of the distance
            proximity_scores.append(1 / distance)


    # Step 3: Collaborative Filtering (Predict ratings using SVD)
    svd_model = collaborative_filtering(patients_to_doctors_ratings_df)  # Get the trained model
    predicted_ratings = []

    doctor_ids_set = set(patients_to_doctors_ratings_df['DoctorID'])
    user_ids_set = set(patients_to_doctors_ratings_df['PatientID'])

    avg_rating = patients_to_doctors_ratings_df['NormalizedRating'].mean()

    for doctor_id in doctors_df['DoctorID']:
        if doctor_id not in doctor_ids_set or user_id not in user_ids_set:
            predicted_ratings.append(avg_rating)
            continue
        # Predict the rating for the current user (patient) and doctor
        predicted_rating = svd_model.predict(user_id, doctor_id).est
        predicted_ratings.append(predicted_rating)


    # Step 4: Normalize experience years
    exp_values = doctors_df['ExperienceYears'].tolist()
    min_exp = min(exp_values)
    max_exp = max(exp_values)
    experience_scores = [(exp - min_exp) / (max_exp - min_exp) if max_exp != min_exp else 1 for exp in exp_values]


    # Step 5: Combine similarity, proximity, and collaborative filtering scores, experience score
    final_scores = []
    for i in range(len(doctor_similarity)):
        score = (
                doctor_similarity[i] * 0.35 +  # Weighted similarity score
                proximity_scores[i] * 0.20 +  # Weighted proximity score
                predicted_ratings[i] * 0.35 + # Weighted collaborative filtering score
                experience_scores[i] * 0.10  # Weight for experience
        )
        final_scores.append(score)


    # Step 6: Return top recommended doctors based on final scores
    recommended_doctors_indices = np.argsort(final_scores)[::-1]  # Sort in descending order
    recommended_doctors = doctors_df.iloc[recommended_doctors_indices]  # Get top N doctors

    distances_df = pd.DataFrame(distances, columns=['distance (Km)'])
    recommended_doctors = pd.concat([recommended_doctors, distances_df], axis=1)

    recommended_doctors.drop(columns=['DoctorID', 'Latitude', 'Longitude'], inplace=True)
    recommended_doctors.rename(columns={'FullName': 'Doctor Name', 'NumberOfReviews': 'Reviews'}, inplace=True)

    return recommended_doctors.reset_index(drop=True)