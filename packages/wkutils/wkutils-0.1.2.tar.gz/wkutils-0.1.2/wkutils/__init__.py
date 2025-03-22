'''
    list_files_in_dir :: returns a list of files in a directory
    find_nth :: find the nth occurrence of a substring in a string
    twoDecimalPlaces :: returns a number as two decimal places
    gross_payment :: returns the gross loan payment
    net_payment :: returns the net loan repayment for mortgages in the netherlands
    calculate_loan_payments :: returns the amount to repay on a loan.
    current_datetime_asstring :: returns the current date and time as string 
''' 

import numpy_financial as npf
import os
from datetime import datetime


def whatever():
    print('whatever')

def current_datetime_asstring():
    """
    Returns the current date and time as a formatted string.

    Returns:
        str: A string representing the current date and time in the format 'YYYY-MM-DD HH:MM:SS'.
    """
    now = datetime.now() # current date and time
    return now.strftime("%Y-%m-%d %H:%M:%S")

def list_files_in_dir(directory):
    """
    Returns a list of all files in the specified directory.

    Args:
        directory (str): The path to the directory to list files from.

    Returns:
        list: A list of file paths in the specified directory.
    """
    filelist = []


    for root, dirs, files in os.walk(directory):
        filelist.extend(os.path.join(root, filename) for filename in files)
    return filelist




def find_nth(haystack: str, needle: str, n: int) -> int:
    '''
        This will find the nth occurrence of a substring in a string 

    Args:
        haystack (str): The text we should search through
        needle (str): What we are searching for
        n (int): Which occurrence of the substring should we search for ? 0 is the first occurrence !

    Returns:
        int: The position in the haystack where you find the nth occurrence of needle
        
    '''
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def twoDecimalPlaces(answer):
    '''
        This simply formats the input as two decimal places.
    '''
    return("%.2f" % answer)

def gross_payment(rate, nper, pv):
    '''
        
    '''
    return float(twoDecimalPlaces(npf.pmt(rate/12, nper*12, pv)))

def net_payment(grosspayment):
    return float(twoDecimalPlaces(grosspayment * (1-0.22)))

def calculate_loan_payments(rate, nper, pv):
    gp = gross_payment(rate, nper, pv)
    np = net_payment(gp)
    print('Gross payment:', gp)
    print('Net payment:', np)