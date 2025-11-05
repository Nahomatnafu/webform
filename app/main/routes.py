from flask import render_template, flash, redirect, url_for, request, abort, current_app, send_file
from flask import send_from_directory
from app import db
from app.main.forms import InviteForm, IDForm, GroupForm
from flask_login import current_user, login_required
import sqlalchemy as sa
from app.models import Link, Form, Group
from datetime import datetime, timezone, timedelta
import os
import filetype
from app.main import bp
from app.export_utils import create_group_export, get_image_filename

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """Dashboard showing user's groups and legacy links"""
    form = InviteForm()
    if form.validate_on_submit():
        # Legacy link generation (no group) - expires in 7 days
        now = datetime.now(timezone.utc)
        link = Link(
            created_at=now,
            end_at=now + timedelta(days=7),
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
        # Get the first form for this link (for legacy links)
        query = sa.select(Form).where(Form.link_id == link_id).limit(1)
        return db.session.scalars(query).first()

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
        sa.select(Link).where(Link.id == link_id)
    )
    if link.is_active() == False:
        abort(404)

    form = IDForm(allowed=current_app.config['UPLOAD_EXTENSIONS'])
    if form.validate_on_submit():
        # Generate unique ID for this form submission
        form_id = secrets.token_urlsafe(16)

        f = Form(
            id=form_id,
            link_id=link.id,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            eye_color=form.eye_color.data,
            hair_color=form.hair_color.data,
            address=form.address.data,
            date_of_birth=form.date_of_birth.data,
            height=form.height.data,
            weight=form.weight.data,
            gender=form.gender.data,
            state=form.state.data,
            city=form.city.data,
            zip_code=form.zip_code.data,
            organ_donor=form.organ_donor.data,
            restrictions_corrective_lenses=form.restrictions_corrective_lenses.data,
            group_id=link.group_id
        )
        if form.middle_name.data:
            f.middle_name = form.middle_name.data

        # Save image with form ID instead of link ID
        form.image.data.save(os.path.join(current_app.config['UPLOAD_PATH'], form_id))

        # Increment group count if this link belongs to a group
        if link.group:
            link.group.current_count += 1

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

    # Try to get the form to generate a better filename
    form = db.session.get(Form, filename)
    if form:
        # Use FirstName_LastName_id format
        download_name = f"{form.first_name}_{form.last_name}_{form.id}.{extension}"
    else:
        download_name = f'{filename}.{extension}'

    return send_from_directory(current_app.config['UPLOAD_PATH'], filename, as_attachment=True, download_name=download_name)

@bp.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    """Manage groups for form collection"""
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data,
            description=form.description.data,
            max_capacity=form.max_capacity.data,
            expiration_type=form.expiration_type.data,
            expiration_hours=form.expiration_hours.data if form.expiration_type.data == 'hours' else None,
            creator=current_user
        )
        db.session.add(group)
        db.session.commit()
        flash(f'Group "{group.name}" created successfully!')
        return redirect(url_for('main.groups'))

    page = request.args.get('page', 1, type=int)
    query = current_user.groups.select().order_by(Group.created_at.desc())
    groups_paginated = db.paginate(query, page=page, per_page=current_app.config['LINK_PER_PAGE'], error_out=False)
    next_url = url_for('main.groups', page=groups_paginated.next_num) \
        if groups_paginated.has_next else None
    prev_url = url_for('main.groups', page=groups_paginated.prev_num) \
        if groups_paginated.has_prev else None

    return render_template('groups.html', title='Groups', form=form, groups=groups_paginated.items,
                         next_url=next_url, prev_url=prev_url)

@bp.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def view_group(group_id):
    """View group details and generate links"""
    group = db.first_or_404(
        sa.select(Group).where(Group.id == group_id).where(Group.user_id == current_user.id)
    )

    # Generate link form
    form = InviteForm()
    if form.validate_on_submit():
        now = datetime.now(timezone.utc)

        # Calculate expiration based on group settings
        if group.expiration_type == 'hours' and group.expiration_hours:
            end_at = now + timedelta(hours=group.expiration_hours)
        else:
            # Never expire - set to far future
            end_at = now + timedelta(days=365*10)

        # Check if group is full
        if group.is_full():
            flash('This group has reached its capacity limit!', 'error')
            return redirect(url_for('main.view_group', group_id=group_id))

        link = Link(
            created_at=now,
            end_at=end_at,
            creator=current_user,
            group=group
        )
        db.session.add(link)
        db.session.commit()
        flash('Link generated successfully!')
        return redirect(url_for('main.view_group', group_id=group_id))

    # Get links for this group
    page = request.args.get('page', 1, type=int)
    query = group.links.select().order_by(Link.created_at.desc())
    links = db.paginate(query, page=page, per_page=current_app.config['LINK_PER_PAGE'], error_out=False)
    next_url = url_for('main.view_group', group_id=group_id, page=links.next_num) \
        if links.has_next else None
    prev_url = url_for('main.view_group', group_id=group_id, page=links.prev_num) \
        if links.has_prev else None

    def get_form(link_id):
        # Get the first form for this link
        query = sa.select(Form).where(Form.link_id == link_id).limit(1)
        return db.session.scalars(query).first()

    # Get all forms for this group for the submissions section
    forms_query = sa.select(Form).where(Form.group_id == group_id).order_by(Form.submitted_at.desc())
    all_forms = db.session.scalars(forms_query).all()

    return render_template('view_group.html', title=group.name, group=group, form=form,
                         links=links.items, next_url=next_url, prev_url=prev_url, get_form=get_form, all_forms=all_forms)

@bp.route('/group/<int:group_id>/export')
@login_required
def export_group(group_id):
    """Export group submissions to Excel"""
    group = db.first_or_404(
        sa.select(Group).where(Group.id == group_id).where(Group.user_id == current_user.id)
    )

    # Get all forms for this group
    query = sa.select(Form).where(Form.group_id == group_id).order_by(Form.submitted_at.desc())
    forms = db.session.scalars(query).all()

    if not forms:
        flash('No submissions to export for this group.', 'warning')
        return redirect(url_for('main.view_group', group_id=group_id))

    # Create Excel file
    excel_file = create_group_export(group, forms)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{group.name.replace(' ', '_')}_submissions_{timestamp}.xlsx"

    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/group/<int:group_id>/export-photos')
@login_required
def export_group_photos(group_id):
    """Export all group submission photos as a ZIP file"""
    import zipfile
    import io

    group = db.first_or_404(
        sa.select(Group).where(Group.id == group_id).where(Group.user_id == current_user.id)
    )

    # Get all forms for this group
    query = sa.select(Form).where(Form.group_id == group_id).order_by(Form.submitted_at.desc())
    forms = db.session.scalars(query).all()

    if not forms:
        flash('No submissions to export for this group.', 'warning')
        return redirect(url_for('main.view_group', group_id=group_id))

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for form in forms:
            # Get image filename
            image_path = os.path.join(current_app.config['UPLOAD_PATH'], form.id)

            if os.path.exists(image_path):
                # Create filename as FirstName_LastName_id
                filename = f"{form.first_name}_{form.last_name}_{form.id}"

                # Get file extension
                kind = filetype.guess(image_path)
                if kind:
                    filename += f".{kind.extension}"

                # Add file to ZIP
                with open(image_path, 'rb') as f:
                    zip_file.writestr(filename, f.read())

    zip_buffer.seek(0)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{group.name.replace(' ', '_')}_photos_{timestamp}.zip"

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )