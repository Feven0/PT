import os, re
import json
import copy
import numpy as np
import math
import heapq
from collections import Counter

from api.utils import (
    get_default_download_folder,
    get_default_output_folder, 
    delete_files_and_subdirectories,
    measure_execution_time,
    read_json,
    write_file,
    write_json,
    get_prompt,
    delete_file,
    delete_folder    
)
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

module_dir= os.path.dirname(__file__)
data_path = lambda x: os.path.join(module_dir, "data", x)
prompt_path = lambda x: os.path.join(module_dir, "prompts", x)


def read_file(file_name):
    try:
        file = open(file_name, "r")
        content = file.read()
        file.close()
        return content
    except:
        return ""


def cosine_similarity(vec1, vec2):
    """
    Calculate the cosine similarity between two vectors.
    """
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
    magnitude_vec1 = math.sqrt(sum(v1 ** 2 for v1 in vec1))
    magnitude_vec2 = math.sqrt(sum(v2 ** 2 for v2 in vec2))

    if magnitude_vec1 == 0 or magnitude_vec2 == 0:
        return 0  # Avoid division by zero

    return dot_product / (magnitude_vec1 * magnitude_vec2)


def check_add_competencies(data):
    competencies = [
    "programming language", "data engineering", "analytics engineering", 
    "automation", "mathematics", "statistics", "deep learning", 
    "machine learning", "database", "software development", 
    "ai science", "bi analytics", "frontend development", 
    "backend development", "full stack development", 
    "deploying genai systems", "collaboration", "communication", 
    "management", "professionalism" ]

    output = [x for x in data]
    entry_names = [entry["name"] for entry in data]
    for competency in competencies:
        if competency not in entry_names:
            output.append({"name": competency, "sfia_level": 0})
        
            

    return output

def get_competency_from_profile(profile, min_sfia_level=0):
    target_competency = []
    for k in profile["competencies"]:
        sfia_level = max(int(k["sfia_level"]), min_sfia_level)
        
        target_competency.append({
                                    "name": k["name"].lower() , 
                                    "sfia_level": sfia_level
                                })
    return target_competency

def split_competencies(competency):
    
    try:
        checked_competency = check_add_competencies(competency)
    except Exception as e:
        logger.error(f"Error in check_add_competencies: {str(e)}")
        raise
    
    output = {
        "AI Engineering": [],
        "Data Engineering": [],
        "Software Engineering": [],
        "Career Skills": []
    }

    categories = {
        "AI Engineering": ["mathematics", "machine learning", "deep learning", "ai science", "deploying genai systems"],
        "Data Engineering": ["data engineering", "analytics engineering", "database", "statistics", "bi analytics"],
        "Software Engineering": ["programming language", "software development", "frontend development", "backend development", "full stack development", "automation"],
        "Career Skills": ["collaboration", "communication", "management", "professionalism"]
    }
    
    for item in checked_competency:
        for category, competencies in categories.items():
            if item["name"] in competencies:
                output[category].append(item)
                break

    return output

def extract_track_competency(data, target_competency, consensus_competency): 
    '''
    We expect data to be a  dictionary    
    '''  
    
    # make a deep copy of the data 
    output = copy.deepcopy(data)
    
    # copy static data
    static = read_json(prompt_path("hragent/recommendation_structure.json"))
    output["recommendation"] = static
    
    try:
        target_comp_dict = split_competencies(target_competency)
        consensus_comp_dict = split_competencies(consensus_competency)
    except Exception as e:
        print("")
        print('target_competency', target_competency)
        print("")
        print("")
        print('consensus_competency', consensus_competency)
        print("")
        logger.error(f"Error in categorising target and consensus competencies: {str(e)}")
        raise
            
    # copy analysis data
    try:        
        tracks = data["analysis"]["tracks"]
        analysis_comp_dict = {}        
        for index, analysis_item in enumerate(tracks):                                       
            if isinstance(analysis_item, dict):  
                title = analysis_item.get("title", "")                    
                if title:
                    analysis_comp_dict[title] = analysis_item
    except Exception as e:
        logger.error(f"Error in extracting analysis tracks: {str(e)}")
        raise
    
    # Update the tracks
    try:
        updated_tracks = []
        for title in consensus_comp_dict.keys():  
            if title in analysis_comp_dict.keys():
                item = analysis_comp_dict[title]
            else:
                item = {}                
                item["title"] = title
                item["analysis"] = {"detail": [],
                                    "description":""
                                    }
            
            #
            item["target_competency"] = target_comp_dict.get(title, [])
            item["consensus_competency"] = consensus_comp_dict.get(title, [])
            updated_tracks.append(item)
            
        if updated_tracks:
            output["analysis"]["tracks"] = updated_tracks
        else:
            output["analysis"]["tracks"] = tracks        
    except Exception as e:
        logger.error(f"Error in updating tracks: {str(e)}")
        raise
    
    return output

def dict_to_vector(competencies, all_competencies, min_sfia_level=0):
    """
    Convert a dictionary of competencies to a SFIA vector.
    The dimensions name are given by all_competencies.
    """
    vec = []
    competencies_dict = {comp['name'].lower(): int(comp['sfia_level']) 
                                for comp in competencies}
    # print(competencies_dict)
    nzero = 0
    for competency in all_competencies:
        sfia_level = competencies_dict.get(competency, min_sfia_level)
        if sfia_level < 1:
          nzero += 1
        vec.append(sfia_level)  # Default SFIA level is 0 if not found

    return vec, nzero

def get_reference_sfia_profiles():
    try:
        # with open(data_path("cv_competency.json"), "r") as file:
        #     all_profiles = json.load(file)
                
        with open(data_path("profile_competency.json"), "r") as file:
            all_profiles = json.load(file)
                
    except Exception as e:
        logger.error(f'Unable to fetch reference SFIA profiles! Error: {str(e)}')
        raise
                        
    output = {}
    try:
        for k, v in all_profiles.items():
            output[k] = get_competency_from_profile(v, min_sfia_level=2) 
    except Exception as e:
        print('all_profiles.keys()', all_profiles.keys())
        logger.error(f'Error getting reference sfia_levels: {str(e)}')
        raise
    
    return output

    
def get_reference_cvs():
    try:
        sfia_reference = get_reference_sfia_profiles()

        all_profile_list = [f for f in os.listdir(data_path("trainees_cv")) if f.endswith(".cv")]
        
        output = []
        for k in all_profile_list:
            # print(c.replace("profile", "cv"))            
            c = k.replace("profile", "cv").replace(".json",".txt")
            if c in sfia_reference:            
                item = {
                        'name': c,
                        'cv_filename': read_file(k)
                        }
                output.append(item)
          
        return output
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return []


def find_top_similar_dicts_cosine(target, 
                                  references, 
                                  all_competencies,
                                  n=5
                                ):
    """
    Find the top 5 most similar dictionaries in the list of dictionaries 
    to the target dictionary using cosine similarity.
    """
    target_vector, nzero = dict_to_vector(target, all_competencies)
    logger.good(f"Number of zero values in target cv: {nzero}", fg="yellow")
    
    similarity_list = []

    invalid_references = {}
    for name, item in references.items():

        reference_vector, nzero = dict_to_vector(item, all_competencies)    
            
        if nzero>0:
            key = f"n={nzero}"
            if key in invalid_references:                
                invalid_references[key] += 1
            else:
                invalid_references[key] = 1

        if nzero > 0:      
            logger.warn(f"Skipping user_file={name} for nzero={nzero}")      
            continue
      
        similarity = cosine_similarity(target_vector, reference_vector)

        similarity_list.append((similarity, item))

    if invalid_references:
        logger.good(f"Frequency of Invalid Reference CVs with sfia_level==0:", fg="yellow")
        print(json.dumps(invalid_references, indent=4))
    
    # Get the top 5 results
    top_results = heapq.nlargest(n, similarity_list, key=lambda x: x[0])
    top_refs = [d for sim, d in top_results]
    top_scores = [sim for sim, d in top_results]

    return top_refs, top_scores

    
def get_reference_competncy_items(target_cv_sfia, all_competencies, n=5):
    all_profiles = get_reference_sfia_profiles()
    top_refs, top_scores = find_top_similar_dicts_cosine(target_cv_sfia, 
                                                        all_profiles, 
                                                        all_competencies,
                                                        n=n
                                                        )
    
    
    # print(top_5_indexs)
    return top_refs, top_scores

def weighted_average(competency_name, top_refs, weights):
    total_weight = sum(weights)
    weighted_sum = 0

    for w, comp_list in zip(weights, top_refs):
        for comp in comp_list:
            if comp['name'] == competency_name:
                weighted_sum += int(comp['sfia_level']) * w

    if total_weight == 0:
        return 0
    else:
        return weighted_sum / total_weight

def most_frequent_sfias(competency_name, top_refs):
    sfia_levels = []
    for comp_list in top_refs:
        for comp in comp_list:
            if comp['name'].rstrip() == competency_name:
                sfia_levels.append(int(comp['sfia_level']))

    if len(sfia_levels) == 0:
      return 0
    # print(sfia_levels)
    return Counter(sfia_levels).most_common(1)[0][0]

def get_consensus_competency(target, top_refs, top_scores, all_competencies, 
                             min_sfia_level=2):
 
    total_similarity = sum(top_scores)
    if total_similarity == 0:
        total_similarity = 1
    weights = [sim / total_similarity for sim in top_scores]

    reference_dict = {}

    for competency_name in all_competencies:
        # Calculate weighted average SFIA level
        weighted_avg = weighted_average(competency_name, top_refs, weights)
        mode_sfias = most_frequent_sfias(competency_name, top_refs)

        # Combine using an equal weighting approach
        consensus_sfias = (weighted_avg + mode_sfias) / 2
        reference_dict[competency_name] = round(consensus_sfias)
        
    # Update the consensus_dict with the target_dict
    output = []
    available_competencies = []
    for target_competency in target:
        name = target_competency["name"].rstrip()
        available_competencies.append(name)
        
        tsfia_level = int(target_competency["sfia_level"])
        csfia_level = reference_dict.get(name, min_sfia_level)
        csfia_level = max(csfia_level, min_sfia_level)
        
        if tsfia_level > csfia_level:
            value = tsfia_level
        else:
            value = csfia_level
            
        output.append({"name": name, "sfia_level": value})

    # Add the missing competencies
    for competency_name in all_competencies:
        if competency_name not in available_competencies:
            csfia_level = reference_dict.get(competency_name, min_sfia_level)
            csfia_level = max(csfia_level, min_sfia_level)
            output.append({"name": competency_name, 
                           "sfia_level": csfia_level
                           })
            
    return output


def get_difference_competency(target, top_refs, top_scores, all_competencies, 
                              stat='average', min_sfia_level=2):
    
    differences = {}
    reference_dict = {}
    for reference in top_refs:
        for reference_competency in reference:
            rname = reference_competency["name"].rstrip()
            rsfia_level = int(reference_competency["sfia_level"])
            reference_dict[rname] = min(rsfia_level, min_sfia_level)
            
            for target_competency in target:            
                tname = target_competency["name"].rstrip()                
                if tname == rname:                    
                    tsfia_level = int(target_competency["sfia_level"])
                    if rsfia_level < min_sfia_level:
                        rsfia_level = min_sfia_level
                                            
                        
                    sfia_level_diff = rsfia_level - tsfia_level

                    # Store the result
                    if tname in differences.keys():
                        differences[tname].append(sfia_level_diff)
                    else:
                        differences[tname] = [sfia_level_diff]
                        
                    break;
  
    merged_differences = []
    available_competencies = []
    for target_competency in target:
        name = target_competency["name"].rstrip()
        available_competencies.append(name)
        
        tsfia_level = int(target_competency["sfia_level"])
        svec = differences.get(name, [])
        
        if len(svec) == 0:
            value = tsfia_level
        else:
            if stat=='median':
                dsfia = np.median(svec)
                
            elif stat=='max':
                dsfia = max(svec)
                
            elif stat=='min':
                dsfia = min(svec)
                
            else:
                dsfia = sum(svec)/len(svec)
                
            value = tsfia_level + dsfia
            
        #
        merged_differences.append({"name": name, "sfia_level": value})
               

    # Add the missing competencies
    for competency_name in all_competencies:
        if competency_name not in available_competencies:
            csfia_level = reference_dict.get(competency_name, min_sfia_level)
            csfia_level = max(csfia_level, min_sfia_level)
            merged_differences.append({"name": competency_name, 
                           "sfia_level": csfia_level
                           })              

    return merged_differences


        
def sfia_values():
    filename = data_path("profile_competency_list.json")
    with_skills = True
    competency_holder = None
    sfia_identifier_prompt = prompt_path("hragent/sfia_identifier_prompt.txt")  #Mistralgenerated.json
    sfia_identifier_prompt = read_file(sfia_identifier_prompt)
    try:
        with open(filename, "r") as file:
            competency_holder = json.load(file)

        sfia_identifier_prompt = sfia_identifier_prompt.replace("{amount}", str(len(competency_holder.keys())))
        sfia_identifier_prompt_skill = sfia_identifier_prompt.replace("{competency_holder}", str(competency_holder))
        sfia_identifier_prompt = sfia_identifier_prompt.replace("{competency_holder}", str(competency_holder.keys()))

        return competency_holder, sfia_identifier_prompt, sfia_identifier_prompt_skill
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        raise
    
def get_competency(competency_holder, target_sfia, stat='average', n=5, min_sfia_level=2):
    
    # Get all competencies
    try:
        target_competency =  get_competency_from_profile(target_sfia)
        all_competencies = list(competency_holder.keys())   
    except Exception as e:        
        print('target_sfia',json.dumps(target_sfia, indent=4))
        logger.error(f'Error in get_competency. Unable to get target competency: {str(e)}')
        raise
    
    # Get the top 5 most similar dictionaries
    try:        
        top_profiles, top_score = get_reference_competncy_items(target_competency,
                                                                all_competencies,
                                                                n=n)        
    except Exception as e:
        print('all_competencies', all_competencies)
        print('target_competency', target_competency)        
        logger.error(f'Error in get_competency. Unable to get similar dicts: {str(e)}')
        raise
    
    # Get the consensus and difference competencies
    try:
        consensus_competency = get_consensus_competency(target_competency,
                                                        top_profiles, 
                                                        top_score, 
                                                        all_competencies,
                                                        min_sfia_level=min_sfia_level
                                                        )
    except Exception as e:
        print('target_competency', target_competency)
        print(f'top_{n}_score', top_score)             
        logger.error(f'Error in get_competency. Unable to get consensus competency: {str(e)}')
        raise
    
    # Get the difference competencies
    try:                
        difference_competency = get_difference_competency(target_competency,
                                                          top_profiles, 
                                                          top_score, 
                                                          all_competencies,                                                          
                                                          stat=stat,
                                                          min_sfia_level=min_sfia_level
                                                          )                
    except Exception as e:
        print('target_competency', target_competency)
        print(f'top_{n}_score', top_score)   
        logger.error(f'Error in get_competency. Unable to get difference competency: {str(e)}')
        raise
  
    return target_competency, consensus_competency, difference_competency
