import pandas as pd
import requests
import json
from io import StringIO
import argparse
import os
import compute  # assumes compute.py defines generate_formula_data()
import plotly.express as px

# URL of the IERS CSV
CSV_URL = "https://datacenter.iers.org/data/csv/bulletina.longtime.csv"

def fetch_and_parse_csv(url):
    """Download CSV and parse semicolon-delimited content."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error downloading CSV: {e}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(StringIO(response.text), sep=';', engine='python')
        return df
    except pd.errors.ParserError as e:
        print(f"Error parsing CSV: {e}")
        return pd.DataFrame()

def extract_3d_points(df):
    """Extract only x_pole, y_pole, and Year columns for volumetric display."""
    required_cols = ["x_pole", "y_pole", "Year"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing expected columns in CSV: {missing_cols}")
        return []

    points = [
        {"x": row["x_pole"], "y": row["y_pole"], "z": row["Year"]}
        for _, row in df.iterrows()
        if not pd.isnull(row["x_pole"]) and not pd.isnull(row["y_pole"]) and not pd.isnull(row["Year"])
    ]
    return points

def render_3d_chart(points, output_path, title="3D Scatter"):
    """Render a 3D scatter plot and save as PNG using Plotly + Kaleido."""
    if not points:
        print(f"No points to render for {title}")
        return

    df = pd.DataFrame(points)
    fig = px.scatter_3d(df, x='x', y='y', z='z', color='z', title=title, opacity=0.8)
    fig.write_image(output_path)
    print(f"Pre-rendered chart saved to {output_path}")

def main(output_json, images_dir):
    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # Step 1: Fetch IERS CSV
    df = fetch_and_parse_csv(CSV_URL)
    iers_points = extract_3d_points(df)

    # Step 2: Generate formula points
    try:
        formula_points = compute.generate_formula_data()
    except Exception as e:
        print(f"Error generating formula points: {e}")
        formula_points = []

    # Step 3: Save JSON
    volumetric_data = {"iers": iers_points, "formula": formula_points}
    with open(output_json, "w") as f:
        json.dump(volumetric_data, f, indent=2)
    print(f"volumetric_data.json updated: {len(iers_points)} IERS points, {len(formula_points)} formula points.")

    # Step 4: Pre-render charts
    render_3d_chart(iers_points, os.path.join(images_dir, "iers.png"), title="IERS Dataset")
    render_3d_chart(formula_points, os.path.join(images_dir, "formula.png"), title="Formula Dataset")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch IERS data and output volumetric JSON + charts.")
    parser.add_argument(
        "--output_json",
        type=str,
        default="gh-pages/docs/volumetric_data.json",
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--images_dir",
        type=str,
        default="gh-pages/docs/images",
        help="Directory to store pre-rendered chart images"
    )
    args = parser.parse_args()
    main(args.output_json, args.images_dir)
