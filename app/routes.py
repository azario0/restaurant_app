from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import Admin, Product, Order, OrderItem
from app.forms import LoginForm, ProductForm, CheckoutForm
import os
from werkzeug.utils import secure_filename
from config import Config
import json

main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)
user = Blueprint('user', __name__)

@main.route('/')
def index():
    return redirect(url_for('user.products'))

@admin.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid username or password')
    return render_template('admin/login.html', form=form)

@admin.route('/logout')
@login_required
def logout():
    logout_user()   
    return redirect(url_for('main.index'))

@admin.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

@admin.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        filename = secure_filename(form.image.data.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        form.image.data.save(filepath)
        product = Product(name=form.name.data, price=form.price.data, image_filename=filename)
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_product.html', form=form)

@admin.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            product.image_filename = filename
        db.session.commit()
        flash('Product updated successfully')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_product.html', form=form, product=product)

@admin.route('/delete_product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    for order_item in product.order_items:
        order_item.product_id = None
    
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé avec succès')
    return redirect(url_for('admin.dashboard'))

@admin.route('/orders')
@login_required
def orders():
    orders = Order.query.all()
    return render_template('admin/orders.html', orders=orders)

@user.route('/products')
def products():
    products = Product.query.all()
    return render_template('user/products.html', products=products)

@user.route('/checkout', methods=['GET', 'POST'])
def checkout():
    form = CheckoutForm()
    if form.validate_on_submit():
        order = Order(name=form.name.data, surname=form.surname.data, phone=form.phone.data, total=0)
        db.session.add(order)
        db.session.flush()

        cart = request.form.get('cart')
        cart_items = json.loads(cart)
        total = 0

        for item in cart_items:
            product = Product.query.get(item['id'])
            quantity = item['quantity']
            total += product.price * quantity
            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity)
            db.session.add(order_item)

        order.total = total
        db.session.commit()
        flash('Order placed successfully')
        return redirect(url_for('user.products'))

    return render_template('user/checkout.html', form=form)

@main.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if Admin.query.first() is not None:
        flash('Admin already exists.')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        flash('Admin account created successfully.')
        return redirect(url_for('admin.login'))
    
    return render_template('create_admin.html')