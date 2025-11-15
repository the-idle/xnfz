# app/crud/crud_procedure.py
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.question_management import Procedure
from app.schemas.procedure import ProcedureCreate, ProcedureUpdate

class CRUDProcedure(CRUDBase[Procedure, ProcedureCreate, ProcedureUpdate]):
    def create_with_bank(
        self, db: Session, *, obj_in: ProcedureCreate, question_bank_id: int
    ) -> Procedure:
        """
        创建一个新的工序/点位，并与一个题库关联。
        """
        db_obj = Procedure(**obj_in.model_dump(), question_bank_id=question_bank_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

crud_procedure = CRUDProcedure(Procedure)