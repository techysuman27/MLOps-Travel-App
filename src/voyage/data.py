"""Source contracts and time-aware splits; identifiers never become predictors."""
import hashlib
from pathlib import Path

import pandas as pd

SCHEMAS = {
    "flights": ["travelCode", "userCode", "from", "to", "flightType", "price", "time", "distance", "agency", "date"],
    "users": ["code", "company", "name", "gender", "age"],
    "hotels": ["travelCode", "userCode", "name", "place", "days", "price", "total", "date"],
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_data(data_dir="data/raw"):
    frames = {}
    for name, columns in SCHEMAS.items():
        path = Path(data_dir) / f"{name}.csv"
        df = pd.read_csv(path, keep_default_na=False)
        if set(df.columns) != set(columns):
            raise ValueError(f"{name}: columns do not match source contract")
        if df.empty or df.isna().any().any() or df.astype(str).apply(lambda s: s.str.strip().eq("")).any().any():
            raise ValueError(f"{name}: empty data or missing fields")
        if df.duplicated().any():
            raise ValueError(f"{name}: duplicate rows must be investigated")
        for col in set(columns) & {"travelCode", "userCode", "code", "age", "days", "price", "total", "time", "distance"}:
            df[col] = pd.to_numeric(df[col], errors="raise")
            if not df[col].map(lambda x: float('-inf') < x < float('inf')).all():
                raise ValueError(f"{name}.{col}: non-finite values")
            if (df[col] < 0).any():
                raise ValueError(f"{name}.{col}: negative values")
        if "date" in df:
            df["date"] = pd.to_datetime(df["date"], format="%m/%d/%Y", errors="raise")
        frames[name] = df
    users, flights, hotels = (frames[x] for x in ("users", "flights", "hotels"))
    if not users.code.is_unique:
        raise ValueError("User codes must be unique")
    if not set(users.gender).issubset({"female", "male", "none"}):
        raise ValueError("Unexpected source gender label")
    for name in ("flights", "hotels"):
        if not frames[name].userCode.isin(users.code).all():
            raise ValueError(f"{name}: orphan user reference")
    if (flights['from'] == flights['to']).any() or (flights[['price', 'time', 'distance']] <= 0).any().any():
        raise ValueError("Invalid flight route or non-positive flight measurements")
    if (hotels[['days', 'price', 'total']] <= 0).any().any():
        raise ValueError("Non-positive hotel values")
    if ((hotels.days * hotels.price - hotels.total).abs() > 0.02).any():
        raise ValueError("Hotel total differs from days times nightly price")
    trip_keys = pd.MultiIndex.from_frame(flights[['travelCode', 'userCode']])
    if not pd.MultiIndex.from_frame(hotels[['travelCode', 'userCode']]).isin(trip_keys).all():
        raise ValueError("Hotel trip has no flight")
    return frames


def chronological_split(df, group_trips=False):
    """Use date quantiles; purge trips crossing either boundary."""
    cut1 = df.date.quantile(0.70).normalize()
    cut2 = df.date.quantile(0.85).normalize()
    if group_trips:
        groups = df.groupby(['travelCode', 'userCode']).date
        first, last = groups.transform('min'), groups.transform('max')
    else:
        first = last = df.date
    masks = [last < cut1, (first >= cut1) & (last < cut2), first >= cut2]
    splits = [df.loc[m].copy() for m in masks]
    if any(x.empty for x in splits):
        raise ValueError("Insufficient dated observations for train/validation/test")
    info = {"validation_start": str(cut1.date()), "test_start": str(cut2.date()),
            "train_rows": len(splits[0]), "validation_rows": len(splits[1]), "test_rows": len(splits[2]),
            "purged_rows": len(df) - sum(map(len, splits))}
    return (*splits, info)
