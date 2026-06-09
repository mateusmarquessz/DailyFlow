from datetime import date

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import ReportExportFormat, ReportPeriod, ReportSummary
from app.services.report_export import build_excel, build_pdf
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])

_EXPORT_MEDIA_TYPES = {
    ReportExportFormat.pdf: "application/pdf",
    ReportExportFormat.excel: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
_EXPORT_EXTENSIONS = {
    ReportExportFormat.pdf: "pdf",
    ReportExportFormat.excel: "xlsx",
}
_EXPORT_BUILDERS = {
    ReportExportFormat.pdf: build_pdf,
    ReportExportFormat.excel: build_excel,
}


def _service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("/summary", response_model=ReportSummary)
def get_summary(
    period: ReportPeriod = ReportPeriod.weekly,
    reference_date: date | None = None,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(_service),
) -> ReportSummary:
    summary = service.build_summary(current_user.id, period, reference_date=reference_date)
    return ReportSummary.model_validate(summary)


@router.get("/export")
def export_report(
    period: ReportPeriod = ReportPeriod.weekly,
    format: ReportExportFormat = ReportExportFormat.pdf,
    reference_date: date | None = None,
    current_user: User = Depends(get_current_user),
    service: ReportService = Depends(_service),
) -> Response:
    summary = service.build_summary(current_user.id, period, reference_date=reference_date)
    content = _EXPORT_BUILDERS[format](summary, user_name=current_user.name)
    filename = f"dailyflow-relatorio-{period.value}-{summary['end_date'].isoformat()}.{_EXPORT_EXTENSIONS[format]}"
    return Response(
        content=content,
        media_type=_EXPORT_MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
