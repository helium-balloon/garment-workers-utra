# Income of Households
# UTRA Fall 2025, Garment Workers in Bangladesh Diaries Analysis
# Created: 12/10/25
# Last edited: 12/10/25 by Megan Ball

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#importing  data and making a copy 
clean_df = pd.read_csv("Bangladesh\clean-data\clean_Bangladesh_GWD_Diaries.csv", index_col=False)

# amts per week
weekly_df = clean_df.copy()
weekly_df = weekly_df[weekly_df['Type'] == 'Inflow'] # for now only setting to have outflow spending
weekly_df['Original_verified_amount'] = weekly_df['Verified_amount']
weekly_df['Verified_amount'] = weekly_df['Verified_amount'].replace(999, np.nan) # replace so sum doesn't include 999

# median amount of income per week
# line graph overlaying the consumption graph

median_income = weekly_df.groupby('Week')['Verified_amount'].median().reset_index()
median_income.to_csv("Bangladesh\output\median_income_week.csv")

## graph using consumption from other graph:

# --- Your stacked bar chart ---

consump_df = pd.read_csv("Bangladesh\output\median_cat8_week.csv", index_col='Week')

colors = ["limegreen", "orange", "gold", "paleturquoise", "skyblue", 
          "royalblue", "midnightblue", "gray"]

fig, ax1 = plt.subplots(figsize=(10,6))

consump_df.plot(
    kind='bar',
    stacked=True,
    color=colors,
    ax=ax1
)

ax1.set_title('Median Weekly Spend by Category (%) and Median Income per Week')
ax1.set_xlabel('Week')
ax1.set_ylabel('Percent of Total Spend')
ax1.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')

# --- Load your CSV file ---
income_df = pd.read_csv("Bangladesh\output\median_income_week.csv")

# --- Line chart overlay ---
ax2 = ax1.twinx()

ax2.plot(
    income_df['Week'],
    income_df['Verified_amount'],
    marker='.',
    color='black',
    linewidth=1
)

ax2.set_ylabel('Median Income')

plt.tight_layout()
plt.figtext(.50, .03, "Calculated median over each week by category", fontsize=8)
plt.savefig("Bangladesh\output\median_cat8_week_with_income.png")
plt.show()
