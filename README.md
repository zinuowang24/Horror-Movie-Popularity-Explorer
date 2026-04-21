# What Drives Horror Movie Popularity?
## An Interactive Explorer for Audience Preference Patterns

**Repository:** https://github.com/zinuowang24/Horror-Movie-Popularity-Explorer  
**Product:** Local Streamlit app in this repository  
**Run command:** `python -m streamlit run app.py`  
**Demo video:** 

## 1. Problem & User
This project explores **what factors are associated with the popularity of horror movies**. It is designed for **content planners in streaming or film distribution, junior media analysts, and horror movie fans** who want a simple interactive tool to understand audience preference patterns and benchmark titles more clearly.

## 2. Data
This project uses the **Horror Movies Dataset** from Kaggle:  
https://www.kaggle.com/datasets/sujaykapadnis/horror-movies-dataset

**Access date:** 20 April 2026

Main files used in this repository:
- `data/horror_movies.csv` — raw dataset
- `data_cleaned/horror_movies_cleaned.csv` — cleaned dataset

Key fields used in the analysis include:
- `title`
- `genre_names`
- `popularity`
- `vote_count`
- `vote_average`
- `release_date` / `release_year`
- `runtime`
- `budget`
- `revenue`
- `original_language`
- collection-related fields

## 3. Methods
The project was built in Python and follows a clear end-to-end workflow:

1. Load the raw dataset in the analysis notebook
2. Clean and standardise relevant variables
3. Analyse how popularity is associated with genre combinations, release year, vote behaviour, runtime, budget, revenue, and collection status
4. Save cleaned data, summary tables, and charts into structured folders
5. Build a local **Streamlit** app (`app.py`) to present the findings interactively

The repository also includes `requirements.txt` so the project can be run locally after cloning.

## 4. Key Findings
- Horror movies combined with genres such as **thriller** and **mystery** often show stronger popularity patterns than horror-only titles.
- **More recent releases** tend to have higher popularity values in this dataset.
- **Vote count** is strongly associated with popularity, suggesting that audience engagement is an important signal.
- Movies with **moderate runtimes** often perform better than very short or very long titles.
- These results are **exploratory associations**, not causal conclusions.

## 5. How to run
Clone the repository, install the required packages, and run the Streamlit app locally:

```bash
git clone https://github.com/zinuowang24/Horror-Movie-Popularity-Explorer.git
cd Horror-Movie-Popularity-Explorer
pip install -r requirements.txt
python -m streamlit run app.py
After running the command, open the local address shown in the terminal, usually:http://localhost:8501

## 6. Product link / Demo
**Product / Tool:** Local Streamlit app in this repository  
**Repository link:** https://github.com/zinuowang24/Horror-Movie-Popularity-Explorer  
**How to launch locally:** `python -m streamlit run app.py`  
**Demo video:** To be added

## 7. Limitations & next steps
### Limitations
- This is an **exploratory analysis**, so the results should not be interpreted as causal.
- The dataset’s `popularity` field is treated as an observed platform metric, not a complete measure of business success.
- Some variables contain missing values or inconsistent reporting, which may affect interpretation.

### Next steps
- Improve the app’s benchmarking logic and feature explanations
- Add more interactive comparison options for users
- Optionally expand the analysis with additional movie metadata
- Add the final demo video link
