from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.models.users import User
from src.security import Settings

config = ConnectionConfig(
    MAIL_USERNAME=Settings().MAIL_FROM,
    MAIL_PASSWORD=Settings().MAIL_PASSWORD,
    MAIL_FROM=Settings().MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_FROM_NAME='My Digital Books Collection',
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_email(user: User):
    user.username = user.username.replace('-', ' ')
    body_content = f"""
    <h3>Congrats! You're now registered in My Digital Books Collection!</h3></br>
    <p>You're logged as <b>{user.username}</b> with <b>{user.email}</b></p>
    """
    message = MessageSchema(
        body=body_content,
        subject='Signed in the collection',
        subtype=MessageType.html,
        recipients=[user.email],
    )

    fm = FastMail(config)
    await fm.send_message(message)
