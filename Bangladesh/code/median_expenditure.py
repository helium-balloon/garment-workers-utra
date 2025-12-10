# Exploration into Weekly Spending
# UTRA Fall 2025, Garment Workers in Bangladesh Diaries Analysis
# Created: 10/21/25
# Last edited: 12/10/25 Megan Ball

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#importing  data and making a copy 
clean_df = pd.read_csv("Bangladesh\clean-data\clean_Bangladesh_GWD_Diaries.csv", index_col=False)

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

# simple median by item_category
category_median_overall = weekly_df.groupby('Item_category')['Original_verified_amount'].median().reset_index()
category_median_overall.to_csv("Bangladesh\output\median_catall_overall.csv")

#### The next two graphs are the medians based on week by all categories then by the 8 finer categories

## save one denominator to work off of - based on the fine grain categories - used for all calculations
med1 = weekly_df.groupby(['Week', 'Item_category'])['Original_verified_amount'].median().reset_index()

#weekly totals = sum of medians across all fine-grained categories
week_totals = med1.groupby('Week')['Original_verified_amount'].sum().reset_index()
week_totals = week_totals.rename(columns={'Original_verified_amount': 'weekly_total'})

med1 = med1.merge(week_totals, on='Week', how='left')
med1['Percent'] = (med1['Original_verified_amount'] / med1['weekly_total']) * 100

## amt and percent change
pivot_amt = med1.pivot(index='Week', columns='Item_category', values='Original_verified_amount').fillna(0)
pivot_pct = pivot_amt.pct_change() * 100
pivot_pct = pivot_pct.round(2)
pivot_pct = pivot_pct.add_suffix("_pct_change")
final_pct = pd.concat([pivot_amt, pivot_pct], axis=1)
final_pct.to_csv("Bangladesh\output\median_catall_week_amt_pct.csv")

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
plt.savefig("Bangladesh\output\median_catall_week.png")
plt.show()

pivot_df.to_csv("Bangladesh\output\median_catall_week.csv")

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

## making it so we add up the medians - THIS WORKS HOW I WANT IT TO
# mapping_fin = weekly_df[['Item_category', 'category_split']].drop_duplicates()
# med_fin = med1.merge(mapping_fin, on='Item_category', how='left')

# # group to get the category total per week (will be the numerator in percent)
# median_grouped_fin = (
#     med_fin.groupby(['Week', 'category_split'])['Original_verified_amount']
#     .sum()
#     .reset_index()
#     .rename(columns={'Original_verified_amount': 'category_median_weekly_total'})
# )
# median_grouped_fin.rename(columns={'category_split': 'category'}, inplace=True)

# weekly median percentage from item_category analysis where category is financial
financial_pct = median_grouped[median_grouped['category'] == 'Financial'][['Week', 'Percent']] \
    .rename(columns={'Percent':'Financial_pct'})

# median amount per tool
tool_medians = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby(['Week','category_split'])['Original_verified_amount'] \
    .sum().reset_index().rename(columns={'Original_verified_amount': 'sum_category_weekly_total'})
## changed to median

# this is based on medians for each category, without taking into account base median percentage
tool_medians_for_amt = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby(['Week','category_split'])['Original_verified_amount'] \
    .median().reset_index().rename(columns={'Original_verified_amount': 'category_weekly_total'})
tool_medians_for_amt.rename(columns={'category_split': 'category'}, inplace=True)

# median total financial amount per week (not the percentage)
fin_total_medians = weekly_df[weekly_df['category_label2']=='Financial'] \
    .groupby('Week')['Original_verified_amount'] \
    .sum().reset_index().rename(columns={'Original_verified_amount':'fin_median_total'})

tool_medians = tool_medians.merge(fin_total_medians, on='Week')
# tool_medians.to_csv("output/tools.csv")
tool_medians['fin_prop'] = tool_medians['sum_category_weekly_total'] / tool_medians['fin_median_total']

# compare median of tool to median percent calculated earlier
tool_medians = tool_medians.merge(financial_pct, on='Week')
tool_medians['Percent'] = tool_medians['fin_prop'] * tool_medians['Financial_pct']
tool_medians.rename(columns={'category_split': 'category'}, inplace=True)
# tool_medians.to_csv("output/tool_median.csv")

## final version with the 8 put together categories
cat_med = median_grouped.copy()
# cat_med.to_csv("output/beforeconcatcheck.csv")
cat_med = cat_med[cat_med['category'] != "Financial"]
category_median = pd.concat([cat_med, tool_medians], join='inner', ignore_index=True)
category_median = category_median.sort_values(by=['Week', 'category'])
# category_median.to_csv("output/aaacheck.csv")

category_median_amt = pd.concat([cat_med, tool_medians_for_amt], join='inner', ignore_index=True)
category_median_amt = category_median_amt.sort_values(by=['Week', 'category'])
# category_median_amt.to_csv("output/secondmergeaaacheck.csv")
# category_median = category_median.merge(median_grouped_fin, on=['Week', 'category'])
# category_median.to_csv("output/secondmergeaaacheck.csv")

# percentage change
pivot_amt = category_median_amt.pivot(index='Week', columns='category', values='category_weekly_total').fillna(0)
pivot_pct = pivot_amt.pct_change() * 100
pivot_pct = pivot_pct.round(2)
pivot_pct = pivot_pct.add_suffix("_pct_change")

final_pct = pd.concat([pivot_amt, pivot_pct], axis=1)
final_pct.to_csv("Bangladesh\output\median_cat8_week_amt_pct.csv")

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
plt.savefig("Bangladesh\output\median_cat8_week.png")
plt.show()

pivot_df.to_csv("Bangladesh\output\median_cat8_week.csv")



#### The next two graphs are the medians based on week and household by all categories then by the 8 finer categories

## Denominator going to base all calculations on, grouped by week and household and take median
med_hh = weekly_df.groupby(['Week', 'HHID', 'Item_category'])['Original_verified_amount'].median().reset_index()

#weekly totals = sum across all fine-grained categories 
week_hh_grouped = med_hh.groupby(['Week', 'HHID'])['Original_verified_amount'].sum().reset_index()
week_hh_grouped = week_hh_grouped.rename(columns={'Original_verified_amount': 'weekly_total'})

med_hh = med_hh.merge(week_hh_grouped, on=['Week', 'HHID'], how='left')
med_hh['Percent'] = (med_hh['Original_verified_amount'] / med_hh['weekly_total']) * 100
med_hh.to_csv('Bangladesh\output\med_hhweek.csv')
# to make into the chart I was thinking of, I need to go down one more time and group again. 
# how can I make sure I'm not taking the median of medians?

# pivot_df = med_hh.pivot(index='Week', columns='Item_category', values='Percent').fillna(0)
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
# plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
# plt.tight_layout()
# plt.figtext(.50,.03,"Calculated median over each week and household by category", fontsize='8')
# plt.savefig("output/median_catall_wkhh.png")
# plt.show()

# pivot_df.to_csv("output/median_catall_wkhh.csv")

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

# pivot_df = category_median.pivot(index='Week', columns='category', values='Percent').fillna(0)
# pivot_df = pivot_df.round(2)

# colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", "royalblue", "midnightblue", "gray"]

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
# plt.savefig("output/median_cat8_wkhh.png")
# plt.show()

# pivot_df.to_csv("output/median_cat8_wkhh.csv")


## median consumption based on just household - take the median spent for the household based on all the weeks

# Weekly consumption per household
weekly_hh = weekly_df.groupby(['Week', 'HHID'])['Original_verified_amount'].sum().reset_index()

# Median weekly consumption per household
median_by_hh = weekly_hh.groupby('HHID')['Original_verified_amount'].median().reset_index()
median_by_hh.rename(columns={'Original_verified_amount': 'median_weekly_consumption'}, inplace=True)

# median_by_hh.to_csv('output/median_weekly_consumption_by_HH.csv', index=False)

## save to the clean data set
weekly_df = weekly_df.merge(median_by_hh, on='HHID',how='left')
weekly_df.to_csv('Bangladesh\clean-data\clean_Bangladesh_GWD_Diaries_w_median_consump.csv')