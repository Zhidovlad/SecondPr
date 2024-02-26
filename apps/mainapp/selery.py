from flask import Flask, jsonify, request
from celery import Celery
from flask_mail import Mail, Message

app = Flask(__name__)

# Настройки Flask-Mail
app.config['MAIL_SERVER'] = 'your_mail_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

# Настройка Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Настройка Flask-Mail
mail = Mail(app)

# Пример асинхронной задачи для отправки электронной почты
@celery.task
def send_email(subject, recipients, body):
    with app.app_context():
        message = Message(subject=subject, recipients=recipients, body=body)
        mail.send(message)

# Пример REST-маршрута для отправки электронной почты
@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.json
    subject = data.get('subject')
    recipients = data.get('recipients')
    body = data.get('body')

    # Запуск асинхронной задачи для отправки электронной почты
    send_email.apply_async(args=[subject, recipients, body])

    return jsonify({'status': 'Email will be sent asynchronously.'}), 202

if __name__ == '__main__':
    app.run(debug=True)
