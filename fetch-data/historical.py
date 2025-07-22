import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from tqdm import tqdm


#### HELPERS

def filter_by_event(df, event_code):
    """
    Filter a DataFrame of competitions for those that include a specific event.
    Returns:
    - pd.DataFrame filtered to rows where event_code is present in 'events'
    """
    return df[df['events'].apply(lambda x: event_code in x if isinstance(x, list) else False)]

############
### 1 - Competitions
############

all_dfs = []

# 1. Load competitions from 2015 to 2025
for year in range(2010, 2026):
    url = f'https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/competitions/{year}.json'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        if items:
            df = pd.json_normalize(items, sep='_')
            df['comp_id'] = df['id'].str.replace(rf'{year}$', '', regex=True)
            df['isChampionship'] = False  # Mark as regular competition
            all_dfs.append(df)
        else:
            print(f"No competitions found for {year}")
    else:
        print(f"Failed to load competitions for {year}: HTTP {response.status_code}")

# 2. Load the championships
championship_url = 'https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/championships-page-1.json'
response = requests.get(championship_url)

if response.status_code == 200:
    data = response.json()
    items = data.get('items', [])
    if items:
        champ_df = pd.json_normalize(items, sep='_')
        champ_df['comp_id'] = champ_df['id'].str.replace(r'\d{4}$', '', regex=True)
        champ_df['isChampionship'] = True  # Mark as championship
        all_dfs.append(champ_df)
else:
    print(f"Failed to load championships: HTTP {response.status_code}")

# 3. Combine all into one DataFrame
full_df = pd.concat(all_dfs, ignore_index=True)
# Ensure 'date_from' is a datetime type
full_df['date_from'] = pd.to_datetime(full_df['date_from'], errors='coerce')
# Filter rows with date_from >= 2020-01-01
filtered_df = full_df[full_df['date_from'] >= pd.Timestamp('2010-01-01')]
filtered_df = filter_by_event(filtered_df, '333')
filtered_df = filtered_df[filtered_df['isCanceled']==False]
filtered_df=filtered_df[['id','name','city','country','isCanceled','events','externalWebsite','date_from','date_till','venue_coordinates_latitude','venue_coordinates_longitude','comp_id','isChampionship']]


filtered_df = filtered_df.drop_duplicates(subset='id', keep='first')



############
### 2 - Person
############

total_pages = 266


# Initialize list to hold all page DataFrames
all_person_dfs = []
j = 0 

# Loop through each page and collect items
for page in range(1, total_pages + 1):
    j=j+1
    print(j)
    if page == 1:
        url = 'https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/persons.json'
    else:
        url = f'https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/persons-page-{page}.json'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        df = pd.json_normalize(items, sep='_')
        
        # Drop undesired columns if they exist
        df = df.drop(columns=[col for col in df.columns if any(exclude in col for exclude in ['rank', 'medals', 'records', 'results'])], errors='ignore')
        
        all_person_dfs.append(df)

# Concatenate all DataFrames
persons_df = pd.concat(all_person_dfs, ignore_index=True)

persons_df = persons_df.drop(columns=['competitionIds','championshipIds'])


############
### 3 - Results
############


result_dfs = []
i=0
# Loop over each competition in filtered_df
for comp_id in filtered_df['id']:
    url_result = f'https://raw.githubusercontent.com/robiningelbrecht/wca-rest-api/master/api/results/{comp_id}/333.json'
    response = requests.get(url_result)
    time.sleep(0.01)
    print(i)
    i=i+1

    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])

        if items:
            df = pd.json_normalize(items, sep='_')

            # Select and rename desired columns
            df_filtered = df[['competitionId', 'personId', 'round', 'position', 'best', 'average', 'solves']].copy()

            # Append to result list
            result_dfs.append(df_filtered)
        else:
            print(f"No results found for {comp_id}")
    else:
        print(f"Failed to fetch results for {comp_id}: HTTP {response.status_code}")

# Combine all result dataframes
result_df = pd.concat(result_dfs, ignore_index=True)

result_df[['best', 'average']] = result_df[['best', 'average']].replace([-1, 0], 99999)
result_df = result_df.drop(columns=['solves','position'])

round_mapping = {
    'Final': 1,
    'Second round': 2,
    'First round': 3,
    'Semi Final': 4,
    'Qualification round': 5
}

result_df['round'] = result_df['round'].map(round_mapping).astype(int)


result_df = result_df.drop_duplicates(subset=['competitionId', 'personId', 'round'], keep='first')


############
### 3 - Best performance of last 90d and 365d
############


# Step 1: Merge competitions and results

df = result_df.merge(filtered_df[['id', 'date_from']], left_on='competitionId', right_on='id')
df = df.drop(columns='id')
df['date_from'] = pd.to_datetime(df['date_from'])

# Step 2: Filter top 20,000 persons by overall best average (simulated here with fewer)
top_persons = (
    result_df.groupby('personId')['average']
    .mean()
    .nsmallest(20000)  # Keep this as-is, even if fewer people in example
    .index
)
df = df[df['personId'].isin(top_persons)]

# Step 3: Compute rolling performance
df = df.sort_values(['personId', 'date_from'])
df = df.set_index('date_from')

rolled_365 = df.groupby('personId').rolling('365D', closed='both')[['best', 'average']].min()
rolled_365.columns = ['best_365', 'average_365']

rolled_90 = df.groupby('personId').rolling('90D', closed='both')[['best', 'average']].min()
rolled_90.columns = ['best_90', 'average_90']
rolled = pd.concat([rolled_365, rolled_90], axis=1).reset_index()

# Step 4: Reduce to weekly level only
rolled['date_from'] = pd.to_datetime(rolled['date_from'])
rolled['week'] = rolled['date'] - pd.to_timedelta(rolled['date'].dt.weekday, unit='D')
rolled = rolled.groupby(['personId', 'week'])[['best_365', 'average_365', 'best_90', 'average_90']].min().reset_index()

# Step 5: Expand between first and last date per person on weekly basis
min_max = rolled.groupby('personId')['week'].agg(['min', 'max']).reset_index()

weekly_grid = []
for _, row in min_max.iterrows():
    weeks = pd.date_range(start=row['min'], end=row['max'], freq='W-MON')
    weekly_grid.append(pd.DataFrame({'date': weeks, 'personId': row['personId']}))

weekly_df = pd.concat(weekly_grid, ignore_index=True)

# Step 6: Merge and forward fill
rolled = rolled.rename(columns={'week': 'date'})
record_df = weekly_df.merge(rolled, on=['date', 'personId'], how='left')
record_df = record_df.sort_values(['personId', 'date'])

record_df[['best_365', 'average_365', 'best_90', 'average_90']] = (
    record_df.groupby('personId')[['best_365', 'average_365', 'best_90', 'average_90']].ffill()
)

record_df = record_df.drop_duplicates(subset=['date', 'personId'], keep='first')


############
### 4 - Player World Ranking
############

def compute_weekly_ranks(df):
    df['rank90best'] = df['best_90'].rank(method='min')
    df['rank90avg'] = df['average_90'].rank(method='min')
    df['rank365best'] = df['best_365'].rank(method='min')
    df['rank365avg'] = df['average_365'].rank(method='min')
    return df

ranking_df = record_df.groupby('date').apply(compute_weekly_ranks).reset_index(drop=True)
ranking_df = ranking_df[['date', 'personId', 'rank90best', 'rank90avg', 'rank365best', 'rank365avg']]
ranking_df = ranking_df.drop_duplicates(subset=['date', 'personId'], keep='first')

##########
## 6 - Player National ranking
##########

ranking_with_country = ranking_df.merge(persons_df[['id', 'country']], left_on='personId', right_on='id', how='left').drop(columns=['id'])

# For each date and country, compute national rankings of the participants
national_ranking_df = ranking_with_country.groupby(['date', 'country', 'personId'], as_index=False).agg({
    'rank90best': 'min',
    'rank90avg': 'min',
    'rank365best': 'min',
    'rank365avg': 'min'
})


##########
## 7 - Merge world, national rankings and performance by player
##########

combined_df = pd.merge(ranking_df, record_df, on=['date', 'personId'], how='outer')
combined_df = pd.merge(combined_df, national_ranking_df, on=['date', 'personId'], how='outer', suffixes=('', '_national'))

#combined_df = combined_df.drop(columns=["country"])

combined2024_df = combined_df[pd.to_datetime(combined_df['date']) >= pd.Timestamp('2024-01-01')]

############
### 8 - Competition ranking
############



filtered2011_df = filtered_df[pd.to_datetime(filtered_df['date_from']) >= pd.Timestamp('2011-01-01')]


comp_rank_stats_loop = []
j = 0 

for _, row in filtered2011_df.iterrows():
    print(j)
    j=j+1
    comp_id = row['id']
    comp_date = row['date_from']

    participants = result_df[result_df['competitionId'] == comp_id]['personId'].unique()

    # Ranking data
    # Filter ranking entries for participants
    relevant_ranks = ranking_df[ranking_df['personId'].isin(participants)]
    after_rank = relevant_ranks[relevant_ranks['date'] >= comp_date]
    valid_ranks = after_rank.sort_values('date').groupby('personId').first().reset_index()

    # Record data
    relevant_perf = record_df[record_df['personId'].isin(participants)]
    after_perf = relevant_perf[relevant_perf['date'] >= comp_date]
    valid_perf = after_perf.sort_values('date').groupby('personId').first().reset_index()

    stats = {'competition_id': comp_id}

    if not valid_ranks.empty:
        top10_ranks = valid_ranks.nsmallest(10, 'rank90best')
        stats.update({
            'rank90avg_avg': top10_ranks['rank90avg'].mean(),
            'rank365avg_avg': top10_ranks['rank365avg'].mean(),
        })

    if not valid_perf.empty:
        top10_perf = valid_perf.nsmallest(10, 'average_90')
        stats.update({
            'perf90avg': top10_perf['average_90'].mean(),
            'perf365avg': top10_perf['average_365'].mean(),
        })

    comp_rank_stats_loop.append(stats)

# Creating DataFrame from results
comp_ranking_df = pd.DataFrame(comp_rank_stats_loop)

comp_ranking_df = comp_ranking_df.drop_duplicates(subset='competition_id', keep='first')

from concurrent.futures import ThreadPoolExecutor, as_completed


# Store results
comp_rank_stats_loop = []

# Define the function to process one row
def process_competition(row):
    comp_id = row['id']
    comp_date = row['date_from']

    participants = result_df[result_df['competitionId'] == comp_id]['personId'].unique()

    # Ranking data
    relevant_ranks = ranking_df[ranking_df['personId'].isin(participants)]
    after_rank = relevant_ranks[relevant_ranks['date'] >= comp_date]
    valid_ranks = after_rank.sort_values('date').groupby('personId').first().reset_index()

    # Performance data
    relevant_perf = record_df[record_df['personId'].isin(participants)]
    after_perf = relevant_perf[relevant_perf['date'] >= comp_date]
    valid_perf = after_perf.sort_values('date').groupby('personId').first().reset_index()

    stats = {'competition_id': comp_id}

    if not valid_ranks.empty:
        top10_ranks = valid_ranks.nsmallest(10, 'rank90best')
        stats.update({
            'rank90avg_avg': top10_ranks['rank90avg'].mean(),
            'rank365avg_avg': top10_ranks['rank365avg'].mean(),
        })

    if not valid_perf.empty:
        top10_perf = valid_perf.nsmallest(10, 'average_90')
        stats.update({
            'perf90avg': top10_perf['average_90'].mean(),
            'perf365avg': top10_perf['average_365'].mean(),
        })

    return stats

# Use ThreadPoolExecutor with tqdm for progress tracking
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_competition, row) for _, row in filtered2011_df.iterrows()]
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing competitions"):
        comp_rank_stats_loop.append(future.result())

comp_ranking_df = pd.DataFrame(comp_rank_stats_loop)
comp_ranking_df = comp_ranking_df.drop_duplicates(subset='competition_id', keep='first')


##########
## 8 - Insert tables in Supabase
##########

