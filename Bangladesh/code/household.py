# Household Information
# UTRA Fall 2025, Garment Workers in Bangladesh Diaries Analysis
# Created: 11/11/25
# Last edited: 12/3/25 Megan Ball

import pandas as pd
import numpy as np

## clean raw roster data
# - make occupations not case sensitive
# - 

## table
# hh number
# number of members in the household
# number of children in hh --> use occupation and age --> 
#   occupation will be 'student' or 'child' or n/a, check that <18, add up # per hh
# median weekly consumption per member (above figure divided by # of mems of household)
    # median weekly consumption (for each household get consumption for all weeks and take median of these)
# rural/urban --> can use district and subdistrict to map to urban or rural areas - leave out for now
# tab structure of homes
# number of rooms using "Room_Num"
# no information on religion
# marital status? education of responder? - or diff table

# check that households are unique - worker matched to unique hh
# avgs and std error and n of observations, report all 3 for variables tabulating
# each row is variable, columns are avg then std error then n of observations
# export as table
# check for standard package for generating summary stats of variables


diaries_df = pd.read_csv("Bangladesh\clean-data\clean_Bangladesh_GWD_Diaries_w_median_consump.csv", index_col=False)
raw_df = pd.read_csv("raw data\Bangladesh\Bangladesh_GWD_Roster, anon.csv", index_col=False)
household_df = raw_df.copy()

# merge consumption data with household data
# can merge on hhid and resp ID. 1 household to many weeks with the same household

merged_df = pd.merge(diaries_df, household_df, how="left", on=["HHID", "RespID"])

merged_df.to_csv("Bangladesh\clean-data\merged_hh_consumption.csv")

print(household_df.loc[household_df['Gender1'] == 1, 'HH_Role'].value_counts())

diaries_df["DateStart"] = pd.to_datetime(diaries_df["DateStart"])
diaries_df["Month"] = diaries_df["DateStart"].dt.month

week_dates = (
    diaries_df
    .sort_values("DateStart")        # ensure ordering within week
    .groupby("Week", as_index=False)
    .first()[["Week", "DateStart", "DateEnd", "Month"]]   # take the first row of each week
)


week_dates.to_csv("Bangladesh\output\week_date_ranges.csv", index=False)


hh_members = household_df[['Household_mem']].value_counts()
hh_members.to_csv("Bangladesh\output\hh_members.csv")

# BASIC CLEANING / CHECK HOUSEHOLD IDS

# Make sure household IDs exist
assert household_df['HHID'].notna().all(), "Some rows missing household IDs"

# Check if households appear multiple times (they do not) 180 lines, 180 hhs
# HOUSEHOLD SIZE
hh_counts = household_df['HHID'].value_counts()
hh_members = household_df[['Household_mem']]
hh_members = merged_df.groupby('HHID')['Household_mem'].first()   # or mean(), or max()

resp_age = household_df[['resp_age']]
hh_members_max = household_df[['Household_mem']].max()
hh_members_mean = household_df[['Household_mem']].mean()


# NUMBER OF CHILDREN (<18 AND occupation in {student, child, NA})
## ADD THIS LATER
# go through and add each age in each line to a list
# check how many are less than 18
# assign a number to each household

# MEDIAN WEEKLY CONSUMPTION PER MEMBER

med_weekly_consump = (
    merged_df.groupby('HHID')['median_weekly_consumption'].mean()
)

med_weekly_consump_per_member = (
    med_weekly_consump / hh_members
).rename('weekly_consump_per_member').round(2)

df1 = med_weekly_consump.to_frame(name='median_weekly_consumption')
df2 = med_weekly_consump_per_member.to_frame()
final = df1.merge(df2, on="HHID", how="left")
final.to_csv('output/median_consump_hh.csv')

# # HOUSING STRUCTURE (# of rooms)
# rooms = household_df.groupby('hh_id')['Room_Num'].max().rename("num_rooms")

# MARITAL STATUS / EDUCATION OF RESPONDER

# MERGE ALL HOUSEHOLD-LEVEL VARIABLES

hh = pd.concat([
    hh_members,
    resp_age,
    # children,
    med_weekly_consump,
    med_weekly_consump_per_member
    #rooms,
    # responder_info
], axis=1)

# SUMMARY STATS TABLE
# For each variable: mean, standard error, N

def summary_stats(series):
    """Returns mean, standard error, and number of observations."""
    return pd.Series({
        'max': series.max(),
        'min': series.min(),
        'mean': round(series.mean(), 2),
        'std_error': round(series.std() / np.sqrt(series.count()), 2),
        'n': series.count()
    })


summary_table = hh.apply(summary_stats).T

# EXPORT SUMMARY TABLE
summary_table.to_csv("Bangladesh\output\summary_stats_households.csv")
