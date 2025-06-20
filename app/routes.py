from flask import Blueprint, abort, current_app, render_template, send_from_directory, request

from .models import db, Animal
from .repositories.animal_repository import AnimalRepository
from .repositories.image_repository import ImageRepository

bp = Blueprint("main", __name__)

animal_repository = AnimalRepository(db)
image_repository = ImageRepository(db)

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    animals_page = animal_repository.get_paginated_animals_sorted(page=page)
    return render_template('main/index.html', animals_page=animals_page)

@bp.route('/images/<image_id>')
def serve_image(image_id):
    image = image_repository.get_by_id(image_id)
    if not image:
        abort(404)
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        image.storage_filename
    )