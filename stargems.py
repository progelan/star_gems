from app import app




# для сеанса в оболочке:
from app import app, db
from app.models import User, Preference, Gem, TypeGem
from werkzeug.security import generate_password_hash
from datetime import datetime

@app.shell_context_processor
def make_shell_context():
    return {
            'db': db,
            'User': User,
            'generate_password_hash': generate_password_hash,
            'Preference': Preference,
            'Gem': Gem,
            'datetime': datetime,
            'TypeGem': TypeGem,
            }
