import configparser
import json
import os

class cache:
    def __init__(self, cache_file_path) -> None:
        self.cache_file_path = cache_file_path


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


class config:
    def __init__(self, config_file_path, default_structure, *, allow_no_value=False) -> None:
        self.config_file_path = config_file_path
        
        self.config = configparser.ConfigParser(allow_no_value=allow_no_value) # Configparses object
        
        self.default_structure = default_structure
        self.setup()


    def __getitem__(self, section):
        return self.config[section]


    def setup(self):
        if not os.path.exists(self.config_file_path):
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            self.saveConfig()
        
        self.setup_sections()
        self.saveConfig()


    def setup_sections(self):
        self.config.read(self.config_file_path)

        for section in self.default_structure:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            if self.default_structure[section] is not None:
                for key in self.default_structure[section]:
                    value = self.default_structure[section][key]
                    self.config[section].setdefault(key, '' if value is None else value)


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


# Testing
if __name__ == '__main__':
    configPath = os.path.join(os.path.dirname(__file__), "config") # Configs dir path
    configFile = os.path.join(configPath, 'config.ini') # Config.ini path
    
    Config = config(configFile, default_structure={
        'Curseforge': {
            'api_key': None
        },
        'General': {
            'default_output_dir': './',
            'default_mod_loader': 'forge neoforge'
        },
        'Other': {
            'prioritize_CF': 'False'
        }, 
        'Testes_Malignos': None
    }, allow_no_value=True)