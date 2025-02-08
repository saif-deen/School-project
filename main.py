from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import random

app = FastAPI()

DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    school = Column(String)
    study_year = Column(String)
    place_of_residence = Column(String)

Base.metadata.create_all(bind=engine)

# Request Schema
from typing import Optional

class StudentCreateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    school: Optional[str] = None
    study_year: Optional[str] = None
    place_of_residence: Optional[str] = None

    class Config:
        orm_mode = True




# Response Schema
class StudentResponseSchema(StudentCreateSchema):
    id: int  # id is automatically generated

    class Config:
        orm_mode = True




# Helper function to seed database with Arabic data
def seed_data_with_arabic_data():
    db = SessionLocal()

    # Clear existing data
    db.query(Student).delete()
    db.commit()

    arabic_names = [
        "علي أحمد", "محمد سالم", "فاطمة عمر", "سعاد حسين", "خالد مصطفى",
        "مريم حسن", "أحمد عبد الله", "هالة يوسف", "يوسف بشير", "ليلى محمود",
        "حسن علي", "سميرة خليل", "إبراهيم ناصر", "منى صالح", "مروان عيسى",
        "ليلى عبد الرحمن", "عبد الله محمود", "نور الهادي", "رشيد عبد الله", "نجلاء حامد",
        "وسيم محمد", "هدى إبراهيم", "عبد الرحمن علي", "سالم مصطفى", "آية خالد",
        "عبد الباسط حسن", "ريم أحمد", "نادر يوسف", "ياسمين محمود", "جلال بشير",
        "رغدة محمد", "فارس عبد الله", "لينا سالم", "طارق محمود", "نهى عمر",
        "عمر عبد الكريم", "حنان يوسف", "نسرين علي", "حسين سالم", "ماهر إبراهيم",
        "جيهان خالد", "وليد عبد الرحمن", "بدر حسن", "شيماء مصطفى", "بلال ناصر",
        "هاني إبراهيم", "آمنة علي", "نادية حسين", "زهرة سالم", "ماجد أحمد",
        "عبير علي", "رائد مصطفى", "مها عبد الله", "شريف يوسف", "نورا محمود",
        "كريم بشير", "مروى محمد", "زياد عبد الله", "رانيا سالم", "فاطمة حسن",
        "محمود علي", "سعيد ناصر", "صفاء سالم", "مصطفى إبراهيم", "حنين خالد",
        "يحيى عبد الله", "لبنى محمود", "جهاد سالم", "رنا عمر", "نادر حسن",
        "سليمان بشير", "نهال محمد", "حمزة عبد الله", "ريما خليل", "عائشة علي",
        "زيد إبراهيم", "لمياء سالم", "باسم مصطفى", "منى ناصر", "رامي يوسف",
        "روان محمود", "فادي بشير", "نادية محمد", "عمار عبد الله", "سارة سالم",
        "مها إبراهيم", "إسلام ناصر", "هديل علي", "شذى محمود", "هيثم سالم",
        "بشار سعيد", "ليان أحمد", "مالك عبد الله", "سامية يوسف", "نوران حسن",
        "عادل مصطفى", "داليا ناصر", "رائد إبراهيم", "رشا سالم", "زينة خالد"
    ]

    schools = [
        "مدرسة الاستقلال", "مدرسة النور", "مدرسة الفرقان", "مدرسة طرابلس المركز", "مدرسة الأمل الثانوية",
        "مدرسة الهدى", "مدرسة المستقبل", "مدرسة الأقصى", "مدرسة البيان", "مدرسة الفجر الجديد"
    ]

    streets = [
        "شارع عمر المختار", "شارع الاستقلال", "شارع الجمهورية", "شارع النصر", "شارع المدار",
        "شارع سوق الجمعة", "شارع الظهرة", "شارع ميزران", "شارع بن عاشور", "شارع باب بن غشير"
    ]

    study_years = [
        "السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة",
        "السنة السادسة", "السنة السابعة", "السنة الثامنة", "السنة التاسعة", "السنة العاشرة",
        "السنة الحادية عشرة", "السنة الثانية عشرة"
    ]

    ages = list(range(10, 19))  # Ages between 10 and 18 inclusive

    for _ in range(100):  # Maximum of 100 records as requested
        student = Student(
            name=random.choice(arabic_names),
            age=random.choice(ages),
            school=random.choice(schools),
            study_year=random.choice(study_years),
            place_of_residence=random.choice(streets)
        )
        db.add(student)
    db.commit()
    db.close()

#seed_data_with_arabic_data()


# CRUD Operations
@app.post("/students/", response_model=StudentResponseSchema)
def create_student(student: StudentCreateSchema):
    db = SessionLocal()
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    db.close()
    return db_student



@app.get("/students/{student_id}", response_model=StudentResponseSchema)
def get_student(student_id: int):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()
    db.close()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student



@app.get("/students/", response_model=list[StudentResponseSchema])
def list_students():
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    return students







@app.put("/students/{student_id}", response_model=StudentResponseSchema)
def update_student(student_id: int, student_data: StudentCreateSchema):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")

    # Only update fields that are not None
    if student_data.name is not None:
        student.name = student_data.name
    if student_data.age is not None:
        student.age = student_data.age
    if student_data.school is not None:
        student.school = student_data.school
    if student_data.study_year is not None:
        student.study_year = student_data.study_year
    if student_data.place_of_residence is not None:
        student.place_of_residence = student_data.place_of_residence

    # Commit the changes to the database
    db.commit()
    db.refresh(student)
    db.close()

    return student






@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    db = SessionLocal()
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        db.close()
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    db.close()
    return {"detail": f"Student with ID {student_id} deleted successfully"}


@app.get("/students/search/", response_model=list[StudentResponseSchema])  # Use StudentResponseSchema here
def search_students(
    name: str = None,
    age: int = None,
    school: str = None,
    study_year: str = None,
    place_of_residence: str = None
):
    db = SessionLocal()
    query = db.query(Student)

    if name:
        query = query.filter(Student.name == name)
    if age:
        query = query.filter(Student.age == age)
    if school:
        query = query.filter(Student.school == school)
    if study_year:
        query = query.filter(Student.study_year == study_year)
    if place_of_residence:
        query = query.filter(Student.place_of_residence == place_of_residence)

    results = query.all()
    db.close()
    if not results:
        raise HTTPException(status_code=404, detail="No matching students found")
    return results  # No need to add a comma here

