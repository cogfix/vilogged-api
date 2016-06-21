from subprocess import call

def run_migrate():
    call(['python', 'manage.py', 'migrate'])

def set_up_default_user(model):
    try:
        users = model.objects.all()
        if len(users) == 0:
            model(
                username='admin',
                password='test',
                email='admin@vilogged.com'
            )
    except Exception as e:
        print (e)

from django.apps import AppConfig
class MyAppConfig(AppConfig):
    name = 'myapp'
    verbose_name = "My Application"
    def ready(self):
        try:
            run_migrate()
        except Exception as e:
            print (e)