from .models import Restaurant, RestaurantCreate
from .database import get_session, init_db
from sqlmodel import select

def seed():
    init_db()
    sample = [
        Restaurant(name="진미식당", category="한식", city="서울", rating=4.6),
        Restaurant(name="스시히로", category="일식", city="서울", rating=4.5),
        Restaurant(name="부산밀면명가", category="한식", city="부산", rating=4.2),
        Restaurant(name="나폴리피자하우스", category="양식", city="대구", rating=4.1),
        Restaurant(name="타이사바이", category="아시안", city="서울", rating=4.3),
    ]
    with get_session() as session:
        exists = session.exec(select(Restaurant)).first()
        if exists:
            print("이미 데이터가 존재합니다. 건너뜀.")
            return
        session.add_all(sample)
        session.commit()
        print("샘플 데이터 주입 완료!")

if __name__ == "__main__":
    seed()
