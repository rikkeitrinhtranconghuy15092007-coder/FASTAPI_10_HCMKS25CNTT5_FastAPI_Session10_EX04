import uvicorn
from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel
from typing import Optional

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/ecommerce_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ShipmentModel(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(50), default="PREPARING")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Shipment Tracking Analysis API")

class ShipmentResponse(BaseModel):
    id: int
    tracking_number: str
    status: str

class APIResponse(BaseModel):
    status_code: int
    success: bool
    message: str
    data: Optional[ShipmentResponse] = None

@app.get("/shipments/{shipment_id}", status_code=status.HTTP_200_OK, response_model=APIResponse)
async def get_shipment_detail(shipment_id: int, db: Session = Depends(get_db)):
    
    shipment = db.query(ShipmentModel).filter(ShipmentModel.id == shipment_id).first()
    
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status_code": 404,
                "success": False,
                "message": "Mã vận đơn không tồn tại trên hệ thống",
                "data": None
            }
        )
        
    return APIResponse(
        status_code=200,
        success=True,
        message="Tìm thấy thông tin vận đơn thành công!",
        data=ShipmentResponse(
            id=shipment.id,
            tracking_number=shipment.tracking_number,
            status=shipment.status
        )
    )

@app.post("/init-shipments", status_code=status.HTTP_201_CREATED)
async def init_shipments(db: Session = Depends(get_db)):
    if db.query(ShipmentModel).count() == 0:
        db.add_all([
            ShipmentModel(tracking_number="SPX1102", status="PREPARING"),
            ShipmentModel(tracking_number="VNPOST992", status="SHIPPING"),
            ShipmentModel(tracking_number="GHTK883", status="DELIVERED")
        ])
        db.commit()
        return {"message": "Đã khởi tạo nhanh 3 mã vận đơn mẫu có ID: 1, 2, 3"}
    return {"message": "Bảng vận đơn đã có dữ liệu mẫu"}