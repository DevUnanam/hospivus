from django.core.management.base import BaseCommand
import os
import fileinput

class Command(BaseCommand):
    help = 'Renames the Django project references within the config directory and updates project files'

    def add_arguments(self, parser):
        parser.add_argument('old_project_name', type=str, help='The old Django project name')
        parser.add_argument('new_project_name', type=str, help='The new Django project name')

    def handle(self, *args, **kwargs):
        old_project_name = kwargs['old_project_name']
        new_project_name = kwargs['new_project_name']

        # Check if the command is being run from the correct location
        if not os.path.isdir('config') or not os.path.isdir(old_project_name):
            self.stdout.write(self.style.ERROR(
                "Please make sure the command is run from the directory containing the 'config' and "
                f"'{old_project_name}' directories."
            ))
            return

        # Update manage.py to use the new settings path
        manage_file_path = 'manage.py'
        with fileinput.FileInput(manage_file_path, inplace=True) as file:
            for line in file:
                print(line.replace(f"{old_project_name}.settings", f"{new_project_name}.settings"), end='')

        # Update settings module path in wsgi.py, asgi.py, and settings.py
        project_files_to_update = [
            os.path.join(old_project_name, 'wsgi.py'),
            os.path.join(old_project_name, 'asgi.py'),
            os.path.join(old_project_name, 'settings.py'),
        ]

        for file_path in project_files_to_update:
            with fileinput.FileInput(file_path, inplace=True) as file:
                for line in file:
                    print(line.replace(f"{old_project_name}.settings", f"{new_project_name}.settings"), end='')

        # Update files in the config directory
        config_files_to_update = [
            os.path.join('config', 'base.py'),
            os.path.join('config', 'development.py'),
            os.path.join('config', 'production.py'),
        ]

        for config_file in config_files_to_update:
            with fileinput.FileInput(config_file, inplace=True) as file:
                for line in file:
                    print(line.replace(old_project_name, new_project_name), end='')

        # Check and rename the old project directory if it exists
        if os.path.isdir(old_project_name):
            os.rename(old_project_name, new_project_name)

        self.stdout.write(self.style.SUCCESS(
            f"Your Project '{old_project_name}' have been updated to '{new_project_name}'."
        ))
