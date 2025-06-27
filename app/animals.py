from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import hashlib
import uuid
import bleach
from markdown import markdown

from .models import Animal, Image, Adoption, AnimalStatus, AdoptionStatus, db
from .repositories.animal_repository import AnimalRepository
from .repositories.image_repository import ImageRepository
from .repositories.adoption_repository import AdoptionRepository
from .auth import check_rights

bp = Blueprint('animals', __name__, url_prefix='/animals')

animal_repo = AnimalRepository(db)
image_repo = ImageRepository(db)
adoption_repo = AdoptionRepository(db)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def clean_markdown(content):
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'b', 'i', 'strong', 'em', 'tt',
        'p', 'br', 'span', 'div', 'blockquote', 'code', 'hr',
        'ul', 'ol', 'li', 'dd', 'dt', 'dl',
        'img', 'a', 'sub', 'sup'
    ]
    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']
    }
    
    html = markdown(content)
    cleaned = bleach.clean(html, tags=allowed_tags, attributes=allowed_attributes)
    return cleaned

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    animals_page = animal_repo.get_paginated_animals_sorted(page=page)
    return render_template('main/index.html', animals_page=animals_page)

@bp.route('/<int:animal_id>')
def show(animal_id):
    animal = animal_repo.get_animal_by_id(animal_id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    user_adoption = None
    if current_user.is_authenticated:
        user_adoption = adoption_repo.get_user_adoption(current_user.id, animal_id)
    
    adoptions = []
    if current_user.is_authenticated and (current_user.is_admin or current_user.is_moderator):
        adoptions = adoption_repo.get_animal_adoptions(animal_id)
    
    return render_template('animals/show.html', 
                         animal=animal,
                         user_adoption=user_adoption,
                         adoptions=adoptions,
                         AnimalStatus=AnimalStatus,
                         AdoptionStatus=AdoptionStatus)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@check_rights('create_animal')
def create():
    if request.method == 'POST':
        try:
            description = clean_markdown(request.form['description'])
            
            animal = animal_repo.create_animal(
                name=request.form['name'],
                description=description,
                age_months=int(request.form['age_months']),
                breed=request.form['breed'],
                gender=request.form['gender'],
                status=AnimalStatus.AVAILABLE
            )

            if 'images' in request.files:
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                for file in request.files.getlist('images'):
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            image_repo.add_image(file, animal.id)
                        except ValueError as e:
                            current_app.logger.error(f"Validation error: {e}")
                            flash(f'Ошибка при загрузке изображения: {e}', 'danger')
                        except Exception as e:
                            current_app.logger.error(f"Error saving image: {e}")
                            flash('Ошибка при сохранении изображения', 'danger')
            
            flash('Животное успешно добавлено', 'success')
            return redirect(url_for('animals.show', animal_id=animal.id))
            
        except Exception as e:
            current_app.logger.error(f"Error creating animal: {e}")
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
    
    return render_template('animals/form.html')

@bp.route('/<int:animal_id>/edit', methods=['GET', 'POST'])
@login_required
@check_rights('edit_animal')
def edit(animal_id):
    animal = animal_repo.get_animal_by_id(animal_id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    if request.method == 'POST':
        try:
            animal_repo.update_animal(
                animal,
                name=request.form['name'],
                description=clean_markdown(request.form['description']),
                age_months=int(request.form['age_months']),
                breed=request.form['breed'],
                gender=request.form['gender'],
                status=AnimalStatus(request.form['status'])
            )
            
            flash('Данные обновлены', 'success')
            return redirect(url_for('animals.show', animal_id=animal.id))
        except Exception as e:
            current_app.logger.error(f"Error updating animal: {e}")
            flash('При сохранении данных возникла ошибка', 'danger')
    
    return render_template('animals/form.html', animal=animal)

@bp.route('/<int:animal_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_animal')
def delete(animal_id):
    try:
        animal_repo.delete_animal(animal_id)
        flash('Животное успешно удалено', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting animal: {e}")
        flash('Ошибка при удалении животного', 'danger')
    
    return redirect(url_for('animals.index'))

@bp.route('/<int:animal_id>/adopt', methods=['POST'])
@login_required
def create_adoption(animal_id):
    animal = animal_repo.get_animal_by_id(animal_id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    if animal.status not in (AnimalStatus.AVAILABLE, AnimalStatus.ADOPTION):
        flash('Это животное уже не доступно для усыновления', 'warning')
        return redirect(url_for('animals.show', animal_id=animal_id))
    
    if adoption_repo.has_user_adoption(current_user.id, animal_id):
        flash('Вы уже подавали заявку на это животное', 'warning')
        return redirect(url_for('animals.show', animal_id=animal_id))
    
    try:
        adoption_repo.create_adoption(
            user_id=current_user.id,
            animal_id=animal_id,
            contact_info=request.form['contact_info']
        )
        
        animal_repo.update_animal_status(animal_id, AnimalStatus.ADOPTION)
        flash('Заявка подана успешно', 'success')
    except Exception as e:
        current_app.logger.error(f"Error creating adoption: {e}")
        flash('Ошибка при подаче заявки', 'danger')
    
    return redirect(url_for('animals.show', animal_id=animal_id))

@bp.route('/adoptions/<int:adoption_id>/<action>', methods=['POST'])
@login_required
@check_rights('process_adoption')
def process_adoption(adoption_id, action):
    adoption = adoption_repo.get_adoption(adoption_id)
    if not adoption:
        flash('Заявка не найдена', 'danger')
        return redirect(url_for('animals.index'))
    
    try:
        if action == 'accept':
            adoption_repo.accept_adoption(adoption_id)
            flash('Заявка принята. Остальные заявки на это животное отклонены.', 'success')
        elif action == 'reject':
            adoption_repo.reject_adoption(adoption_id)
            flash('Заявка отклонена', 'info')
    except Exception as e:
        current_app.logger.error(f"Error processing adoption: {e}")
        flash('Ошибка при обработке заявки', 'danger')
    
    return redirect(url_for('animals.show', animal_id=adoption.animal_id))