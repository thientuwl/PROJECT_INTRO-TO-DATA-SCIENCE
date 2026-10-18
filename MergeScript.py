
# ============================================================
# IT135IU - INTRODUCTION TO DATA SCIENCE
# TOPIC 2: AIR QUALITY MONITORING STATION PLACEMENT
# ROLE: DATA ENGINEER
# CITY: SEOUL, SOUTH KOREA
# YEAR: 2022
#
# GOAL:
# Load raw data -> Clean -> Transform -> Merge
# -> Validate -> Export final working dataset
# ============================================================

import pandas as pd

# ============================================================
# STEP 1: LOAD THREE RAW DATASETS
# ============================================================

air = pd.read_csv(
    "AIR_HOUR_2022.csv",
    encoding="utf-8-sig"
)

pop = pd.read_csv(
    "주민등록 세대 및 인구 (성별_연도별_구별) 통계.csv",
    encoding="utf-8-sig"
)

density = pd.read_csv(
    "인구밀도 (구별) 통계.csv",
    encoding="utf-8-sig"
)

# Remove extra spaces in column names
for df in [air, pop, density]:
    df.columns = df.columns.str.strip()

print("=== RAW DATASET SHAPES ===")
print("Air Quality:", air.shape)
print("Population:", pop.shape)
print("Area/Density:", density.shape)

print("\nAir quality columns:")
print(air.columns.tolist())


# ============================================================
# STEP 2: PREPARE AIR QUALITY DATA
# ============================================================

# Rename Korean columns to English
air_clean = air.rename(columns={
    "측정일시": "datetime",
    "측정소 코드": "station_code",
    "측정항목": "pollutant_code",
    "평균값": "value",
    "측정기 상태": "status",
    "국가 기준초과 구분": "national_exceed",
    "지자체 기준초과 구분": "local_exceed"
}).copy()

# Convert timestamp
air_clean["datetime"] = pd.to_datetime(
    air_clean["datetime"].astype(str).str.replace(
        r"\.0$", "", regex=True
    ),
    format="%Y%m%d%H",
    errors="raise"
)

# Convert numeric columns
for col in [
    "station_code",
    "pollutant_code",
    "value",
    "status"
]:
    air_clean[col] = pd.to_numeric(
        air_clean[col].astype(str).str.replace(
            ",", "", regex=False
        ),
        errors="coerce"
    )

# Convert pollutant codes to names
pollutant_map = {
    1: "SO2",
    3: "NO2",
    5: "CO",
    6: "O3",
    8: "PM10",
    9: "PM2.5"
}

air_clean["pollutant"] = (
    air_clean["pollutant_code"].map(pollutant_map)
)

# Check unmapped pollutants
unknown_pollutants = air_clean.loc[
    air_clean["pollutant"].isna(),
    "pollutant_code"
].unique()

assert len(unknown_pollutants) == 0, (
    f"Unknown pollutant codes: {unknown_pollutants}"
)

print("\n=== AIR QUALITY CLEANING ===")
print("Rows before filtering:", len(air_clean))
print("\nInstrument status counts:")
print(air_clean["status"].value_counts(dropna=False))

print("\nMissing values:")
print(air_clean.isna().sum())


# ============================================================
# STEP 3: FILTER INVALID SENSOR MEASUREMENTS
# ============================================================

# Keep normal instrument status only
air_valid = air_clean[
    air_clean["status"] == 0
].copy()

print("\n=== FILTER RESULT ===")
print("Original rows:", len(air_clean))
print("Valid rows:", len(air_valid))
print("Removed rows:", len(air_clean) - len(air_valid))

# Check for duplicate station-hour-pollutant records
duplicate_count = air_valid.duplicated(
    subset=["datetime", "station_code", "pollutant"]
).sum()

print("Duplicate measurements:", duplicate_count)

assert duplicate_count == 0, (
    "Duplicate station-hour-pollutant records found."
)


# ============================================================
# STEP 4: PIVOT LONG FORMAT TO WIDE FORMAT
# ============================================================

# One row per station per hour
air_wide = (
    air_valid
    .pivot_table(
        index=["datetime", "station_code"],
        columns="pollutant",
        values="value",
        aggfunc="first"
    )
    .reset_index()
)

air_wide.columns.name = None

print("\n=== AIR WIDE FORMAT ===")
print("Shape:", air_wide.shape)
print("Columns:", air_wide.columns.tolist())
print(air_wide.head())

print("\nMissing pollutants after pivot:")
print(
    air_wide[
        ["CO", "NO2", "O3", "PM10", "PM2.5", "SO2"]
    ].isna().sum()
)


# ============================================================
# STEP 5: MAP STATION CODES TO SEOUL DISTRICTS
# ============================================================

# Mapping used in the earlier project notebook.
# Verify against Seoul station metadata before final submission.

station_map = {
    101: "종로구",
    102: "중구",
    103: "용산구",
    104: "은평구",
    105: "서대문구",
    106: "마포구",
    107: "성동구",
    108: "광진구",
    109: "동대문구",
    110: "중랑구",
    111: "성북구",
    112: "강북구",
    113: "도봉구",
    114: "노원구",
    115: "양천구",
    116: "강서구",
    117: "구로구",
    118: "금천구",
    119: "영등포구",
    120: "동작구",
    121: "관악구",
    122: "서초구",
    123: "강남구",
    124: "송파구",
    125: "강동구"
}

air_wide["district_kr"] = (
    air_wide["station_code"].map(station_map)
)

print("\n=== STATION MAPPING ===")
print(
    "Missing mappings:",
    air_wide["district_kr"].isna().sum()
)
print(
    "Number of districts:",
    air_wide["district_kr"].nunique()
)

assert air_wide["district_kr"].notna().all(), (
    "Some station codes could not be mapped."
)


# ============================================================
# STEP 6: PREPARE POPULATION DATA FOR 2022
# ============================================================

pop = pop.rename(columns={
    "통계연도": "year",
    "구명": "district_kr",
    "세대수": "households",
    "인구수": "population",
    "남자인구수": "male_population",
    "여자인구수": "female_population",
    "행정동코드": "district_code"
})

# Convert year; metadata row becomes NaN
pop["year"] = pd.to_numeric(
    pop["year"], errors="coerce"
)

# Filter 2022 and remove Seoul total row
pop_2022 = pop[
    (pop["year"] == 2022) &
    (pop["district_kr"] != "계")
].copy()

pop_2022["district_kr"] = (
    pop_2022["district_kr"].str.strip()
)

for col in [
    "district_code",
    "population",
    "households",
    "male_population",
    "female_population"
]:
    pop_2022[col] = pd.to_numeric(
        pop_2022[col].astype(str).str.replace(
            ",", "", regex=False
        ),
        errors="coerce"
    )

print("\n=== POPULATION 2022 ===")
print("Shape:", pop_2022.shape)
print(pop_2022.head())


# ============================================================
# STEP 7: PREPARE AREA / POPULATION DENSITY DATA
# ============================================================

density = density.rename(columns={
    "통계연도": "year",
    "구명": "district_kr",
    "인구수": "population",
    "면적": "area_km2",
    "인구밀도": "population_density",
    "행정동코드": "district_code"
})

density["year"] = pd.to_numeric(
    density["year"], errors="coerce"
)

density_2022 = density[
    (density["year"] == 2022) &
    (density["district_kr"] != "계")
].copy()

density_2022["district_kr"] = (
    density_2022["district_kr"].str.strip()
)

for col in [
    "district_code",
    "population",
    "area_km2",
    "population_density"
]:
    density_2022[col] = pd.to_numeric(
        density_2022[col].astype(str).str.replace(
            ",", "", regex=False
        ),
        errors="coerce"
    )

print("\n=== DENSITY 2022 ===")
print("Shape:", density_2022.shape)
print(density_2022.head())


# ============================================================
# STEP 8: MERGE POPULATION + AREA
# ============================================================

# Use demographic variables from population file
pop_extra = pop_2022[
    [
        "year",
        "district_kr",
        "district_code",
        "households",
        "male_population",
        "female_population"
    ]
].copy()

# Merge by year and Korean district name
district_2022 = density_2022.merge(
    pop_extra,
    on=["year", "district_kr"],
    how="left",
    validate="one_to_one",
    suffixes=("", "_pop"),
    indicator=True
)

# Check all district population rows matched
assert (district_2022["_merge"] == "both").all(), (
    "Some districts did not match population data."
)

# Check district codes are consistent
assert (
    district_2022["district_code"] ==
    district_2022["district_code_pop"]
).all(), "District code mismatch."

district_2022 = district_2022.drop(
    columns=["district_code_pop", "_merge"]
)

print("\n=== MERGED DISTRICT DATA ===")
print("Shape:", district_2022.shape)
print(district_2022.head())

assert len(district_2022) == 25, (
    "Expected 25 Seoul districts."
)


# ============================================================
# STEP 9: MERGE AIR QUALITY + DISTRICT DEMOGRAPHICS
# ============================================================

# Normalize Korean district names
air_wide["district_kr"] = (
    air_wide["district_kr"].str.strip()
)

district_2022["district_kr"] = (
    district_2022["district_kr"].str.strip()
)

# Check all district names are compatible
air_districts = set(air_wide["district_kr"])
demo_districts = set(district_2022["district_kr"])

print("\n=== DISTRICT MATCH CHECK ===")
print("Air only:", air_districts - demo_districts)
print("Demographics only:", demo_districts - air_districts)

assert air_districts == demo_districts, (
    "Districts do not match."
)

# Final merge
final_df = air_wide.merge(
    district_2022,
    on="district_kr",
    how="left",
    validate="many_to_one"
)

assert len(final_df) == len(air_wide), (
    "Final merge changed the row count."
)

print("\n=== FINAL MERGE ===")
print("Shape:", final_df.shape)
print(final_df.head())


# ============================================================
# STEP 10: CONVERT DISTRICTS TO ENGLISH
# ============================================================

district_en_map = {
    "종로구": "Jongno-gu",
    "중구": "Jung-gu",
    "용산구": "Yongsan-gu",
    "성동구": "Seongdong-gu",
    "광진구": "Gwangjin-gu",
    "동대문구": "Dongdaemun-gu",
    "중랑구": "Jungnang-gu",
    "성북구": "Seongbuk-gu",
    "강북구": "Gangbuk-gu",
    "도봉구": "Dobong-gu",
    "노원구": "Nowon-gu",
    "은평구": "Eunpyeong-gu",
    "서대문구": "Seodaemun-gu",
    "마포구": "Mapo-gu",
    "양천구": "Yangcheon-gu",
    "강서구": "Gangseo-gu",
    "구로구": "Guro-gu",
    "금천구": "Geumcheon-gu",
    "영등포구": "Yeongdeungpo-gu",
    "동작구": "Dongjak-gu",
    "관악구": "Gwanak-gu",
    "서초구": "Seocho-gu",
    "강남구": "Gangnam-gu",
    "송파구": "Songpa-gu",
    "강동구": "Gangdong-gu"
}

final_df["district"] = (
    final_df["district_kr"].map(district_en_map)
)

assert final_df["district"].notna().all(), (
    "Missing English district translation."
)

print("\n=== ENGLISH DISTRICTS ===")
print(sorted(final_df["district"].unique()))

# Remove Korean column for English-only output
final_df = final_df.drop(columns=["district_kr"])


# ============================================================
# STEP 11: REARRANGE FINAL DATASET COLUMNS
# ============================================================

final_columns = [
    "datetime",
    "station_code",
    "district",
    "CO",
    "NO2",
    "O3",
    "PM10",
    "PM2.5",
    "SO2",
    "population",
    "area_km2",
    "population_density",
    "households",
    "male_population",
    "female_population",
    "district_code",
    "year"
]

final_df = final_df[final_columns]

final_df = (
    final_df
    .sort_values(["datetime", "station_code"])
    .reset_index(drop=True)
)


# ============================================================
# STEP 12: FINAL DATA VALIDATION
# ============================================================

print("\n=== FINAL VALIDATION ===")

print("Rows:", len(final_df))
print("Columns:", len(final_df.columns))

print("Districts:", final_df["district"].nunique())
print("Stations:", final_df["station_code"].nunique())

print(
    "Date range:",
    final_df["datetime"].min(),
    "to",
    final_df["datetime"].max()
)

duplicate_rows = final_df.duplicated(
    subset=["datetime", "station_code"]
).sum()

print("Duplicate station-hours:", duplicate_rows)

print("\nMissing demographic values:")
print(
    final_df[
        ["population", "area_km2", "population_density"]
    ].isna().sum()
)

print("\nMissing pollutant values:")
print(
    final_df[
        ["CO", "NO2", "O3", "PM10", "PM2.5", "SO2"]
    ].isna().sum()
)

# Assert required data quality rules
assert final_df["district"].nunique() == 25
assert duplicate_rows == 0

assert final_df[
    ["population", "area_km2", "population_density"]
].notna().all().all()

print("\nFirst five rows:")
print(final_df.head())


# ============================================================
# STEP 13: EXPORT FINAL WORKING DATASET
# ============================================================

final_df.to_csv(
    "seoul_air_quality_2022_english.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n===================================")
print("DATA ENGINEERING PIPELINE COMPLETE")
print("===================================")
print("File: seoul_air_quality_2022_english.csv")
print("Shape:", final_df.shape)
