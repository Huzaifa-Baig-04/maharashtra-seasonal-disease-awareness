# Maharashtra Seasonal Disease Awareness

A Streamlit public-health awareness dashboard for exploring historical disease reports in Maharashtra. Its sections are Home, Explore Trends, Insights Summary, Climate Insights, and Awareness & Prevention. The summary compares each disease's peak season, district totals and leading categories, and available climate averages. It focuses on accessible seasonal patterns, descriptive comparisons, and general preventive guidance. It does not make predictions, classify risk, diagnose illness, or claim climate causes disease patterns.

## Project data

The notebook outputs have been included under `Data/processed/`, so the app loads the feature-engineered dataset automatically when launched from this project folder. The notebooks use Google Drive at `/content/drive/MyDrive/CEP Seasonal Disease Prediction` and identify these files:

- Preferred: `Data/processed/Maharashtra_Feature_Engineered.csv`
- Alternative: `Data/processed/Maharashtra_Seasonal_Disease_Cleaned.csv`

Both CSVs are included in this project. The dashboard also accepts a CSV upload in its sidebar if you want to use a different copy.

The supplied collection and analysis notebooks are preserved in `notebooks/`. Static chart images embedded in the EDA and statistical-analysis notebooks are extracted to `assets/notebook-eda/` and available in the Home section as a reference gallery. Those notebook charts are fixed to the notebooks' original full-data run; the main dashboard charts respond to the selected filters.

The minimum fields are `Date`, `Disease`, and `Cases`. A date can instead be constructed from `Year`, `Month`, and `Day`. District is read from `district` or `District`. Climate views are enabled when `Temp`, `preci`, or `LAI` is available. The app also accepts common capitalization variants and raw notebook fields such as `year`, `mon`, and `day`. If a `state_ut` field is present, records are filtered to Maharashtra when matching records exist.

## Run locally

Python 3.10 or newer is recommended.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
streamlit run app.py
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` and run `python -m pip install -r requirements.txt` followed by `streamlit run app.py`.

If the dataset is not in the default path, upload the CSV through the sidebar after the app opens. The navigation sections are in the sidebar; the trend and climate pages provide their own filters.

## Publish it online

The app is organized for deployment from the repository root: `app.py`, `requirements.txt`, `Data/processed/`, `assets/`, and `notebooks/` are included. The `.gitignore` keeps local virtual environments and secrets out of Git.

1. Push this project folder to a **public GitHub repository**.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with GitHub and authorize access to the public repository.
3. Choose **Create app**, select the repository and its default branch, and set the app file path to `app.py`.
4. Deploy. Community Cloud provides the public `*.streamlit.app` URL and redeploys when the repository is updated.

See the official [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) for the current interface.

## Interpretation

Displayed case counts are totals in the selected records, not population-adjusted incidence rates. Source reporting coverage and practices affect the totals. Climate charts show historical measurements alongside case reports and are descriptive only. Awareness tips are general information; follow current guidance from Maharashtra public-health authorities and consult a qualified health professional for personal medical concerns.
