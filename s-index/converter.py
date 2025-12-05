import matplotlib.pyplot as plt
#from astropy.stats import LombScargle
import numpy as np
import pandas as pd
import seaborn as sns
import math
import datetime as dt
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit
import statistics  as sts
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import glob

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score

from scipy.stats import shapiro
import matplotlib.pyplot as plt
#from mpl_toolkits.axes_grid1.inset_locator import InsetPosition
#from mpl_toolkits.axes_grid.inset_locator import inset_axes
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.gridspec as gridspec

import matplotlib.offsetbox as offsetbox
import matplotlib.animation as animation

from matplotlib.offsetbox import AnchoredText
from matplotlib.offsetbox import TextArea, VPacker, AnnotationBbox
import statsmodels.api as sm

print("Tudo OK")

#%matplotlib notebook


def date_to_jd(year,month,day):
    """
    Convert a date to Julian Day.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
    
    Returns
    -------
    jd : float
        Julian Day
        
    Examples
    --------
    Convert 6 a.m., February 17, 1985 to Julian Day
    
    >>> date_to_jd(1985,2,17.25)
    2446113.75
    
    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
        
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)
        
    D = math.trunc(30.6001 * (monthp + 1))
    
    jd = B + C + D + day + 1720994.5
    
    return jd
    
    
def jd_to_date(jd):
    """
    Convert Julian Day to date.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    jd : float
        Julian Day
        
    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
        
    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.
    
    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)
    
    """
    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    
       
    return year, month, day
    
def jdtodatestd (jdate):
    fmt = '%Y%j'
    datestd = dt.datetime.strptime(str(jdate), fmt).date()
    return(datestd)


def jd_to_date_year(jd):
    """
    Convert Julian Day to date.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    jd : float
        Julian Day
        
    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
        
    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.
    
    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)
    
    """
    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return year

def jd_to_date_month(jd):
    """
    Convert Julian Day to date.
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    jd : float
        Julian Day
        
    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
        
    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.
    
    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)
    
    """
    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return month
    
    
def hmsm_to_days(hour=0,min=0,sec=0,micro=0):
    """
    Convert hours, minutes, seconds, and microseconds to fractional days.
    
    Parameters
    ----------
    hour : int, optional
        Hour number. Defaults to 0.
    
    min : int, optional
        Minute number. Defaults to 0.
    
    sec : int, optional
        Second number. Defaults to 0.
    
    micro : int, optional
        Microsecond number. Defaults to 0.
        
    Returns
    -------
    days : float
        Fractional days.
        
    Examples
    --------
    >>> hmsm_to_days(hour=6)
    0.25
    
    """
    days = sec + (micro / 1.e6)
    
    days = min + (days / 60.)
    
    days = hour + (days / 60.)
    
    return days / 24.
    
    
def days_to_hmsm(days):
    """
    Convert fractional days to hours, minutes, seconds, and microseconds.
    Precision beyond microseconds is rounded to the nearest microsecond.
    
    Parameters
    ----------
    days : float
        A fractional number of days. Must be less than 1.
        
    Returns
    -------
    hour : int
        Hour number.
    
    min : int
        Minute number.
    
    sec : int
        Second number.
    
    micro : int
        Microsecond number.
        
    Raises
    ------
    ValueError
        If `days` is >= 1.
        
    Examples
    --------
    >>> days_to_hmsm(0.1)
    (2, 24, 0, 0)
    
    """
    hours = days * 24.
    hours, hour = math.modf(hours)
    
    mins = hours * 60.
    mins, min = math.modf(mins)
    
    secs = mins * 60.
    secs, sec = math.modf(secs)
    
    micro = round(secs * 1.e6)
    
    return int(hour), int(min), int(sec), int(micro)
    

def datetime_to_jd(date):
    """
    Convert a `datetime.datetime` object to Julian Day.
    
    Parameters
    ----------
    date : `datetime.datetime` instance
    
    Returns
    -------
    jd : float
        Julian day.
        
    Examples
    --------
    >>> d = datetime.datetime(1985,2,17,6)  
    >>> d
    datetime.datetime(1985, 2, 17, 6, 0)
    >>> jdutil.datetime_to_jd(d)
    2446113.75
    
    """
    days = date.day + hmsm_to_days(date.hour,date.minute,date.second,date.microsecond)
    
    return date_to_jd(date.year,date.month,days)
from datetime import datetime, timedelta

def dc_to_date(start):

    year = int(start)
    rem = start - year

    base = datetime(year, 1, 1)
    result = base + timedelta(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * rem)
    #date = datetime.strftime(result, '%Y-%m-%d')

    
    return result

def jd_to_datetime(jd):
    """
    Convert a Julian Day to an `jdutil.datetime` object.
    
    Parameters
    ----------
    jd : float
        Julian day.
        
    Returns
    -------
    dt : `jdutil.datetime` object
        `jdutil.datetime` equivalent of Julian day.
    
    Examples
    --------
    >>> jd_to_datetime(2446113.75)
    datetime(1985, 2, 17, 6, 0)
    
    """
    year, month, day = jd_to_date(jd)
    
    frac_days,day = math.modf(day)
    day = int(day)
    
    hour,min,sec,micro = days_to_hmsm(frac_days)
    
    return datetime(year,month,day)