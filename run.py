from psych.factory import create_app
from psych.db import disorders_init, accounts_init, update_status, videos_init, appointments_init

import os
import configparser

from datetime import datetime, timedelta
from flask_apscheduler import APScheduler

from flask_mail import Mail

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))


class Config:
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()
mail = Mail()

# interval examples
@scheduler.task("interval", id="status_update", seconds=60)
def status_update():
    with scheduler.app.app_context():
        current_time = (datetime.now() + timedelta(hours=1)
                        ).strftime('%Y/%m/%d_%H')
        print(f"TRY TO UPDATE ACTIVE APPOINMENTS WITH {current_time} ...")
        update_status(machine_time=current_time, mail=mail)
        


if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = False
    app.config['MONGO_URI'] = config['PROD']['DB_URI']

    with app.app_context():
        disorders_init()
        accounts_init()
        videos_init()
        appointments_init()
        print("DB connected!")
        print("DB init!")

    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()

    app.config['SENDER_TUPLE_1'] = config['PROD']['MAIL_SENDER']
    app.config['SENDER_TUPLE_2'] = config['PROD']['MAIL_USERNAME']
    
    app.config.update(
        # EMAIL SETTINGS
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_DEFAULT_SENDER=(app.config['SENDER_TUPLE_1'], app.config['SENDER_TUPLE_2']),
        MAIL_MAX_EMAILS=10,
        MAIL_USERNAME=config['PROD']['MAIL_USERNAME'],
        MAIL_PASSWORD=config['PROD']['MAIL_PASSWORD']
    )
    mail.init_app(app)
    app.run()
