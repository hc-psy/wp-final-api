from psych.factory import create_app
from psych.db import disorders_init, accounts_init, update_status, videos_init

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
        update_status(machine_time=current_time, mail=mail)
        print(f"UPDATE ACTIVE APPOINMENTS WITH {current_time}")


if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = False
    app.config['MONGO_URI'] = config['PROD']['DB_URI']

    with app.app_context():
        disorders_init()
        accounts_init()
        videos_init()
        print("DB connected!")
        print("DB init!")

    app.config.from_object(Config())
    scheduler.init_app(app)
    scheduler.start()

    app.config.update(
        # EMAIL SETTINGS
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_DEFAULT_SENDER=('BeBetter', 'bebetter.app.tw@gmail.com'),
        MAIL_MAX_EMAILS=10,
        MAIL_USERNAME='bebetter.app.tw@gmail.com',
        MAIL_PASSWORD='quljeawrfvcehvne'
    )
    mail.init_app(app)
    app.run()
