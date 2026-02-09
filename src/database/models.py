from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, DateTime, func, Float, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from .database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    l1_manager = Column(String, nullable=True)
    l1_manager_code = Column(String, nullable=True)
    l2_manager = Column(String, nullable=True)
    l2_manager_code = Column(String, nullable=True)
    hrbp_name = Column(String, nullable=True)
    hrbp_code = Column(String, nullable=True)
    location = Column(String, nullable=True)
    joining_date = Column(String, nullable=True)
    exit_date = Column(String, nullable=True)
    date_of_resignation = Column(String, nullable=True)
    survey_initiated_date = Column(String, nullable=True)
    survey_submission_date = Column(String, nullable=True)
    overall_sentiment = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    department = Column(String, index=True, nullable=True)
    sub_department = Column(String, nullable=True)  
    designation = Column(String, nullable=True)

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
    
    exit_category = Column(String, index=True) # e.g., "Salary"
    is_controllable = Column(Boolean, default=True)
    
    employee = relationship("Employee", back_populates="analysis_report")


# class MonthlyReasonStats(Base):
#     __tablename__ = "monthly_reason_stats"
#     id = Column(Integer, primary_key=True, index=True)
#     month = Column(Integer, nullable=False)
#     year = Column(Integer, nullable=False)
#     reason_name = Column(String, nullable=False)
#     percentage = Column(Float, nullable=False)
#     total_count = Column(Integer, nullable=False) # Number of people for this reason
#     total_month_exits = Column(Integer, nullable=False) # Total people who left that month

class DepartmentStats(Base):
    __tablename__ = "department_stats"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    department = Column(String, nullable=False, index=True)
    
    total_exits = Column(Integer, default=0)
    
    # Ensure unique constraint for updates
    __table_args__ = (UniqueConstraint('month', 'year', 'department', name='_dept_month_uc'),)

class CategoryStats(Base):
    __tablename__ = "category_stats"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    department = Column(String, nullable=False, index=True)
    
    reason_name = Column(String, nullable=False) 
    count = Column(Integer, default=0)
    percentage = Column(Float, default=0.0) 
    
    __table_args__ = (UniqueConstraint('month', 'year', 'department', 'reason_name', name='_cat_dept_month_uc'),)

class CategoryDetailedReason(Base):
    __tablename__ = "category_detailed_reasons"

    id = Column(Integer, primary_key=True, index=True)
    
    month = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    department = Column(String, nullable=False, index=True)
    
    category_name = Column(String, nullable=False, index=True)
    
    # The extracted text from Question 16
    employee_answer = Column(Text, nullable=False)