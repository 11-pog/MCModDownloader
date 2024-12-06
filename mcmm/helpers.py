import configparser
import json
import os

class cache:
    def __init__(self, cache_path) -> None:
        self.cache_file_path = cache_path


    def setup(self):
        if not os.path.exists(self.cache_file_path):
            os.makedirs(os.path.dirname(self.cache_file_path), exist_ok=True)
            self.clearCache()


    # TODO: Multiple parts of the current code can have this function implemented.
    def cache(self, key:str, value:any=None) -> dict|None:
        """Simple cache function, caches the data in value to the specified key, return the key data if key is None.

        Args:
            key (str): the specified json key.
            value (any, optional): Value to write to the key. Returns the key value if None. Defaults to None.

        Returns:
            dict|None: The value of the specified key, None if writing.
        """
        
        if value is None:        
            with open(self.cache_file_path, 'r') as f:
                data = json.load(f)
                return data.get(key)
            
        with open(self.cache_file_path, 'r+') as f:
                data = json.load(f)
                data[key] = value
                f.seek(0)
                json.dump(data, f)
                f.truncate()


    def clearCache(self):
        """summary_ Clears the cache
        """
        with open(self.cache_file_path, 'w') as f:
            json.dump({}, f)


# TODO: make so sections, keys, default values, and the allow_no_value value to be input when instancing the class, instead of hard-coding it.
class config:
    def __init__(self, config_file_path) -> None:
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser(allow_no_value=True) # Configparses object
        
        self.sections = ['Curseforge', 'General', 'Other']
        self.setup()


    def __getitem__(self, section):
        return self.config[section]


    def setup(self):
        if not os.path.exists(self.config_file_path):
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            self.saveConfig()
        
        self.setup_sections()


    def setup_sections(self):
        self.config.read(self.config_file_path)

        for section in self.sections:
            if not self.config.has_section(section):
                self.config.add_section(section)

        self.config['Curseforge'].setdefault('api_key', '')

        self.config['General'].setdefault('default_output_dir', './')
        self.config['General'].setdefault('default_mod_loader', 'forge neoforge')

        self.config['Other'].setdefault('prioritize_CF', 'False')

        self.saveConfig()


    def saveConfig(self):
        """Saves the current loaded config into the config.ini file.
        """
        with open(self.config_file_path, 'w') as f:
            self.config.write(f)


    def setConfig(self, section: str, option: str, value: any):
        self.config.set(section, option, value)
        self.saveConfig()



class general:
    def __init__(self) -> None:
        pass
    
    # TODO: Multiple parts of the current code can have this function implemented.
    def get_element(self, input: list, index: int, return_all_until_end: bool = False):
        if 0 <= index < len(input):
            return input[index:] if return_all_until_end else input[index]
        else:
            return None
