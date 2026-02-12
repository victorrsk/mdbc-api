from src.schemas.schemas import UserIn

def clean_user_data(user: UserIn):
    user.username = user.username.lower().replace(' ', '')
    user.email = user.email.replace(' ', '')
    user.password = user.password.replace(' ', '')

    return user
