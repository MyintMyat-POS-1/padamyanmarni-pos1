import os
from app import app, db
from models import Product
from barcode import Code128
from barcode.writer import ImageWriter


output_folder = os.path.join('static', 'barcodes')
os.makedirs(output_folder, exist_ok=True)

with app.app_context():
    products = Product.query.all()

    for product in products:
        if product.barcode:
            file_path = os.path.join(output_folder, product.barcode)

            
            if os.path.exists(file_path + '.png'):
                print(f"ℹ️ Already exists: {file_path}.png")
                continue

                        barcode = Code128(product.barcode, writer=ImageWriter())
            barcode.save(file_path)

            print(f"✅ Generated: {file_path}.png")
