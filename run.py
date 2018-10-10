from flask import Flask
from flasgger import Swagger
from news18.controllers import news18_blueprint
from news18.jobs import news18_jobs
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)
swagger = Swagger(app)
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=news18_jobs, trigger='interval', minutes=2, max_instances=3)
scheduler.start()

app.register_blueprint(news18_blueprint, url_prefix='/api/v1/news18')

if __name__ == '__main__':
    app.run(debug=True)