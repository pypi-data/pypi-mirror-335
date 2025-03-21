# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 09:07:19 2022
Updated on Fri Okt 04 12:21:20 2024

@author: Mohamed
"""

import os
import sys
import logging
import inspect
import datetime
import threading
import time

class Rocklogger():
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _caller_info = None
    @classmethod
    def get_instance(cls, level='info', use_date_in_filename=True, base_dir=None):
        """
        Get or create the singleton instance of Rocklogger.
        
        Args:
            level (str): Logging level ('info', 'debug', 'warning', 'error')
            use_date_in_filename (bool): Whether to include date in log filename
            base_dir (str, optional): Base directory where the 'logs' folder will be created.
                                     If None, the 'logs' folder will be created in the same
                                     location as the calling script.
            
        Returns:
            Rocklogger: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                # Store caller info from the script that first creates the logger
                if cls._caller_info is None:
                    for frame_info in inspect.stack():
                        module = inspect.getmodule(frame_info.frame)
                        if module and module.__name__ != __name__:
                            if module.__file__:
                                dir_name, file_name = os.path.split(module.__file__)
                                file_name = file_name.split('.')[0]
                                cls._caller_info = (dir_name, file_name)
                                break
                    if cls._caller_info is None:
                        cls._caller_info = (os.getcwd(), 'unknown')
                
                # Add a visual separator between instances
                separator = "#" * 80
                print(f"\n{separator}")
                print(f"Created new Rocklogger instance from {cls._caller_info[1]}")
                print(f"{separator}\n")
                
                # Create the instance
                cls._instance = cls(level, use_date_in_filename, base_dir)
            else:
                print(f"Using existing Rocklogger instance (created from {cls._caller_info[1]})")
        return cls._instance
    
    def __init__(self, level='info', use_date_in_filename=True, base_dir=None):
        # Skip initialization if already initialized
        if Rocklogger._initialized:
            return
            
        self.use_date_in_filename = use_date_in_filename
        self.current_date = datetime.datetime.now().strftime("%Y%m%d")
        self.base_dir = base_dir
        self.logger = self.__setup_logger(self.__get_level(level))
        self.__setup_exception_logging()
        self.__start_date_check_thread()
        Rocklogger._initialized = True
    
    def __setup_logger(self, log_lvl):
        caller_dirname, caller_filename = self.__get_caller()
        # Use custom base directory if provided, otherwise use caller's directory
        base_directory = self.base_dir if self.base_dir else caller_dirname
        log_dir = os.path.join(base_directory, 'logs')
        log_file = self.__get_log_file_path(log_dir, caller_filename, '')
        error_log_file = self.__get_log_file_path(log_dir, caller_filename, '_error')
        os.makedirs(log_dir, exist_ok=True)
        
        # General log file handler
        logging.basicConfig(filename=log_file, filemode='a', 
                            format='%(asctime)s - %(filename)s - %(levelname)-8s:  %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S', 
                            level=log_lvl, 
                            force=True)
        
        # Error log file handler
        error_handler = logging.FileHandler(error_log_file, mode='a')
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)-8s:  %(message)s', 
                                            datefmt='%Y-%m-%d %H:%M:%S')
        error_handler.setFormatter(error_formatter)
        logging.getLogger().addHandler(error_handler)
        
        # Console handler
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(log_lvl)
        console_formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)-8s:  %(message)s', 
                                              datefmt='%Y-%m-%d %H:%M:%S')
        console.setFormatter(console_formatter)
        logging.getLogger().addHandler(console)
        
        logger = logging.getLogger(__name__)
        return logger
    
    def __get_log_file_path(self, log_dir, filename, suffix):
        if self.use_date_in_filename:
            return os.path.join(log_dir, f"{filename}{suffix}_{self.current_date}.log")
        else:
            return os.path.join(log_dir, f"{filename}{suffix}.log")
    
    def __get_level(self, log_level_str):
        levels = {
            'info': logging.INFO,
            'debug': logging.DEBUG,
            'warning': logging.WARNING,
            'error': logging.ERROR
        }
        return levels.get(log_level_str.lower(), logging.INFO)
    
    def __get_caller(self):
        # Use the stored caller info from the script that first created the logger
        if Rocklogger._caller_info:
            return Rocklogger._caller_info
            
        # Fallback to the original implementation if _caller_info is not set
        for frame_info in inspect.stack():
            module = inspect.getmodule(frame_info.frame)
            if module and module.__name__ != __name__:
                if module.__file__:
                    dir_name, file_name = os.path.split(module.__file__)
                    file_name = file_name.split('.')[0]
                    return dir_name, file_name
                else:
                    return os.getcwd(), 'interactive_shell'
        return os.getcwd(), 'unknown'
    
    def __setup_exception_logging(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self.logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        sys.excepthook = handle_exception
    
    def __start_date_check_thread(self):
        def check_date_change():
            while True:
                current_date = datetime.datetime.now().strftime("%Y%m%d")
                if current_date != self.current_date:
                    self.current_date = current_date
                    self.__update_log_file_paths()
                time.sleep(60)  # Check every 60 seconds
                
        date_check_thread = threading.Thread(target=check_date_change, daemon=True)
        date_check_thread.start()
    
    def __update_log_file_paths(self):
        caller_dirname, caller_filename = self.__get_caller()
        # Use custom base directory if provided, otherwise use caller's directory
        base_directory = self.base_dir if self.base_dir else caller_dirname
        log_dir = os.path.join(base_directory, 'logs')
        log_file = self.__get_log_file_path(log_dir, caller_filename, '')
        error_log_file = self.__get_log_file_path(log_dir, caller_filename, '_error')
        
        # Update handlers
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self.logger.removeHandler(handler)
        
        self.__setup_logger(self.logger.level)
    
    def get_logger(self):
        return self.logger
    
    def close(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            self.logger.removeHandler(handler)
            handler.close()
        Rocklogger._initialized = False
        Rocklogger._instance = None
            
    def __del__(self):
        self.close()
        
    @classmethod
    def reset(cls):
        """Reset the singleton instance (mainly for testing purposes)"""
        separator = "#" * 80
        print(f"\n{separator}")
        print("Resetting Rocklogger instance")
        print(f"{separator}\n")
        
        if cls._instance:
            cls._instance.close()
        cls._instance = None
        cls._initialized = False
        cls._caller_info = None

if __name__ == "__main__":
    # Initialize with date in filename
    # logger = Rocklogger.get_instance(level='debug', use_date_in_filename=True).get_logger()
    # logger.debug('This is a debug message.')

    # Initialize without date in filename
    logger = Rocklogger.get_instance(level='debug', use_date_in_filename=False).get_logger()
    logger.debug('This is a debug message.')

    # Example code to trigger an uncaught exception
    print("This will be logged.")
    raise Exception("This is an uncaught exception!")
