import pdb
import os
import sys
def _find_marker_path(home_pattern:str,marker_depth:int,debug_flag:int=0)->str:
    try:
        import os, fnmatch
        def find_marker_file(name:str, path:str)->str:
            result=None
            marker_file=None
            for root, dirs, files in os.walk(path):
                for f in files:
                    if name in f:
                        result=os.path.abspath(path)
                        marker_file=f
                        break
            return result,marker_file
        path="./."
        for i in range(1,marker_depth):
            p=path*i
            debug_flag and print("looking for %s in %s" % (str(home_pattern),os.path.abspath(p)))
            top_path,marker_file=find_marker_file(home_pattern,p)
            if (None!=top_path):
                debug_flag and print("Found homedir for marker %s in %s" % (str(home_pattern),os.path.abspath(p)))
                os.environ["MARKERPATH"]=top_path  
                os.environ["MARKERPATH_FILE"]=marker_file
                return top_path,marker_file
    except:
        pass
    debug_flag and print("No marker file found")
    return None,None

def _add_marker_path(start_path:str,marker_file:str,debug_flag:bool=False):
    file_path=os.path.join(start_path,marker_file)
    path_flag=False
    try:
        with open(file_path,'rb') as f:
            for line in f:
                if isinstance(line, bytes):
                    line = line.decode('utf-8')
                path=line.strip()
                if path == "add_all_python_paths":
                    _add_python_paths(start_path, debug_flag)
                    continue
                if not os.path.isabs(path):
                    path = os.path.join(start_path, path)
                if path and path not in sys.path:
                    sys.path.append(path)
                    debug_flag and print(f"Adding {path} to sys.path")
                    path_flag=True
    except FileNotFoundError:
        debug_flag and  print(f"File {file_path} not found")
    except:
        pass
    if debug_flag and False==path_flag:
        print("No path added to sys path")
    return        

def _add_python_paths(start_path: str, debug_flag: bool = False):
    for root, dirs, files in os.walk(start_path):
        if any(file.endswith('.py') for file in files):
            if root not in sys.path:
                sys.path.insert(0, root)  # Add to the beginning of sys.path
                debug_flag and print(f"Adding {root} to sys.path")

def marker_main():
    marker_file=os.environ.get("MARKERPATH_FILE",".marker")
    marker_debug=int(os.environ.get("MARKERPATH_DEBUG",0))
    marker_depth=int(os.environ.get("MARKERPATH_DEPTH","10"))
    start_path,marker_file=_find_marker_path(marker_file,marker_depth=marker_depth,debug_flag=marker_debug)
    if None!=start_path:
        _add_marker_path(start_path,marker_file,debug_flag=marker_debug)
    return
# if "__main__"== __name__ :
#     marker_file=os.environ.get("MARKERPATH_FILE",".marker")
#     marker_debug=os.environ.get("MARKERPATH_DEBUG",False)
#     marker_depth=os.environ.get("MARKERPATH_DEPTH",10)
    
#     start_path,marker_file=_find_marker_path(marker_file,marker_depth=marker_depth,debug_flag=marker_debug)
#     _add_marker_path(start_path,marker_file,debug_flag=marker_debug)
#     print(f"IN __MAIN__ MARKERPATH:")
