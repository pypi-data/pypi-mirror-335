from datetime import timezone, timedelta, datetime
import pytz


class TimeZones:
    utc = timezone.utc

    rome = timezone(timedelta(hours=1))  # time zone invernale o solare
    rome_legal = timezone(timedelta(hours=2))  # timezone estiva o legale

    london = timezone(timedelta(hours=0))  # time zone invernale o solare
    london_legal = timezone(timedelta(hours=1))  # timezone estiva o legale

    tz00 = timezone(timedelta(hours=0))

    tz01 = timezone(timedelta(hours=1))
    tz02 = timezone(timedelta(hours=2))
    tz03 = timezone(timedelta(hours=3))
    tz04 = timezone(timedelta(hours=4))
    tz05 = timezone(timedelta(hours=5))
    tz06 = timezone(timedelta(hours=6))
    tz07 = timezone(timedelta(hours=7))
    tz08 = timezone(timedelta(hours=8))
    tz09 = timezone(timedelta(hours=9))
    tz10 = timezone(timedelta(hours=10))
    tz11 = timezone(timedelta(hours=11))
    tz12 = timezone(timedelta(hours=12))
    tz13 = timezone(timedelta(hours=13))
    tz14 = timezone(timedelta(hours=14))

    tzm01 = timezone(timedelta(hours=-1))
    tzm02 = timezone(timedelta(hours=-2))
    tzm03 = timezone(timedelta(hours=-3))
    tzm04 = timezone(timedelta(hours=-4))
    tzm05 = timezone(timedelta(hours=-5))
    tzm06 = timezone(timedelta(hours=-6))
    tzm07 = timezone(timedelta(hours=-7))
    tzm08 = timezone(timedelta(hours=-8))
    tzm09 = timezone(timedelta(hours=-9))
    tzm10 = timezone(timedelta(hours=-10))
    tzm11 = timezone(timedelta(hours=-11))

    # +2 tra le 2:00 del mattino dell'ultima domenica di marzo e le 3:00 del mattino dell'ultima domenica di ottobre
    # +1 le 3:00 del mattino dell'ultima domenica di ottobre e le 2:00 del mattino dell'ultima domenica di marzo
    dict_zones = {'utc': utc,
                  'rome': rome, 'it': rome, 'IT': rome,
                  'london': london, 'uk': london, 'UK': london,
                  '+00': tz00, '+01': tz01, '+02': tz02, '+03': tz03, '+04': tz04, '+05': tz05, '+06': tz06, '+07': tz07,
                  '+08': tz08, '+09': tz09, '+10': tz10, '+11': tz11, '+12': tz12, '+13': tz13, '+14': tz14,
                  '-00': tz00, '-01': tzm01, '-02': tzm02, '-03': tzm03, '-04': tzm04, '-05': tzm05, '-06': tzm06, '-07': tzm07,
                  '-08': tzm08, '-09': tzm09, '-10': tzm10, '-11': tzm11,}

    def __init__(self, now: datetime = datetime.now()):
        self.now = now
        # self.reset()
        self._rome(now)
        self._london(now)

    # def reset(self):
    #     self.rome = timezone(timedelta(hours=1))  # time zone invernale o solare
    #     self.rome_legal = timezone(timedelta(hours=2))  # timezone estiva o legale

    def zone(self, tz:str=None) -> timezone:
        """
            Restituisce un oggetto timezone basato sulla stringa fornita o sull'orario UTC di default.

            Questo metodo verifica se la stringa fornita rappresenta una zona valida e la converte in un oggetto timezone.
            Se la stringa non è valida, viene sollevato un ValueError.

            Args:
                tz (str, optional): Una stringa che rappresenta la zona oraria desiderata. Può essere uno dei seguenti:
                    - Chiavi definite in `dict_zones` (es. 'rome', 'it', 'UK')
                    - Stringhe rappresentanti fusi orari supportati da `pytz` (es. 'Europe/Rome', 'America/New_York')
                    Se `tz` è None, viene restituito il fuso orario UTC.

            Returns:
                timezone: Un oggetto timezone che rappresenta la zona oraria specificata.

            Raises:
                ValueError: Se la stringa fornita non rappresenta una zona oraria valida.

            Esempi:
                >> tz = TimeZones()
                >> tz.zone('rome')
                datetime.timezone(datetime.timedelta(seconds=3600))

                >> tz.zone('Europe/Rome')
                <DstTzInfo 'Europe/Rome' CET+1:00:00 STD>

                >> tz.zone('Invalid/Timezone')
                ValueError: Invalid/Timezone is not a valid timezone
        """

        # if tz is None it use the UTC timezone
        if tz is None:
            tz = self.dict_zones['utc']

        # if tz is a string compatible with pytz timezones use that one
        elif isinstance(tz, str) and tz not in self.dict_zones:
            if tz in pytz.all_timezones:
                tz = pytz.timezone(tz)  # finds the timezone
                tz = tz.localize(self.now).tzinfo  # convert the timezone with the propre GMT based on the actual time
            else:
                raise ValueError(f'{tz} is not a valid timezone')

        elif isinstance(tz, pytz.tzinfo.BaseTzInfo):  # se la tz passata è stata generata con pytz, puo essere usata
            tz = tz.localize(self.now).tzinfo

        # if the string is in the dict_zones use that one
        elif isinstance(tz, str) and tz in self.dict_zones:
            tz = self.dict_zones[tz]

        elif isinstance(tz, timezone):
            pass

        else:
            raise ValueError(f'{tz} is not a valid timezone')

        return tz

    def _rome(self, now):
        weekday_last_day_of_march = datetime(year=now.year, month=3, day=31).weekday()
        last_sun_of_march = datetime(year=now.year, month=3, day=31 - (weekday_last_day_of_march + 1), hour=2)

        weekday_last_day_of_oct = datetime(year=now.year, month=10, day=31).weekday()
        last_sun_of_oct = datetime(year=now.year, month=10, day=31 - (weekday_last_day_of_oct + 1), hour=3)

        is_legal = last_sun_of_march < now < last_sun_of_oct
        # print(f'is_legal {is_legal}')
        if is_legal:
            self.rome = self.rome_legal
            self.dict_zones['rome'] = self.rome_legal
            self.dict_zones['it'] = self.rome_legal
            self.dict_zones['IT'] = self.rome_legal
            # print(f'rome_legal {self.rome_legal}')
        else:
            self.dict_zones['rome'] = self.rome
            self.dict_zones['it'] = self.rome
            self.dict_zones['IT'] = self.rome
            # print(f'rome_legal {self.rome_legal}')

    def _london(self, now):
        weekday_last_day_of_march = datetime(year=now.year, month=3, day=31).weekday()
        last_sun_of_march = datetime(year=now.year, month=3, day=31 - (weekday_last_day_of_march + 1), hour=2)

        weekday_last_day_of_oct = datetime(year=now.year, month=10, day=31).weekday()
        last_sun_of_oct = datetime(year=now.year, month=10, day=31 - (weekday_last_day_of_oct + 1), hour=3)

        is_legal = last_sun_of_march < now < last_sun_of_oct
        if is_legal:
            self.london = self.london_legal
            self.dict_zones['london'] = self.london_legal
            self.dict_zones['uk'] = self.london_legal
            self.dict_zones['UK'] = self.london_legal
        else:
            self.dict_zones['london'] = self.london
            self.dict_zones['uk'] = self.london
            self.dict_zones['UK'] = self.london