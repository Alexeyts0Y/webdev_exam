from ..models import Animal, Adoption, AnimalStatus
from sqlalchemy import func, desc, case

class AnimalRepository:
    def __init__(self, db):
        self.db = db

    def get_all_animals(self):
        """Получить всех животных без сортировки и пагинации"""
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
        
        # Новый синтаксис для case() в SQLAlchemy 2.0+
        status_order = case(
            (Animal.status == AnimalStatus.AVAILABLE, 0),
            (Animal.status == AnimalStatus.ADOPTION, 1),
            (Animal.status == AnimalStatus.ADOPTED, 2),
            else_=3  # можно добавить значение по умолчанию
        )
        
        query = (
            self.db.session.query(
                Animal,
                func.coalesce(adoption_counts.c.adoption_count, 0).label('adoption_count')
            )
            .outerjoin(adoption_counts, Animal.id == adoption_counts.c.animal_id)
            .order_by(
                status_order,  # Сортировка по статусу
                desc(Animal.created_at)  # Сортировка по дате (сначала новые)
            )
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        
        return query