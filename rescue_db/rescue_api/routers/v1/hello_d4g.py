from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from rescue_api.database import get_db
from rescue_api import models

router = APIRouter()


@router.get("/hello", tags=["test"])
async def root():
    return {"message": "Hello D4G"}


@router.get("/rescuers/{rescuer_id}/assets/{asset_id}", tags=["rescues"])
async def get_rescue(rescuer_id: int, asset_id: int, db: Session = Depends(get_db)):
    rescue = db.query(models.Rescue).filter(
        (models.Rescue.rescuer_id == rescuer_id) & (models.Rescue.asset_id == asset_id)
    ).first()
    if not rescue:
        raise HTTPException(status_code=404, detail="Rescue not found")

    return rescue


@router.put("/rescuers/{rescuer_id}/assets/{asset_id}", tags=["rescues"])
async def update_rescue(
        rescuer_id: int,
        asset_id: int,
        magnet_link: str,
        status: str,
        db: Session = Depends(get_db)
):

    rescue = db.query(models.Rescue).filter(
        (models.Rescue.rescuer_id == rescuer_id) & (models.Rescue.asset_id == asset_id)
    ).first()
    if not rescue:
        raise HTTPException(status_code=404, detail="Rescue not found")

    rescue.magnet_link = magnet_link
    rescue.status = status

    db.commit()
    db.refresh(rescue)

    return rescue
