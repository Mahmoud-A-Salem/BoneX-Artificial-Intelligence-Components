from flask import Flask, request
import schedule
import time
import threading

from recommender import fetch_latest_data, recommend_doctors

app = Flask(__name__)

scheduler_started = False

# Scheduler loop
def run_scheduler():
    schedule.clear()
    schedule.every(30).seconds.do(fetch_latest_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a background thread
def start_scheduler():
    global scheduler_started
    if not scheduler_started:
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        scheduler_started = True

@app.route('/', methods=['GET'])
def home():
    return "Doctor Recommendation System Running..."


@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_id = int(request.form['user_id'])
        location_str = request.form['user_location']
        user_location = tuple(map(float, location_str.split(',')))

        recommended_doctors = recommend_doctors(user_id=user_id, user_location=user_location)

        return recommended_doctors.to_json(orient='records')
    except Exception as e:
        return {"error": str(e)}, 400  # Return error message in case of failure


if __name__ == '__main__':
    fetch_latest_data() # Fetch the data initially
    start_scheduler()  # Start scheduler BEFORE starting the Flask app
    app.run(debug=True, use_reloader=False)
