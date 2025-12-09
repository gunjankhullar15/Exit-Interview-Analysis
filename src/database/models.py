from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship
from src.database.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    # department = Column(String, nullable=True)
    # designation = Column(String, nullable=True)
    
    l1_manager = Column(String, nullable=True)
    l1_manager_code = Column(String, nullable=True)
    l2_manager = Column(String, nullable=True)
    l2_manager_code = Column(String, nullable=True)
    hrbp_name = Column(String, nullable=True)
    hrbp_code = Column(String, nullable=True)
    location = Column(String, nullable=True)
    joining_date = Column(String, nullable=True)
    exit_date = Column(String, nullable=True)
    #date_of_resignation = Column(String, nullable=True)
    survey_initiated_date = Column(String, nullable=True)
    survey_submission_date = Column(String, nullable=True)
    overall_sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    survey_response = relationship("SurveyResponse", back_populates="employee", uselist=False)
    analysis_report = relationship("AnalysisReport", back_populates="employee", uselist=False)

class SurveyResponse(Base):
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    raw_answers = Column(JSON, nullable=False)
    status = Column(String, default="PENDING") 
    
    employee = relationship("Employee", back_populates="survey_response")

class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    full_analysis_json = Column(JSON, nullable=True)
    
    employee = relationship("Employee", back_populates="analysis_report")