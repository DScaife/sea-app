from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Asset, User
from .forms import AssetForm, ALLOWED_ASSET_STATUSES
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
    form = AssetForm()

    if current_user.role == "admin":
        form.status.choices = [(status, status) for status in ALLOWED_ASSET_STATUSES]
        if request.method == "GET":
            form.status.data = "Active"
    else:
        form.status.choices = [("Pending Approval", "Pending Approval")]
        form.status.data = "Pending Approval"

    if form.validate_on_submit():
        status = form.status.data if current_user.role == "admin" else "Pending Approval"
        asset = Asset(
            name=form.name.data.strip(),
            category=form.category.data.strip(),
            purchase_date=form.purchase_date.data,
            status=status,
            user_id=current_user.id,
        )
        db.session.add(asset)
        db.session.commit()
        flash("Asset created successfully!", "success")
        return redirect(url_for("main.asset_list"))

    elif form.is_submitted():
        for errors in form.errors.values():
            for error in errors:
                flash(error, "danger")

    return render_template("new_asset.html", form=form)


@main.route("/asset/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_asset(id):
    asset = db.get_or_404(Asset, id)

    if current_user.role != "admin" and asset.user_id != current_user.id:
        flash("Access denied.", "danger")
        return redirect(url_for("main.asset_list"))

    form = AssetForm(obj=asset)
    if current_user.role == "admin":
        form.status.choices = [(status, status) for status in ALLOWED_ASSET_STATUSES]
    else:
        form.status.choices = [("Pending Approval", "Pending Approval")]
        if request.method == "GET":
            form.status.data = "Pending Approval"

    if form.validate_on_submit():
        asset.name = form.name.data.strip()
        asset.category = form.category.data.strip()
        asset.purchase_date = form.purchase_date.data
        if current_user.role == "admin":
            if form.status.data in ALLOWED_ASSET_STATUSES:
                asset.status = form.status.data
        else:
            asset.status = "Pending Approval"

        db.session.commit()
        flash("Asset updated successfully!", "success")
        return redirect(url_for("main.asset_list"))

    elif form.is_submitted():
        for errors in form.errors.values():
            for error in errors:
                flash(error, "danger")

    return render_template("edit_asset.html", asset=asset, form=form)


@main.route("/asset/delete/<int:id>", methods=["POST"])
@login_required
def delete_asset(id):
    asset = db.get_or_404(Asset, id)

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

    asset = db.get_or_404(Asset, id)
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

    asset = db.get_or_404(Asset, id)
    asset.status = "Rejected"
    db.session.commit()
    flash("Asset rejected!", "warning")
    return redirect(url_for("main.asset_list"))
