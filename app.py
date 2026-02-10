
import streamlit as st
from supabase import create_client
import pandas as pd

# Connect to DB
supabase = create_client("https://nyjamsyqhoezdwbjaydf.supabase.co", "sb_publishable_K7eMGcayO1nxXLUAgkRrww_jCUchW3a")

st.set_page_config(layout="wide", page_title="NIL Tool")
st.title("🏈 NIL Evaluation Dashboard")

# Sidebar
teams = supabase.table("teams").select("id, name").order("name").execute()
if teams.data:
    df_teams = pd.DataFrame(teams.data)
    team_name = st.sidebar.selectbox("Select Team", df_teams['name'])
    team_id = df_teams[df_teams['name'] == team_name].iloc[0]['id']

    # Main Data
    players = supabase.table("players").select("*").eq("team_id", team_id).execute()
    if players.data:
        df_players = pd.DataFrame(players.data)

        # Get Valuations
        p_ids = df_players['id'].tolist()
        try:
            valuations = supabase.table("valuations").select("*").in_("player_id", p_ids).order("date", desc=True).execute()
            df_val = pd.DataFrame(valuations.data)
        except:
            df_val = pd.DataFrame()

        if not df_val.empty:
            df_val = df_val.drop_duplicates('player_id')
            df_final = pd.merge(df_players, df_val[['player_id', 'calculated_value']], left_on='id', right_on='player_id', how='left')
            df_final['calculated_value'] = df_final['calculated_value'].fillna(500)
        else:
            df_final = df_players
            df_final['calculated_value'] = 500

        # ... (existing code above)

df_final = df_final.drop_duplicates(subset=["name"])
# Display
display = df_final[['name', 'position', 'calculated_value']].rename(columns={'calculated_value': 'NIL Value'})
display = display.sort_values('NIL Value', ascending=False)

# ... (existing code below)
        
        # Display
        display = df_final[['name', 'position', 'calculated_value']].rename(columns={'calculated_value': 'NIL Value'})
        display = display.sort_values('NIL Value', ascending=False)

        st.metric("Total Roster Value", f"${display['NIL Value'].sum():,.0f}")
        st.dataframe(display.style.format({'NIL Value': '${:,.2f}'}), use_container_width=True)
    else:
        st.info("No players found.")
