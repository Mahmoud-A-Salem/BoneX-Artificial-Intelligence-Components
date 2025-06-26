import pandas as pd
import numpy as np
from helper_functions import calculate_distance


raw_data = [
    {"doctorId": "0818ceb3-3005-42c7-b7fd-dec77956d2f7", "yearsOfExperience": 9, "rating": 0, "latitude": 35.5, "longitude": 35.5},
    {"doctorId": "1192ae1b-4ba6-4599-9d62-34abc016cda1", "yearsOfExperience": 7, "rating": 0, "latitude": 0, "longitude": 0},
    {"doctorId": "1a411200-b7d5-4ba4-85f5-6267fac23b3f", "yearsOfExperience": 9, "rating": 0, "latitude": 35.5, "longitude": 35.5},
    {"doctorId": "29bdfc5d-384b-478d-b249-45b0499a57aa", "yearsOfExperience": 5, "rating": 0, "latitude": 1, "longitude": 1},
    {"doctorId": "65ea349b-4663-49b0-87d3-c951fc556ee4", "yearsOfExperience": 4, "rating": 0, "latitude": 29.9932668, "longitude": 31.3072233},
    {"doctorId": "6a9dc8dc-3c1d-4b87-9bf4-e03f939825b8", "yearsOfExperience": 15, "rating": 0, "latitude": 35.2, "longitude": 33.2},
    {"doctorId": "84c1500c-e578-4bae-b7b2-307bf2d3f6e1", "yearsOfExperience": 12, "rating": 3.5, "latitude": 0, "longitude": 0},
    {"doctorId": "b9999085-ded2-43b8-8486-940a1363bb34", "yearsOfExperience": 20, "rating": 0, "latitude": 30.0444, "longitude": 31.2357},
    {"doctorId": "c49fa15a-41f9-4842-ae4e-9f2b9fedfe88", "yearsOfExperience": 10, "rating": 0, "latitude": 37.5, "longitude": 37.5},
    {"doctorId": "d984b1cf-d9d0-43d3-a84b-c0e9779fa4db", "yearsOfExperience": 6, "rating": 0, "latitude": 29.9933707, "longitude": 31.3071971},
    {"doctorId": "dd23d059-6e71-4e4c-a712-e59ebe1c05f8", "yearsOfExperience": 20, "rating": 0, "latitude": 30.0444, "longitude": 31.2357},
    {"doctorId": "e8a38de2-c709-436c-9d73-ad1a981bcc39", "yearsOfExperience": 14, "rating": 0, "latitude": 29.9932272, "longitude": 31.3072329},
    {"doctorId": "e9c03f3a-664b-4ab3-9c91-e3a0cfa86cba", "yearsOfExperience": 4, "rating": 0, "latitude": 29.9739715, "longitude": 31.3427151},
    {"doctorId": "fca36747-574b-4140-b23b-03bae9f17a16", "yearsOfExperience": 20, "rating": 5, "latitude": 30.0444, "longitude": 31.2357}
]


doctors_df = pd.DataFrame(raw_data).rename(columns={
    'doctorId': 'DoctorID',
    'yearsOfExperience': 'ExperienceYears',
    'latitude': 'Latitude',
    'longitude': 'Longitude',
    'rating': 'Rating'
})

def recommend_doctors(user_location):

    # Calculate proximity scores
    proximity_scores = []
    distances = []

    for doctor_id in doctors_df['DoctorID'].tolist():
        doctor_location = doctors_df[doctors_df['DoctorID'] == doctor_id][['Latitude', 'Longitude']].values.flatten()
        distance = calculate_distance(user_location, doctor_location)
        distances.append(distance)

    doctors_df['Distance'] = distances

    threshold_distance = 1

    for distance in distances:
        if distance < threshold_distance:
            # If the distance is less than 1 km, assign a high proximity score (1)
            proximity_scores.append(1)
        else:
            # Otherwise, calculate the inverse of the distance
            proximity_scores.append(1 / distance)



    # Normalize Ratings
    rating_values = doctors_df['Rating'].tolist()
    min_rating = min(rating_values)
    max_rating = max(rating_values)
    normalized_ratings = [(exp - min_rating) / (max_rating - min_rating) if max_rating != min_rating else 1 for exp in rating_values]


    # Normalize experience years
    exp_values = doctors_df['ExperienceYears'].tolist()
    min_exp = min(exp_values)
    max_exp = max(exp_values)
    experience_scores = [(exp - min_exp) / (max_exp - min_exp) if max_exp != min_exp else 1 for exp in exp_values]


    # Combine proximity, experience score, rating
    final_scores = []
    for i in range(len(doctors_df['DoctorID'])):
        score = (
                proximity_scores[i] * 0.40 +  # Weighted proximity score
                normalized_ratings[i] * 0.30 + # Weighted collaborative filtering score
                experience_scores[i] * 0.30  # Weight for experience
        )
        final_scores.append(score)


    # Return recommended doctors based on final scores
    recommended_doctors_indices = np.argsort(final_scores)[::-1]  # Sort in descending order
    recommended_doctors = doctors_df[["DoctorID", "Distance"]].iloc[recommended_doctors_indices]

    return recommended_doctors.astype({'DoctorID': 'str'}).reset_index(drop=True)