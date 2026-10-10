import pandas as pd
import streamlit as st
from config.geo_database import CITY_COUNTRY_MAP


def normalize_name(name) -> str | None:
    if pd.isna(name):
        return None
    name = str(name).lower().strip()
    name = name.replace('the ', '')
    return name


def validate_city_country(city: str, country: str) -> bool:

    if pd.isna(city) or pd. isna(country):
        return False
    
    city_norm = normalize_name(city)
    country_norm = normalize_name(country)

    if country_norm in CITY_COUNTRY_MAP:
        valid_cities = [normalize_name(c) for c in CITY_COUNTRY_MAP[country_norm]]
        return city_norm in valid_cities
    
    return False


def get_valid_cities_for_country(
    df: pd.DataFrame,
    city_column: str,
    country: str,
    country_column: str
) -> list:
    try:
        country_norm = normalize_name(country)
        
        if not country_norm:
            raise ValueError("Country name is missing or invalid.")
        
        same_country = df[df[country_column]. str.lower(). str.strip() == country_norm]
        cities_in_data = same_country[city_column].dropna().unique()
        
        # Validate each city
        valid_cities = []
        for city in cities_in_data:
            if validate_city_country(city, country):
                valid_cities.append(city)
        
        # If we have valid cities from data, use them
        if valid_cities:
            return valid_cities
        
        # Otherwise, use our database
        if country_norm in CITY_COUNTRY_MAP:
            # Prefer English names (no non-ASCII characters)
            return [c for c in CITY_COUNTRY_MAP[country_norm] 
                   if not any(ord(ch) > 127 for ch in c)]
        
        # If the country is not in the database, raise an error
        raise KeyError(f"Country '{country}' not found in the database.")
    
    except KeyError as e:
        st.warning(f"Warning: {e}")
        return ["Unknown"]
    
    except ValueError as e:
        st. warning(f"Warning: {e}")
        return ["Unknown"]
    
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return ["Unknown"]