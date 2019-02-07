import pandas as pd
import xlsxwriter
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
testing_premium = float(input("Enter the testing premium: "))
testing_width = float(input("Enter the testing width: "))
num_contracts = int(input("Enter the number of contracts: "))
purchase_day = input("Enter the weekday of purchase: ")

weeks_list = []
for file in os.listdir('underlying_daily_performance'):
    df_spy_performance = pd.read_csv(f'underlying_daily_performance/{file}')
    new_week = True
    for i in range(1, len(df_spy_performance.index)):
        if int(df_spy_performance['Date'][i].split('-')[0]) in testing_years:
            current_date = datetime.date(int(df_spy_performance['Date'][i].split('-')[0]), int(df_spy_performance['Date'][i].split('-')[1]),
                                         int(df_spy_performance['Date'][i].split('-')[2]))
            next_date = datetime.date(int(df_spy_performance['Date'][i + 1].split('-')[0]), int(df_spy_performance['Date'][i + 1].split('-')[1]),
                                      int(df_spy_performance['Date'][i + 1].split('-')[2]))
            if new_week:
                current_week = Week()
                new_week = False
            current_week.days_list.append(Day(current_date, float(df_spy_performance['Open'][i]), float(df_spy_performance['Close'][i]), float(df_spy_performance['High'][i]), float(df_spy_performance['Low'][i])))
            if new_week == False and next_date - current_date >= datetime.timedelta(days=3):
                weeks_list.append(current_week)
                new_week = True

for file in os.listdir('option_price_data'):
    df_options = pd.read_csv(f'option_price_data/{file}')
    for i in range(1, len(df_options.index)):
        buy_date = datetime.date(int(df_options['date'][i].split('/')[0]), int(df_options['date'][i].split('/')[1]),
                                 int(df_options['date'][i].split('/')[2]))
        exp_date = datetime.date(int(df_options['exdate'][i].split('/')[0]),
                                 int(df_options['exdate'][i].split('/')[1]),
                                 int(df_options['exdate'][i].split('/')[2]))
        for week in weeks_list:
            for day in week.days_list:
                if buy_date == day.date and (exp_date == week.days_list[-1].date or exp_date == week.days_list[-1].date + datetime.timedelta(days=1)):
                    print(exp_date)
                    if df_options['cp_flag'][i] == 'C' and not float(df_options['strike_price'][i])/ 1000 in day.call_option_chain['strike']:
                        if float(df_options['strike_price'][i]) / 1000 >= day.day_close and float(df_options['best_offer'][i]) >= .04:
                            day.call_option_chain['strike'].append(float(df_options['strike_price'][i]) / 1000)
                            day.call_option_chain['premium'].append(float(df_options['best_offer'][i]))
                    elif df_options['cp_flag'][i] == 'P' and not float(df_options['strike_price'][i])/ 1000 in day.put_option_chain['strike']:
                        if float(df_options['strike_price'][i]) / 1000 <= day.day_close and float(df_options['best_offer'][i]) >= .04:
                            day.put_option_chain['strike'].append(float(df_options['strike_price'][i]) /1000)
                            day.put_option_chain['premium'].append(float(df_options['best_offer'][i]))

for week in weeks_list:
    for day in week.days_list:
        if len(day.call_option_chain['strike']) > 1 and len(day.put_option_chain['strike']) > 1:
            day.data_cleansing()

with open(f'pickle_data/{testing_years[0]} - {testing_years[-1]}.pickle', 'wb') as pickle_out:
    pickle.dump(weeks_list, pickle_out)

# weeks_list = []
# with open(f'pickle_data/{testing_years[0]} - {testing_years[-1]}.pickle', 'rb') as pickle_in:
#     weeks_list = pickle.load(pickle_in)

# writer = pd.ExcelWriter('debugging.xlsx', engine='xlsxwriter')
# df = pd.DataFrame(weeks_list[200].days_list[0].call_option_chain)
# df.to_excel(writer, sheet_name='calls')
# df = pd.DataFrame(weeks_list[200].days_list[0].put_option_chain)
# df.to_excel(writer, sheet_name='puts')
# writer.save()
# writer.close()

print('\nIndividual Week Performance:\n')

total_profit = 0
for week in weeks_list:
    print(f'\nWeek start: {week.days_list[0].date}')
    print(f'Week end: {week.days_list[-1].date}')
    for day in week.days_list:
        if day.weekday_str == purchase_day and len(day.call_option_chain['strike']) != 0:
            try:
                profit = day.calc_profit(week.days_list[-1].day_close)
            except:
                break

            print(f'Underlying at position open: {day.day_close:,.2f}')
            print(f'Underlying at position close: {week.days_list[-1].day_close:,.2f}')
            print(f'Underlying percent change: {(week.days_list[-1].day_close - day.day_close) / day.day_close * 100:.2f}%')
            print(f'Total Premium {day.total_premium}')
            if profit <= testing_premium * 100:
                total_profit += profit
            print(f'Week\'s profit: ${day.profit:,.2f}')

print(f'\nTotal profit for year(s) {testing_years[0]} to {testing_years[-1]}:')
print(f'${total_profit:,.2f}\n')
end = datetime.datetime.now()
print(f'Elapsed time: {end - start}')
