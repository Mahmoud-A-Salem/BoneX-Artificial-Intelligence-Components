from geopy.distance import geodesic

def calculate_distance(user_location, doctor_location):
    return geodesic(user_location, doctor_location).km  # Returns distance in kilometers

