from psych.factory import create_app
from psych.db import disorders_init

import os
import configparser


config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))

if __name__ == "__main__":
    app = create_app()
    app.config['DEBUG'] = True
    app.config['MONGO_URI'] = config['PROD']['DB_URI']

    with app.app_context():
        disorders_init()
        print("DB connected!")
        print("DB init!")
    
    app.run()