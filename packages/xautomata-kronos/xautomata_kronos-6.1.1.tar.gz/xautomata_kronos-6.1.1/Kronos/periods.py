from typing import Literal

class Periods:
    td = None

    def in_periods(self, period:['seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'years']='seconds') -> int:
        """
        convert a time difference into the chosen time period

        Args:
            period: the approximation required to get the time difference

        Returns:
            number of time element selected
        """
        if period in 'seconds':
            td = int(self.td.total_seconds())
        elif period in 'minutes':
            td = int(self.td.total_seconds()/60)
        elif period in 'hours':
            td = int(self.td.total_seconds()/(60*60))
        elif period in 'days':
            td = int(self.td.total_seconds()/(60*60*24))
        elif period in 'weeks':
            td = int(self.td.total_seconds()/(60*60*24*7))
        elif period in 'months':
            td = int((self.td.total_seconds()/(60*60*24*7*(52/12))))
        elif period in 'years':
            td = int(self.td.total_seconds()/(60*60*24*7*52))
        else:
            raise NotImplementedError

        return td

    def in_seconds(self) -> int:
        """
        convert a time difference into seconds

        Returns:
            number of seconds
        """
        return self.in_periods('seconds')

    def in_minutes(self) -> int:
        """
        convert a time difference into minutes

        Returns:
            number of minutes
        """
        return self.in_periods('minutes')

    def in_hours(self) -> int:
        """
        convert a time difference into hours

        Returns:
            number of hours
        """
        return self.in_periods('hours')

    def in_days(self) -> int:
        """
        convert a time difference into days

        Returns:
            number of days
        """
        return self.in_periods('days')

    def in_weeks(self) -> int:
        """
        convert a time difference into weeks

        Returns:
            number of weeks
        """
        return self.in_periods('weeks')

    def in_months(self) -> int:
        """
        convert a time difference into months

        Returns:
            number of months
        """
        return self.in_periods('months')

    def in_years(self) -> int:
        """
        convert a time difference into years

        Returns:
            number of years
        """
        return self.in_periods('years')