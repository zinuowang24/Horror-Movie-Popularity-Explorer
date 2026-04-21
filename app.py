from pathlib import Path
import re

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="What Drives Horror Movie Popularity?",
    page_icon="🎬",
    layout="wide"
)

# =========================
# Horror Theme Colours
# =========================
PRIMARY_RED = "#8B0000"
SECTION_RED = "#A52A2A"
ACCENT_RED = "#D94F4F"
DARK_TEXT = "#2B2B2B"
MID_GREY = "#5F6368"
LIGHT_BG = "#F7F7F7"
CARD_BG = "#FAFAFA"
CARD_BORDER = "#E5E7EB"


# =========================
# Paths
# =========================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data_cleaned" / "horror_movies_cleaned.csv"

OUTPUTS_DIR = BASE_DIR / "outputs"
OVERVIEW_DIR = OUTPUTS_DIR / "00_overview"
GENRE_DIR = OUTPUTS_DIR / "01_genre_popularity"
YEAR_DIR = OUTPUTS_DIR / "02_release_year_popularity"
VOTES_DIR = OUTPUTS_DIR / "03_votes_ratings_popularity"
RUNTIME_DIR = OUTPUTS_DIR / "04_runtime_budget_collection"


# =========================
# Global Style
# =========================
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {LIGHT_BG};
        color: {DARK_TEXT};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    p, li, label, div {{
        color: {DARK_TEXT};
    }}

    .stMetric {{
        background-color: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-left: 6px solid {PRIMARY_RED};
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }}

    [data-testid="stSidebar"] {{
        background-color: #F3F4F6;
    }}

    [data-testid="stSidebar"] * {{
        color: {DARK_TEXT};
    }}

    hr {{
        border: none;
        height: 1px;
        background-color: #D1D5DB;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# =========================
# Helpers
# =========================
def page_title(text):
    st.markdown(
        f"<h1 style='color:{PRIMARY_RED}; margin-bottom:0.25rem; font-weight:800;'>{text}</h1>",
        unsafe_allow_html=True
    )


def section_header(text):
    st.markdown(
        f"<h2 style='color:{SECTION_RED}; margin-top:1.2rem; margin-bottom:0.4rem; font-weight:700;'>{text}</h2>",
        unsafe_allow_html=True
    )


def subsection_header(text):
    st.markdown(
        f"<h3 style='color:{MID_GREY}; margin-top:0.8rem; margin-bottom:0.3rem; font-weight:700;'>{text}</h3>",
        unsafe_allow_html=True
    )


def clean_column_names(df):
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df


def safe_numeric(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_display_table(df):
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    out.columns = [str(col).replace("_", " ").title() for col in out.columns]
    return out


def read_csv_with_optional_extension(path_without_ext):
    csv_path = Path(str(path_without_ext) + ".csv")
    if csv_path.exists():
        return clean_column_names(pd.read_csv(csv_path))

    if path_without_ext.exists():
        return clean_column_names(pd.read_csv(path_without_ext))

    return pd.DataFrame()


def explode_genres(df, genre_col="genre_names"):
    if genre_col not in df.columns:
        return pd.DataFrame(columns=["genre"])

    temp = df.copy()
    temp[genre_col] = temp[genre_col].fillna("").astype(str)

    def split_genres(text):
        parts = re.split(r"\s*\|\s*|\s*,\s*|\s*;\s*", text)
        return [p.strip() for p in parts if p.strip()]

    temp["genre_list"] = temp[genre_col].apply(split_genres)
    exploded = temp.explode("genre_list")
    exploded = exploded.rename(columns={"genre_list": "genre"})
    exploded = exploded[exploded["genre"].notna()]
    exploded = exploded[exploded["genre"] != ""]
    return exploded


def apply_horror_theme(fig):
    fig.update_layout(
        paper_bgcolor=LIGHT_BG,
        plot_bgcolor="white",
        font=dict(color=DARK_TEXT),
        title_font=dict(color=SECTION_RED, size=20),
        xaxis=dict(
            title_font=dict(color=DARK_TEXT),
            tickfont=dict(color=MID_GREY),
            gridcolor="#E5E7EB",
            zerolinecolor="#E5E7EB"
        ),
        yaxis=dict(
            title_font=dict(color=DARK_TEXT),
            tickfont=dict(color=MID_GREY),
            gridcolor="#E5E7EB",
            zerolinecolor="#E5E7EB"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(color=DARK_TEXT)
        )
    )
    return fig


# =========================
# Data Loading
# =========================
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)
    df = clean_column_names(df)

    numeric_cols = [
        "release_year",
        "popularity",
        "vote_average",
        "vote_count",
        "runtime",
        "budget",
        "revenue",
        "collection"
    ]
    df = safe_numeric(df, numeric_cols)

    if "title" not in df.columns:
        if "movie_title" in df.columns:
            df["title"] = df["movie_title"]
        elif "original_title" in df.columns:
            df["title"] = df["original_title"]
        elif "name" in df.columns:
            df["title"] = df["name"]
        else:
            df["title"] = "Unknown Title"

    if "genre_names" not in df.columns:
        if "genres" in df.columns:
            df["genre_names"] = df["genres"]
        else:
            df["genre_names"] = ""

    if "collection" not in df.columns:
        if "revenue" in df.columns:
            df["collection"] = df["revenue"]
        else:
            df["collection"] = np.nan

    return df


# =========================
# Overview Summary Loading
# =========================
@st.cache_data
def load_overview_tables():
    dataset_summary_df = read_csv_with_optional_extension(OVERVIEW_DIR / "dataset_summary")
    descriptive_stats_df = read_csv_with_optional_extension(OVERVIEW_DIR / "descriptive_stats")
    missing_summary_df = read_csv_with_optional_extension(OVERVIEW_DIR / "missing_summary")
    return dataset_summary_df, descriptive_stats_df, missing_summary_df


# =========================
# Feature Summary Loading
# =========================
@st.cache_data
def load_feature_summary_tables():
    genre_counts_df = read_csv_with_optional_extension(GENRE_DIR / "genre_counts")
    genre_popularity_df = read_csv_with_optional_extension(GENRE_DIR / "genre_popularity_summary")
    genre_rating_df = read_csv_with_optional_extension(GENRE_DIR / "genre_rating_summary")
    genre_vote_count_df = read_csv_with_optional_extension(GENRE_DIR / "genre_vote_count_summary")

    release_year_counts_df = read_csv_with_optional_extension(YEAR_DIR / "release_year_counts")
    release_year_popularity_df = read_csv_with_optional_extension(YEAR_DIR / "release_year_popularity_summary")
    release_year_rating_df = read_csv_with_optional_extension(YEAR_DIR / "release_year_rating_summary")

    audience_response_df = read_csv_with_optional_extension(VOTES_DIR / "audience_response_summary")
    vote_average_popularity_df = read_csv_with_optional_extension(VOTES_DIR / "vote_average_popularity_summary")
    vote_count_popularity_df = read_csv_with_optional_extension(VOTES_DIR / "vote_count_popularity_summary")

    budget_summary_df = read_csv_with_optional_extension(RUNTIME_DIR / "budget_summary")
    collection_vs_noncollection_df = read_csv_with_optional_extension(RUNTIME_DIR / "collection_vs_noncollection_summary")
    runtime_budget_revenue_df = read_csv_with_optional_extension(RUNTIME_DIR / "runtime_budget_revenue_summary")
    runtime_popularity_df = read_csv_with_optional_extension(RUNTIME_DIR / "runtime_popularity_summary")

    return {
        "genre_counts": genre_counts_df,
        "genre_popularity": genre_popularity_df,
        "genre_rating": genre_rating_df,
        "genre_vote_count": genre_vote_count_df,
        "release_year_counts": release_year_counts_df,
        "release_year_popularity": release_year_popularity_df,
        "release_year_rating": release_year_rating_df,
        "audience_response": audience_response_df,
        "vote_average_popularity": vote_average_popularity_df,
        "vote_count_popularity": vote_count_popularity_df,
        "budget_summary": budget_summary_df,
        "collection_vs_noncollection": collection_vs_noncollection_df,
        "runtime_budget_revenue": runtime_budget_revenue_df,
        "runtime_popularity": runtime_popularity_df
    }


# =========================
# Page: Overview
# =========================
def show_overview(df):
    page_title("What Drives Horror Movie Popularity?")
    st.markdown(
        f"<h3 style='color:{MID_GREY}; margin-top:0;'>An interactive explorer for understanding audience preference patterns in horror movies</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
This app helps users explore which movie characteristics are associated with higher popularity in horror films.

**Research Question**  
What factors are associated with the popularity of horror movies?

**Target Users**  
- Content planners at streaming platforms or distributors  
- Junior analysts  
- Horror movie fans
"""
    )

    st.caption("The app focuses on four key factors linked with popularity in the dataset: genre mix, release year, vote activity and ratings, and runtime.")

    total_movies = len(df)

    if "release_year" in df.columns and df["release_year"].notna().any():
        min_year = int(df["release_year"].min())
        max_year = int(df["release_year"].max())
        year_range = f"{min_year} - {max_year}"
    else:
        year_range = "N/A"

    avg_popularity = round(df["popularity"].mean(), 2) if "popularity" in df.columns and df["popularity"].notna().any() else 0
    median_rating = round(df["vote_average"].median(), 2) if "vote_average" in df.columns and df["vote_average"].notna().any() else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Movies", f"{total_movies:,}")
    c2.metric("Year Range", year_range)
    c3.metric("Average Popularity", avg_popularity)
    c4.metric("Median Rating", median_rating)

    st.markdown("---")

    section_header("Key Findings")
    st.markdown(
        """
- **Genre:** Mixed horror genres, especially titles combined with thriller, mystery, or adventure elements, tend to be more popular than pure horror films.  
- **Release Year:** Newer horror movies tend to show higher popularity, with a clear increase in recent years.  
- **Votes & Ratings:** Vote count appears to be the strongest popularity signal, and mid-to-strong audience ratings are generally associated with higher popularity.  
- **Runtime:** Horror movies with moderate runtimes tend to achieve stronger popularity than very short or very long titles.
"""
    )

    st.markdown("---")

    dataset_summary_df, descriptive_stats_df, missing_summary_df = load_overview_tables()

    section_header("Dataset Summary")
    st.caption("A compact overview of the dataset used in this app.")
    if not dataset_summary_df.empty:
        st.dataframe(clean_display_table(dataset_summary_df), use_container_width=True, hide_index=True)
    else:
        st.info("dataset_summary.csv was not found in outputs/00_overview.")

    section_header("Descriptive Statistics")
    st.caption("Descriptive statistics for the main numeric variables.")
    if not descriptive_stats_df.empty:
        st.dataframe(clean_display_table(descriptive_stats_df), use_container_width=True)
    else:
        st.info("descriptive_stats.csv was not found in outputs/00_overview.")

    section_header("Missing Data Summary")
    st.caption("This table shows data completeness and possible quality limitations.")
    if not missing_summary_df.empty:
        st.dataframe(clean_display_table(missing_summary_df), use_container_width=True)
    else:
        st.info("missing_summary.csv was not found in outputs/00_overview.")


# =========================
# Page: Success Scorer
# =========================
def show_success_scorer(df):
    page_title("Success Scorer")
    st.caption("A simple benchmark tool for exploring popularity potential based on patterns observed in the dataset.")

    st.markdown(
        """
This page provides a simple rule-based benchmark score based on patterns observed in the dataset, especially around runtime, ratings, and vote activity.

The score should be interpreted as an exploratory benchmark rather than a prediction.  
It reflects broad popularity patterns in the dataset and does not provide a causal or predictive guarantee.
"""
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        runtime_input = st.slider("Runtime (minutes)", 60, 180, 100)

    with col2:
        rating_input = st.slider("Average Rating", 0.0, 10.0, 6.0, 0.1)

    with col3:
        vote_input = st.slider("Vote Count", 0, 5000, 500)

    score = 0

    if 85 <= runtime_input <= 120:
        score += 30
    elif 75 <= runtime_input <= 130:
        score += 20
    else:
        score += 10

    if rating_input >= 7.0:
        score += 35
    elif rating_input >= 6.0:
        score += 25
    elif rating_input >= 5.0:
        score += 15
    else:
        score += 5

    if vote_input >= 1500:
        score += 35
    elif vote_input >= 700:
        score += 25
    elif vote_input >= 300:
        score += 15
    else:
        score += 5

    st.metric("Estimated Popularity Score", f"{score}/100")

    if score >= 75:
        st.success("This profile looks relatively strong compared with typical movies in the dataset.")
    elif score >= 50:
        st.info("This profile looks moderate. Some features are supportive, but not all.")
    else:
        st.warning("This profile looks relatively weak based on the simple rule-based scoring logic.")

    st.markdown("---")

    section_header("How to Read the Score")
    st.markdown(
        """
- Runtime between 81 and 120 minutes is treated as the strongest benchmark pattern  
- Ratings in the stronger observed range contribute positively to the score  
- Higher vote counts contribute positively and reflect the strongest popularity signal in the dataset  
- The result is designed for interpretation support, not formal prediction
"""
    )


# =========================
# Page: Feature Insights
# =========================
def show_feature_insights(df):
    page_title("Feature Insights")
    st.caption("This page summarises the main analytical findings across four key factors: genre mix, release year, votes and ratings, and runtime.")

    st.markdown(
        """
The charts below provide the evidence behind the main findings reported in the app.
"""
    )

    summaries = load_feature_summary_tables()

    # -------------------------
    # Release Year
    # -------------------------
    section_header("Popularity by Release Year")
    release_year_popularity_df = summaries["release_year_popularity"]

    if not release_year_popularity_df.empty and {"release_year", "popularity"}.issubset(release_year_popularity_df.columns):
        plot_df = release_year_popularity_df.dropna(subset=["release_year", "popularity"]).sort_values("release_year")

        fig_year = px.line(
            plot_df,
            x="release_year",
            y="popularity",
            markers=True,
            title="Average Popularity by Release Year"
        )
        fig_year.update_traces(
            line=dict(color=PRIMARY_RED, width=3),
            marker=dict(color=ACCENT_RED, size=7)
        )
        fig_year.update_layout(xaxis_title="Release Year", yaxis_title="Average Popularity")
        fig_year = apply_horror_theme(fig_year)
        st.plotly_chart(fig_year, use_container_width=True)
    else:
        if "release_year" in df.columns and "popularity" in df.columns:
            fallback_df = (
                df.dropna(subset=["release_year", "popularity"])
                .groupby("release_year", as_index=False)["popularity"]
                .mean()
                .sort_values("release_year")
            )
            if not fallback_df.empty:
                fig_year = px.line(
                    fallback_df,
                    x="release_year",
                    y="popularity",
                    markers=True,
                    title="Average Popularity by Release Year"
                )
                fig_year.update_traces(
                    line=dict(color=PRIMARY_RED, width=3),
                    marker=dict(color=ACCENT_RED, size=7)
                )
                fig_year.update_layout(xaxis_title="Release Year", yaxis_title="Average Popularity")
                fig_year = apply_horror_theme(fig_year)
                st.plotly_chart(fig_year, use_container_width=True)
            else:
                st.info("No release year popularity data available.")
        else:
            st.info("No release year popularity data available.")

    # -------------------------
    # Rating vs Popularity
    # -------------------------
    section_header("Rating vs Popularity")
    vote_average_popularity_df = summaries["vote_average_popularity"]

    if not vote_average_popularity_df.empty and {"vote_average", "popularity"}.issubset(vote_average_popularity_df.columns):
        plot_df = vote_average_popularity_df.dropna(subset=["vote_average", "popularity"])

        fig_rating = px.scatter(
            plot_df,
            x="vote_average",
            y="popularity",
            title="Relationship Between Rating and Popularity",
            opacity=0.75
        )
        fig_rating.update_traces(
            marker=dict(color=SECTION_RED, size=9, line=dict(width=0))
        )
        fig_rating.update_layout(xaxis_title="Average Rating", yaxis_title="Popularity")
        fig_rating = apply_horror_theme(fig_rating)
        st.plotly_chart(fig_rating, use_container_width=True)
    else:
        if "vote_average" in df.columns and "popularity" in df.columns:
            fallback_df = df.dropna(subset=["vote_average", "popularity"]).copy()
            if not fallback_df.empty:
                hover_cols = [c for c in ["title", "release_year", "vote_count"] if c in fallback_df.columns]
                fig_rating = px.scatter(
                    fallback_df,
                    x="vote_average",
                    y="popularity",
                    hover_data=hover_cols,
                    title="Relationship Between Rating and Popularity",
                    opacity=0.65
                )
                fig_rating.update_traces(
                    marker=dict(color=SECTION_RED, size=8, line=dict(width=0))
                )
                fig_rating.update_layout(xaxis_title="Average Rating", yaxis_title="Popularity")
                fig_rating = apply_horror_theme(fig_rating)
                st.plotly_chart(fig_rating, use_container_width=True)
            else:
                st.info("No rating popularity data available.")
        else:
            st.info("No rating popularity data available.")

    # -------------------------
    # Vote Count vs Popularity
    # -------------------------
    section_header("Vote Count vs Popularity")
    vote_count_popularity_df = summaries["vote_count_popularity"]

    if not vote_count_popularity_df.empty and {"vote_count", "popularity"}.issubset(vote_count_popularity_df.columns):
        plot_df = vote_count_popularity_df.dropna(subset=["vote_count", "popularity"])

        fig_vote = px.scatter(
            plot_df,
            x="vote_count",
            y="popularity",
            title="Relationship Between Vote Count and Popularity",
            opacity=0.75
        )
        fig_vote.update_traces(
            marker=dict(color=ACCENT_RED, size=9, line=dict(width=0))
        )
        fig_vote.update_layout(xaxis_title="Vote Count", yaxis_title="Popularity")
        fig_vote = apply_horror_theme(fig_vote)
        st.plotly_chart(fig_vote, use_container_width=True)
    else:
        if "vote_count" in df.columns and "popularity" in df.columns:
            fallback_df = df.dropna(subset=["vote_count", "popularity"]).copy()
            if not fallback_df.empty:
                hover_cols = [c for c in ["title", "release_year", "vote_average"] if c in fallback_df.columns]
                fig_vote = px.scatter(
                    fallback_df,
                    x="vote_count",
                    y="popularity",
                    hover_data=hover_cols,
                    title="Relationship Between Vote Count and Popularity",
                    opacity=0.65
                )
                fig_vote.update_traces(
                    marker=dict(color=ACCENT_RED, size=8, line=dict(width=0))
                )
                fig_vote.update_layout(xaxis_title="Vote Count", yaxis_title="Popularity")
                fig_vote = apply_horror_theme(fig_vote)
                st.plotly_chart(fig_vote, use_container_width=True)
            else:
                st.info("No vote count popularity data available.")
        else:
            st.info("No vote count popularity data available.")

    # -------------------------
    # Runtime Pattern
    # -------------------------
    section_header("Runtime Pattern")
    runtime_popularity_df = summaries["runtime_popularity"]

    if not runtime_popularity_df.empty:
        if "runtime_band" not in runtime_popularity_df.columns:
            possible_band_cols = [c for c in runtime_popularity_df.columns if "runtime" in c and "band" in c]
            if possible_band_cols:
                runtime_popularity_df = runtime_popularity_df.rename(columns={possible_band_cols[0]: "runtime_band"})

        if "avg_popularity" in runtime_popularity_df.columns and "popularity" not in runtime_popularity_df.columns:
            runtime_popularity_df["popularity"] = runtime_popularity_df["avg_popularity"]

        if {"runtime_band", "popularity"}.issubset(runtime_popularity_df.columns):
            plot_df = runtime_popularity_df.dropna(subset=["runtime_band", "popularity"])

            fig_runtime = px.bar(
                plot_df,
                x="runtime_band",
                y="popularity",
                title="Average Popularity by Runtime Band"
            )
            fig_runtime.update_traces(marker_color=PRIMARY_RED)
            fig_runtime.update_layout(xaxis_title="Runtime Band", yaxis_title="Average Popularity")
            fig_runtime = apply_horror_theme(fig_runtime)
            st.plotly_chart(fig_runtime, use_container_width=True)
        else:
            st.info("runtime_popularity_summary exists, but required columns were not found.")
    else:
        if "runtime" in df.columns and "popularity" in df.columns:
            temp = df.dropna(subset=["runtime", "popularity"]).copy()
            if not temp.empty:
                bins = [0, 80, 100, 120, 140, 1000]
                labels = ["<=80", "81-100", "101-120", "121-140", "140+"]
                temp["runtime_band"] = pd.cut(temp["runtime"], bins=bins, labels=labels)

                runtime_summary = (
                    temp.groupby("runtime_band", as_index=False)["popularity"]
                    .mean()
                    .dropna()
                )

                if not runtime_summary.empty:
                    fig_runtime = px.bar(
                        runtime_summary,
                        x="runtime_band",
                        y="popularity",
                        title="Average Popularity by Runtime Band"
                    )
                    fig_runtime.update_traces(marker_color=PRIMARY_RED)
                    fig_runtime.update_layout(xaxis_title="Runtime Band", yaxis_title="Average Popularity")
                    fig_runtime = apply_horror_theme(fig_runtime)
                    st.plotly_chart(fig_runtime, use_container_width=True)
                else:
                    st.info("No runtime popularity data available.")
        else:
            st.info("No runtime popularity data available.")

    # -------------------------
    # Genre Pattern
    # -------------------------
    section_header("Genre Pattern")
    genre_popularity_df = summaries["genre_popularity"]

    if not genre_popularity_df.empty:
        if "genre" not in genre_popularity_df.columns:
            possible_genre_cols = [c for c in genre_popularity_df.columns if "genre" in c]
            if possible_genre_cols:
                genre_popularity_df = genre_popularity_df.rename(columns={possible_genre_cols[0]: "genre"})

        if "avg_popularity" in genre_popularity_df.columns and "popularity" not in genre_popularity_df.columns:
            genre_popularity_df["popularity"] = genre_popularity_df["avg_popularity"]

        popularity_col = "avg_popularity" if "avg_popularity" in genre_popularity_df.columns else "popularity"

        if {"genre", popularity_col}.issubset(genre_popularity_df.columns):
            plot_df = genre_popularity_df.dropna(subset=["genre", popularity_col]).sort_values(popularity_col, ascending=False).head(15)

            fig_genre = px.bar(
                plot_df,
                x="genre",
                y=popularity_col,
                title="Top Genres by Average Popularity"
            )
            fig_genre.update_traces(marker_color=SECTION_RED)
            fig_genre.update_layout(xaxis_title="Genre", yaxis_title="Average Popularity")
            fig_genre = apply_horror_theme(fig_genre)
            st.plotly_chart(fig_genre, use_container_width=True)
        else:
            st.info("genre_popularity_summary exists, but required columns were not found.")
    else:
        exploded = explode_genres(df, "genre_names")

        if not exploded.empty and "popularity" in exploded.columns:
            genre_summary = (
                exploded.groupby("genre", as_index=False)
                .agg(movie_count=("title", "count"), avg_popularity=("popularity", "mean"))
                .sort_values("avg_popularity", ascending=False)
            )

            genre_summary = genre_summary[genre_summary["movie_count"] >= 5].head(15)

            if not genre_summary.empty:
                fig_genre = px.bar(
                    genre_summary,
                    x="genre",
                    y="avg_popularity",
                    title="Top Genres by Average Popularity"
                )
                fig_genre.update_traces(marker_color=SECTION_RED)
                fig_genre.update_layout(xaxis_title="Genre", yaxis_title="Average Popularity")
                fig_genre = apply_horror_theme(fig_genre)
                st.plotly_chart(fig_genre, use_container_width=True)
            else:
                st.info("Not enough genre observations after filtering.")
        else:
            st.info("Genre information is not available.")

    # -------------------------
    # Optional Supporting Tables
    # -------------------------
    st.markdown("---")
    section_header("Supporting Summary Tables")

    with st.expander("Show additional summary tables from outputs"):
        table_map = {
            "Genre Counts": summaries["genre_counts"],
            "Genre Rating Summary": summaries["genre_rating"],
            "Genre Vote Count Summary": summaries["genre_vote_count"],
            "Release Year Counts": summaries["release_year_counts"],
            "Release Year Rating Summary": summaries["release_year_rating"],
            "Audience Response Summary": summaries["audience_response"],
            "Budget Summary": summaries["budget_summary"],
            "Collection vs Non-Collection Summary": summaries["collection_vs_noncollection"],
            "Runtime Budget Revenue Summary": summaries["runtime_budget_revenue"]
        }

        shown_any = False
        for label, table_df in table_map.items():
            if not table_df.empty:
                subsection_header(label)
                st.dataframe(clean_display_table(table_df), use_container_width=True)
                shown_any = True

        if not shown_any:
            st.info("No additional summary tables were found.")


# =========================
# Page: Benchmark Explorer
# =========================
def show_benchmark_explorer(df):
    page_title("Benchmark Explorer")
    st.caption("Filter movies and compare titles across core variables to support practical benchmarking.")

    st.markdown(
        """
This page helps users benchmark movies against the main popularity-related factors highlighted in the analysis, including release year, vote activity, runtime, and broader performance indicators.
"""
    )

    if df.empty:
        st.warning("Main dataset not found.")
        return

    working_df = df.copy()

    if "popularity" not in working_df.columns:
        st.warning("The 'popularity' column is missing.")
        return

    threshold = st.slider("Popularity benchmark percentile", 50, 95, 80)
    cutoff = np.nanpercentile(working_df["popularity"].dropna(), threshold) if working_df["popularity"].notna().any() else np.nan

    benchmark_df = working_df[working_df["popularity"] >= cutoff].copy() if not pd.isna(cutoff) else pd.DataFrame()

    c1, c2, c3 = st.columns(3)
    c1.metric("Benchmark Percentile", f"Top {100-threshold}%")
    c2.metric("Popularity Cutoff", round(cutoff, 2) if not pd.isna(cutoff) else "N/A")
    c3.metric("Benchmark Movies", len(benchmark_df))

    st.markdown("---")

    compare_cols = [c for c in ["popularity", "vote_average", "vote_count", "runtime", "collection"] if c in working_df.columns]

    if compare_cols:
        overall_summary = working_df[compare_cols].mean(numeric_only=True).rename("Overall Mean")
        benchmark_summary = benchmark_df[compare_cols].mean(numeric_only=True).rename("Benchmark Mean")

        compare_table = pd.concat([overall_summary, benchmark_summary], axis=1).reset_index()
        compare_table.columns = ["Metric", "Overall Mean", "Benchmark Mean"]
        compare_table["Overall Mean"] = compare_table["Overall Mean"].round(2)
        compare_table["Benchmark Mean"] = compare_table["Benchmark Mean"].round(2)

        metric_name_map = {
            "popularity": "Popularity",
            "vote_average": "Average Rating",
            "vote_count": "Vote Count",
            "runtime": "Runtime (mins)",
            "collection": "Collection"
        }
        compare_table["Metric"] = compare_table["Metric"].replace(metric_name_map)

        section_header("Benchmark vs Overall")
        st.dataframe(compare_table, use_container_width=True, hide_index=True)

    section_header("Benchmark Movie Table")

    top_n = st.slider("Number of benchmark movies to display", 10, 100, 30, 5)

    preferred_cols = [
        "title",
        "release_year",
        "genre_names",
        "popularity",
        "vote_count",
        "vote_average",
        "runtime"
    ]

    if "collection" in benchmark_df.columns and benchmark_df["collection"].notna().sum() > 0:
        preferred_cols.append("collection")
    elif "revenue" in benchmark_df.columns and benchmark_df["revenue"].notna().sum() > 0:
        preferred_cols.append("revenue")

    show_cols = [c for c in preferred_cols if c in benchmark_df.columns]

    if not benchmark_df.empty and show_cols:
        display_df = benchmark_df[show_cols].copy()

        if "popularity" in display_df.columns:
            display_df = display_df.sort_values("popularity", ascending=False)

        display_df = display_df.head(top_n)

        if "popularity" in display_df.columns:
            display_df["popularity"] = display_df["popularity"].round(2)

        if "vote_average" in display_df.columns:
            display_df["vote_average"] = display_df["vote_average"].round(1)

        if "runtime" in display_df.columns:
            display_df["runtime"] = display_df["runtime"].round(0).astype("Int64")

        if "vote_count" in display_df.columns:
            display_df["vote_count"] = display_df["vote_count"].round(0).astype("Int64")

        if "collection" in display_df.columns:
            display_df["collection"] = display_df["collection"].round(0).astype("Int64")

        if "revenue" in display_df.columns:
            display_df["revenue"] = display_df["revenue"].round(0).astype("Int64")

        rename_map = {
            "title": "Title",
            "release_year": "Release Year",
            "genre_names": "Genres",
            "popularity": "Popularity",
            "vote_count": "Vote Count",
            "vote_average": "Average Rating",
            "runtime": "Runtime (mins)",
            "collection": "Collection",
            "revenue": "Revenue"
        }
        display_df = display_df.rename(columns=rename_map)

        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No benchmark movies available for display.")


# =========================
# Page: Method & Limitations
# =========================
def show_method_limitations(df):
    page_title("Method & Limitations")
    st.caption("This page explains the data source, cleaning logic, analysis methods, and interpretation limits of the app.")

    st.markdown(
        """
## Data Source
This app uses a cleaned horror movie dataset stored locally in `data_cleaned/horror_movies_cleaned.csv`, together with precomputed summary outputs stored in the `outputs/` folder.

## Summary File Usage
To improve stability, clarity, and speed:
- **Overview** reads summary tables from `outputs/00_overview/`
- **Feature Insights** reads grouped summary results from:
  - `outputs/01_genre_popularity/`
  - `outputs/02_release_year_popularity/`
  - `outputs/03_votes_ratings_popularity/`
  - `outputs/04_runtime_budget_collection/`
- **Benchmark Explorer** and **Success Scorer** continue to use the cleaned movie-level dataset for interactive exploration

## Cleaning Logic
Before analysis, the dataset was standardised for consistent use across the app.  
This included:
- normalising column names
- converting key numeric fields where needed
- standardising title fields
- standardising genre fields
- using revenue as collection where a collection field was not directly available

## Analysis Methods
The app is based on descriptive analysis rather than predictive modelling.  
Main methods include:
- summary statistics
- grouped comparisons
- trend analysis
- benchmark comparison
- a simple rule-based scoring feature for interpretation support

## Interpretation Notes
The findings in this app should be interpreted as associations rather than causal effects.  
The visualisations and score are designed to support exploratory understanding and practical benchmarking.  
They should not be treated as predictive or causal guarantees.

## Limitations
- Popularity is treated as an observed outcome rather than a causal measure  
- Missing values and inconsistent genre labels may affect interpretation  
- The Success Scorer is a heuristic rather than a predictive model  
- Results depend on the available horror movie sample and source quality
"""
    )

    if not df.empty:
        section_header("Available Columns in Cleaned Dataset")
        cols_df = pd.DataFrame({"column_name": df.columns})
        st.dataframe(cols_df, use_container_width=True, hide_index=True)


# =========================
# Main
# =========================
def main():
    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "Overview",
            "Success Scorer",
            "Feature Insights",
            "Benchmark Explorer",
            "Method & Limitations"
        ]
    )

    df = load_data()

    if df.empty:
        st.error(
            "Could not find the cleaned dataset.\n\n"
            "Expected path: data_cleaned/horror_movies_cleaned.csv"
        )
        st.stop()

    if page == "Overview":
        show_overview(df)
    elif page == "Success Scorer":
        show_success_scorer(df)
    elif page == "Feature Insights":
        show_feature_insights(df)
    elif page == "Benchmark Explorer":
        show_benchmark_explorer(df)
    elif page == "Method & Limitations":
        show_method_limitations(df)


if __name__ == "__main__":
    main()