import os
import django
import random
import urllib.request
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from marketplace.models import Category, Product
from django.db import transaction

# Ensure products media directory exists
MEDIA_DIR = Path('media/products')
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

@transaction.atomic
def run():
    # 1. Ensure Users Exist
    users_data = [
        {'username': 'Kamal18', 'password': 'User@0618', 'email': 'swathikamal8@gmail.com', 'role': User.SELLER},
        {'username': 'Owner@08', 'password': 'Admin@0618', 'email': 'Admin18@gmail.com', 'role': User.ADMIN}
    ]

    users = {}
    for data in users_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={'email': data['email'], 'role': data['role']}
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"User {user.username} created.")
        users[data['username']] = user

    # 2. Ensure Categories Exist
    categories = ['Electronics', 'Fashion', 'Home Decor', 'Handicrafts', 'Organic Food']
    cat_objs = {}
    for cat_name in categories:
        cat, created = Category.objects.get_or_create(name=cat_name)
        cat_objs[cat_name] = cat

    # 3. Bulk Products Data (Approx 55)
    products_input = [
        # Missing/Original Products
        ('Handmade Silk Saree', 'Exquisite hand-woven silk saree with traditional patterns.', 5000, 'Handicrafts'),
        ('Pure Honey (500g)', '100% natural, unfiltered wild honey.', 450, 'Organic Food'),
        ('Eco-friendly Bamboo Lamp', 'Sustainable and stylish lighting for your home.', 1200, 'Home Decor'),
        ('Smart Solar Charger', 'Portable solar panel for charging devices on the go.', 1500, 'Electronics'),

        # Electronics
        ('Wireless Earbuds', 'High-quality sound with noise cancellation.', 1500, 'Electronics'),
        ('Smart Watch', 'Track your health and notifications.', 2500, 'Electronics'),
        ('Portable Power Bank', '10000mAh fast charging.', 800, 'Electronics'),
        ('Bluetooth Speaker', 'Compact with powerful bass.', 1200, 'Electronics'),
        ('USB-C Hub', 'Multi-port adapter for laptops.', 600, 'Electronics'),
        ('LED Desk Lamp', 'Adjustable brightness and color.', 450, 'Electronics'),
        ('Wireless Mouse', 'Ergonomic design for comfort.', 350, 'Electronics'),
        ('Gaming Mousepad', 'Large surface for smooth movement.', 250, 'Electronics'),
        ('Phone Tripod', 'Flexible legs for any surface.', 200, 'Electronics'),
        ('Screen Cleaner Kit', 'For laptops and smartphones.', 150, 'Electronics'),
        
        # Fashion
        ('Cotton T-Shirt', '100% organic cotton, breathable.', 400, 'Fashion'),
        ('Denim Jacket', 'Classic style for all seasons.', 1800, 'Fashion'),
        ('Leather Wallet', 'Slim and durable.', 700, 'Fashion'),
        ('Sunglasses', 'UV protection with stylish frames.', 550, 'Fashion'),
        ('Canvas Sneakers', 'Casual and comfortable footwear.', 900, 'Fashion'),
        ('Woolen Scarf', 'Warm and soft for winter.', 300, 'Fashion'),
        ('Formal Shirt', 'Perfect for office wear.', 1200, 'Fashion'),
        ('Running Shoes', 'Lightweight with great grip.', 2200, 'Fashion'),
        ('Backpack', 'Spacious with laptop compartment.', 1500, 'Fashion'),
        ('Wristband', 'Simple accessory for daily wear.', 100, 'Fashion'),
 
        # Home Decor
        ('Scented Candle', 'Lavender fragrance for relaxation.', 250, 'Home Decor'),
        ('Wall Clock', 'Modern minimalist design.', 800, 'Home Decor'),
        ('Throw Pillow', 'Soft velvet cover.', 400, 'Home Decor'),
        ('Picture Frame', 'Classic wooden frame.', 350, 'Home Decor'),
        ('Indoor Plant Pot', 'Ceramic with elegant finish.', 600, 'Home Decor'),
        ('Table Runner', 'Hand-woven cotton.', 450, 'Home Decor'),
        ('Vase', 'Hand-blown glass.', 700, 'Home Decor'),
        ('Fairy Lights', 'Warm white glow for cozy nights.', 200, 'Home Decor'),
        ('Dreamcatcher', 'Traditional handmade design.', 300, 'Home Decor'),
        ('Curtain Set', 'Blackout fabric for privacy.', 1800, 'Home Decor'),
 
        # Handicrafts
        ('Clay Pottery Set', 'Eco-friendly kitchenware.', 1200, 'Handicrafts'),
        ('Embroidered Bag', 'Traditional patterns from local artisans.', 850, 'Handicrafts'),
        ('Wooden Carved Figurine', 'Intricate detail, handmade.', 1500, 'Handicrafts'),
        ('Paper Mache Box', 'Decorative storage.', 400, 'Handicrafts'),
        ('Bamboo Basket', 'Natural and sustainable.', 500, 'Handicrafts'),
        ('Metal Art Piece', 'Unique wall hanging.', 2000, 'Handicrafts'),
        ('Beaded Jewelry Kit', 'DIY craft for kids.', 350, 'Handicrafts'),
        ('Terracotta Lamp', 'Rustic look for your home.', 650, 'Handicrafts'),
        ('Hand-painted Coasters', 'Set of 4 vibrant designs.', 300, 'Handicrafts'),
        ('Traditional Mask', 'Cultural wall decor.', 1100, 'Handicrafts'),
 
        # Organic Food
        ('Organic Green Tea', 'Rich in antioxidants.', 350, 'Organic Food'),
        ('Raw Almonds (250g)', 'Natural and crunchy.', 450, 'Organic Food'),
        ('Wildflower Honey', 'Unfiltered and pure.', 550, 'Organic Food'),
        ('Quinoa Seeds (500g)', 'Superfood for healthy meals.', 600, 'Organic Food'),
        ('Coconut Oil (1L)', 'Cold-pressed organic.', 700, 'Organic Food'),
        ('Dried Figs', 'Sweet and nutritious.', 400, 'Organic Food'),
        ('Himalayan Pink Salt', 'Rich in minerals.', 150, 'Organic Food'),
        ('Peanut Butter', 'Unsweetened, 100% natural.', 300, 'Organic Food'),
        ('Flax Seeds', 'Good source of Omega-3.', 200, 'Organic Food'),
        ('Organic Jaggery Powder', 'Healthy sugar substitute.', 180, 'Organic Food'),
    ]

    seller_user = users['Kamal18']
    admin_user = users['Owner@08']

    # Set User-Agent for downloads
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)

    def download_product_image(product_name):
        image_name = f"{product_name.lower().replace(' ', '_')}_{random.randint(100, 999)}.jpg"
        image_path = f'products/{image_name}'
        local_path = MEDIA_DIR / image_name
        
        keyword = product_name.replace(' ', ',')
        url = f"https://loremflickr.com/800/600/{keyword}"
        
        print(f"Downloading image for {product_name}...")
        try:
            urllib.request.urlretrieve(url, local_path)
            return image_path
        except Exception as e:
            print(f"Failed to download image for {product_name}: {e}")
            return None

    # Update products from list
    for name, desc, price, cat_name in products_input:
        seller = random.choice([seller_user, admin_user])
        
        product, created = Product.objects.get_or_create(name=name)
        
        # Always update with fresh data and a new image if missing
        product.seller = seller
        product.category = cat_objs[cat_name]
        product.description = desc
        product.price = price
        if created:
            product.stock = random.randint(10, 100)
            
        if not product.image:
            product.image = download_product_image(name)
            
        product.save()
        status = "added" if created else "updated"
        print(f"Product {name} {status}.")

    # Fallback for any other orphaned products
    orphans = Product.objects.filter(django.db.models.Q(image='') | django.db.models.Q(image=None))
    if orphans.exists():
        print(f"\nProcessing {orphans.count()} orphaned products...")
        for product in orphans:
            product.image = download_product_image(product.name)
            product.save()
            print(f"Orphaned product {product.name} updated with image.")

    print(f"Finished. Total products: {Product.objects.count()}")

if __name__ == '__main__':
    run()
