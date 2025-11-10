# Exploration into Weekly Spending
# UTRA Fall 2025, Garment Workers in Bangladesh Diaries Analysis
# Created: 10/21/25
# Last edited: 11/7/25 Megan Ball

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#importing  data and making a copy 
clean_df = pd.read_csv("clean-data\clean_Bangladesh_GWD_Diaries.csv", index_col=False)

# amts per week
weekly_df = clean_df.copy()
weekly_df = weekly_df[weekly_df['Type'] == 'Outflow'] # for now only setting to have outflow spending
weekly_df['Original_verified_amount'] = weekly_df['Verified_amount']
weekly_df['Verified_amount'] = weekly_df['Verified_amount'].replace(999, np.nan) # replace so sum doesn't include 999

# create categories
categories_label = {1: '1. Education', 2: '2. Food', 3:'3. Essentials', 4: '4. Financial', 5: '5. Other'}
categories_label2 = {1: 'Education', 2: 'Food', 3:'Essentials', 4: 'Financial', 5: 'Other'}
item_categories_label = {'FOOD': 2, 'FINANCIAL': 4, 'TRANSPORT': 3, 'CLOTHING': 5, 'EMPLOYMENT': 5,
                         'RECREATIONAL SUBSTANCES':5,'HEALTH': 3, 'HOUSEHOLD ITEM':5 , 'COMMUNICATION':3, 
                         'PERSONAL HYGIENE': 3, 'COSMETIC': 5, 'CHARITY OR RELIGIOUS':5, 
                         'HOUSING':3 , 'SERVICE': 5, 'EDUCATION': 1, 'LEISURE':5 , 'MISCELLANEOUS':5 , 'UTILITIES':3, 
                         'LEGAL FEE OR CONTRIBUTION':5 , 'FUEL':3 , 'HOUSEHOLD APPLIANCE':5, 'ELECTRONIC DEVICE': 5, 
                         'HOLIDAY OR CELEBRATION':5 , 'LIVESTOCK':5, 
                         'CONSTRUCTION': 5, 'AGRICULTURE': 5, 'WEDDING':5 }
smaller_essentials = {'FOOD': 2, 'FINANCIAL': 4, 'TRANSPORT': 3, 'CLOTHING': 5, 'EMPLOYMENT': 5,
                         'RECREATIONAL SUBSTANCES':5,'HEALTH': 5, 'HOUSEHOLD ITEM':5 , 'COMMUNICATION':3, 
                         'PERSONAL HYGIENE': 5, 'COSMETIC': 5, 'CHARITY OR RELIGIOUS':5, 
                         'HOUSING':3 , 'SERVICE': 5, 'EDUCATION': 1, 'LEISURE':5 , 'MISCELLANEOUS':5 , 'UTILITIES':3, 
                         'LEGAL FEE OR CONTRIBUTION':5 , 'FUEL':3 , 'HOUSEHOLD APPLIANCE':5, 'ELECTRONIC DEVICE': 5, 
                         'HOLIDAY OR CELEBRATION':5 , 'LIVESTOCK':5, 
                         'CONSTRUCTION': 5, 'AGRICULTURE': 5, 'WEDDING':5 }
weekly_df['all_categories'] = weekly_df['Item_category'].map(item_categories_label)
weekly_df['category_label'] = weekly_df['all_categories'].map(categories_label)
weekly_df['category_label2'] = weekly_df['all_categories'].map(categories_label2)

weekly_df['smaller_essentials_categories'] = weekly_df['Item_category'].map(smaller_essentials)
weekly_df['category_label_ess2'] = weekly_df['smaller_essentials_categories'].map(categories_label2)

tool_map = {
    'Cash Transfer': 'Cash Transfer',
    'Savings': 'Savings',
    'Loan': 'Loan',
    'Insurance': 'Insurance',
}
weekly_df['category_split'] = np.where(
    weekly_df['category_label'] == '4. Financial',
    weekly_df['Tool'].map(tool_map),
    weekly_df['category_label2']
)
# category split 2 takes into account the smaller group of essentials
weekly_df['category_split2'] = np.where(
    weekly_df['category_label'] == '4. Financial',
    weekly_df['Tool'].map(tool_map),
    weekly_df['category_label_ess2']
)


#Weekly with nan variable for verified amount with all the categories
week_groups = dict(tuple(clean_df.groupby('Week')))
# weekly categories
all_categories = weekly_df.groupby(['Week', 'Item_category'])['Verified_amount'].sum().reset_index()
# ^ sum didn't change when I added the nan? unsure, savings is a lot
all_categories['weekly_category_spend'] = all_categories['Verified_amount']
# # # total amt/week
all_categories['weekly_totals'] = all_categories.groupby('Week')['weekly_category_spend'].transform('sum')
# # # percentage share/category
all_categories['Percent'] = (all_categories['weekly_category_spend'] / all_categories['weekly_totals']) * 100


pivot_df = all_categories.pivot(index='Week', columns='Item_category', values='Percent').fillna(0)

n = 20
colors = plt.cm.turbo(np.linspace(0, 1, n))
rng = np.random.default_rng(42)
rng.shuffle(colors)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    color=colors
)

plt.title('Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/weekly_percent_all.png")
plt.show()

# plot this as a table
pivot_df = pivot_df.round(2)
pivot_df.to_csv("output/weekly_percent_all.csv")

#Weekly percent with 5 categories with nan variable for verified amount
week_groups = dict(tuple(clean_df.groupby('Week')))
# weekly categories
weekly_fivecate_nan = weekly_df.groupby(['Week', 'category_label'])['Verified_amount'].sum().reset_index()
# ^ sum didn't change when I added the nan? unsure, savings is a lot
weekly_fivecate_nan['weekly_category_spend'] = weekly_fivecate_nan['Verified_amount']
# # # total amt/week
weekly_fivecate_nan['weekly_totals'] = weekly_fivecate_nan.groupby('Week')['weekly_category_spend'].transform('sum')
# # # percentage share/category
weekly_fivecate_nan['Percent'] = (weekly_fivecate_nan['weekly_category_spend'] / weekly_fivecate_nan['weekly_totals']) * 100

pivot_df = weekly_fivecate_nan.pivot(index='Week', columns='category_label', values='Percent').fillna(0)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    colormap='Paired' 
)

plt.title('Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/weekly_percent_category_nan.png")
plt.show()

#Weekly with 5 categories with no nan variable for verified amount
week_groups = dict(tuple(clean_df.groupby('Week')))
# weekly categories
weekly_fivecate = weekly_df.groupby(['Week', 'category_label'])['Original_verified_amount'].sum().reset_index()
# ^ sum didn't change when I added the nan? unsure, savings is a lot
weekly_fivecate['weekly_category_spend'] = weekly_fivecate['Original_verified_amount']
# # # total amt/week
weekly_fivecate['weekly_totals'] = weekly_fivecate.groupby('Week')['weekly_category_spend'].transform('sum')
# # # percentage share/category
weekly_fivecate['Percent'] = (weekly_fivecate['weekly_category_spend'] / weekly_fivecate['weekly_totals']) * 100

pivot_df = weekly_fivecate.pivot(index='Week', columns='category_label', values='Percent').fillna(0)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    colormap='Paired' 
)

plt.title('Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/weekly_percent_category_nonan.png")
plt.show()


# adding financial sorting

justfinancial_df = weekly_df[weekly_df['category_label'] == "4. Financial"]
## for output, most of these are cash transfers, but even so, because the amount of saving is larger, it is approx the same
print(justfinancial_df['Tool'].value_counts())

financial_df = weekly_df.groupby(['Week', 'category_split'])['Original_verified_amount'].sum().reset_index()
financial_df['weekly_category_spend'] = financial_df['Original_verified_amount']
# # # total amt/week
financial_df['weekly_totals'] = financial_df.groupby('Week')['weekly_category_spend'].transform('sum')
# # # percentage share/category
financial_df['Percent'] = (financial_df['weekly_category_spend'] / financial_df['weekly_totals']) * 100

pivot_df = financial_df.pivot(index='Week', columns='category_split', values='Percent').fillna(0)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    colormap='tab20' 
)

plt.title('Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/weekly_percent_split_financial.png")
plt.show()

pivot_df = pivot_df.round(2)
pivot_df.to_csv("output/weekly_percent_split_financial.csv")


# weekly_df.to_csv("clean-data\weekly_Bangladesh_GWD_Diaries.csv")

# median expenditure per week for the 8 categories

median_df = weekly_df.groupby(['Week', 'category_split'])['Original_verified_amount'].median().reset_index()
median_df['weekly_category_median_spend'] = median_df['Original_verified_amount']
# # # total amt/week
median_df['weekly_totals'] = median_df.groupby('Week')['weekly_category_median_spend'].transform('sum')
# # # percentage share/category
median_df['Percent'] = (median_df['weekly_category_median_spend'] / median_df['weekly_totals']) * 100

pivot_df = median_df.pivot(index='Week', columns='category_split', values='Percent').fillna(0)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    colormap='tab20' 
)

plt.title('Median Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/median_percent_split_financial.png")
plt.show()

pivot_df = pivot_df.round(2)
pivot_df.to_csv("output/median_percent_split_financial.csv")


#####################################################
## Repeating Weekly Percent Split Financial and Median Percent Split Financial
## To compare against the smaller essentials group that only contains: transport, housing, utilities, fuel, and comms

financial_df_ess = weekly_df.groupby(['Week', 'category_split2'])['Original_verified_amount'].sum().reset_index()
financial_df_ess['weekly_category_spend'] = financial_df_ess['Original_verified_amount']
# # # total amt/week
financial_df_ess['weekly_totals'] = financial_df_ess.groupby('Week')['weekly_category_spend'].transform('sum')
# # # percentage share/category
financial_df_ess['Percent'] = (financial_df_ess['weekly_category_spend'] / financial_df_ess['weekly_totals']) * 100

pivot_df = financial_df_ess.pivot(index='Week', columns='category_split2', values='Percent').fillna(0)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    colormap='tab20' 
)

plt.title('Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/weekly_percent_split_financial_ess.png")
plt.show()

pivot_df = pivot_df.round(2)
pivot_df.to_csv("output/weekly_percent_split_financial_ess.csv")


# median expenditure per week for the 8 categories

median_df = weekly_df.groupby(['Week', 'category_split2'])['Original_verified_amount'].median().reset_index()
median_df['weekly_category_median_spend'] = median_df['Original_verified_amount']
# # # total amt/week
median_df['weekly_totals'] = median_df.groupby('Week')['weekly_category_median_spend'].transform('sum')
# # # percentage share/category
median_df['Percent'] = (median_df['weekly_category_median_spend'] / median_df['weekly_totals']) * 100

pivot_df = median_df.pivot(index='Week', columns='category_split2', values='Percent').fillna(0)

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    colormap='tab20' 
)

plt.title('Median Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("output/median_percent_split_financial_ess.png")
plt.show()

pivot_df = pivot_df.round(2)
pivot_df.to_csv("output/median_percent_split_financial_ess.csv")
