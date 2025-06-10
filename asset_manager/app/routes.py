from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Asset
from datetime import datetime

# Create a blueprint for your main routes
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/assets')
def asset_list():
    assets = Asset.query.all()
    return render_template('assets.html', assets=assets)

@main.route('/asset/new', methods=['GET', 'POST'])
def new_asset():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        purchase_date = request.form.get('purchase_date')  # Entered as 'YYYY-MM-DD'
        status = request.form.get('status')

        # Validate and convert the purchase date from string to a date object
        try:
            purchase_date_obj = datetime.strptime(purchase_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('main.new_asset'))

        asset = Asset(
            name=name,
            category=category,
            purchase_date=purchase_date_obj,
            status=status
        )
        db.session.add(asset)
        db.session.commit()
        flash('Asset created successfully!', 'success')
        return redirect(url_for('main.asset_list'))
        
    return render_template('new_asset.html')

@main.route('/asset/edit/<int:id>', methods=['GET', 'POST'])
def edit_asset(id):
    asset = Asset.query.get_or_404(id)
    if request.method == 'POST':
        asset.name = request.form.get('name')
        asset.category = request.form.get('category')
        purchase_date = request.form.get('purchase_date')
        try:
            asset.purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(url_for('main.edit_asset', id=id))
        asset.status = request.form.get('status')
        
        db.session.commit()
        flash('Asset updated successfully!', 'success')
        return redirect(url_for('main.asset_list'))
        
    return render_template('edit_asset.html', asset=asset)

@main.route('/asset/delete/<int:id>', methods=['POST'])
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully!', 'danger')
    return redirect(url_for('main.asset_list'))
