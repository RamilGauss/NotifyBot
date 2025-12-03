import calendar

class DateUtils:
    @staticmethod
    def DayStrToNumberEn(dayStr):
        fullDays = list(calendar.day_name)
        abbrDays = list(calendar.day_abbr)
        normalizedStr = dayStr.capitalize()
        if normalizedStr in fullDays:
            return fullDays.index(normalizedStr)
        if normalizedStr in abbrDays:
            return abbrDays.index(normalizedStr)
        return None

    @staticmethod
    def ConvertWeekDayRuToEn(dayStr):
        weekdays = list(calendar.day_name)
        weekDict = {
            "е": DateUtils.EveryDay(),
            "пн": weekdays[0],
            "вт": weekdays[1],
            "ср": weekdays[2],
            "чт": weekdays[3],
            "пт": weekdays[4],
            "сб": weekdays[5],
            "вс": weekdays[6],
        }
        if dayStr in weekDict:
            return weekDict[dayStr]
        return None

    @staticmethod
    def ConvertWeekDayEnToRu(dayStr):
        weekdays = list(calendar.day_name)
        weekDict = {
            DateUtils.EveryDay() : "ежедневно",
            weekdays[0] : "понедельник",
            weekdays[1] : "вторник",
            weekdays[2] : "среда",
            weekdays[3] : "четверг",
            weekdays[4] : "пятница",
            weekdays[5] : "суббота",
            weekdays[6] : "воскресенье",
        }
        if dayStr in weekDict:
            return weekDict[dayStr]
        return None

    @staticmethod
    def EveryDay():
        return "every day"