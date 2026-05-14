"""Router Restaurants & Menus."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Restaurant, Menu
from app.schemas import RestaurantOut, MenuOut

router = APIRouter(prefix="/restaurants", tags=["Restaurants & Menus"])

@router.get("/", response_model=List[RestaurantOut])
def list_restaurants(lat: float = 5.36, lon: float = -4.01, radius_km: float = 5.0, db: Session = Depends(get_db)):
    """Liste les restaurants ouverts dans un rayon donné (km) autour d'un point GPS."""
    # Pour SQLite (sans PostGIS), on fait un filtre simple sur lat/lon
    # En production avec PostGIS, on utilisera ST_DWithin
    restaurants = db.query(Restaurant).filter(Restaurant.is_open == True).all()
    # Filtrage approximatif lat/lon (1 deg ~ 111km)
    result = []
    for r in restaurants:
        if r.lat and r.lon:
            dist = ((r.lat - lat)**2 + (r.lon - lon)**2)**0.5 * 111
            if dist <= radius_km:
                result.append(r)
    return result

@router.get("/{restaurant_id}/menus", response_model=List[MenuOut])
def get_menus(restaurant_id: UUID, db: Session = Depends(get_db)):
    """Retourne le menu d'un restaurant spécifique."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant non trouvé")
    menus = db.query(Menu).filter(Menu.restaurant_id == restaurant_id, Menu.is_available == True).all()
    return menus
