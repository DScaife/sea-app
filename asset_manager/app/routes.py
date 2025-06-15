from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Asset, User
from datetime import datetime
from flask_login import login_required, current_user

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return redirect(url_for("auth.login"))


@main.route("/assets")
@login_required
def asset_list():
    status_filter = request.args.get("status")
    user_filter = request.args.get("user")

    query = Asset.query

    if current_user.role != "admin":
        query = query.filter_by(user_id=current_user.id)
    else:
        if user_filter:
            query = query.join(Asset.submitter).filter(User.username == user_filter)

    if status_filter:
        query = query.filter_by(status=status_filter)

    assets = query.all()
    return render_template("assets.html", assets=assets)


@main.route("/asset/new", methods=["GET", "POST"])
@login_required
def new_asset():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        purchase_date = request.form.get("purchase_date")
        if current_user.role == "admin":
            status = request.form.get("status", "Active")
        else:
            status = "Pending Approval"

        try:
            purchase_date_obj = datetime.strptime(purchase_date, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for("main.new_asset"))

        asset = Asset(
            name=name,
            category=category,
            purchase_date=purchase_date_obj,
            status=status,
            user_id=current_user.id,
        )
        db.session.add(asset)
        db.session.commit()
        flash("Asset created successfully!", "success")
        return redirect(url_for("main.asset_list"))

    return render_template("new_asset.html")


@main.route("/asset/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_asset(id):
    asset = Asset.query.get_or_404(id)

    if current_user.role != "admin" and asset.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("main.asset_list"))

    if request.method == "POST":
        asset.name = request.form.get("name")
        asset.category = request.form.get("category")
        purchase_date = request.form.get("purchase_date")
        try:
            asset.purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for("main.edit_asset", id=id))

        asset.status = request.form.get("status")

        db.session.commit()
        flash("Asset updated successfully!", "success")
        return redirect(url_for("main.asset_list"))

    return render_template("edit_asset.html", asset=asset)


@main.route("/asset/delete/<int:id>", methods=["POST"])
@login_required
def delete_asset(id):
    asset = Asset.query.get_or_404(id)

    if current_user.role != "admin" and asset.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("main.asset_list"))

    db.session.delete(asset)
    db.session.commit()
    flash("Asset deleted successfully!", "danger")
    return redirect(url_for("main.asset_list"))


@main.route("/asset/approve/<int:id>", methods=["POST"])
@login_required
def approve_asset(id):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.asset_list"))

    asset = Asset.query.get_or_404(id)
    asset.status = "Active"
    db.session.commit()
    flash("Asset approved!", "success")
    return redirect(url_for("main.asset_list"))


@main.route("/asset/reject/<int:id>", methods=["POST"])
@login_required
def reject_asset(id):
    if current_user.role != "admin":
        flash("Access denied.", "danger")
        return redirect(url_for("main.asset_list"))

    asset = Asset.query.get_or_404(id)
    asset.status = "Rejected"
    db.session.commit()
    flash("Asset rejected!", "warning")
    return redirect(url_for("main.asset_list"))
