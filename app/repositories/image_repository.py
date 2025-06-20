import hashlib
import uuid
import os
from werkzeug.utils import secure_filename
from flask import current_app
from ..models import Image

class ImageRepository:
    def __init__(self, db):
        self.db = db

    def get_by_id(self, image_id):
        return self.db.session.get(Image, image_id)

    def add_image(self, file, animal_id=None):
        """
        Добавить новое изображение
        :param file: Файл изображения
        :param animal_id: ID животного (обязательно для сохранения)
        :return: Объект Image
        """
        if animal_id is None:
            raise ValueError("animal_id is required for image")

        # Проверяем, есть ли уже такое изображение
        existing_image = self._find_by_md5_hash(file)
        if existing_image:
            return existing_image

        # Создаем новое изображение
        file_name = secure_filename(file.filename)
        md5_hash = self._calculate_md5(file)
        
        image = Image(
            id=str(uuid.uuid4()),
            file_name=file_name,
            mime_type=file.mimetype,
            md5_hash=md5_hash,
            animal_id=animal_id  # Устанавливаем animal_id сразу
        )

        # Сохраняем файл на диск
        self._save_file(file, image)
        
        # Добавляем в БД
        self.db.session.add(image)
        self.db.session.commit()
        
        return image

    def _find_by_md5_hash(self, file):
        """Найти существующее изображение по хешу"""
        md5_hash = self._calculate_md5(file)
        return self.db.session.execute(
            self.db.select(Image).filter(Image.md5_hash == md5_hash)
        ).scalar()

    def _calculate_md5(self, file):
        """Вычислить MD5 хеш файла"""
        file.seek(0)
        md5_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)
        return md5_hash

    def _save_file(self, file, image):
        """Сохранить файл на диск"""
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, image.storage_filename)
        file.save(file_path)
