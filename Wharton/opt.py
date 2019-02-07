import pandas as pd
import datetime
import os
import pickle

start = datetime.datetime.now()

class Day:
    def __init__(self, date, open, close, high, low):
        self.date = date
        self.day_open = open
        self.day_close = close
        self.day_high = high
        self.day_low = low
        self.put_option_chain = {'strike': [], 'premium': []}
        self.call_option_chain = {'strike': [], 'premium': []}

        if date.weekday() == 0:
            self.weekday_str = 'Monday'
        elif date.weekday() == 1:
            self.weekday_str = 'Tuesday'
        elif date.weekday() == 2:
            self.weekday_str = 'Wednesday'
        elif date.weekday() == 3:
            self.weekday_str = 'Thursday'
        elif date.weekday() == 4:
            self.weekday_str = 'Friday'

    def data_cleansing(self):
        for i in range(1, len(self.call_option_chain['strike'])):
            delta = self.call_option_chain['strike'][i] - self.call_option_chain['strike'][i - 1]
            if delta <= 0 or delta > 2.5:
                self.call_option_chain['strike'] = self.call_option_chain['strike'][:i]
                self.call_option_chain['premium'] = self.call_option_chain['premium'][:i]
                break

        for i in range(1, len(self.put_option_chain['strike'])):
            delta = self.put_option_chain['strike'][i] - self.put_option_chain['strike'][i - 1]
            if delta <= 0 or delta > 2.5:
                self.put_option_chain['strike'] = self.put_option_chain['strike'][:i]
                self.put_option_chain['premium'] = self.put_option_chain['premium'][:i]
                break

    def calc_profit(self, week_close):
        call_buy_index = 0
        while self.day_close > self.call_option_chain['strike'][call_buy_index]:
            call_buy_index += 1

        try:
            call_sell_index = self.call_option_chain['strike'].index(self.call_option_chain['strike'][call_buy_index] + testing_width)
        except ValueError:
            call_buy_index += 1
            call_sell_index = self.call_option_chain['strike'].index(self.call_option_chain['strike'][call_buy_index] + testing_width)

        self.call_premium = self.call_option_chain['premium'][call_buy_index] - self.call_option_chain['premium'][call_sell_index]
        while self.call_premium > testing_premium / 2.0:
            call_buy_index += 1
            call_sell_index += 1
            self.call_premium = self.call_option_chain['premium'][call_buy_index] - self.call_option_chain['premium'][call_sell_index]

        self.put_option_chain['strike'].reverse()
        self.put_option_chain['premium'].reverse()
        put_buy_index = 0
        while self.day_close < self.put_option_chain['strike'][put_buy_index]:
            put_buy_index += 1
        try:
            put_sell_index = self.put_option_chain['strike'].index(self.put_option_chain['strike'][put_buy_index] - testing_width)
        except ValueError:
            put_buy_index += 1
            put_sell_index = self.put_option_chain['strike'].index(self.put_option_chain['strike'][put_buy_index] - testing_width)

        self.put_premium = self.put_option_chain['premium'][put_buy_index] - self.put_option_chain['premium'][put_sell_index]
        while self.put_premium > testing_premium / 2.0:
            put_buy_index += 1
            put_sell_index += 1
            self.put_premium = self.put_option_chain['premium'][put_buy_index] - self.put_option_chain['premium'][put_sell_index]

        self.total_premium = self.call_premium + self.put_premium
        self.buy_put_strike = self.put_option_chain['strike'][put_buy_index]
        self.sell_put_strike = self.put_option_chain['strike'][put_sell_index]
        self.buy_call_strike = self.call_option_chain['strike'][call_buy_index]
        self.sell_call_strike = self.call_option_chain['strike'][call_sell_index]

        if week_close >= self.buy_put_strike and week_close <= self.buy_call_strike:
            self.profit = -self.total_premium  * 100 * num_contracts
        elif week_close > self.buy_call_strike and week_close < self.sell_call_strike:
            self.profit = ((week_close - self.buy_call_strike) - self.total_premium) * 100 * num_contracts
        elif week_close < self.buy_put_strike and week_close > self.sell_put_strike:
            self.profit = ((self.buy_put_strike - week_close) - self.total_premium) * 100 * num_contracts
        elif week_close >= self.sell_call_strike or week_close <= self.sell_put_strike:
            self.profit = (testing_width - self.total_premium) * 100 * num_contracts
        else:
            raise Exception("Something went horribly wrong...")

        return self.profit


class Week:
    def __init__(self):
        self.days_list = []


first_year = int(input("Enter the beginning year: "))
last_year = int(input("Enter the last year: "))
testing_years = range(first_year, last_year + 1)
testing_width = 1.0
num_contracts = 1


# testing_premium = float(input("Enter the testing premium: "))
# purchase_day = input("Enter the weekday of purchase: ")

testing_day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']

weeks_list = []
with open(f'pickle_data/{testing_years[0]} - {testing_years[-1]}.pickle', 'rb') as pickle_in:
    weeks_list = pickle.load(pickle_in)

best_parameters = {'total_profit': 0.0, 'premium': 0.0, 'weekday': '', 'max_loss': 0.0, 'max_profit': 0.0, 'roi': 0.0}
worst_parameters = {'total_profit': 0.0, 'premium': 0.0, 'weekday': '', 'max_loss': 0.0, 'max_profit': 0.0, 'roi': 0.0}

testing_premium = 0.2
while testing_premium <= 0.85:
    for purchase_day in testing_day_list:
        parameters_profit = 0
        max_loss = 0
        max_profit = 0
        for week in weeks_list:
            for day in week.days_list:
                if day.weekday_str == purchase_day and len(day.call_option_chain['strike']) != 0:
                    try:
                        profit = day.calc_profit(week.days_list[-1].day_close)
                    except:
                        break

                    if profit <= testing_premium * 100 * num_contracts:
                        parameters_profit += profit
                        if parameters_profit < max_loss:
                            max_loss = parameters_profit
                        elif parameters_profit > max_profit:
                            max_profit = parameters_profit

        roi = (parameters_profit - abs(max_loss)) / abs(max_loss)

        print('\nPerformance:')
        print(f'Profit: ${parameters_profit:,.2f}')
        print(f'Max loss: ${max_loss:,.2f}')
        print(f'Max Profit: ${max_profit:,.2f}')
        print(f'ROI: {roi * 100:.2}%')
        print('Parameters')
        print(f'Premium: {testing_premium}')
        print(f'Purchase day: {purchase_day}')

        if parameters_profit > best_parameters['total_profit']:
            best_parameters['total_profit'] = parameters_profit
            best_parameters['max_loss'] = max_loss
            best_parameters['max_profit'] = max_profit
            best_parameters['premium'] = testing_premium
            best_parameters['weekday'] = purchase_day
            best_parameters['roi'] = roi
        elif parameters_profit < worst_parameters['total_profit']:
            worst_parameters['total_profit'] = parameters_profit
            worst_parameters['max_loss'] = max_loss
            worst_parameters['max_profit'] = max_profit
            worst_parameters['premium'] = testing_premium
            worst_parameters['weekday'] = purchase_day
            worst_parameters['roi'] = roi

    testing_premium += 0.05

print('\nBest Parameters:\n')
print('Performance')
print(f'Profit: ${best_parameters["total_profit"]:,.2f}')
print(f'Max loss: ${best_parameters["max_loss"]:,.2f}')
print(f'Max profit: ${best_parameters["max_profit"]:,.2f}')
print(f'ROI: {best_parameters["roi"] * 100:.2f}%')
print('Parameters')
print(f'Premium: {best_parameters["premium"]:.2f}')
print(f'Purchase day: {best_parameters["weekday"]}')

print('\nWorst Parameters:\n')
print('Performance')
print(f'Profit: ${worst_parameters["total_profit"]:,.2f}')
print(f'Max loss: ${worst_parameters["max_loss"]:,.2f}')
print(f'Max profit: ${worst_parameters["max_profit"]:,.2f}')
print(f'ROI: {worst_parameters["roi"] * 100:.2f}%')
print('Parameters')
print(f'Premium: {worst_parameters["premium"]:.2f}')
print(f'Purchase day: {worst_parameters["weekday"]}')

end = datetime.datetime.now()
print(f'\nElapsed time: {end - start}')
