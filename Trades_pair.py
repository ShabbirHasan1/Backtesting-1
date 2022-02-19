# TODO: restrict the values of trade attributes especially dates and trade_position

import datetime as dt
import pandas as pd

def finding_stop_loss_day(eq_curve,stop_loss):
    for day in eq_curve.index:
        if eq_curve.loc[day]<stop_loss:
            return day


class Trades_pair:
    trades_count = 0
    trade_position_str = {1: "Long", -1: "Short"}


    def __init__(self, entry_date=dt.date(1000, 1, 1), entry_price_1=0,entry_price_2=0, exit_date=dt.date(1000, 1, 1),
                 exit_price_1=0,exit_price_2=0,
                 trade_pos=1, price_data_1=pd.DataFrame,price_data_2=pd.DataFrame,
                 contract_1="Nz1 Index",contract_2="Af1 Index",trade_qty=1,stop_loss=-1,
                 stop_loss_series_apply="Close"):

        Trades_pair.trades_count += 1

        self.contract_1=contract_1
        self.contract_2 = contract_2
        self.price_data_1 = price_data_1
        self.price_data_2=price_data_2
        self.trade_number = Trades_pair.trades_count
        self.entry_date = entry_date
        self.entry_price_1 = entry_price_1
        self.entry_price_2 = entry_price_2
        self.exit_date = exit_date
        self.exit_price_1 = exit_price_1
        self.exit_price_2 = exit_price_2
        self.trade_position = trade_pos
        self.trade_qty=trade_qty
        self.trade_pnl_1 = (self.exit_price_1 / self.entry_price_1 - 1) * self.trade_position
        self.trade_pnl_2 = (self.exit_price_2 / self.entry_price_2 - 1) * self.trade_position*-1
        self.trade_pnl=self.trade_pnl_2+self.trade_pnl_1
        self.duration = (self.exit_date - self.entry_date).days
        self.trade_side = Trades_pair.trade_position_str[trade_pos]
        self.profitable = (self.trade_pnl > 0)
        self.stop_loss_series_apply=stop_loss_series_apply
        self.stop_loss=stop_loss
        self.stop_loss_triggered="False"

        (self.max_DD, self.max_DD_duration, self.max_profit, self.max_loss, self.max_recovery) = \
            self.DD_calc()

    def get_trade_data(self):
        return {"Contract_1":self.contract_1,
                "Contract_2":self.contract_2,
                "Trade Number": self.trade_number,
                "Entry Date": self.entry_date,
                "Entry Price 1": self.entry_price_1,
                "Entry Price 2": self.entry_price_2,
                "Exit Date": self.exit_date,
                "Exit Price 1": self.exit_price_1,
                "Exit Price 2": self.exit_price_2,
                "Trade Position": self.trade_position,
                "Trade Quantity":self.trade_qty,
                "Trade Pnl 1": self.trade_pnl_1,
                "Trade Pnl 2": self.trade_pnl_2,
                "Trade Pnl": self.trade_pnl,
                "Trade Duration": self.duration,
                "Max DD": self.max_DD,
                "Max DD Duration": self.max_DD_duration,
                "Max Profit": self.max_profit,
                "Max Loss": self.max_loss,
                "Max Recovery": self.max_recovery,
                "Profitable": self.profitable,
                "Trade Side": self.trade_side,
                "Stop_loss_trigerred":self.stop_loss_triggered}

    def DD_calc(self):


        def rolling_count(val):
            if val < 0:
                rolling_count.count += 1
            else:
                rolling_count.count = 0
            return rolling_count.count

        baseamount = 1000000
        no_of_shares_1 = (baseamount / self.entry_price_1)*self.trade_position
        no_of_shares_2 = (baseamount / self.entry_price_2)*self.trade_position*-1

        price_series_1 = self.price_data_1["Close"]
        price_series_1[-1] = self.exit_price_1
        price_series_2 = self.price_data_2["Close"]
        price_series_2[-1] = self.exit_price_2

        price_change_series_1 = price_series_1.diff()
        price_change_series_1[0] = price_series_1[0]-self.entry_price_1
        price_change_series_2 = price_series_2.diff()
        price_change_series_2[0] = price_series_2[0]-self.entry_price_2

        pnl_series_1=(no_of_shares_1 * price_change_series_1)
        pnl_series_2 = (no_of_shares_2 * price_change_series_2)
        pnl_series=pnl_series_2+pnl_series_1

        eq_curve = (pnl_series.cum()) / baseamount
        max_profit = max(eq_curve.max(), 0)
        max_loss = min(eq_curve.min(), 0)
        dd_curve = ((1 + eq_curve) / (1 + eq_curve.cummax())) - 1
        max_DD = dd_curve.min()
        DD_duration = dd_curve.apply(rolling_count)
        max_DD_duration = DD_duration.max()

        recovery_curve = ((1 + eq_curve) / (1 + eq_curve.cummin())) - 1
        max_recovery = recovery_curve.max()

        return max_DD, max_DD_duration, max_profit, max_loss, max_recovery

    def stop_loss_apply(self):

        baseamount = 1000000
        no_of_shares_1 = (baseamount / self.entry_price_1)*self.trade_position
        no_of_shares_2 = (baseamount / self.entry_price_2)*self.trade_position*-1


        if self.stop_loss_series_apply=="Close":
            price_series_1 = self.price_data_1["Close"]
            price_series_1[-1] = self.exit_price_1
            price_series_2 = self.price_data_2["Close"]
            price_series_2[-1] = self.exit_price_2

            price_change_series_1 = price_series_1.diff()
            price_change_series_1[0] = price_series_1[0] - self.entry_price_1
            price_change_series_2 = price_series_2.diff()
            price_change_series_2[0] = price_series_2[0] - self.entry_price_2

            pnl_series_1 = (no_of_shares_1 * price_change_series_1)
            pnl_series_2 = (no_of_shares_2 * price_change_series_2)
            pnl_series = pnl_series_2 + pnl_series_1

            eq_curve = (pnl_series.cum()) / baseamount

            if eq_curve.min()<self.stop_loss:
                stop_loss_day=finding_stop_loss_day(eq_curve,self.stop_loss)

                self.stop_loss_triggered=True
                self.exit_date=stop_loss_day
                self.exit_price_1=price_series_1.loc[stop_loss_day]
                self.exit_price_2=price_series_2.loc[stop_loss_day]

                self.trade_pnl=eq_curve.loc[stop_loss_day]
                self.duration=(self.exit_date-self.entry_date).days
                self.profitable=(self.trade_pnl>0)