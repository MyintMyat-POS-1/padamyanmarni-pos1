from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import random
import barcode
from barcode.writer import ImageWriter
from barcode.codex import Code128

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='cashier')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    barcode = db.Column(db.String(50), nullable=True)


def generate_barcode_image(barcode_number):
    folder = os.path.join('static', 'barcodes')
    os.makedirs(folder, exist_ok=True)
    filepath_without_ext = os.path.join(folder, str(barcode_number))
    filepath_with_ext = filepath_without_ext + ".png"
    if not os.path.exists(filepath_with_ext):
        code128 = Code128(barcode_number, writer=ImageWriter())
        code128.save(filepath_without_ext)
    return filepath_with_ext


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username,
                                    password=password).first()
        if user:
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid username or password"
    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    role = session.get('role')
    products = Product.query.all()

    for product in products:
        if product.barcode:
            generate_barcode_image(product.barcode)

    total_inventory_value = sum(p.price * p.stock for p in products)

    if role == 'admin':
        return render_template('admin_dashboard.html',
                               products=products,
                               total_inventory_value=total_inventory_value)
    elif role == 'cashier':
        return render_template('cashier_dashboard.html',
                               products=products,
                               total_inventory_value=total_inventory_value)
    else:
        return redirect(url_for('login'))


def sale():
    return render_template('sale.html')


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        barcode_number = request.form['barcode']

        if not barcode_number:
            barcode_number = str(random.randint(100000000000, 999999999999))

        generate_barcode_image(barcode_number)

        new_product = Product(name=name,
                              price=price,
                              stock=stock,
                              barcode=barcode_number)
        db.session.add(new_product)
        db.session.commit()

    return render_template('add_product.html')


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)

    # Delete barcode image
    if product.barcode:
        filepath = os.path.join('static', 'barcodes', f"{product.barcode}.png")
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/sale', methods=['GET', 'POST'])
def sale():
    if 'username' not in session:
        return redirect(url_for('login'))

    products = Product.query.all()
    message = None

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity', type=int)
        barcode = request.form.get('barcode')

        if barcode:
            product = Product.query.filter_by(barcode=barcode).first()
            if not product:
                message = "Product with this barcode not found."
            elif quantity > product.stock:
                message = "Not enough stock available."
            else:
                product.stock -= quantity
                db.session.commit()
                message = f"Sold {quantity} of {product.name} successfully."
        elif product_id:
            product = Product.query.get(product_id)
            if not product:
                message = "Product not found."
            elif quantity > product.stock:
                message = "Not enough stock available."
            else:
                product.stock -= quantity
                db.session.commit()
                message = f"Sold {quantity} of {product.name} successfully."
        else:
            message = "Please scan a barcode or select a product."

        return render_template('sale.html', products=products, message=message)

    return render_template('sale.html', products=products)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(
            User(username='admin', password='adminpass', role='admin'))
    if not User.query.filter_by(username='cashier1').first():
        db.session.add(
            User(username='cashier1', password='cashierpass', role='cashier'))

    if not Product.query.first():
        sample_products = [
            Product(name="Wine", price=1000.0, stock=5,
                    barcode="579340769370"),
            Product(name="Whisky",
                    price=800.0,
                    stock=3,
                    barcode="699789159401")
        ]
        for p in sample_products:
            if p.barcode:
                generate_barcode_image(p.barcode)
        db.session.bulk_save_objects(sample_products)

    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
