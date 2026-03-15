from flask_babel import get_locale
from src import create_app

app = create_app()

with app.test_request_context(headers={"Accept-Language": "zh-CN,zh;q=0.9"}):
    current_locale = get_locale()
    print(f"Current locale: {current_locale}")
    print(f"Type: {type(current_locale)}")
    print(f"String representation: {str(current_locale)}")
