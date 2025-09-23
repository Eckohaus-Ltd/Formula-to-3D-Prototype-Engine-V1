import pandas as pd
import plotly.express as px
import requests
import json
from io import StringIO
import argparse
import compute  # assumes compute.py defines generate_formula_data()
import os

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

def pre_render_charts(iers_points, formula_points, output_path):
    """Optional: Render 3D charts to static images using Plotly."""
    try:
        # Create output folder for images
        img_dir = os.path.join(os.path.dirname(output_path), "images")
        os.makedirs(img_dir, exist_ok=True)

        # Convert lists of points to DataFrames
        iers_df = pd.DataFrame(iers_points)
        formula_df = pd.DataFrame(formula_points)

        if not iers_df.empty:
            fig = px.scatter_3d(iers_df, x="x", y="y", z="z",
                                color="z", color_continuous_scale="Viridis",
                                title="IERS Earth Orientation Parameters")
            fig.write_image(os.path.join(img_dir, "iers_plot.png"))
            print(f"IERS plot saved to {img_dir}/iers_plot.png")

        if not formula_df.empty:
            fig = px.scatter_3d(formula_df, x="x", y="y", z="z",
                                color="z", color_continuous_scale="Plasma",
                                title="Formula Volumetric Data")
            fig.write_image(os.path.join(img_dir, "formula_plot.png"))
            print(f"Formula plot saved to {img_dir}/formula_plot.png")

    except ImportError:
        print("Plotly or Kaleido not installed. Skipping pre-rendering.")
    except Exception as e:
        print(f"Error pre-rendering charts: {e}")

def main(output_path):
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Step 1: Fetch and parse CSV
    df = fetch_and_parse_csv(CSV_URL)

    # Step 2: Extract 3D points
    iers_points = extract_3d_points(df)

    # Step 3: Generate formula points using compute.py
    try:
        formula_points = compute.generate_formula_data()
    except Exception as e:
        print(f"Error generating formula points: {e}")
        formula_points = []

    # Step 4: Combine into JSON
    volumetric_data = {
        "iers": iers_points,
        "formula": formula_points
    }

    # Step 5: Save JSON
    try:
        with open(output_path, "w") as f:
            json.dump(volumetric_data, f, indent=2)
        print(f"volumetric_data.json updated: {len(iers_points)} IERS points, {len(formula_points)} formula points.")
    except Exception as e:
        print(f"Error writing JSON file: {e}")

    # Step 6: Optional pre-render charts
    pre_render_charts(iers_points, formula_points, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch IERS data and output volumetric JSON.")
    parser.add_argument(
        "--output",
        type=str,
        default="gh-pages/docs/volumetric_data.json",
        help="Path to output JSON file"
    )
    args = parser.parse_args()
    main(args.output)
