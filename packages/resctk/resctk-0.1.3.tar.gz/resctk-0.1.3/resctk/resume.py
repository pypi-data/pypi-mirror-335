import pdfplumber
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk import pos_tag
from sentence_transformers import SentenceTransformer
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import re
from datetime import datetime
from copy import deepcopy
#custom import
from . import error_messages

#Universal container/cacher for loading models and avoiding reloads
model_load_cache = {}

def get_name(resume_text:str)->str:
    """
    Extracts the candidate's name from the resume.

    Args:
        resume_text (str): The extracted text of the resume.

    Returns:
        str: The extracted name or a message indicating no name was found.

    Notes:
        - Uses regex to identify a name pattern at the beginning of the resume.
        - Assumes proper capitalization (e.g., "John Doe").
        - Returns a predefined error message if no name is detected.
    """
    name_pattern = re.findall(
        r'(?i)^(?:[A-Z][a-z\'-]+(?:\s[A-Z][a-z\'-]+)*)', resume_text, re.MULTILINE)
    name = name_pattern[0] if name_pattern else error_messages.no_sections["name"]
    return name
        
def get_phone_number(resume:str)->str:
    """
    Extracts phone number(s) from the resume.

    Args:
        resume (str): The extracted text of the resume.

    Returns:
        str: The extracted phone number(s) or a message indicating no phone number was found.

    Notes:
        - Supports international formats (e.g., "+1 123-456-7890").
        - Returns multiple phone numbers as a comma-separated string.
    """
    phone_pattern = re.findall(r'\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{3,4}[\s.-]?\d{3,4}', resume)
    if phone_pattern:
        phone_numbers = ", ".join(phone_pattern)  # Join multiple numbers as a string
    else:
        phone_numbers = error_messages.no_sections["phone"]
    return phone_numbers

def get_email(resume:str)->str:
    """
    Extracts email address(es) from the resume.

    Args:
        resume (str): The extracted text of the resume.

    Returns:
        str: The extracted email address(es) or a message indicating no email was found.

    Notes:
        - Matches standard email formats (e.g., "example@email.com").
        - Returns multiple emails as a comma-separated string.
    """
    email_pattern = re.findall(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+', resume)
    if email_pattern:
        email = phone_numbers = ", ".join(email_pattern)
    else:
        email = error_messages.no_sections["email"]
    return email

def get_experience(resume: str) -> str:
    """
    Extracts the 'Experience' section from a resume.

    Args:
        resume (str): The extracted text of the resume.

    Returns:
        str: The extracted experience details or a message indicating no experience details were found.

    Notes:
        - Identifies experience sections using common variations (e.g., "Work Experience", "Employment").
        - Extracts content until the next major section (e.g., Education, Skills, Projects).
        - If no clear ending section is found, captures text until the end of the resume.
    """
    experience_pattern = re.compile(
        r"(?i)(?:Experience|Work Experience|Employment|Professional Experience)\s*(.*?)(?=\n(?:Education|Skills|Awards|Employment|Interests|Summary|Contributions|References|Projects|Project Work|Project|Certificates|Certificate|Certifications|\Z))",
        re.DOTALL
    )
    experience_search = experience_pattern.search(resume)
    
    if experience_search:
        experience = experience_search.group(1).strip()
        return experience if experience else error_messages.no_sections["experience"]
    
    # Fallback: If no termination section exists, return everything after "Experience" till the end
    experience_fallback_pattern = re.compile(r"(?i)(?:Experience|Work Experience|Employment|Professional Experience)\s*(.*)", re.DOTALL)
    fallback_search = experience_fallback_pattern.search(resume)
    
    return fallback_search.group(1).strip() if fallback_search else error_messages.no_sections["experience"]

def get_skills(resume: str) -> str:
    """
    Extracts the 'Skills' section from a resume.

    Args:
        resume (str): The extracted text of the resume.

    Returns:
        str: The extracted skills details or a message indicating no skills were found.

    Notes:
        - Identifies the 'Skills' section using common variations (e.g., "Technical Skills", "Relevant Skills").
        - Extracts content until the next major section (e.g., Experience, Education, Projects).
        - If no clear ending section is found, captures text until the end of the resume.
    """
    skills_pattern = re.compile(
        r"(?i)(?:Skills|Technical Skills|Relevant Skills)\s*(.*?)(?=\n(?:Experience|Work Experience|Professional Experience|Education|Awards|Employment|Interests|Summary|Contributions|References|Projects|Project Work|Project|Certificate|Certificates|Certifications|\Z))",
        re.DOTALL
    )
    skills_search = skills_pattern.search(resume)
    
    if skills_search:
        skills = skills_search.group(1).strip()
        return skills if skills else error_messages.no_sections["skills"]
    
    # Fallback: If no termination section exists, return everything after "Skills" till the end
    skills_fallback_pattern = re.compile(r"(?i)(?:Skills|Technical Skills|Relevant Skills)\s*(.*)", re.DOTALL)
    fallback_search = skills_fallback_pattern.search(resume)
    
    return fallback_search.group(1).strip() if fallback_search else error_messages.no_sections["skills"]

def get_education(resume: str) -> str:
    """
    Extracts the 'Education' section from a resume.

    Args:
        resume (str): The extracted text of the resume.

    Returns:
        str: The extracted education details or a message indicating no education details were found.

    Notes:
        - Identifies the 'Education' section using common variations (e.g., "Education", "Academic Background", "Qualifications").
        - Extracts content until the next major section (e.g., Experience, Skills, Projects).
        - If no clear ending section is found, captures text until the end of the resume.
        - Returns a predefined error message if no education details are detected.
    """
    education_pattern = re.compile(
        r"(?i)(?:Education|Academic Background|Qualifications)\s*(.*?)(?=\n(?:Experience|Work Experience|Professional Experience|Skills|Awards|Employment|Interests|Summary|Contributions|References|Projects|Project Work|Project|Certificate|Certificates|Certifications|\Z))",
        re.DOTALL
    )
    education_search = education_pattern.search(resume)
    
    if education_search:
        education = education_search.group(1).strip()
        return education if education else error_messages.no_sections["education"]
    
    # Fallback: If no termination section exists, capture till last
    education_fallback_pattern = re.compile(r"(?i)(?:Education|Academic Background|Qualifications)\s*(.*)", re.DOTALL)
    fallback_search = education_fallback_pattern.search(resume)

    return fallback_search.group(1).strip() if fallback_search else error_messages.no_sections["education"]

def get_projects(resume: str) -> str:
    """
    Extracts the 'Projects' section from a resume.

    Args:
        resume (str): The extracted text of the resume.

    Returns:
        str: The extracted project details or a message indicating no projects were found.

    Notes:
        - Identifies the 'Projects' section using common variations (e.g., "Project Work", "Projects", "Project").
        - Extracts content until the next major section (e.g., Experience, Skills, Education).
        - If no clear ending section is found, captures text until the end of the resume.
        - Returns a predefined error message if no projects are detected.
    """
    project_pattern = re.compile(
        r"(?i)(?:Project Work|Projects|Project)\s*(.*?)(?=\n(?:Experience|Work Experience|Professional Experience|Education|Skills|Awards|Employment|Interests|Summary|Contributions|References|Certificate|Certificates|Certifications|\Z))",
        re.DOTALL
    )
    project_search = project_pattern.search(resume)

    if project_search:
        project = project_search.group(1).strip()
        return project if project else error_messages.no_sections["projects"]

    # Fallback: Capture till end if no termination section is found
    project_fallback_pattern = re.compile(r"(?i)(?:Project Work|Projects|Project)\s*(.*)", re.DOTALL)
    fallback_search = project_fallback_pattern.search(resume)

    return fallback_search.group(1).strip() if fallback_search else error_messages.no_sections["projects"]

def get_custom_section(resume: str, section_name: str, variations: list):
    """
    Extracts a custom section from a resume based on provided section name variations.

    Args:
        resume (str): The extracted text of the resume.
        section_name (str): The name of the section to extract.
        variations (list): A list of possible variations of the section name.

    Returns:
        str: The extracted section content or a message indicating the section was not found.

    Notes:
        - Uses regex to locate the section based on provided variations.
        - Extracts content until the next major resume section (e.g., Experience, Skills, Education).
        - If no clear ending section is found, it captures text until the end of the resume.
        - Returns a standardized message if the section is missing.
    """
    custom_pattern = re.compile(
        rf"(?i)\b(?:{'|'.join(map(re.escape, variations))})(?:\s*(?:and|&|/)\s*\w+)*\b\s*(.*?)(?=\n(?:" 
        r"Experience|Work Experience|Professional Experience|Education|Skills|Projects|Project Work|Project|"
        r"Employment|Interests|Summary|Certificates|Contributions|References|Certificate|Certificates|Certifications|Awards|\Z))",
        re.DOTALL
    )
    match = custom_pattern.search(resume)

    if match:
        custom_section = match.group(1).strip()
        return custom_section if custom_section else f"{section_name} section not found."

    # Fallback: Capture till end if no termination section is found
    fallback_pattern = re.compile(rf"(?i)\b(?:{'|'.join(map(re.escape, variations))})\b\s*(.*)", re.DOTALL)
    fallback_search = fallback_pattern.search(resume)

    return fallback_search.group(1).strip() if fallback_search else f"{section_name} section not found."

def get_experience_years(experience_section:str)->str:
    """
    Extracts and calculates the total experience duration from a given experience section.

    Args:
        experience_section (str): The text containing work experience details.

    Returns:
        str: The total experience formatted as "X year(s) and Y month(s)".

    Notes:
        - Extracts years and months using regex patterns.
        - Determines the earliest and latest work periods to compute the experience duration.
        - Handles month name variations and converts them to numerical format.
        - Ensures a fixed format output, even if months are missing.
        - If no valid years are found, returns a predefined "no data" message.
    """
    year_pattern = r'\b(19\d{2}|20\d{2})\b'
    month_pattern = r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b'

    # Extract years and months
    years = sorted(set(map(int, re.findall(year_pattern, experience_section))))
    months = re.findall(month_pattern, experience_section, re.IGNORECASE)

    if not years:
        return error_messages.no_data["no_data"] #------------------------------fixed format of output
    
    start_year, end_year = years[0], years[-1]
    
    #determine range using months
    start_month = months[0] if months else "January"
    end_month = months[-1] if len(months) > 1 else "December"

    #month names to numbers
    month_map = {m[:3].lower(): i+1 for i, m in enumerate([
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ])}

    start_month_num = month_map[start_month[:3].lower()]
    end_month_num = month_map[end_month[:3].lower()]

    #experience duration
    start_date = datetime(start_year, start_month_num, 1)
    end_date = datetime(end_year, end_month_num, 1)
    delta = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    years_exp = delta // 12
    months_exp = delta % 12
    if years_exp < 0:
        years_exp = 0
    if months_exp < 0:
        months_exp = 0
    return f"{years_exp} year(s) and {months_exp} month(s)" #-------------------fixed format of output

def get_company_names(info_section:str, spacy_model = "en_core_web_md" )->list:
    """
    Extracts company names from a given text using spaCy's Named Entity Recognition (NER).

    Args:
        info_section (str): The section of text (e.g., work experience) to extract company names from.
        spacy_model (str, optional): The spaCy model to use for entity recognition. 
                                     Defaults to "en_core_web_md".

    Returns:
        list: A list of extracted company names. If no companies are found, returns a predefined 
              error message from `error_messages.no_data["company_data"]`.
    """
    if spacy_model not in model_load_cache:
        model_load_cache[spacy_model] = spacy.load(spacy_model)
    
    model = model_load_cache[spacy_model]
    doc = model(info_section)
    companies = []
    for entity in doc.ents:
        if entity.label_=="ORG" and entity.text.strip("● / + ") not in companies:
            companies.append((entity.text))
    if companies:
        return companies
    else:
        return error_messages.no_data["company_data"]

def get_highest_education(info_section: str):
    """
    Identifies the highest level of education mentioned in a given text.

    Parameters:
    ----------
    info_section (str): The text containing education details.

    Returns:
    -------
    tuple: The highest education level found and its index in the hierarchy, or an error message.
    """
    education_keywords = [
        "phd", "doctorate", "doctor of philosophy",
        "master's","masters","master", "msc", "ma", "mba", "m.tech", "m.e.",
        "bachelor's","bachelors","bachelor", "bsc", "ba", "b.tech", "b.e.", "bba",
        "diploma", "associate"
    ]
    pattern = r'\b(' + '|'.join(re.escape(edu) for edu in education_keywords) + r')\b'
    matches = re.findall(pattern, info_section, re.IGNORECASE)
    if matches:
        normalized_matches = [match.lower() for match in matches]
        highest_edu = min(normalized_matches, key=lambda x: education_keywords.index(x))
        return highest_edu, education_keywords.index(highest_edu)
    else:
        return error_messages.no_data["education_data"],len(education_keywords)
    
def get_university_name(info_section: str, words_b4_keywords = 3,words_after_keywords=2,add_keywords:str = None )->str:
    """
    Extracts university or institution names from a given text.

    Parameters:
    ----------
    info_section (str): The text containing education details.
    words_b4_keywords (int, optional): Number of words before the keyword to consider. Default is 5.
    words_after_keywords (int, optional): Number of words after the keyword to consider. Default is 2.
    add_keywords (str, optional): Additional keywords to consider for identifying universities.

    Returns:
    -------
    list: A list of matching university names, or an error message if none are found.
    """
    university_keywords = ["University", "Institute", "College", "School", "Academy", "Polytechnic"]
    if add_keywords:
        university_keywords.extend(add_keywords.split(","))
        
    pattern = (
        r'((?:\S+\s+){0,' + str(words_b4_keywords) + r'}'  # Up to 5 words before
        r'(?:' + '|'.join(university_keywords) + r')'  # University keyword
        r'(?:\s+\S+){0,' + str(words_after_keywords) + r'})'  # Up to 2 words after
    )
    matches = re.findall(pattern, info_section, re.IGNORECASE)
    if not matches:
        return error_messages.no_data["university_data"]
    return " ".join(matches)

def get_keywords(text:str, tfidf=10,ner=10, ner_model="en_core_web_sm")->list:
    """
    Extracts keywords using both TF-IDF and Named Entity Recognition (NER).

    Parameters:
    ----------
    text (str): The input text to extract keywords from.
    tfidf (int, optional): Number of keywords to extract using TF-IDF. Default is 10.
    ner (int, optional): Number of Named Entities to extract. Default is 10.
    ner_model (str, optional): The spaCy model to use for NER. Default is "en_core_web_sm".

    Returns:
    -------
    list[str]: A list of extracted keywords.

    Example:
    --------
    >>> get_keywords("Google and Microsoft are tech giants. AI is the future of innovation.", tfidf=5, ner=5)
    ['google', 'microsoft', 'ai', 'tech', 'innovation']
    """

    if not isinstance(text, str) or not text.strip():  # to handle empty text
        return []
    
    # TF-IDF Extraction
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        tfidf_keywords = [word for word, _ in sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)][:tfidf]
    except ValueError:  # Catch TF-IDF errors for short/empty text
        tfidf_keywords = []

    # NER Extraction
    if ner_model not in model_load_cache:
        model_load_cache[ner_model] = spacy.load(ner_model)
    doc = model_load_cache[ner_model](text)
    ner_keywords = list({ent.text.lower() for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "GPE", "NORP"]})[:ner]
    
    combined_keywords = set(tfidf_keywords).union(set(ner_keywords))
    return list(combined_keywords)

def match_keywords(list1: list[str], list2: list[str], ignore_case: bool = True) -> list[str]:
    """
    Finds common keywords between two lists.

    This function compares two lists of keywords and returns a list of matches.
    It optionally ignores case while comparing.

    Parameters:
    ----------
    list1 (list[str]): First list of keywords.
    list2 (list[str]): Second list of keywords.
    ignore_case (bool, optional): If True (default), comparison is case-insensitive.

    Returns:
    -------
    list[str]: A list of common elements found in both lists.

    Example:
    --------
    >>> match_keywords(["Python", "Java", "C++"], ["java", "C#", "python"])
    ['python', 'java']
    >>> match_keywords(["Python", "Java", "C++"], ["java", "C#", "python"], ignore_case=False)
    []
    """
    if not isinstance(list1, list) or not isinstance(list2, list):
        raise ValueError("Both inputs must be lists.")

    if ignore_case:
        list1, list2 = set(map(str.lower, map(str, list1))), set(map(str.lower, map(str, list2)))
    else:
        list1, list2 = set(map(str, list1)), set(map(str, list2))

    return list(list1 & list2)

def extract_resume(resume)->str:
    """
    Extracts text from a PDF resume.

    This function reads a PDF file and extracts text from all its pages, 
    ensuring proper handling of multi-page documents.

    Parameters:
    ----------
    resume_path (str): 
        Path to the resume PDF file.

    Returns:
    -------
    str:
        Extracted text content from the PDF.

    Example:
    --------
    >>> extract_resume("resume.pdf")
    'John Doe Software Engineer Experience at XYZ...'
    """
    doc = pdfplumber.open(resume)
    text = doc.pages
    corpus =""
    for i in text:
        page_text = i.extract_text(x_tolerance = 2)
        if page_text:
            corpus += page_text + "\n"
    doc.close() 
    return corpus.strip()

def parse_resume(extracted_resume :str, extra_sections:list = None, regex_parse:bool = False, merge_repetition = False)->dict:
    """
    Parses an extracted resume text into structured sections.

    The function tokenizes the resume content and assigns tokens to predefined sections. 
    If regex_parse is enabled, it extracts structured information such as name, email, 
    phone number, skills, experience, projects, and education using regex-based methods.

    Parameters:
    ----------
    extracted_resume (str): 
        The raw text content of the resume.

    extra_sections (list, optional): 
        Additional section names to be considered beyond the default ones. 
        Defaults to None.

    regex_parse (bool, optional): 
        If True, uses regex-based parsing for specific fields like name, email, etc. 
        If False, uses token-based sectioning. Defaults to False.

    merge_repetition (bool, optional): 
        If True, merges repeated sections (e.g., multiple "education" entries). 
        Defaults to False.

    Returns:
    -------
    dict:
        A dictionary containing structured resume sections.

    Example:
    --------
    >>> resume_text = "Education: BSc in CS\nWork Experience: Software Engineer at XYZ\nSkills: Python, Java"
    >>> parse_resume(resume_text, regex_parse=True)
    {'name': 'John Doe', 'email': 'john@example.com', 'phone': '123-456-7890', 
     'skills': 'Python, Java', 'experience': 'Software Engineer at XYZ', 
     'projects': 'N/A', 'education': 'BSc in CS'}
    """
    sections = ["skills","references","project","projects","work experience","experience","employment", 
                "education" ,"interests", "contributions","contribution","awards",
                "summary","certifications"]
      
    if extra_sections:
        sections.extend(map(str.lower,extra_sections))
    
    group = {}

    if regex_parse == False:
        tokens = word_tokenize(extracted_resume)
        prev_token = "personal information"
        updater = ""
        section_counter = 1

        for token in tokens:
            token_lower = token.lower()
            
            if token_lower not in sections:
                updater = updater + " " + token
                group[prev_token] = updater.strip()
            else:
                if token_lower in group:
                    section_counter += 1
                    token_lower = token_lower+str(section_counter)
                
                group[token_lower] = ""
                updater = ""
                prev_token = token_lower
        
        if merge_repetition:
            for key in list(group):
                group = merge_repetitions(group, section=key)
    
    else:
        group.update({"name":get_name(extracted_resume),
                    "email":get_email(extracted_resume),
                    "phone":get_phone_number(extracted_resume),
                    "skills":get_skills(extracted_resume),
                    "experience":get_experience(extracted_resume),
                    "projects":get_projects(extracted_resume),
                    "education":get_education(extracted_resume)
                    })    
    return group
        
def check_repetitions(parsed_resume:dict,section:str)->int:
    """
    Counts the number of repeated sections in a parsed resume.

    This function checks how many keys in the parsed resume dictionary 
    start with the given section name (case-insensitive).

    Parameters:
    parsed_resume (dict): A dictionary where keys represent section names 
                          and values contain the extracted content.
    section (str): The section name to check for repetitions.

    Returns:
    int: The count of keys that start with the given section name.

    Example:
    >>> parsed_resume = {"education_1": "BSc in CS", "education_2": "MSc in AI", "experience": "Software Engineer"}
    >>> check_repetitions(parsed_resume, "education")
    2
    """
    count = 0
    for key in parsed_resume.keys():
        if key.startswith(section.lower()):
            count += 1
    return count

def merge_repetitions(parsed_resume: dict, section: str = None) -> dict:
    """
    Merges repeated sections in a parsed resume dictionary.

    If `section` is provided, only keys related to that section are merged.
    Otherwise, all sections with repetitive keys are merged.

    Parameters:
    parsed_resume (dict): The parsed resume data with potential duplicate sections.
    section (str, optional): A specific section to merge (e.g., "experience", "education").

    Returns:
    dict: A cleaned dictionary with merged sections.

    Example:
    >>> resume_data = {
            "experience_1": "Worked at X.",
            "experience_2": "Promoted at X.",
            "education": "BSc in CS"
        }
    >>> merge_repetitions(resume_data, "experience")
    {'experience': 'Worked at X. Promoted at X.', 'education': 'BSc in CS'}
    """
    new_parsed_data = parsed_resume.copy()
    merged_data = {}
    keys_to_remove = set()

    keys = sorted(new_parsed_data.keys())  # Sorting ensures consistent order

    if section:
        # If section is provided, only merge keys that start with the given section
        relevant_keys = [key for key in keys if key.startswith(section)]
    else:
        # If no section is provided, consider all keys for merging
        relevant_keys = keys

    for key in relevant_keys:
        base_key = key.rstrip("0123456789_")  # Remove numbers and underscores at the end

        if base_key not in merged_data:
            merged_data[base_key] = str(new_parsed_data[key])
        else:
            merged_data[base_key] += " " + str(new_parsed_data[key])

        keys_to_remove.add(key)

    for key, value in merged_data.items():
        new_parsed_data[key] = value

    for key in keys_to_remove:
        if key not in merged_data:  # Keep only cleaned-up base keys
            new_parsed_data.pop(key, None)

    return new_parsed_data


def semantic_similarity(resume:str,job_description:str,sentence_transformer_model = "paraphrase-MiniLM-L3-v2")->float:
    """
    Computes the semantic similarity between a resume and a job description.

    This function uses a Sentence Transformer model to encode both the resume and job description
    into vector representations and calculates their cosine similarity. The similarity score is 
    then normalized to a range of [0, 1], where:
        - `0.0` indicates completely opposite meanings.
        - `0.5` indicates no significant similarity.
        - `1.0` indicates perfect similarity.

    Parameters:
    resume (str): The resume text.
    job_description (str): The job description text.
    sentence_transformer_model (str, optional): The Sentence Transformer model to use for encoding.
                                                Defaults to "paraphrase-MiniLM-L3-v2".

    Returns:
    float: A normalized similarity score between 0 and 1.

    Example:
    >>> semantic_similarity("Software Engineer with Python skills", "Looking for a Python Developer")
    0.85
    """
    if not resume or not job_description: 
        return 0

    try:
        if sentence_transformer_model not in model_load_cache: 
            model_load_cache[sentence_transformer_model] = SentenceTransformer(sentence_transformer_model)
        '''model_load_cache is the universal cacher for
            loading and storing models temporarily'''
        senc= model_load_cache[sentence_transformer_model].encode(resume)
        jenc = model_load_cache[sentence_transformer_model].encode(job_description)
        senc=np.reshape(senc,(1,-1))
        jenc=np.reshape(jenc,(1,-1))
        sim = model_load_cache[sentence_transformer_model].similarity(senc,jenc)
        val = sim.numpy().astype(float)
        set_range = (val + 1)/2 #normalizing 0-opp. meaning, 0.5-no similarity, 1-completely similar
        return set_range.item()
    
    except Exception as e:
        print(f"Error loading model or computing similarity: {e}. \n Kindly fix the error before recomputing as the score obtained is not valid !!")
        return 0
    
def count_action_verbs(text:str)->dict:
    """
    Count occurrences of action verbs in a given text.

    This function tokenizes the input text, removes stopwords, tags parts of speech, 
    and identifies verbs (excluding auxiliary verbs). It then counts the occurrences 
    of each action verb.

    Parameters:
    text (str): The input text from which action verbs will be extracted.

    Returns:
    dict: A dictionary where keys are action verbs and values are their respective counts.

    Example:
    >>> text = "Developed a machine learning model. Created a dashboard. Managed a team."
    >>> count_action_verbs(text)
    {'developed': 1, 'created': 1, 'managed': 1}
    """
    if not text.strip():  # Handle empty input
        return {}

    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    pos_tags = pos_tag(words)
    action_verbs = [word for word, tag in pos_tags if tag.startswith('VB') and word not in stop_words]
    verb_counts = {}
    for verb in action_verbs:
        if verb in verb_counts:
            verb_counts[verb] += 1
        else:
            verb_counts[verb] = 1  
    return verb_counts

def compare_experience(resume_experience_years: str, required_experience_years: str)->int:
    """
    Compare experience from a resume against the required experience.

    This function expects experience values in the format: "x year(s) y month(s)".  
    It converts both values into total months and returns:
    - `0` if the resume experience is less than the required experience.
    - `1` if the resume experience meets or exceeds the required experience.

    Parameters:
    resume_experience_years (str): Experience from the resume in the format "x year(s) y month(s)".
    required_experience_years (str): Required experience in the same format.

    Returns:
    int: `1` if resume experience is sufficient, otherwise `0`.

    Example:
    >>> compare_experience("3 year(s) 6 month(s)", "2 year(s) 9 month(s)")
    1
    >>> compare_experience("1 year(s) 4 month(s)", "2 year(s) 0 month(s)")
    0
    """    
    if resume_experience_years == error_messages.no_data["no_data"] or required_experience_years == error_messages.no_data["no_data"]:
        return 0
    resume_experience_years = resume_experience_years.replace("year(s)", "").replace("month(s)", "").replace("and", "").strip()
    required_experience_years = required_experience_years.replace("year(s)", "").replace("month(s)", "").replace("and", "").strip()
    y1, m1 = map(int, resume_experience_years.split())
    y2, m2 = map(int, required_experience_years.split())
    #everything to months
    resume_months = y1 * 12 + m1
    required_months = y2 * 12 + m2

    return 0 if resume_months < required_months else 1

def decreasing_score(x,k=2):
    return 1 / (1 + np.exp(x - k))