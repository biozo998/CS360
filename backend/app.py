import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from sync import main as run_etl_sync
from api.routes import api_bp

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) # Enable CORS for frontend connection

# Register the Blueprint
app.register_blueprint(api_bp)

def job_daily_sync():
    logger.info("Scheduler Triggered: Running ETL sync...")
    run_etl_sync()

# Configure APScheduler
scheduler = BackgroundScheduler()
# Run daily at 07:30 and 13:00 on weekdays (Mon-Fri)
scheduler.add_job(job_daily_sync, 'cron', day_of_week='mon-fri', hour='7,13', minute='30,0')
scheduler.start()

@app.route("/api/v1/health")
def health_check():
    return jsonify({"status": "ok", "service": "Backend ETL Engine"})

@app.route("/api/v1/sync/manual", methods=["POST"])
def trigger_manual_sync():
    # In a real scenario, you might want to run this asynchronously (e.g., Celery) to not block the request
    # For now, we will just call it synchronously for testing purposes.
    logger.info("Manual sync triggered via API")
    try:
        run_etl_sync()
        return jsonify({"status": "success", "message": "Manual sync completed."})
    except Exception as e:
        logger.error(f"Manual sync failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    logger.info(f"Starting Backend Server on port {config.PORT}...")
    try:
        app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG, use_reloader=False) # use_reloader=False prevents double scheduler initiation
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
