import uuid
from pathlib import Path
import json

# The file that has the user's data
user_data = Path('user_data.json')

# Checks if user data exists
if not user_data.exists():
    with open(user_data, 'w') as f:
        json.dump({"users": {}}, f)

