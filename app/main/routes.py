from flask import render_template, flash, redirect, url_for, request, abort, current_app
from flask import send_from_directory
from app import db
from app.main.forms import InviteForm, IDForm
from flask_login import current_user, login_required
import sqlalchemy as sa
from app.models import Link, Form
from datetime import datetime, timezone, timedelta
import os
import filetype
from app.main import bp

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = InviteForm()
    if form.validate_on_submit():
        now = datetime.now(timezone.utc)
        delta = timedelta(
            weeks=form.weeks.data,
            days=form.days.data,
            hours=form.hours.data,
            minutes=form.minutes.data,
            seconds=form.seconds.data
        )
        link = Link(
            created_at=now,
            end_at=now + delta,
            creator=current_user
        )
        db.session.add(link)
        db.session.commit()
        flash('Link generated successfully!')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    query = current_user.links.select().order_by(Link.created_at.desc())
    links = db.paginate(query, page=page, per_page=current_app.config['LINK_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=links.next_num) \
        if links.has_next else None
    prev_url = url_for('main.index', page=links.prev_num) \
        if links.has_prev else None

    def get_form(link_id):
        return db.session.get(Form, link_id)

    return render_template('index.html', title='Home', links=links.items, form=form, next_url=next_url, prev_url=prev_url, get_form=get_form)


@bp.route('/user')
@login_required
def user():
    page = request.args.get('page', 1, type=int)
    query = current_user.links.select().order_by(Link.created_at.desc())
    links = db.paginate(query, page=page, per_page=current_app.config['LINK_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', page=links.next_num) \
        if links.has_next else None
    prev_url = url_for('main.user', page=links.prev_num) \
        if links.has_prev else None
    return render_template('user.html', title="User", links=links.items, next_url=next_url, prev_url=prev_url)
    

@bp.route('/form/<link_id>', methods=['GET', 'POST'])
def form(link_id):
    link = db.first_or_404(
        sa.select(Link).where(Link.id == link_id).where(Link.used == False)
    )
    if link.is_active() == False:
        abort(404)
    
    form = IDForm(allowed=current_app.config['UPLOAD_EXTENSIONS'])
    if form.validate_on_submit():
        f = Form(id=link.id,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            eye_color=form.eye_color.data,
            hair_color=form.hair_color.data,
            date_of_birth=form.date_of_birth.data,
            height=form.height.data,
            weight=form.weight.data,
            gender=form.gender.data,
            state=form.state.data,
            city=form.city.data,
            zip_code=form.zip_code.data,
            organ_donor= form.organ_donor.data,
            restrictions_corrective_lenses=form.restrictions_corrective_lenses.data
        )
        if form.middle_name.data:
            f.middle_name = form.middle_name.data
        
        form.image.data.save(os.path.join(current_app.config['UPLOAD_PATH'], link.id))
        link.used = True
        db.session.add(f)
        db.session.commit()
        return redirect(url_for('main.success'))
    return render_template('form.html', title='IDForm', form=form)

@bp.route('/success')
def success():
    return render_template('success.html', title='Success')

@bp.route('/view-form/<form_id>')
@login_required
def view_form(form_id):
    form = db.first_or_404(
        sa.select(Form).where(Form.id == form_id)
    )
    return render_template('view_form.html', title='View Form', form=form)

@bp.route('/uploads/<filename>')
@login_required
def upload(filename):
    filepath = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    kind = filetype.guess(filepath)
    mimetype = kind.mime if kind else 'application/octet-stream'
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename, as_attachment=False, mimetype=mimetype)

@bp.route('/download/<filename>')
@login_required
def download(filename):
    filepath = os.path.join(current_app.config['UPLOAD_PATH'], filename)
    kind = filetype.guess(filepath)
    extension = kind.extension if kind else 'jpg'
    return send_from_directory(current_app.config['UPLOAD_PATH'], filename, as_attachment=True, download_name=f'{filename}.{extension}')