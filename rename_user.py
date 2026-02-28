import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

def rename():
    old_username = 'Kamal_swathi18'
    new_username = 'Kamal18'
    
    try:
        user = User.objects.get(username=old_username)
        user.username = new_username
        user.save()
        print(f"Successfully renamed user '{old_username}' to '{new_username}'.")
    except User.DoesNotExist:
        print(f"User '{old_username}' not found. It might have already been renamed.")
    except Exception as e:
        print(f"Error renaming user: {e}")

if __name__ == '__main__':
    rename()
