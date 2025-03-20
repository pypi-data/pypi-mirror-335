
from datetime import date
from dataclasses import dataclass

from inoopa_utils.custom_types.addresses import Country


@dataclass(slots=True)
class PerEmployeeCategory:
    """Hold the counting of a metric."""
    total: int | None = None
    distinct: int | None = None
    emp_0: int = 0
    emp_1_to_4: int = 0
    emp_5_to_10: int = 0
    emp_10_to_19: int = 0
    emp_20_to_49: int = 0
    emp_50_to_99: int = 0
    emp_100_to_199: int = 0
    emp_200_to_499: int = 0
    emp_500_to_999: int = 0
    emp_1000_plus: int = 0
    unknown: int = 0


@dataclass(slots=True)
class CompanyStats:
    """
    Hold the metrics of our company collection at a given point in time.
    Each metric is divided by employee category.
    """
    date: date
    country: Country
    active_companies: PerEmployeeCategory 
    websites: PerEmployeeCategory 
    emails: PerEmployeeCategory
    phones: PerEmployeeCategory 
    attributed_phones: PerEmployeeCategory 


@dataclass(slots=True)
class DecisionMakersStats:
    """
    Hold the stats of the decision_makers collection at a given point in time.
    Each metric is divided by employee category.
    Each metric has a _dm version that counts unique decision makers.
    Each metric has a _companies version that counts unique companies with at least 1 matching DM.
    """
    date: date
    country: Country
    with_name_dms: PerEmployeeCategory
    with_job_title_dms: PerEmployeeCategory
    with_department_dms: PerEmployeeCategory
    with_responsibility_level_dms: PerEmployeeCategory
    with_linkedin_url_dms: PerEmployeeCategory
    with_email_dms: PerEmployeeCategory
    with_name_companies: PerEmployeeCategory
    with_job_title_companies: PerEmployeeCategory
    with_department_companies: PerEmployeeCategory
    with_responsibility_level_companies: PerEmployeeCategory
    with_linkedin_url_companies: PerEmployeeCategory
    with_email_companies: PerEmployeeCategory


def dict_to_company_stats(company_stats: dict) -> CompanyStats:
    """Convert a dict from the DB to a CompanyStats dataclass."""
    company_stats_fmt = CompanyStats(
        date=company_stats["date"],
        country=Country(company_stats["country"]),
        active_companies=PerEmployeeCategory(**company_stats["active_companies"]),
        websites=PerEmployeeCategory(**company_stats["websites"]),
        phones=PerEmployeeCategory(**company_stats["phones"]),
        emails=PerEmployeeCategory(**company_stats["emails"]),
        attributed_phones=PerEmployeeCategory(**company_stats["attributed_phones"]),
    )
    return company_stats_fmt


def dict_to_decision_makers_stats(decision_makers_stats: dict) -> DecisionMakersStats:
    """Convert a dict from the DB to a DecisionMakersStats dataclass."""
    decision_makers_stats_fmt = DecisionMakersStats(
        date=decision_makers_stats["date"],
        country=Country(decision_makers_stats["country"]),
        with_name_dms=PerEmployeeCategory(**decision_makers_stats["with_name_dms"]),
        with_job_title_dms=PerEmployeeCategory(**decision_makers_stats["with_job_title_dms"]),
        with_department_dms=PerEmployeeCategory(**decision_makers_stats["with_department_dms"]),
        with_responsibility_level_dms=PerEmployeeCategory(**decision_makers_stats["with_responsibility_level_dms"]),
        with_linkedin_url_dms=PerEmployeeCategory(**decision_makers_stats["with_linkedin_url_dms"]),
        with_email_dms=PerEmployeeCategory(**decision_makers_stats["with_email_dms"]),
        with_name_companies=PerEmployeeCategory(**decision_makers_stats["with_name_companies"]),
        with_job_title_companies=PerEmployeeCategory(**decision_makers_stats["with_job_title_companies"]),
        with_department_companies=PerEmployeeCategory(**decision_makers_stats["with_department_companies"]),
        with_responsibility_level_companies=PerEmployeeCategory(**decision_makers_stats["with_responsibility_level_companies"]),
        with_linkedin_url_companies=PerEmployeeCategory(**decision_makers_stats["with_linkedin_url_companies"]),
        with_email_companies=PerEmployeeCategory(**decision_makers_stats["with_email_companies"]),
    )
    return decision_makers_stats_fmt

