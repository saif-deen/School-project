import random
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.llms.base import LLM
from langchain.agents.agent_types import AgentType
from together import Together



# Initialize FastAPI
app = FastAPI()

# Database setup (SQLite with connection pool)
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections every 30 minutes
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define Student Model
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    school = Column(String)
    study_year = Column(String)
    place_of_residence = Column(String)


Base.metadata.create_all(bind=engine)


# Load environment variables from .env file
load_dotenv()

from pathlib import Path
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Raise an error if the key is missing
if not TOGETHER_API_KEY:
    raise ValueError("Missing TOGETHER_API_KEY environment variable")

print("API Key Loaded Successfully!")  # Debugging message


# Pydantic Schemas
class StudentCreateSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    school: Optional[str] = None
    study_year: Optional[str] = None
    place_of_residence: Optional[str] = None

    class Config:
        orm_mode = True


class StudentResponseSchema(StudentCreateSchema):
    id: int


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper function to seed database with Arabic data
def seed_data_with_arabic_data():
    db = SessionLocal()
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

seed_data_with_arabic_data()


# Student CRUD Endpoints
@app.post("/students/", response_model=StudentResponseSchema)
def create_student(student: StudentCreateSchema, db: Session = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students/{student_id}", response_model=StudentResponseSchema)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/students/", response_model=list[StudentResponseSchema])
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"detail": f"Student {student_id} deleted"}


# AI Agent Setup
class TogetherAILLM(LLM):
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or TOGETHER_API_KEY  # Ensure TOGETHER_API_KEY is loaded

    def _call(self, prompt: str, **kwargs) -> str:
        try:
            response = Together(api_key=self.api_key).chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TogetherAI API error: {str(e)}")

    @property
    def _llm_type(self) -> str:
        return "TogetherAI"



# Initialize LangChain SQL Agent
together_ai = TogetherAILLM()
sql_database = SQLDatabase(engine)
sql_agent = create_sql_agent(
    llm=together_ai,
    db=sql_database,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
    max_execution_time=30,
    output_parser_type="action_only",
    agent_executor_kwargs={
        "return_intermediate_steps": True,
        "early_stopping_method": "generate",
    }
)


# AI Query Endpoint
@app.get("/ask_agent/")
def ask_agent(question: str):
    try:
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")

        enhanced_question = f"""
        Please answer the following question about the student database:
        {question}
        Available tables: students
        Student fields: id, name, age, school, study_year, place_of_residence
        Note: Many records contain Arabic text.
        """

        response = sql_agent.run(enhanced_question)
        return {"response": response, "status": "success"}
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Agent error: {error_details}")
        return {"error": str(e), "status": "error"}


# Health Check Endpoint
@app.get("/health")
def health_check():
    try:
        with SessionLocal() as db:
            db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


