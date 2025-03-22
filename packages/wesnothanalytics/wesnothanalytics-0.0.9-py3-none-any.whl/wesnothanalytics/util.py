import re
import os
import json

from .classes import Bucket



def load_config(fname):
    

    """
This function defines how the package reads in config files.

Input will the the filename of the config file inside the configs folder (include extensions, exclude the folder name as it's implied).
Output will be the contents of the file in dictionary format.


Parameters:
  * `fname` (string): The name of the config file, including extension and not including the file path (folder).
 
Returns:
  * None

Example:

load_config("dictionary.json")

 
    """   
    
    module_dir = os.path.dirname(__file__)
    config_path = os.path.join(module_dir,f'configs/{fname}')

    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)

        
    return config_data




def prep_replay(content):
    
    # Removing extra text
    text = content.replace("\t","")
    text = re.sub(r'\s*Ladder_[0-9]+(_[0-9]+)?',"",text)
    text = re.sub(r'\s+(Re)?[bB]alanced(_[0-9]+)?',"",text)
    text = text.replace("L_","")
    text = text.replace("Dark Sorceress","Dark Sorcerer")
    text = text.strip()

    bucket = Bucket(text)

    pattern = re.compile(r'^\d+\.\d+\.\d+$')
    assert bool(pattern.match(bucket.version))

    if (bucket["replay_start"] or bucket["scenario"]) and bucket["replay"]:
        return bucket
    else:
        raise Exception("This must be a valid Wesnoth replay.")