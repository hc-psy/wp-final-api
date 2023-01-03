from psych.factory import create_app
from psych.db import disorders_init, accounts_init, update_status, videos_init

import os
import configparser

from datetime import datetime, timedelta
from flask_apscheduler import APScheduler

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))


class Config:
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()


# interval examples
@scheduler.task("interval", id="status_update", seconds=60)
def status_update():
    with scheduler.app.app_context():
        current_time = (datetime.now() + timedelta(hours=1)
                        ).strftime('%Y/%m/%d_%H')
        update_status(machine_time=current_time)
        print(f"UPDATE ACTIVE APPOINMENTS WITH {current_time}")


if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True
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

    app.run()
