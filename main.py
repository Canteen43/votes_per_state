
import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Website with data on electoral votes
url = "https://www.archives.gov/electoral-college/allocation"

# Using a requests with a header to mimic browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

response = requests.get(url, headers=headers)

# Using the content of the response to read the tables
df = pd.read_html(response.content)[0]

# Cleaning up the input
# Concatenating the three columns
df = pd.concat([df.loc[:,0], df.loc[:,1], df.loc[:,2]], ignore_index=True).to_frame(name= "state_and_votes")
# Splitting the column into two and getting rid of 'votes' after number
for i in range(len(df)):
    df.loc[i, "state"], df.loc[i, "votes"] = df.loc[i, "state_and_votes"].split(sep=' - ')
    df.loc[i, "votes"] = int(df.loc[i, "votes"].split()[0])
# dropping original column
df.drop(columns="state_and_votes", inplace=True)

# First table looks good. Now the second table needs to be imported, cleaned and then united with the first

url2 = "https://www.britannica.com/topic/largest-U-S-state-by-population"

response2 = requests.get(url2, headers=headers)

df2 = pd.read_html(response2.content)[0]

for i in range(len(df2)):
    df2.loc[i, "state"] = df2.loc[i, "U.S. state"].split(sep='. ')[1]
    df2.loc[i, "population"] = int(df2.loc[i, "population: estimate"].split()[2].replace(",",""))

df2.drop(columns=["population: census", "population: estimate", "U.S. state"], inplace=True)

# Washington DC is missing (678972 inhabitants in 2023 estimate)
df2.loc[len(df2)] = ['District of Columbia', 678972]

# Sorting and re-indexing df2
df2.sort_values(by='state', inplace=True)
df2.reset_index(drop=True, inplace=True)

# Checking if states and their names are equal
# print(df['state'].equals(df2['state']))

# Merging the two dataframes
df = pd.concat([df, df2.population], axis=1)

# Creating the votes per 1,000,000 people
df["votes_p_100k"] = df["votes"] / df["population"] * 1000000

# Finding the states with most and least voting power.
max_state = df[df.votes_p_100k == df.votes_p_100k.max()].state.iloc[0]
min_state = df[df.votes_p_100k == df.votes_p_100k.min()].state.iloc[0]
print(f"\nThe state with most voting power is {max_state} and the one with least is {min_state}.\n\n")

# I decided to add an input that shows your voting power relative to other states.
user_state = input("Type the name of the state your interested in: ")
while (df.state != user_state).all():
   user_state = input(f"{user_state} is not a state or spelled incorrectly! Try again: ")

while user_state != "exit":
    percentage_texas = \
        df[df.state == user_state].votes_p_100k.iloc[0] / \
        df[df.state == "Texas"].votes_p_100k.iloc[0]
    percentage_wyoming = \
        df[df.state == user_state].votes_p_100k.iloc[0] / \
        df[df.state == "Wyoming"].votes_p_100k.iloc[0]
    print(
        f"Votes in {user_state} have {percentage_wyoming * 100:.0f}% of the voting power of Wyoming "
        f"and {percentage_texas * 100:.0f}% of the voting power of Texas ")
    user_state = input("\nEnter another state or type \"exit\": ")
    while (df.state != user_state).all() and user_state != "exit":
        user_state = input(f"{user_state} is not a state or spelled incorrectly! Try again: ")
print("\nGoodbye!\n\n")




