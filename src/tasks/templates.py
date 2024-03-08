from email.message import EmailMessage

from src.auth.models import User
from src.config import config


def get_email_template_register(
        username: str, user_email: str
) -> EmailMessage:
    email = EmailMessage()
    email['Subject'] = 'Регистрация пользователя'
    email['From'] = config.SMTP_USER
    email['To'] = user_email

    email.set_content(
        '<div>'
            f'<h1>Здравствуйте, {username}, спасибо за регистрацию на сайте NoteVi.</h1>'
            '<img src="https://telecomdom.com/wp-content/uploads/2019/12/company-online-registration-spain_1519046020.jpg" width="600">'
        '</div>',
        subtype='html'
    )
    return email


def get_email_template_verify(
        username: str, user_email: str, token: str
) -> EmailMessage:
    email = EmailMessage()
    email['Subject'] = 'Верификация пользователя NoteVi'
    email['From'] = config.SMTP_USER
    email['To'] = user_email

    email.set_content(
        '<div>'
            f'<h1>Здравствуйте, {username}, вы запросили верификацию на сайте NoteVi.</h1>'
            '<p>Подтвердите свою почту, перейдя по ссылке.</p>'
            f'<a href="{config.APP_URL}/api/v{config.APP_VERSION}/auth/accept?token={token}">'
                'Подтвердить регистрацию'
            '</a>'
        '</div>',
        subtype='html'
    )

    # email.add_related(requests.post, 'text', 'html', cid='verification-link', encoding='utf-8')
    return email
