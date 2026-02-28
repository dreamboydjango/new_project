import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketplace.models import Product

def check_images():
    products = Product.objects.all()
    total = products.count()
    with_image = products.exclude(image='').exclude(image=None).count()
    without_image = total - with_image
    
    print(f"Total Products: {total}")
    print(f"Products with Images: {with_image}")
    print(f"Products WITHOUT Images: {without_image}")
    
    if without_image > 0:
        print("\nProducts missing images:")
        for p in products.filter(django.db.models.Q(image='') | django.db.models.Q(image=None)):
            print(f"- {p.name} (ID: {p.id})")

if __name__ == '__main__':
    check_images()
