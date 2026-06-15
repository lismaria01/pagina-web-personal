import os
import json
import locale
from datetime import datetime

def _parse_date_flexible(app, d):
    """
    Robustly parse a date string from a few common formats. If all formats
    fail, log a warning and return a default date to prevent crashing.
    """
    date_str = str(d)
    # Add any other date formats you might use in your markdown files
    formats_to_try = [
        '%Y-%m-%d',  # eg. 2023-12-25
        '%d-%m-%Y',  # eg. 25-12-2023
        '%B %d, %Y', # eg. December 25, 2023
    ]
    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    app.logger.warning(f"Could not parse date '{date_str}' with any known format. Using a default date.")
    return datetime(1970, 1, 1)

def _set_locale(app, lang: str):
    """Sets the locale for date formatting based on the language."""
    try:
        if lang == 'es':
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        else:
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    except locale.Error:
        app.logger.warning(f"Locale for '{lang}' not supported on this system. Using default.")

def load_site_data(app, lang: str) -> dict:
    """Loads and combines site data from JSON files for a given language."""
    # Construct absolute paths to data files to avoid issues with the working directory.
    base_path = app.root_path
    shared_data_path = os.path.join(base_path, 'data', 'shared_data.json')
    lang_data_path = os.path.join(base_path, 'data', f'{lang}.json')

    # Load shared data that is not language-specific
    with open(shared_data_path, 'r', encoding='utf-8') as f:
        shared_data = json.load(f)

    # Load language-specific data
    with open(lang_data_path, 'r', encoding='utf-8') as f:
        lang_data = json.load(f)

    # Merge the shared data and the language-specific data
    shared_projects = {p['id']: p for p in shared_data['projects']}
    merged_projects = []
    for p_lang in lang_data['projects']:
        project_id = p_lang['id']
        if project_id in shared_projects:
            merged_projects.append({**shared_projects[project_id], **p_lang})
    lang_data['projects'] = merged_projects

    lang_data['education'] = [{**e, **lang_data['education'][i]} for i, e in enumerate(shared_data['education'])]
    lang_data['experience'] = [{**w, **lang_data['experience'][i]} for i, w in enumerate(shared_data['experience'])]
    lang_data['publications'] = [{**p, **lang_data['publications'][i]} for i, p in enumerate(shared_data['publications'])]
    lang_data['social_links'] = shared_data['social_media']
    return lang_data