import os
from .resume import *

def score_resume(resume,job_descr:str,after_decimal=4,status_message=True):
    """
    Computes a weighted resume score based on various semantic, keyword, and experience-related criteria.

    Args:
        resume: The file or text containing the resume content.
        job_descr (str): The job description text to compare against.
        after_decimal (int, optional): Number of decimal places to round the final score. Defaults to 4.
        status_message (bool, optional): Display the status message in terminal when the function is called. 
    Returns:
        float: A score (out of 5) representing the overall match between the resume and the job description.
    
    Scoring Rules:
        1. Overall semantic similarity between the resume and job description.
        2. Skill relevance based on semantic similarity and extracted keywords.
        3. Experience relevance based on semantic similarity, extracted keywords, and experience duration comparison.
        4. Education match based on the highest degree obtained.
        5. Keyword match score for skills and experience.
        6. Skill relevance to project descriptions (if available).
        7. Action verb usage frequency to assess impactfulness of descriptions.
    
    Notes:
        - Uses NLP-based methods (TF-IDF, Named Entity Recognition, and Semantic Similarity).
        - Merges repeated sections before analysis.
        - Calculates weighted scores for each rule and returns a final score out of 5.
    """
    if status_message:
        print("\nScoring in progress!..... ⏳\n")
    document = extract_resume(resume)
    parsed_doc = parse_resume(document)
    merged_doc = merge_repetitions(parsed_doc)

    overall_sem_score = semantic_similarity(resume=document,job_description=job_descr) if document else 0 #---------rule 1
    
    skill_jd_score, skills_keywords = 0, []
    if merged_doc.get("skills"):
        skill_jd_score = semantic_similarity(merged_doc["skills"],job_descr) #-------------------rule 2
        skills_keywords = get_keywords(text=merged_doc["skills"],tfidf=15,ner=15)
    
    exp_jd_score, exp_keywords, res_experience = 0, [], error_messages.no_data["no_data"]
    for section in ["experience", "employment", "work experience"]: 
        if merged_doc.get(section):
            exp_jd_score = semantic_similarity(merged_doc[section], job_descr) #---------------------------rule 2.2
            res_experience = get_experience_years(merged_doc[section])
            exp_keywords = get_keywords(text=merged_doc[section], tfidf=15, ner=15)
            break

    job_desc_experience = get_experience_years(document)
    exp_score = compare_experience(res_experience,job_desc_experience) #----------------------rule 3
    
    edu_score=0
    if merged_doc.get("education"):
        _,res_edu = get_highest_education(info_section=merged_doc["education"])
        _,jd_edu = get_highest_education(info_section=job_descr)
        if res_edu is not None and jd_edu is not None:
            edu_score = 1 if res_edu <= jd_edu else 0 #-------------------------------------------------------------------rule 4

    jd_keywords = get_keywords(text = job_descr,tfidf=15,ner=15)
    skill_keywrd_score = len(match_keywords(skills_keywords,jd_keywords))/len(jd_keywords) if jd_keywords else 0 #------------------------rule 5
    exp_keywrd_score = len(match_keywords(exp_keywords,jd_keywords))/len(jd_keywords) if jd_keywords else 0 #-----------------------------rule 5.2
    
    skill_projct_score = 0
    if merged_doc.get("skills"):
        for project_section in ["projects", "project"]:
            if merged_doc.get(project_section):
                skill_projct_score = semantic_similarity(merged_doc["skills"], merged_doc[project_section]) #---------------------------------rule 6
                break 

    verb_counts = count_action_verbs(document)
    counter = sum(1 for count in verb_counts.values() if count > 2)
    action_word_score = decreasing_score(counter) #-------------------------------------------rule 7   
    
    weighted_scores = (
                       round(overall_sem_score*0.15,after_decimal) + 
                       round(skill_jd_score*0.20,after_decimal) + 
                       round(exp_jd_score*0.20,after_decimal) + 
                       round(exp_score*0.10,after_decimal) + 
                       round(edu_score*0.10,after_decimal) + 
                       round(skill_keywrd_score*0.10,after_decimal) + 
                       round(exp_keywrd_score*0.10,after_decimal) + 
                       round(skill_projct_score*0.03,after_decimal) + 
                       round(action_word_score*0.02,after_decimal)
                       )
    
    return round(weighted_scores*5,after_decimal) # score out of 5 

def screen_all(folder_path: str, job_descr: str, rename_files=False, status_message=True):
    """
    Screens and scores all resumes in a given folder against a job description.

    Args:
        folder_path (str): The path to the folder containing resumes (PDF files).
        job_descr (str): The job description text to compare against.
        rename_files (bool, optional): If True, renames files in parent folder by prefixing them with their score. Defaults to False.
        status_message (bool, optional): Display the status message in terminal when the function is called.

    Returns:
        list: A sorted list of tuples [(filename, score), ...] in descending order of score.

    Notes:
        - Extracts resumes from PDFs and evaluates them using `score_resume`.
        - Sorts resumes based on their match score (highest first).
        - If `rename_files` is enabled, renames files with their respective scores.
    """
    if status_message:
        print("\n🔍 Screening all resumes... Please wait, this may take a few minutes!")
        print("☕ Grab a coffee in the meantime! ☕\n")
    resume_scores = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".pdf")):
                file_path = os.path.join(folder_path, filename)
                score = score_resume(file_path, job_descr,status_message=False)  # Assuming score_resume works with file paths
                resume_scores[filename] = score
    
    # Sort resumes by score (highest first)
    sorted_resumes = sorted(resume_scores.items(), key=lambda x: x[1], reverse=True)

    if rename_files:
        for index, (filename, score) in enumerate(sorted_resumes):
            file_extension = os.path.splitext(filename)[1]
            new_name = f"{score:.2f}_{filename}" 
            new_path = os.path.join(folder_path, new_name)
            old_path = os.path.join(folder_path, filename)

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                print(f"Error renaming {filename}: {e}")
    if status_message:
        print("\n✅ Screening completed! Here are the results:\n")
    return sorted_resumes
