# %load StockCompliance_py\StockCompliance.py
import requests
import pandas as pd
import csv

apikey = f"apikey=<Log into https://financialmodelingprep.com/developer/docs/. Get Api Key>" #### ***
urlStr = "https://financialmodelingprep.com/api/v3/"
urlEvStr = f"{urlStr}enterprise-values/"
urlProfStr = f"{urlStr}profile/"
period = "period=quarter"
params = f"?{period}&{apikey}"
paramsProfile = f"?{apikey}"
icfile = '../industrycompliant.csv'
icdict = {}

with open(icfile, mode='r') as infile:
    reader = csv.reader(infile)
    icdict = {rows[0]: rows[1] for rows in reader}


class StockCompliantClass(object):

    def __init__(self, symbol):
        self.scdict = dict()
        self.cmdict = dict()
        self.icdict = dict()
        balance_sheet_data = requests.get(
            f"{urlStr}financials/balance-sheet-statement/{symbol}{params}").json()
        self.balance_sheet = balance_sheet_data['financials'][0]
        income_data = requests.get(
            f"{urlStr}financials/income-statement/{symbol}{params}").json()
        self.income = income_data['financials'][0]
        enterp_vals_data = requests.get(f"{urlEvStr}{symbol}{params}").json()
        self.enterp_vals = enterp_vals_data[0]
        profile_data = requests.get(f"{urlProfStr}{symbol}{params}").json()
        self.profile = profile_data[0]

    def getstockvalues(self):
        self.scdict["Filing Date"] = self.balance_sheet['date']
        self.scdict["Company Name"] = self.profile["companyName"]
        self.scdict["Industry"] = self.profile["industry"]
        self.scdict["Short Term Investments"] = float(
            self.balance_sheet['Short-term investments'])
        self.scdict["Cash and Short Term Investments"] = float(
            self.balance_sheet['Cash and short-term investments'])
        self.scdict["Cash and Cash Equivalents"] = float(
            self.balance_sheet['Cash and cash equivalents'])
        self.scdict["Receivables"] = float(self.balance_sheet['Receivables'])
        self.scdict["Total Liquid Assets"] = self.scdict["Short Term Investments"] + self.scdict[
            "Cash and Short Term Investments"] + self.scdict["Receivables"]
        self.scdict["Total Assets"] = float(self.balance_sheet['Total assets'])
        self.scdict["Total Debt"] = float(self.balance_sheet['Total debt'])
        self.scdict["Total Illiquid Assets"] = (
            self.scdict["Total Assets"] - self.scdict["Total Liquid Assets"])
        self.scdict["Number of Shares"] = float(
            self.enterp_vals['numberOfShares'])
        self.scdict["Net Liquid Assets Per Share"] = (
            self.scdict["Total Assets"] - self.scdict["Receivables"] -
            self.scdict["Total Liquid Assets"]) / self.scdict[
            "Number of Shares"]
        self.scdict["Interest Bearing Debt To Asset Pct"] = self.scdict["Total Debt"] / \
            self.scdict["Total Assets"]
        self.scdict["Illiquid Assets To Assets Pct"] = self.scdict["Total Illiquid Assets"] / \
            self.scdict["Total Assets"]
        self.scdict["Revenue"] = float(self.income['Revenue'])
        self.scdict["Interest Expense"] = float(
            self.income['Interest Expense'])
        self.scdict["Stock Price"] = float(self.enterp_vals['stockPrice'])
        self.scdict["Investments To Total Assets Pct"] = self.scdict["Cash and Cash Equivalents"] / self.scdict[
            "Total Assets"]
        self.scdict["Interest To Total Revenue Pct"] = self.scdict["Interest Expense"] / \
            self.scdict["Revenue"]
        return self.scdict

    def getcompliancemetrics(self, symbol):
        self.cmdict["Interest Bearing Debt To Asset  Compl"] = self.scdict["Interest Bearing Debt To Asset Pct"] < 0.37
        self.cmdict["Illiquid Assets To Assets Compl"] = self.scdict["Illiquid Assets To Assets Pct"] > 0.25
        self.cmdict["Investments To Total Assets Compl"] = self.scdict["Investments To Total Assets Pct"] < 0.33
        self.cmdict["Income To Total Revenue Compl"] = self.scdict["Interest To Total Revenue Pct"] < 0.05
        self.cmdict["Net Liquid Assets To Price Compl"] = self.scdict["Stock Price"] > self.scdict[
            "Net Liquid Assets Per Share"]
        self.cmdict["Industry Compliance"] = "Yes"
        if (icdict[symbol] == "N"):
            self.cmdict["Industry Compliance"] = "No"

        if (self.cmdict["Interest Bearing Debt To Asset  Compl"] == True and self.cmdict[
            "Illiquid Assets To Assets Compl"] == True and self.cmdict["Investments To Total Assets Compl"] == True and
            self.cmdict["Income To Total Revenue Compl"] == True and self.cmdict[
                "Net Liquid Assets To Price Compl"] == True and self.cmdict["Industry Compliance"] == "Yes"):
            self.cmdict["Overall Compliance"] = "Yes"
        else:
            self.cmdict["Overall Compliance"] = "No"
        return self.cmdict


symbolList = input("Enter ticker symbol: ")
symbolList = symbolList.replace(' ', '')
for symbol in symbolList.split(","):
    scinstance = StockCompliantClass(symbol)
    scdict = scinstance.getstockvalues()
    cmdict = scinstance.getcompliancemetrics(symbol)
    result = "Yes"
    if (cmdict["Overall Compliance"] == False):
        result = "No"
    print("\n*******************")
    print("** Symbol = ", symbol, "    Overall Compliance = ", result)
    for name, value in scdict.items():
        print(name, "=", value)
    print("** Compliance Metrics")
    for name, value in cmdict.items():
        print("  ", name, "=", value)
