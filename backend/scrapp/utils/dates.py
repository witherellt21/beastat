from datetime import datetime

from dateutil.relativedelta import relativedelta


def age_to_birthday(
    age: str, date: str, date_fmt: str = "%Y-%m-%d"
) -> datetime:
    age_years, age_days = age.split(".")

    return datetime.strptime(date, date_fmt) - relativedelta(
        years=int(age_years), days=int(age_days)
    )


def birthday_to_age(
    birthday: datetime, date: str, date_fmt: str = "%Y-%m-%d"
) -> str:
    date_dt = datetime.strptime(date, date_fmt) # Convert the date to datetime
    age = relativedelta(date_dt, birthday) # Get the current age in years, months, days

    # Subtract this years birthday from the current date to get the number of days elapsed
    days_since_last_bday = date_dt - (birthday + relativedelta(years=age.years))

    return ".".join([str(age.years), str(days_since_last_bday.days)])