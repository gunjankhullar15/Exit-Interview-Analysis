from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.database import get_db
from src.database.models import AnalysisReport, Employee, MonthlyReasonStats
from src.database.schemas import DateRangeRequest, ComparisonRequest, MonthYearRequest
from typing import Dict

router = APIRouter()

@router.post("/analytics/monthly-distribution")
async def get_monthly_distribution(req: MonthYearRequest, db: AsyncSession = Depends(get_db)):
    """
    Returns pre-calculated reasons and percentages for a specific month.
    Used for Pie Charts.
    """
    stmt = select(MonthlyReasonStats).where(
        MonthlyReasonStats.month == req.month,
        MonthlyReasonStats.year == req.year
    )
    result = await db.execute(stmt)
    stats = result.scalars().all()

    if not stats:
        return {
            "status": "info",
            "message": "No data found for this period. Please generate reports first.",
            "data": []
        }

    return {
        "month": req.month,
        "year": req.year,
        "total_exits": stats[0].total_month_exits,
        "data": [
            {
                "reason": s.reason_name,
                "percentage": s.percentage,
                "count": s.total_count
            } for s in stats
        ]
    }

@router.post("/analytics/compare-periods")
async def compare_periods(req: ComparisonRequest, db: AsyncSession = Depends(get_db)):
    """
    Compares two dynamic date ranges (DD/MM/YYYY). 
    Calculates on-the-fly to allow for Quarterly or Yearly comparisons.
    """
    
    async def get_stats_for_range(start, end):
        stmt = select(AnalysisReport).join(Employee).filter(
            Employee.exit_date >= start,
            Employee.exit_date <= end
        )
        res = await db.execute(stmt)
        reports = res.scalars().all()
        
        total = len(reports)
        if total == 0: return {}, 0
        
        counts = {}
        for r in reports:
            cat = r.exit_category or "Other"
            counts[cat] = counts.get(cat, 0) + 1
        
        return {k: (v/total)*100 for k, v in counts.items()}, total

    # Get stats for both periods
    curr_data, curr_total = await get_stats_for_range(req.current_period.start_date, req.current_period.end_date)
    prev_data, prev_total = await get_stats_for_range(req.previous_period.start_date, req.previous_period.end_date)

    if curr_total == 0 or prev_total == 0:
        return {"status": "error", "message": "One of the periods has no data to compare."}

    comparison = []
    all_reasons = set(curr_data.keys()) | set(prev_data.keys())

    for reason in all_reasons:
        c_pct = curr_data.get(reason, 0)
        p_pct = prev_data.get(reason, 0)
        delta = p_pct - c_pct # Positive delta = Improvement (reason decreased)

        comparison.append({
            "reason": reason,
            "previous_percentage": round(p_pct, 2),
            "current_percentage": round(c_pct, 2),
            "improvement_delta": round(delta, 2),
            "status": "Improved" if delta > 0 else "Worsened" if delta < 0 else "Stable"
        })

    return {
        "current_total": curr_total,
        "previous_total": prev_total,
        "comparison_results": comparison
    }