import requests
import pandas as pd

apikey = f"apikey=<Log into https://financialmodelingprep.com/developer/docs/. Get Api Key>" #### ****
urlStr = "https://financialmodelingprep.com/api/v3/financials/"
urlEvStr = "https://financialmodelingprep.com/api/v3/enterprise-values/"
urlProfStr = "https://financialmodelingprep.com/api/v3/profile/"
period = "period=quarter"
params = f"?{period}&{apikey}"
paramsProfile = f"?{apikey}"


class StockCompliantClass(object):

    def __init__(self, symbol):
        self.scdict = dict()
        self.cmdict = dict()
        balance_sheet_data = requests.get(f"{urlStr}balance-sheet-statement/{symbol}{params}").json()
        self.balance_sheet = balance_sheet_data['financials'][0]
        income_data = requests.get(f"{urlStr}income-statement/{symbol}{params}").json()
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
        self.scdict["total_illiquid_assets"] = (
            self.scdict["Total Assets"] - self.scdict["Total Liquid Assets"])
        self.scdict["Number of Shares"] = float(
            self.enterp_vals['numberOfShares'])
        self.scdict["net_liquid_assets_per_share"] = (
            self.scdict["Total Assets"] - self.scdict["Receivables"] -
            self.scdict["Total Liquid Assets"]) - self.scdict[
            "Number of Shares"]
        self.scdict["intt_bearing_debt_to_asset_pct"] = self.scdict["Total Debt"] / \
            self.scdict["Total Assets"]
        self.scdict["illiquid_assets_to_assets_pct"] = self.scdict["Total Liquid Assets"] / \
            self.scdict["Total Assets"]
        self.scdict["total_current_assets"] = float(
            self.balance_sheet['Total current assets'])
        self.scdict["total_liabilities"] = float(
            self.balance_sheet['Total liabilities'])
        self.scdict["revenue"] = float(self.income['Revenue'])
        self.scdict["interest_expense"] = float(
            self.income['Interest Expense'])
        self.scdict["Stock Price"] = float(self.enterp_vals['stockPrice'])
        self.scdict["investments_to_total_assets_pct"] = self.scdict["Cash and Cash Equivalents"] / self.scdict[
            "Total Assets"]
        self.scdict["income_to_total_revenue_pct"] = self.scdict["interest_expense"] / \
            self.scdict["revenue"]
        return self.scdict

    def getcompliancemetrics(self):
        self.cmdict["intt_bearing_debt_to_asset_compl"] = self.scdict["intt_bearing_debt_to_asset_pct"] < 0.37
        self.cmdict["illiquid_assets_to_assets_compl"] = self.scdict["illiquid_assets_to_assets_pct"] > 0.25
        self.cmdict["investments_to_total_assets_compl"] = self.scdict["investments_to_total_assets_pct"] < 0.33
        self.cmdict["income_to_total_revenue_compl"] = self.scdict["income_to_total_revenue_pct"] < 0.05
        self.cmdict["net_liquidassets_to_marketprice_compl"] = self.scdict["Stock Price"] > self.scdict[
            "net_liquid_assets_per_share"]
        self.cmdict["Overall Compliance"] = self.cmdict["intt_bearing_debt_to_asset_compl"] == True and self.cmdict[
            "illiquid_assets_to_assets_compl"] == True and self.cmdict["investments_to_total_assets_compl"] == True and \
            self.cmdict["income_to_total_revenue_compl"] == True and self.cmdict[
            "net_liquidassets_to_marketprice_compl"] == True
        return self.cmdict


symbolList = input("Enter ticker symbol: ")
symbolList = symbolList.replace(' ', '')
for symbol in symbolList.split(","):
    scinstance = StockCompliantClass(symbol)
    scdict = scinstance.getstockvalues()
    cmdict = scinstance.getcompliancemetrics()
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

