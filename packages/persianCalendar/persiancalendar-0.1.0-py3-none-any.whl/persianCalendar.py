import datetime, math

def convert_number(n, to_persian=True):
    s = str(n)
    return s.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")) if to_persian else s

def gregorian_to_jalali(gy, gm, gd):
    g_dm = [0, 31,28,31,30,31,30,31,31,30,31,30,31]
    if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0):
        g_dm[2] = 29
    gy2 = gy - 1600; gm2 = gm - 1; gd2 = gd - 1
    g_day_no = 365 * gy2 + math.floor((gy2+3)/4) - math.floor((gy2+99)/100) + math.floor((gy2+399)/400)
    for i in range(gm2):
        g_day_no += g_dm[i+1]
    g_day_no += gd2
    j_day_no = g_day_no - 79
    j_np = math.floor(j_day_no/12053)
    j_day_no %= 12053
    jy = 979 + 33*j_np + 4*math.floor(j_day_no/1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += math.floor((j_day_no-1)/365)
        j_day_no = (j_day_no-1)%365
    if j_day_no < 186:
        jm = 1 + math.floor(j_day_no/31)
        jd = 1 + (j_day_no % 31)
    else:
        jm = 7 + math.floor((j_day_no-186)/30)
        jd = 1 + ((j_day_no-186) % 30)
    return (jy, jm, jd)

def jalali_to_gregorian(jy, jm, jd):
    if jy > 979:
        gy = 1600; jy -= 979
    else:
        gy = 621
    days = (365*jy) + (math.floor(jy/33)*8) + math.floor(((jy%33)+3)/4)
    for i in range(1, jm):
        days += 31 if i<=6 else 30
    days += jd-1
    g_day_no = days+79
    gy += 400*math.floor(g_day_no/146097)
    g_day_no %= 146097
    leap = True
    if g_day_no >= 36525:
        g_day_no -= 1
        gy += 100*math.floor(g_day_no/36524)
        g_day_no %= 36524
        if g_day_no < 365:
            leap = False
        else:
            g_day_no += 1
    gy += 4*math.floor(g_day_no/1461)
    g_day_no %= 1461
    if g_day_no >= 366:
        leap = False
        g_day_no -= 1
        gy += math.floor(g_day_no/365)
        g_day_no %= 365
    gd = g_day_no+1
    g_dm = [0,31,28,31,30,31,30,31,31,30,31,30,31]
    if leap:
        g_dm[2] = 29
    gm = 0
    for i in range(1,13):
        if gd <= g_dm[i]:
            gm = i
            break
        gd -= g_dm[i]
    return (gy, gm, gd)

class PersianCalendar:
    def __init__(self, use_persian_numbers=True, nowruz_time=datetime.time(12,30,31)):
        self.use_persian_numbers = use_persian_numbers
        self.nowruz_time = nowruz_time
        self.jalali_month_names = {
            1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
            5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
            9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
        }
        self.english_day_names = {
            "Saturday": "Saturday", "Sunday": "Sunday", "Monday": "Monday",
            "Tuesday": "Tuesday", "Wednesday": "Wednesday", "Thursday": "Thursday",
            "Friday": "Friday"
        }
        self.english_to_persian_day = {
            "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
            "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه", "Thursday": "پنج‌شنبه",
            "Friday": "جمعه"
        }

    def today_jalali(self):
        t = datetime.date.today()
        return gregorian_to_jalali(t.year, t.month, t.day)

    def format_date(self, dt_tuple):
        jy, jm, jd = dt_tuple
        s = f"{jy:04d}/{jm:02d}/{jd:02d}"
        return convert_number(s, self.use_persian_numbers)

    def get_hijri_date(self):
        return datetime.date.today().strftime("%Y-%m-%d")

    def get_nowruz(self, year):
        g = jalali_to_gregorian(year, 1, 1)
        base_target = datetime.datetime(g[0], g[1], g[2],
                                        self.nowruz_time.hour,
                                        self.nowruz_time.minute,
                                        self.nowruz_time.second)
        return base_target - datetime.timedelta(days=1) + datetime.timedelta(minutes=1)

    def next_nowruz(self):
        now = datetime.datetime.now()
        jy, _, _ = self.today_jalali()
        candidate = self.get_nowruz(jy+1)
        if now >= candidate:
            candidate = self.get_nowruz(jy+2)
        return candidate - now

    def _last_weekday_of_month(self, jy, jm, weekday):
        if jm <= 6:
            days = 31
        elif jm <= 11:
            days = 30
        else:
            days = 30 if self._is_esfand_30(jy) else 29
        d = datetime.date(*jalali_to_gregorian(jy, jm, days))
        while d.weekday() != weekday:
            d -= datetime.timedelta(days=1)
        return gregorian_to_jalali(d.year, d.month, d.day)

    def _is_esfand_30(self, jy):
        return ((jy-474) % 2820 + 474 + 38)*682 % 2816 < 682

    def next_chaharshanbe_suri(self):
        now = datetime.datetime.now()
        jy, _, _ = self.today_jalali()
        event = self._last_weekday_of_month(jy, 12, weekday=1)
        g = jalali_to_gregorian(*event)
        target = datetime.datetime(g[0], g[1], g[2], 0, 0, 0)
        if now >= target:
            event = self._last_weekday_of_month(jy+1, 12, weekday=1)
            g = jalali_to_gregorian(*event)
            target = datetime.datetime(g[0], g[1], g[2], 0, 0, 0)
        return f"{(target - now).days} days"

    def next_school_end(self):
        now = datetime.datetime.now()
        jy, _, _ = self.today_jalali()
        candidate = self._last_weekday_of_month(jy, 2, weekday=2) 
        g = jalali_to_gregorian(*candidate)
        target = datetime.datetime(g[0], g[1], g[2], 23, 59, 59)
        if now >= target:
            return "0 days"
        return f"{(target - now).days} days"

    def next_sizdah_bedar(self):
        now = datetime.datetime.now()
        jy, jm, jd = self.today_jalali()
        target_year = jy if (jm == 1 and jd < 13) else jy + 1
        g = jalali_to_gregorian(target_year, 1, 13)
        target = datetime.datetime(g[0], g[1], g[2], 0, 0, 0)
        if now >= target:
            target_year += 1
            g = jalali_to_gregorian(target_year, 1, 13)
            target = datetime.datetime(g[0], g[1], g[2], 0, 0, 0)
        return f"{(target - now).days} days"

    def current_time(self):
        t = datetime.datetime.now().time().strftime("%H:%M:%S")
        return convert_number(t, self.use_persian_numbers)

    def current_day_names(self):
        today = datetime.date.today()
        eng_day = today.strftime("%A")
        fa_day = self.english_to_persian_day.get(eng_day, eng_day)
        return fa_day, eng_day

    def week_number(self):
        jy, jm, jd = self.today_jalali()
        if jm <= 6:
            day_of_year = (jm - 1)*31 + jd
        else:
            day_of_year = 6*31 + (jm - 7)*30 + jd
        week_num = ((day_of_year - 1) // 7) + 1
        return convert_number(week_num, self.use_persian_numbers)

    def current_jalali_month_name(self):
        jy, jm, _ = self.today_jalali()
        name = self.jalali_month_names.get(jm, "")
        return name

    def current_gregorian_month_name(self):
        return datetime.date.today().strftime("%B")