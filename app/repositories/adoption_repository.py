from ..models import AdoptionStatus, Adoption

from datetime import datetime

class AdoptionRepository:
    def __init__(self, db):
        self.db = db

    def get_adoption(self, adoption_id):
        return self.db.session.get(Adoption, adoption_id)

    def get_user_adoption(self, user_id, animal_id):
        return self.db.session.execute(
            self.db.select(Adoption)
            .filter_by(user_id=user_id, animal_id=animal_id)
        ).scalar()

    def get_animal_adoptions(self, animal_id):
        return self.db.session.execute(
            self.db.select(Adoption)
            .filter_by(animal_id=animal_id)
            .order_by(Adoption.application_date.desc())
        ).scalars()

    def has_user_adoption(self, user_id, animal_id):
        return self.get_user_adoption(user_id, animal_id) is not None

    def create_adoption(self, user_id, animal_id, contact_info):
        adoption = Adoption(
            user_id=user_id,
            animal_id=animal_id,
            contact_info=contact_info,
            status=AdoptionStatus.PENDING,
            application_date=datetime.now()
        )
        self.db.session.add(adoption)
        self.db.session.commit()
        return adoption

    def accept_adoption(self, adoption_id):
        adoption = self.get_adoption(adoption_id)
        if adoption:
            adoption.status = AdoptionStatus.ACCEPTED
            self.db.session.execute(
                self.db.update(Adoption)
                .where(
                    Adoption.animal_id == adoption.animal_id,
                    Adoption.id != adoption.id,
                    Adoption.status == AdoptionStatus.PENDING
                )
                .values(status=AdoptionStatus.REJECTED_ADOPTED)
            )
            self.db.session.commit()

    def reject_adoption(self, adoption_id):
        adoption = self.get_adoption(adoption_id)
        if adoption:
            adoption.status = AdoptionStatus.REJECTED
            self.db.session.commit()