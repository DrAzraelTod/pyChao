# -*- coding: utf-8 -*-
import datetime


def show_day_num(num):
    if (num != 11) and ((num % 10) == 1):
        return str(num) + "st"
    elif (num != 12) and ((num % 10) == 2):
        return str(num) + "nd"
    elif (num != 13) and ((num % 10) == 3):
        return str(num) + "rd"
    else:
        return str(num) + "th"


def is_leap_year(year):
    if (year % 100 != 0) and (year % 4 == 0):
        return True
    elif (year % 100 == 0) and (year % 400 == 0):
        return True
    else:
        return False


def leap_year_correction(aDay, year):
    if is_leap_year(year) and (aDay > 60):
        return aDay - 1
    else:
        return aDay


class ddate(object):
    dSeasonNum = 0
    dDayOfWeek = 0
    dDayOfSeason = 0
    d_yold = 0
    dSeasonHoliday = 0
    dApostleHoliday = 0
    dStTibs = False

    #    def __new__(self):
    #        pass
    def __init__(self):
        self.dSeasonNum = 0
        self.dDayOfWeek = 0
        self.dDayOfSeason = 0
        self.d_yold = 0
        self.dSeasonHoliday = False
        self.dApostleHoliday = False
        self.dStTibs = False

    def __str__(self):
        if self.dStTibs:
            return "ST TIBS DAY!"
        else:
            msg = self.dWeekdays[int(self.dDayOfWeek)] + \
                  u', the ' + show_day_num(self.dDayOfSeason) + \
                  u' day of ' + self.dSeasons[int(self.dSeasonNum)] + \
                  u' in the YOLD ' + str(self.d_yold) + '.'
            if self.dSeasonHoliday:
                msg = msg + u' Celebrate ' + self.dSeasonHolidays[int(self.dSeasonNum)] + '!'
            if self.dApostleHoliday:
                msg = msg + u' Celebrate ' + self.dApostleHolidays[int(self.dSeasonNum)] + '!'
            return msg

    dSeasons = ["Chaos", "Discord", "Confusion", "Bureaucracy", "The Aftermath"]
    dWeekdays = ["Sweetmorn", "Boomtime", "Pungenday", "Prickle-Prickle", "Setting Orange"]
    dApostleHolidays = ["Mungday", "Mojoday", "Syaday", "Zaraday", "Maladay"]
    dSeasonHolidays = ["Chaoflux", "Discoflux", "Confuflux", "Bureflux", "Afflux"]

    def check_holiday(self, day):
        if day == 5:
            self.dApostleHoliday = True
        if day == 50:
            self.dSeasonHoliday = True

    def from_date(self, aDate):
        day_of_year = aDate.timetuple()[7]
        corrected_day = leap_year_correction(day_of_year, aDate.year) - 1
        self.dDayOfSeason = (corrected_day % 73) + 1
        self.dDayOfWeek = (corrected_day % 5)
        self.dSeasonNum = (corrected_day / 73)
        self.d_yold = aDate.year + 1166
        self.dStTibs = is_leap_year(aDate.year) and (day_of_year == 60)
        self.check_holiday(self.dDayOfSeason)

    def today(self):
        pass
