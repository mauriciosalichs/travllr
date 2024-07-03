from flask_script import Manager
from flask_migrate import MigrateCommand
from app import app, db  # Importa tu aplicación y la instancia de SQLAlchemy

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()