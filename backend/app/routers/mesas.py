from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Mesa
from app.schemas import MesaResponse

router = APIRouter(prefix="/mesas", tags=["Mesas & Códigos QR"])

@router.get("/{qr_code}", response_model=MesaResponse)
def validar_mesa_por_qr(qr_code: str, db: Session = Depends(get_db)):
    """
    HU14: Valida si un código QR escaneado por el cliente corresponde a una mesa física real
    en el salón del establecimiento.
    """
    mesa = db.query(Mesa).filter(Mesa.qr_code == qr_code).first()
    if not mesa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código QR inválido. La mesa no existe en el sistema."
        )
    return mesa