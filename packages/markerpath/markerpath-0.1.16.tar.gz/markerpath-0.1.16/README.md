Usage:

1. Create a file with extension .marker in your base directory.  
2. Contents of this file
    an empty file
    OR
    lines of path relative to the base directory marked by the marker file. These paths will be appended to sys.path
    OR
    add_all_python_paths

3. In your python file with main anywhere under the base directory.
    import markerpath

    3.1 This will create a environment variable 
        MARKERPATH=<the base directory>

    3.2 Access this as such
        import os
        marker_home=os.environ["MARKERPATH"]
4. Provides a global dictionary called 
    markerpath_global 
    key "logger" that holds the python logger object.

5. Provides a inject_logger_member that will inject the self.logger ( or any name you chose ). This member can be used in the __init__

6. The user can initialize the global markerpath_global with markerpath_global_initialize

7. The config value is parsed if passed ar an argument --config  or in defaults  like
    markerpath_confg.xml
    config/markerpath_config.xml




