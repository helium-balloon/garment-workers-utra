# Exploration into Weekly Spending
# UTRA Fall 2025, Garment Workers in Bangladesh Diaries Analysis
# Created: 10/21/25
# Last edited: 12/2/25 Megan Ball

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import textwrap

#importing  data and making a copy 
clean_df = pd.read_csv("clean-data\clean_Bangladesh_GWD_Diaries.csv", index_col=False)

# amts per week
weekly_df = clean_df.copy()
weekly_df = weekly_df[weekly_df['Type'] == 'Outflow'] # for now only setting to have outflow spending
weekly_df['Original_verified_amount'] = weekly_df['Verified_amount']
weekly_df['Verified_amount'] = weekly_df['Verified_amount'].replace(999, np.nan) # replace so sum doesn't include 999

# create categories
categories_label = {1: '1. Food', 2: '2. Education', 3:'3. Essentials', 4: '4. Financial', 5: '5. Other'}
categories_label2 = {1:'1. Food' , 2: '2. Education', 3:'3. Essentials', 4: 'Financial', 5: '8. Other'}
item_categories_label = {'FOOD': 1, 'FINANCIAL': 4, 'TRANSPORT': 3, 'CLOTHING': 5, 'EMPLOYMENT': 5,
                         'RECREATIONAL SUBSTANCES':5,'HEALTH': 3, 'HOUSEHOLD ITEM':5 , 'COMMUNICATION':3, 
                         'PERSONAL HYGIENE': 3, 'COSMETIC': 5, 'CHARITY OR RELIGIOUS':5, 
                         'HOUSING':3 , 'SERVICE': 5, 'EDUCATION': 2, 'LEISURE':5 , 'MISCELLANEOUS':5 , 'UTILITIES':3, 
                         'LEGAL FEE OR CONTRIBUTION':5 , 'FUEL':3 , 'HOUSEHOLD APPLIANCE':5, 'ELECTRONIC DEVICE': 5, 
                         'HOLIDAY OR CELEBRATION':5 , 'LIVESTOCK':5, 
                         'CONSTRUCTION': 5, 'AGRICULTURE': 5, 'WEDDING':5 }
weekly_df['all_categories'] = weekly_df['Item_category'].map(item_categories_label)
weekly_df['category_label'] = weekly_df['all_categories'].map(categories_label)
weekly_df['category_label2'] = weekly_df['all_categories'].map(categories_label2)

tool_map = {
    'Cash Transfer': '4. Cash Transfer',
    'Savings': '7. Savings',
    'Loan': '6. Loan',
    'Insurance': '5. Insurance',
}
weekly_df['category_split'] = np.where(
    weekly_df['category_label'] == '4. Financial',
    weekly_df['Tool'].map(tool_map),
    weekly_df['category_label2']
)

# print(weekly_df['category_split'].value_counts())

#### The next two graphs are the medians based on week by all categories then by the 8 finer categories

## save one denominator to work off of - based on the fine grain categories - used for all calculations
med1 = weekly_df.groupby(['Week', 'Item_category'])['Original_verified_amount'].median().reset_index()

#weekly totals = sum of medians across all fine-grained categories - use as denominator!
week_totals = med1.groupby('Week')['Original_verified_amount'].sum().reset_index()
week_totals = week_totals.rename(columns={'Original_verified_amount': 'weekly_total'})

med1 = med1.merge(week_totals, on='Week', how='left')
med1['Percent'] = (med1['Original_verified_amount'] / med1['weekly_total']) * 100

pivot_amt = med1.pivot(index='Week', columns='Item_category', values='Original_verified_amount').fillna(0)
pivot_amt = pivot_amt.round(2)
pivot_amt.to_csv("output/median_catall_week_amt.csv")
pivot_df = med1.pivot(index='Week', columns='Item_category', values='Percent').fillna(0)
pivot_df = pivot_df.round(2)

colors = [
    "black","dimgray","lightgray","darkorange","orange","gold","khaki","brown",
    "chocolate","sienna",
    "tan","skyblue","deepskyblue","steelblue","dodgerblue",
    "royalblue","navy","slateblue","mediumpurple","purple","orchid","magenta","hotpink",
    "deeppink","teal","darkcyan","mediumturquoise"
]

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    color=colors 
)

plt.title('Median Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.tight_layout()
plt.figtext(.50,.03,"Calculated median over each week by category", fontsize='8')
plt.savefig("output/median_catall_week.png")
plt.show()

pivot_df.to_csv("output/median_catall_week.csv")

## making it so we add up the medians - THIS WORKS HOW I WANT IT TO
mapping = weekly_df[['Item_category', 'category_label2']].drop_duplicates()
med_fine = med1.merge(mapping, on='Item_category', how='left')

# group to get the category total per week (will be the numerator in percent)
median_grouped = (
    med_fine.groupby(['Week', 'category_label2'])['Original_verified_amount']
    .sum()
    .reset_index()
    .rename(columns={'Original_verified_amount': 'category_weekly_total'})
)

# group to get spend total per week, will be denominator in percent
week_totals = (
    med_fine.groupby('Week')['Original_verified_amount']
    .sum()
    .reset_index()
    .rename(columns={'Original_verified_amount': 'weekly_total'})
)
median_grouped = median_grouped.merge(week_totals, on='Week')
median_grouped['Percent'] = median_grouped['category_weekly_total'] / median_grouped['weekly_total'] * 100
median_grouped.rename(columns={'category_label2': 'category'}, inplace=True)
# median_grouped.to_csv("output/med_grouped_whole.csv")

financial_pct = median_grouped[median_grouped['category'] == 'Financial'][['Week', 'Percent']] \
    .rename(columns={'Percent':'Financial_pct'})

# median amount per tool
tool_medians = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby(['Week','category_split'])['Original_verified_amount'] \
    .sum().reset_index()

# median total financial amount per week (not the percentage)
fin_total_medians = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby('Week')['Original_verified_amount'] \
    .sum().reset_index().rename(columns={'Original_verified_amount':'fin_median_total'})

tool_medians = tool_medians.merge(fin_total_medians, on='Week')
# tool_medians.to_csv("output/tools.csv")
tool_medians['fin_prop'] = tool_medians['Original_verified_amount'] / tool_medians['fin_median_total']

tool_medians = tool_medians.merge(financial_pct, on='Week')
tool_medians['Percent'] = tool_medians['fin_prop'] * tool_medians['Financial_pct']
tool_medians.rename(columns={'category_split': 'category'}, inplace=True)
# tool_medians.to_csv("output/tool_median.csv")


## final version with the 8 put together categories
category_median = median_grouped.copy()
category_median = category_median[category_median['category'] != "Financial"]
category_median = pd.concat([category_median, tool_medians], join='inner', ignore_index=True)
category_median = category_median.sort_values(by=['Week', 'category'])
category_median.to_csv("output/aaacheck.csv")

pivot_amt = category_median.pivot(index='Week', columns='category', values='category_weekly_total').fillna(0)
pivot_amt = pivot_amt.round(2)
pivot_amt.to_csv("output/median_cat8_week_amt.csv")

pivot_df = category_median.pivot(index='Week', columns='category', values='Percent').fillna(0)
pivot_df = pivot_df.round(2)

colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", "royalblue", "midnightblue", "gray"]

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    color=colors 
)

plt.title('Median Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.figtext(.50,.03,"Calculated median over each week by category", fontsize='8')
plt.savefig("output/median_cat8_week.png")
plt.show()

pivot_df.to_csv("output/median_cat8_week.csv")



#### The next two graphs are the medians based on week and household by all categories then by the 8 finer categories

## group by week and by household
# for each household, take the median of each item category
# for each household, take the median per week (total spend)
# can get percent share for each item per household - item/total
# then take the median over all household

# # Total spending per household per week per category
# household_weekly = weekly_df.groupby(['Week', 'HHID', 'Item_category'])['Original_verified_amount'].sum().reset_index()
# # Total spending per household per week (all categories)
# household_totals = household_weekly.groupby(['Week', 'HHID'])['Original_verified_amount'].sum().reset_index(name='total_spend')
# merged = household_weekly.merge(household_totals, on=['Week', 'HHID'])
# # Dividing summed amount of spend per category by the total expenditure of the household that week
# merged['Percent'] = merged['Original_verified_amount'] / merged['total_spend']
# # median share across households for each category-week
# median_share = merged.groupby(['Week', 'Item_category'])['Percent'].median().reset_index()
# # change to normalize percent, before ranging from 100-400%
# median_share['Week_total'] = median_share.groupby('Week')['Percent'].transform('sum')
# median_share['percent_normalized'] = median_share['Percent'] / median_share['Week_total'] * 100

# median_share['Week'] = median_share['Week'].astype(int)
# pivot_df = median_share.pivot(index='Week', columns='Item_category', values='percent_normalized').fillna(0)
# # moved rounded to be before plotting and spreadsheet
# pivot_df = pivot_df.round(2)


## Denominator going to base all calculations on, grouped by week and household and take median
med_hh = weekly_df.groupby(['Week', 'HHID', 'Item_category'])['Original_verified_amount'].median().reset_index()


## get the median for each item_category per week
# med_hh = (
#     med_hh.groupby(['Week', 'HHID'])['Original_verified_amount']
#     .median()
#     .reset_index()
# )

#weekly totals = sum across all fine-grained categories 
week_totals = med_hh.groupby(['Week', 'HHID'])['Original_verified_amount'].sum().reset_index()
week_totals = week_totals.rename(columns={'Original_verified_amount': 'weekly_total'})

med_hh = med_hh.merge(week_totals, on=['Week', 'HHID'], how='left')
med_hh['Percent'] = (med_hh['Original_verified_amount'] / med_hh['weekly_total']) * 100
med_hh.to_csv('output/med_hhweek.csv')

pivot_df = med_hh.pivot(index='Week', columns='Item_category', values='Percent').fillna(0)
pivot_df = pivot_df.round(2)

colors = [
    "black","dimgray","lightgray","darkorange","orange","gold","khaki","brown",
    "chocolate","sienna",
    "tan","skyblue","deepskyblue","steelblue","dodgerblue",
    "royalblue","navy","slateblue","mediumpurple","purple","orchid","magenta","hotpink",
    "deeppink","teal","darkcyan","mediumturquoise"
]

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    color=colors 
)

plt.title('Median Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.tight_layout()
plt.figtext(.50,.03,"Calculated median over each week and household by category", fontsize='8')
plt.savefig("output/median_catall_wkhh.png")
plt.show()

pivot_df.to_csv("output/median_catall_wkhh.csv")

## making it so we add up the medians
mapping_5 = weekly_df[['Item_category', 'category_label2']].drop_duplicates()
med_fine = med_hh.merge(mapping_5, on='Item_category', how='left')

# group to get the category total per week (will be the numerator in percent)
median_grouped = (
    med_fine.groupby(['Week', 'category_label2'])['Original_verified_amount']
    .sum()
    .reset_index()
    .rename(columns={'Original_verified_amount': 'category_weekly_total'})
)

# group to get spend total per week, will be denominator in percent
week_totals = (
    med_fine.groupby('Week')['Original_verified_amount']
    .sum()
    .reset_index()
    .rename(columns={'Original_verified_amount': 'weekly_total'})
)
median_grouped = median_grouped.merge(week_totals, on='Week')
median_grouped['Percent'] = median_grouped['category_weekly_total'] / median_grouped['weekly_total'] * 100
median_grouped.rename(columns={'category_label2': 'category'}, inplace=True)
# median_grouped.to_csv("output/med_grouped_whole.csv")

financial_pct = median_grouped[median_grouped['category'] == 'Financial'][['Week', 'Percent']] \
    .rename(columns={'Percent':'Financial_pct'})

# median amount per tool
tool_medians = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby(['Week','category_split'])['Original_verified_amount'] \
    .sum().reset_index()

# median total financial amount per week (not the percentage)
fin_total_medians = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby('Week')['Original_verified_amount'] \
    .sum().reset_index().rename(columns={'Original_verified_amount':'fin_median_total'})

tool_medians = tool_medians.merge(fin_total_medians, on='Week')
# tool_medians.to_csv("output/tools.csv")
tool_medians['fin_prop'] = tool_medians['Original_verified_amount'] / tool_medians['fin_median_total']

tool_medians = tool_medians.merge(financial_pct, on='Week')
tool_medians['Percent'] = tool_medians['fin_prop'] * tool_medians['Financial_pct']
tool_medians.rename(columns={'category_split': 'category'}, inplace=True)
# tool_medians.to_csv("output/tool_median.csv")


## final version with the 8 put together categories
category_median = median_grouped.copy()
category_median = category_median[category_median['category'] != "Financial"]
category_median = pd.concat([category_median, tool_medians], join='inner', ignore_index=True)
category_median = category_median.sort_values(by=['Week', 'category'])
# category_median.to_csv("output/aaacheck.csv")

pivot_df = category_median.pivot(index='Week', columns='category', values='Percent').fillna(0)
pivot_df = pivot_df.round(2)

colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", "royalblue", "midnightblue", "gray"]

pivot_df.plot(
    kind='bar',
    stacked=True,
    figsize=(10,6),
    color=colors 
)

plt.title('Median Weekly Spend by Category (%)')
plt.xlabel('Week')
plt.ylabel('Percent of Total Spend')
plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.figtext(.50,.03,"Calculated median over each week by category", fontsize='8')
plt.savefig("output/median_cat8_wkhh.png")
plt.show()

pivot_df.to_csv("output/median_cat8_wkhh.csv")



# # print(weekly_df['category_split'])
# weekly_df.to_csv("clean-data\weekly_Bangladesh_GWD_Diaries.csv")
# # generate another variable - check that denominator is remaining the same, that just splitting

# # For the median spend for households, this is calculated by getting the total spending per category per week 
# # per household and dividing it by the total spend per week of the household. This gives the share of spending 
# # per category for each hh. Next, across households, I merged the spending and took the median for each 
# # category, then normalized to get % out of 100

# # This is different from the original strategy of getting the median of spend per category per week. Here, if there 
# # was a large purchase, it was disproportionately shown, such as livestock spending being 63% of week 21

# # Total spending per household per week per category
# household_weekly = weekly_df.groupby(['Week', 'HHID', 'Item_category'])['Original_verified_amount'].sum().reset_index()
# # Total spending per household per week (all categories)
# household_totals = household_weekly.groupby(['Week', 'HHID'])['Original_verified_amount'].sum().reset_index(name='total_spend')
# merged = household_weekly.merge(household_totals, on=['Week', 'HHID'])
# # Dividing summed amount of spend per category by the total expenditure of the household that week
# merged['Percent'] = merged['Original_verified_amount'] / merged['total_spend']
# # median share across households for each category-week
# median_share = merged.groupby(['Week', 'Item_category'])['Percent'].median().reset_index()
# # change to normalize percent, before ranging from 100-400%
# median_share['Week_total'] = median_share.groupby('Week')['Percent'].transform('sum')
# median_share['percent_normalized'] = median_share['Percent'] / median_share['Week_total'] * 100

# median_share['Week'] = median_share['Week'].astype(int)
# pivot_df = median_share.pivot(index='Week', columns='Item_category', values='percent_normalized').fillna(0)
# # moved rounded to be before plotting and spreadsheet
# pivot_df = pivot_df.round(2)

# # n = 20
# # colors = plt.cm.nipy_spectral(np.linspace(0, 1, n))
# # rng = np.random.default_rng(42)
# # rng.shuffle(colors)

# colors = [
#     "black","dimgray","lightgray","darkorange","orange","gold","khaki","brown",
#     "chocolate","sienna",
#     "tan","skyblue","deepskyblue","steelblue","dodgerblue",
#     "royalblue","navy","slateblue","mediumpurple","purple","orchid","magenta","hotpink",
#     "deeppink","teal","darkcyan","mediumturquoise"
# ]


# pivot_df.plot(
#     kind='bar',
#     stacked=True,
#     figsize=(10,6),
#     color=colors
# )

# plt.title('Median Household Weekly Spend by Category (%)')
# plt.xlabel('Week')
# plt.ylabel('Percent of Total Spend')
# plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
# plt.tight_layout()
# plt.figtext(.50,.03,"Source: Categories pulled from 'Item_Category' Variable in GWD Bangladesh Diaries", fontsize='8')
# plt.figtext(.50,.02,"Calculated median over each week by category and household", fontsize='8')
# plt.savefig("output/median_weekly_spend_all.png")
# plt.show()

# # plot this as a table
# pivot_df.to_csv("output/median_weekly_spend_all.csv")

# ### OLD median strategy for all categories - by week and category

# median_df = weekly_df.groupby(['Week', 'Item_category'])['Original_verified_amount'].median().reset_index()
# median_df['weekly_category_median_spend'] = median_df['Original_verified_amount']
# # # # total amt/week
# median_df['weekly_totals'] = median_df.groupby('Week')['weekly_category_median_spend'].transform('sum')
# # # # percentage share/category
# median_df['Percent'] = (median_df['weekly_category_median_spend'] / median_df['weekly_totals']) * 100

# pivot_df = median_df.pivot(index='Week', columns='Item_category', values='Percent').fillna(0)
# pivot_df = pivot_df.round(2)

# colors = [
#     "black","dimgray","lightgray","darkorange","orange","gold","khaki","brown",
#     "chocolate","sienna",
#     "tan","skyblue","deepskyblue","steelblue","dodgerblue",
#     "royalblue","navy","slateblue","mediumpurple","purple","orchid","magenta","hotpink",
#     "deeppink","teal","darkcyan","mediumturquoise"
# ]

# pivot_df.plot(
#     kind='bar',
#     stacked=True,
#     figsize=(10,6),
#     color=colors 
# )

# plt.title('Median Weekly Spend by Category (%)')
# plt.xlabel('Week')
# plt.ylabel('Percent of Total Spend')
# plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
# plt.tight_layout()
# plt.figtext(.50,.03,"Calculated median over each week by category", fontsize='8')
# plt.savefig("output/OLDmedian_category_week_all.png")
# plt.show()

# pivot_df.to_csv("output/OLDmedian_category_week_all.csv")


# # Median household expenditure per week for the 8 categories: Food, Essentials, Education, Other, + 4 financial

# # Total spending per household per week per category
# # change from category split to category_label2 to keep denominator the same as above
# household_weekly = weekly_df.groupby(['Week', 'HHID', 'category_label2'])['Original_verified_amount'].sum().reset_index()
# # Total spending per household per week 
# household_totals = household_weekly.groupby(['Week', 'HHID'])['Original_verified_amount'].sum().reset_index(name='total_spend')
# merged = household_weekly.merge(household_totals, on=['Week','HHID'])
# # Dividing summed amount of spend per category by the total expenditure of the household that week
# merged['Percent'] = merged['Original_verified_amount'] / merged['total_spend']

# median_share = merged.groupby(['Week', 'category_label2'])['Percent'].median().reset_index()
# # change to normalize percent, before ranging from 100-400%
# median_share['Week_total'] = median_share.groupby('Week')['Percent'].transform('sum')
# median_share['percent_normalized'] = median_share['Percent'] / median_share['Week_total'] * 100

# median_share['Week'] = median_share['Week'].astype(int)
# pivot_df = median_share.pivot(index='Week', columns='category_label2', values='percent_normalized').fillna(0)
# # moved rounded to be before plotting and spreadsheet
# pivot_df = pivot_df.round(2)


# # weekly_df['Percent_split'] = weekly_df.apply(split_financial, axis=1)


# # median_split = weekly_df.groupby(['Week', 'category_split'])['Percent_split'].median().reset_index()

# # # Normalize so that all percentages per week sum to 100
# # median_split['Week_total'] = median_split.groupby('Week')['Percent_split'].transform('sum')
# # median_split['percent_normalized'] = median_split['Percent_split'] / median_split['Week_total'] * 100


# # median share across households for each category-week
# # median_share = merged.groupby(['Week', 'category_label2'])['Percent'].median().reset_index()

# # # change to normalize percent
# # median_share['Week_total'] = median_share.groupby('Week')['Percent'].transform('sum')
# # median_share['percent_normalized'] = median_share['Percent'] / median_share['Week_total'] * 100

# # median_share['Week'] = median_share['Week'].astype(int)
# # pivot_df = median_share.pivot(index='Week', columns='category_split', values='percent_normalized').fillna(0)
# # # moved rounded to be before plotting and spreadsheet
# # pivot_df = pivot_df.round(2)
# pivot_df.to_csv("output/med_weekly_split_financial.csv")

# # n = 20
# # colors = plt.cm.nipy_spectral(np.linspace(0, 1, n))
# # rng = np.random.default_rng(42)
# # rng.shuffle(colors)

# colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", "royalblue", "midnightblue", "gray"]

# # "lightblue", "deepskyblue", "cornflowerblue", "navy",


# pivot_df.plot(
#     kind='bar',
#     stacked=True,
#     figsize=(10,6),
#     color=colors
# )

# plt.title('Median Household Weekly Spend by Category (%)')
# plt.xlabel('Week')
# plt.ylabel('Normalized Percent of Household Spend')
# plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
# category_desc = (
#     "Source: Categories pulled from 'Item_Category' variable in GWD "
#     "Bangladesh Diaries then sorted into Food, Education, Essentials (which "
#     "includes Utilities, Transport, Communications, Fuel, "
#     "Housing, Personal hygiene, and Health), the four "
#     "financial categories of Cash Transfer, Insurance, "
#     "Loan, and Savings (which were found by sorting all "
#     "Financial data points using the 'Tool' variable), and "
#     "Other (containing all other categories) "
# )
# # Wrap text at 80 characters
# wrapped_text = textwrap.fill(category_desc, width=30)
# plt.figtext(.80,.10,wrapped_text, fontsize='8', wrap=True)
# plt.tight_layout()
# plt.figtext(.50,.02,"Calculated median over each week by category and household", fontsize='8')
# plt.savefig("output/median_weekly_split_financial.png")
# plt.show()


# # ### OLD STRATEGY
# # #Median expenditure per week for the 8 categories: Food, Essentials, Education, Other, + 4 financial

# # median_df = weekly_df.groupby(['Week', 'category_split'])['Original_verified_amount'].median().reset_index()
# # median_df['weekly_category_median_spend'] = median_df['Original_verified_amount']
# # # # # total amt/week
# # median_df['weekly_totals'] = median_df.groupby('Week')['weekly_category_median_spend'].transform('sum')
# # # # # percentage share/category
# # median_df['Percent'] = (median_df['weekly_category_median_spend'] / median_df['weekly_totals']) * 100

# # pivot_df = median_df.pivot(index='Week', columns='category_split', values='Percent').fillna(0)
# # pivot_df = pivot_df.round(2)

# # colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", "royalblue", "midnightblue", "gray"]

# # pivot_df.plot(
# #     kind='bar',
# #     stacked=True,
# #     figsize=(10,6),
# #     color=colors 
# # )

# # plt.title('Median Weekly Spend by Category (%)')
# # plt.xlabel('Week')
# # plt.ylabel('Percent of Total Spend')
# # plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
# # plt.tight_layout()
# # plt.figtext(.50,.03,"Calculated median over each week by category", fontsize='8')
# # plt.savefig("output/weekly_split_financial_medianfirst.png")
# # plt.show()

# # pivot_df.to_csv("output/med_weekly_split_financial.csv")


# # ### old strategy - just the 5 categories to see if baseline is the same?

# # # Version 2: broad categories
# # med2 = weekly_df.groupby(['Week', 'category_label2'])['Original_verified_amount'].median().reset_index()

# # # merge in the SAME weekly totals from med1
# # med2 = med2.merge(week_totals, on='Week', how='left')

# # # compute percentages using identical denominator
# # med2['Percent'] = (med2['Original_verified_amount'] / med2['weekly_total']) * 100

# # # median_df = weekly_df.groupby(['Week', 'category_label2'])['Original_verified_amount'].median().reset_index()
# # # median_df['weekly_category_median_spend'] = median_df['Original_verified_amount']
# # # # # # total amt/week
# # # median_df['weekly_totals'] = median_df.groupby('Week')['weekly_category_median_spend'].transform('sum')
# # # # # # percentage share/category
# # # median_df['Percent'] = (median_df['weekly_category_median_spend'] / median_df['weekly_totals']) * 100

# # pivot_df = med2.pivot(index='Week', columns='category_label2', values='Percent').fillna(0)
# # pivot_df = pivot_df.round(2)

# # colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", "royalblue", "midnightblue", "gray"]

# # pivot_df.plot(
# #     kind='bar',
# #     stacked=True,
# #     figsize=(10,6),
# #     color=colors 
# # )

# # plt.title('Median Weekly Spend by Category (%)')
# # plt.xlabel('Week')
# # plt.ylabel('Percent of Total Spend')
# # plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
# # plt.tight_layout()
# # plt.figtext(.50,.03,"Calculated median over each week by category", fontsize='8')
# # plt.savefig("output/NEWmedian_category_week2.png")
# # plt.show()

# # pivot_df.to_csv("output/NEWmedian_category_week2.csv")



