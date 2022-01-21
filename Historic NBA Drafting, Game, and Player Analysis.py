#!/usr/bin/env python
# coding: utf-8

# # Data: The NBA drafting, player, and game data are sourced from stats.nba.com via the nba_api.
# # exploratory data analysis of NBA historic drafting, player, and team data.

# In[1]:


import numpy as np
import pandas as pd
import sqlite3 as sql
import plotly.express as px
import os


# In[36]:


# connect to SQL database
db_path = r'C:\Users\Administrator\Desktop\basketball.sqlite'
connection = sql.connect(db_path) 
table = pd.read_sql_query("SELECT * FROM sqlite_master ", connection)
print(table)


# In[243]:


table1 = pd.read_sql("SELECT * from Game_Inactive_Players ", connection)
print(table1)
list(table1.columns.values)


# ### 1. How does the NBA drafting count change over time from 1949 to 2020?

# In[34]:


## How does the NBA drafting count change over time from 1949 to 2020?

query =""" select yeardraft as year,count(nameplayer) as total_drafted 
            from draft
            group by yeardraft"""

draftyear = pd.read_sql(query,connection)
print(draftyear)
fig = px.line(draftyear,x='year',y='total_drafted',
             title='NBA Drafting Trend from 1949 to 2020')
fig.show()


# #### It's quite surprising that NBA has way more drafts in the 70s and 80s comparing the 2000s.
# #### In the year of 1970, there were 239 drafts and there were 228 drafts in the year of 1984 whereas NBA only
# #### drafted around 60 players per year in the recent years.

# ### 2. What are the top 10 NBA team that drafted most number of player from university?

# In[197]:


## What are the top 10 NBA team that drafted most number of player from university?

query = ''' select nameTeam , count(distinct nameplayer) as count_drafted
            from draft 
            group by idteam
            order by count_drafted desc
            limit 10'''
teamdrafted = pd.read_sql(query,connection)
print(teamdrafted)
fig1 = px.bar(teamdrafted,x='nameTeam',y='count_drafted',
                title = 'Top 10 NBA team that drafted most number of player from university')
fig1.show()


# #### Atlanta Hawks (514), Sacramento Kings (511), Philadelphia 76ers (487) are the top 3 teams that drafted the most number of players over time.

# ### 3. When did the teams first start to draft players from the universities?

# In[208]:


## When did the teams first start to draft players from the universities?

query = """select min(yeardraft) as first_year ,
            nameteam as team,
            COUNT(DISTINCT yearDraft) AS years_drafted,
            COUNT(DISTINCT idPlayer) AS total_drafted_to_date
            from draft
            group by idteam
            order by first_year"""
team_first_draft_year = pd.read_sql(query,connection)
print(team_first_draft_year)


# In[204]:


print("For each year, how many team first started drafting new players?")
team_first_draft_year["first_year"].value_counts()


# #### From the above sumary table, we can observe that most of the teams first started drafting players in 1949-1950 season.

# ### 4. Where are the players coming from?

# In[209]:


### Where are the players coming from? 
### Do most of the players coming from high school, university, or from other professional basketball team?

query ="""select typeOrganizationFrom as draft_from, count(distinct idplayer) as count_player
        from draft
        group by draft_from"""
draft_player_from = pd.read_sql(query,connection)
print(draft_player_from)

px.pie(draft_player_from,values='count_player' ,names='draft_from')


# #### Historically speaking, we can see that the majority of the players (95.3%) were been drafted from either College or University.
# #### Very small fraction of the players are drafted from either other baskbetball team/club or high school to play in NBA.

# ### ️5. From 1949 to 2020, how did the total number of participated team count changes 
# ### and how did the total game count changes along with it overall?

# In[72]:


from plotly.subplots import make_subplots # make subplot for dual axes plot


# In[218]:


### ️From 1949 to 2020, how did the total number of participated team count changes 
### and how did the total game count changes along with it overall?
query = """ select id , nickname, min(YEARFOUNDED) as yearfound from team_history
            group by id
            order by yearfound """
query =""" select season_id-20000 as season,count(distinct TEAM_NAME_HOME) as count_team,count(distinct GAME_ID) as count_game
            from game
            group by season
            order by season """

participated_team = pd.read_sql(query,connection)
print(participated_team)

fig = make_subplots(specs=[[{"secondary_y": True}]])
total_count_team = px.bar(participated_team, x='season',y='count_team')
total_count_game = px.line(participated_team, x='season',y='count_game')
total_count_team.update_traces(name="team totals", showlegend =True)
total_count_game.update_traces(name='game totals', showlegend =True,line_color='red')
fig.add_trace(total_count_team.data[0], secondary_y=False)
fig.add_trace(total_count_game.data[0], secondary_y=True)
fig.update_yaxes(title_text='team totals',secondary_y=False)
fig.update_yaxes(title_text='game totals',secondary_y=True)


# #### From 1946 to 2020, we can observe that the total game and total team counts increases over the years 0 from 11 teams playing 331 games to 30 teams playing 1080 games in the 2020 season.
# #### 2020-2021 is special: Each team will play 72 regular-season games, which is 10 games fewer than in a typical, 82-game NBA season.

# ### 6. From 1949 to 2020, how did home game game won percentage among all the games change over time?

# In[216]:


### From 1949 to 2020, how did home game game won percentage among all the games change over time?

query = '''
        select (game1.season_id-20000) as season, round(100 * count(game1.wl_home)/game2.total_game,3) as homewin_percentage
        from game as game1
        join (select game_id,season_id, count(wl_home) as total_game from game group by season_id) as game2
        on game1.season_id = game2.season_ID
        where game1.wl_home ='W'
        group by game1.season_id
          '''



fig = pd.read_sql(query,connection)
print(fig)
px.line(fig,x='season',y='homewin_percentage')


# #### Overall, the home game won percentage decreased from 75.35% to 51.67% from 1950s to 2020.

# In[219]:


query = """
    SELECT 
        SEASON_ID-20000 AS season,
        TEAM_ID_HOME AS team_id,
        TEAM_NAME_HOME AS team_name,
        SUM(CASE WL_HOME 
                WHEN'W' THEN 1
                ELSE 0
            END) AS win_count,
        COUNT(TEAM_ID_HOME) AS team_game_count,
        "home" AS game_location
    FROM Game
    GROUP BY SEASON_ID, TEAM_ID_HOME 
    
    UNION
    
    SELECT 
        SEASON_ID-20000 AS season,
        TEAM_ID_AWAY AS team_id,
        TEAM_NAME_AWAY AS team_name,
        SUM(CASE WL_AWAY 
                WHEN'W' THEN 1
                ELSE 0
            END) AS win_count,
        COUNT(TEAM_ID_AWAY) AS team_game_count,
        "away" AS game_location
    FROM Game
    GROUP BY SEASON_ID, TEAM_ID_AWAY
"""
team_level_home_game_stats = pd.read_sql(query, connection)
team_level_home_game_stats["win_percentage"] = round(
    100 * team_level_home_game_stats["win_count"] / team_level_home_game_stats["team_game_count"], 2)
team_level_home_game_stats


# In[221]:


cols_to_drop = ["team_id", "team_name", "win_count", "team_game_count"]
median_win_pct = team_level_home_game_stats.drop(cols_to_drop, axis=1).groupby(["season", "game_location"]).mean().reset_index()
print(median_win_pct)

px.line(median_win_pct, x="season", y="win_percentage", 
           color="game_location", title="1946-2020: median of the team level game won percentage by game location")


# #### With some variation, we can observe that the home game game won percentages have been relatively higher than the away game game won percentage. 
# #### The areas between the two curves have decreased over the years.

# ### 7. How does the free throw percentage (FT%) changes over time from 1949 to 2020? 
# ### For each season, which team had the best FT%?

# In[229]:


### How does the free throw percentage (FT%) changes over time from 1949 to 2020? 
### For each season, which team had the best FT%?

query = '''    SELECT 
        SEASON_ID-20000 AS season,
        TEAM_ID_HOME AS team_id,
        TEAM_NAME_HOME AS team_name,
        FT_PCT_HOME AS free_throw_percentage,
        COUNT(TEAM_ID_HOME) AS team_game_count,
        "home" AS game_location
    FROM Game
    GROUP BY SEASON_ID, TEAM_ID_HOME 
    
    UNION
    
    SELECT 
        SEASON_ID-20000 AS season,
        TEAM_ID_AWAY AS team_id,
        TEAM_NAME_AWAY AS team_name,
        FT_PCT_AWAY AS free_throw_percentage,
        COUNT(TEAM_ID_AWAY) AS team_game_count,
        "away" AS game_location
    FROM Game
    GROUP BY SEASON_ID, TEAM_ID_AWAY'''
FT_PCT=pd.read_sql(query,connection)
print(FT_PCT)

FT_PCT=FT_PCT.dropna().query("free_throw_percentage < 1").reset_index(drop=True)
cols_to_drop = ["team_id", "team_name", "team_game_count"]
median_ft_pct = FT_PCT.drop(cols_to_drop, axis=1).groupby(["season", "game_location"]).mean().reset_index()
px.line(median_ft_pct, x="season", y="free_throw_percentage", 
           color="game_location", title="1946-2020: median of the team level free throw percentage by game location")


# #### The FP% starts from 70% and increased over the years to 75% for median NBA season overall FP% among all the games.

# ### 8. How does the three point field goal percentage (3P%) changes over time from 1949 to 2020?
# ### For each season, which team had the best 3P%?

# In[228]:


### How does the three point field goal percentage (3P%) changes over time from 1949 to 2020?
### For each season, which team had the best 3P%?
query = '''select SEASON_ID-20000 AS SEASON,TEAM_ID_HOME AS TEAM_ID,TEAM_NAME_HOME AS TEAM_NAME, FG3_PCT_HOME AS FG3_PCT, 
        "HOME" AS LOCATION FROM GAME
        GROUP BY SEASON,TEAM_ID_HOME 
        UNION
        SELECT SEASON_ID-20000 AS SEASON,TEAM_ID_AWAY AS TEAM_ID,TEAM_NAME_AWAY AS TEAM_NAME, FG3_PCT_AWAY AS FG3_PCT, 
        'AWAY' AS LOCATION FROM GAME
        GROUP BY SEASON,TEAM_ID_AWAY'''
FG3_PCT = pd.read_sql(query,connection)
print(FG3_PCT)

FG3_PCT = FG3_PCT.dropna().query("FG3_PCT < 1").reset_index(drop=True)
cols_to_drop = ["TEAM_ID", "TEAM_NAME"]
FG3_PCT_MEDIAN=FG3_PCT.drop(cols_to_drop, axis=1).groupby(["SEASON", "LOCATION"]).mean().reset_index()
print(FG3_PCT_MEDIAN)
px.line(FG3_PCT_MEDIAN.query("SEASON > 1986"),y='FG3_PCT',x='SEASON',color='LOCATION')


# ### 9. Who are the top 10 NBA players based on 2020-2021 season salary?

# In[232]:


### Who are the top 10 NBA players based on 2020-2021 season salary?

query = '''select slugSeason as season,
            nameTeam,namePlayer,
            2021 - strftime('%Y', Player_Attributes.BIRTHDATE) AS age,
            ROUND(value/1000000,1) AS salary_in_millions 
        from Player_Salary
        JOIN Player ON
            Player_Salary.namePlayer = Player.full_name
        JOIN Player_Attributes ON
            Player.ID = Player_Attributes.ID
            where slugseason = '2020-21' 
            order by value desc
            limit 10
            '''
top10salary = pd.read_sql(query,connection)
top10salary


# #### From the above table results, we can see that Stephen Curry from Golden State Warriors have 2020-21 season salary of 43 Millions.
# #### The top 10 earning NBA players are all in their 30s.

# ## 10.What are the game play stats for the top 10 earning NBA players based on the data available in this table?

# In[233]:


## What are the game play stats for the top 10 earning NBA players based on the data available in this table?

query = '''SELECT namePlayer AS player_name,
        nameTeam AS team_name,
        Player_Attributes.DRAFT_YEAR AS draft_year,
        Player_Attributes.POSITION AS game_position,
        Player_Attributes.PTS AS points,
        Player_Attributes.AST AS assists,
        Player_Attributes.REB AS rebounds,
        ROUND(value/1000000) AS salary_in_millions
    FROM Player_Salary
    JOIN Player ON
        Player_Salary.namePlayer = Player.full_name
    JOIN Player_Attributes ON
        Player.ID = Player_Attributes.ID
    WHERE slugSeason = '2020-21'
    ORDER BY salary_in_millions DESC
    LIMIT 10 '''

player_salary_top_10_game_stats = pd.read_sql(query, connection)
player_salary_top_10_game_stats

