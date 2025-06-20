from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import hashlib
import uuid
import bleach
from markdown import markdown

from .models import db, Animal, Image, Adoption, AnimalStatus, AdoptionStatus
from .repositories.animal_repository import AnimalRepository
from .repositories.image_repository import ImageRepository
from .auth import check_rights

bp = Blueprint('animals', __name__, url_prefix='/animals')

animal_repo = AnimalRepository(db)
image_repo = ImageRepository(db)

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
    cleaned = bleach.clean(
        html, 
        tags=allowed_tags, 
        attributes=allowed_attributes
    )
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
        user_adoption = db.session.execute(
            db.select(Adoption)
            .filter_by(user_id=current_user.id, animal_id=animal_id)
        ).scalar()
    
    adoptions = []
    if current_user.is_authenticated and (current_user.is_admin or current_user.is_moderator):
        adoptions = db.session.execute(
            db.select(Adoption)
            .filter_by(animal_id=animal_id)
            .order_by(Adoption.application_date.desc())
        ).scalars()
    
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
            
            animal = Animal(
                name=request.form['name'],
                description=description,
                age_months=int(request.form['age_months']),
                breed=request.form['breed'],
                gender=request.form['gender'],
                status=AnimalStatus.AVAILABLE,
                created_at=datetime.now()
            )
            db.session.add(animal)
            db.session.flush()

            if 'images' in request.files:
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                for file in request.files.getlist('images'):
                    if file and file.filename and allowed_file(file.filename):
                        try:
                            image = image_repo.add_image(file, animal.id)
                        except ValueError as e:
                            current_app.logger.error(f"Validation error: {e}")
                            flash(f'Ошибка при загрузке изображения: {e}', 'danger')
                        except Exception as e:
                            current_app.logger.error(f"Error saving image: {e}")
                            flash('Ошибка при сохранении изображения', 'danger')
            
            db.session.commit()
            flash('Животное успешно добавлено', 'success')
            return redirect(url_for('animals.show', animal_id=animal.id))
            
        except Exception as e:
            db.session.rollback()
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
            animal.name = request.form['name']
            animal.description = clean_markdown(request.form['description'])
            animal.age_months = int(request.form['age_months'])
            animal.breed = request.form['breed']
            animal.gender = request.form['gender']
            animal.status = AnimalStatus(request.form['status'])
            
            db.session.commit()
            flash('Данные обновлены', 'success')
            return redirect(url_for('animals.show', animal_id=animal.id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating animal: {e}")
            flash('При сохранении данных возникла ошибка', 'danger')
    
    return render_template('animals/form.html', animal=animal)

@bp.route('/<int:animal_id>/delete', methods=['POST'])
@login_required
@check_rights('delete_animal')
def delete(animal_id):
    animal = animal_repo.get_animal_by_id(animal_id)
    if not animal:
        flash('Животное не найдено', 'danger')
        return redirect(url_for('animals.index'))
    
    try:
        for image in animal.images:
            try:
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.storage_filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                current_app.logger.error(f"Error deleting image file: {e}")
                continue
        
        db.session.delete(animal)
        db.session.commit()
        flash('Животное успешно удалено', 'success')
    except Exception as e:
        db.session.rollback()
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
    
    existing_adoption = db.session.execute(
        db.select(Adoption)
        .filter_by(user_id=current_user.id, animal_id=animal_id)
    ).scalar()
    
    if existing_adoption:
        flash('Вы уже подавали заявку на это животное', 'warning')
        return redirect(url_for('animals.show', animal_id=animal_id))
    
    try:
        adoption = Adoption(
            user_id=current_user.id,
            animal_id=animal_id,
            contact_info=request.form['contact_info'],
            status=AdoptionStatus.PENDING,
            application_date=datetime.now()
        )
        db.session.add(adoption)
        
        animal.status = AnimalStatus.ADOPTION
        
        db.session.commit()
        flash('Заявка подана успешно', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating adoption: {e}")
        flash('Ошибка при подаче заявки', 'danger')
    
    return redirect(url_for('animals.show', animal_id=animal_id))

@bp.route('/adoptions/<int:adoption_id>/<action>', methods=['POST'])
@login_required
@check_rights('process_adoption')
def process_adoption(adoption_id, action):
    adoption = db.session.get(Adoption, adoption_id)
    if not adoption:
        flash('Заявка не найдена', 'danger')
        return redirect(url_for('animals.index'))
    
    try:
        if action == 'accept':
            adoption.status = AdoptionStatus.ACCEPTED
            adoption.animal.status = AnimalStatus.ADOPTED

            db.session.execute(
                db.update(Adoption)
                .where(
                    Adoption.animal_id == adoption.animal_id,
                    Adoption.id != adoption.id,
                    Adoption.status == AdoptionStatus.PENDING
                )
                .values(status=AdoptionStatus.REJECTED_ADOPTED)
            )
            
            flash('Заявка принята. Остальные заявки на это животное отклонены.', 'success')
        elif action == 'reject':
            adoption.status = AdoptionStatus.REJECTED

            has_pending = db.session.execute(
                db.select(Adoption)
                .where(
                    Adoption.animal_id == adoption.animal_id,
                    Adoption.status == AdoptionStatus.PENDING
                )
            ).scalar()
            
            if has_pending:
                adoption.animal.status = AnimalStatus.ADOPTION
            else:
                adoption.animal.status = AnimalStatus.AVAILABLE
            
            flash('Заявка отклонена', 'info')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing adoption: {e}")
        flash('Ошибка при обработке заявки', 'danger')
    
    return redirect(url_for('animals.show', animal_id=adoption.animal_id))

def update_animal_status(animal_id):
    animal = animal_repo.get_animal_by_id(animal_id)
    if not animal:
        return

    accepted = db.session.execute(
        db.select(Adoption)
        .where(
            Adoption.animal_id == animal_id,
            Adoption.status == AdoptionStatus.ACCEPTED
        )
    ).scalar()
    
    if accepted:
        animal.status = AnimalStatus.ADOPTED
    else:
        pending = db.session.execute(
            db.select(Adoption)
            .where(
                Adoption.animal_id == animal_id,
                Adoption.status == AdoptionStatus.PENDING
            )
        ).scalar()
        
        if pending:
            animal.status = AnimalStatus.ADOPTION
        else:
            animal.status = AnimalStatus.AVAILABLE
    
    db.session.commit()