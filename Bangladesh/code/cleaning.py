# Data Set Cleaning
# UTRA Fall 2025, Garment Workers in Bangladesh Diaries Analysis
# Created: 10/21/25
# Last edited: 11/7/25 Megan Ball

import pandas as pd

#importing raw data and making a copy for cleaning
raw_df = pd.read_csv("raw-data\Bangladesh_GWD_Diaries.csv", index_col=False)
clean_df = raw_df.copy()

# found that some purpose were h or b
clean_df['Purpose'] = clean_df['Purpose'].str.upper()
# some lower case item categories
clean_df['Item_category'] = clean_df['Item_category'].str.upper()

# making value labels for exchange gender and purpose
label_maps = {
    'Exchange_gender': {
        1: 'Male',
        2: 'Female',
        3: 'Unknown or Not Applicable',
        4: 'Male and Female (for groups)'
    },
    'Purpose': {
        'B': 'Business',
        'H': 'Household',
        'X': 'Mixed'
    }
}

for col, mapping in label_maps.items():
    clean_df[f'{col}_label'] = clean_df[col].map(mapping)

# split into days of the week
# currently labeled with day of week or # of days
clean_df['Day'] = clean_df['Day'].str.upper()
day_of_week = {'SUNDAY':1, 'MONDAY':2, 'TUESDAY':3, 'WEDNESDAY':4 , 'THURSDAY':5 , 'FRIDAY':6 , 'SATURDAY':7 }
clean_df['Day_of_week'] = clean_df['Day'].map(day_of_week)
day_of_week_labels = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday' , 5: 'Thursday' , 6: 'Friday' , 7: 'Saturday'}
clean_df['Day_of_week_label'] = clean_df['Day_of_week'].map(day_of_week_labels)

# number of days
number_days_label = {'SUNDAY':1, 'MONDAY':1, 'TUESDAY':1, 'WEDNESDAY':1 , 'THURSDAY':1 , 'FRIDAY':1 , 'SATURDAY':1 , '2': 2, '3':3, '4':4, '5':5, '6':6, '7':7, '0':0, 'DK': 'DK'}
clean_df['Number_days_label'] = clean_df['Day'].map(number_days_label)

# drop observations marked as seller/o''
clean_df = clean_df[clean_df['ID1'] != 'Seller']

clean_df.to_csv("clean-data\clean_Bangladesh_GWD_Diaries.csv")

# print(weekly_df['Item_category'].value_counts())

# testing to ensure same amount of values
print(clean_df['Purpose'].value_counts(),clean_df['Purpose_label'].value_counts())
print(clean_df['Exchange_gender'].value_counts(),clean_df['Exchange_gender_label'].value_counts())
print(clean_df['Day'].value_counts(), clean_df['Day_of_week'].value_counts(), clean_df['Day_of_week_label'].value_counts(), clean_df['Number_days_label'].value_counts())
print(clean_df['Item_category'].value_counts())


# what unique values do we have to use?

print(clean_df['ID1'].count(), clean_df['ID1'].nunique())
print(clean_df['ID2'].count(), clean_df['ID2'].nunique())

# 114,676 of both ID1 and ID2, but there are 114,666 unique ID1 and 114,667 unique ID2
nonunique_ID1 = clean_df.groupby('ID1').filter(lambda x: len(x) > 1)
print(nonunique_ID1)
# # non unique ID1 is "Seller" and 109911

nonunique_ID2 = clean_df.groupby('ID2').filter(lambda x: len(x) > 1)
print(nonunique_ID2)
# # non unique ID2 is when ID1 is Seller and ID2 is "o"""

# unique households?
print(clean_df['HHID'].count(), clean_df['HHID'].nunique())
# there are 181 unique households, is also household '1' where we get the duplicates

# repondent ID
print(clean_df['RespID'].count(), clean_df['RespID'].nunique())
# there are 180 unique RespID
