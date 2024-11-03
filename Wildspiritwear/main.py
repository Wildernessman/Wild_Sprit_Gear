import os
from app import app, db
from models import Admin, Section
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, login_required, logout_user
from werkzeug.utils import secure_filename
import uuid

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    try:
        sections = Section.query.order_by(Section.position).all()
        return render_template('index.html', sections=sections)
    except Exception as e:
        app.logger.error(f'Error in index route: {str(e)}')
        return 'An error occurred while loading the page', 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            admin = Admin.query.filter_by(username=request.form['username']).first()
            if admin and admin.check_password(request.form['password']):
                login_user(admin)
                return redirect(url_for('admin_dashboard'))
            flash('Invalid credentials')
        except Exception as e:
            app.logger.error(f'Error in admin login: {str(e)}')
            flash('An error occurred during login')
    return render_template('admin_login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    try:
        sections = Section.query.order_by(Section.position).all()
        return render_template('admin.html', sections=sections)
    except Exception as e:
        app.logger.error(f'Error in admin dashboard: {str(e)}')
        return 'An error occurred while loading the dashboard', 500

@app.route('/admin/update/<int:section_id>', methods=['POST'])
@login_required
def update_section(section_id):
    try:
        section = Section.query.get_or_404(section_id)
        
        content = request.form['content']
        if len(content) <= 500:
            section.content = content
        else:
            flash('Content exceeds maximum length of 500 characters')
            return redirect(url_for('admin_dashboard'))
        
        for file_type in ['video', 'image']:
            if file_type in request.files:
                file = request.files[file_type]
                if file and file.filename:
                    allowed_extensions = ALLOWED_VIDEO_EXTENSIONS if file_type == 'video' else ALLOWED_IMAGE_EXTENSIONS
                    if not allowed_file(file.filename, allowed_extensions):
                        flash(f'Invalid {file_type} file type')
                        return redirect(url_for('admin_dashboard'))
                    
                    try:
                        old_path = getattr(section, f'{file_type}_path')
                        if old_path:
                            old_file = os.path.join(app.config['UPLOAD_FOLDER'], old_path)
                            if os.path.exists(old_file):
                                os.remove(old_file)
                        
                        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        setattr(section, f'{file_type}_path', filename)
                    except Exception as e:
                        app.logger.error(f'Error saving {file_type}: {str(e)}')
                        flash(f'Error saving {file_type} file')
                        return redirect(url_for('admin_dashboard'))
        
        db.session.commit()
        flash('Section updated successfully')
        return redirect(url_for('admin_dashboard'))
    
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating section: {str(e)}')
        flash('An error occurred while updating the section')
        return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
