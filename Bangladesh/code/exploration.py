import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ADM_RATE (admission rate) 
raw_df = pd.read_csv("raw-data\Bangladesh_GWD_Diaries.csv")
clean_df = raw_df.copy()

# count of each item-category

# df = df['Purpose']
# print(df.shape) 
# print(df.info())
# print(df.head())
# print(df.columns)
# print(df.describe(include='object'))

# print(df.isnull().sum() ) # Missing values per column

# sns.countplot(data=df, x='Purpose')
# plt.xticks(rotation=45)
# plt.title("Purpose Counts")
# plt.savefig("consumption-graphs/purpose_counts.png")
# plt.show()

# sns.countplot(data=df, x='Item_category')
# plt.xticks(rotation=45)
# plt.title("Item Category Counts")
# plt.savefig("consumption-graphs/item_category_counts.png")
# plt.show()

# want to look at by household
# print(df['HHID'].value_counts())

# hhid = 1226
# hhsubset = df[df['HHID'] == hhid]

# hhsubset['Week'] = pd.to_numeric(hhsubset['Week'], errors='coerce')
# df.hist(column='Week', bins=50)
# plt.savefig("week_distribution.png")
# plt.show()

# df = hhsubset

# group by household, means
# print(df.groupby('HHID').mean(numeric_only=True)) # need to figure out how to deal with the categorical variables as well
# will want to group by for only specific variables


# want to look at by household and by week

clean_df.to_csv("clean-data\clean_Bangladesh_GWD_Diaries.csv")


