from datetime import datetime
import os
from flask import current_app
from ..models import Animal, Adoption, AnimalStatus
from sqlalchemy import func, desc, case

class AnimalRepository:
    def __init__(self, db):
        self.db = db

    def get_all_animals(self):
        return self.db.session.execute(self.db.select(Animal)).scalars()
    
    def get_animal_by_id(self, animal_id):
        return self.db.session.execute(self.db.select(Animal).filter_by(id=animal_id)).scalar()
    
    def get_paginated_animals_sorted(self, page=1, per_page=10):
        adoption_counts = (
            self.db.session.query(
                Adoption.animal_id,
                func.count(Adoption.id).label('adoption_count')
            )
            .group_by(Adoption.animal_id)
            .subquery()
        )

        status_order = case(
            (Animal.status == AnimalStatus.AVAILABLE, 0),
            (Animal.status == AnimalStatus.ADOPTION, 1),
            (Animal.status == AnimalStatus.ADOPTED, 2),
            else_=3
        )
        
        query = (
            self.db.session.query(
                Animal,
                func.coalesce(adoption_counts.c.adoption_count, 0).label('adoption_count')
            )
            .outerjoin(adoption_counts, Animal.id == adoption_counts.c.animal_id)
            .order_by(
                status_order,
                desc(Animal.created_at)
            )
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        
        return query
    
    def create_animal(self, name, description, age_months, breed, gender, status):
        animal = Animal(
            name=name,
            description=description,
            age_months=age_months,
            breed=breed,
            gender=gender,
            status=status,
            created_at=datetime.now()
        )
        self.db.session.add(animal)
        self.db.session.commit()
        return animal

    def update_animal(self, animal, **kwargs):
        for key, value in kwargs.items():
            setattr(animal, key, value)
        self.db.session.commit()

    def update_animal_status(self, animal_id, status):
        animal = self.get_animal_by_id(animal_id)
        if animal:
            animal.status = status
            self.db.session.commit()

    def delete_animal(self, animal_id):
        animal = self.get_animal_by_id(animal_id)
        if animal:
            for image in animal.images:
                try:
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], image.storage_filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except Exception as e:
                    current_app.logger.error(f"Error deleting image file: {e}")
            
            self.db.session.delete(animal)
            self.db.session.commit()