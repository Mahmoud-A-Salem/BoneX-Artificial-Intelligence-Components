from flask import Flask, request, Response
import json

from recommender import recommend_doctors

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Doctor Recommendation System Running..."


@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        location_str = request.form['user_location']
        user_location = tuple(map(float, location_str.split(',')))

        recommended_doctors = recommend_doctors(user_location=user_location)

        # Convert the DataFrame to JSON
        json_data = recommended_doctors.to_json(orient='records')

        return Response(json_data, mimetype='application/json')
    except Exception as e:
        return {"error": str(e)}, 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)