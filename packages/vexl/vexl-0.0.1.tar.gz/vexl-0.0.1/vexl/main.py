#🍃🍀 
#version 0.0.1

#-- all import --
import os
import sys
import venv
import subprocess


#-- all varitable --
n = len(sys.argv)

#-- all functions --
def create_env(name_env,packages=None, system_site_packages=False):
    try:
        venv.create(name_env, with_pip=True, system_site_packages=system_site_packages)
        if sys.platform == "win32":
            python_executable = os.path.join(name_env, "Scripts", "python.exe")
        else:
            print("This is not a windows system")

        if packages:
            subprocess.check_call([python_executable, "-m", "pip", "install", *packages])
        f = open("env.ps1", "w")
        f.write((f"""cd {name_env}\\Scripts \n.\\activate\ncd ..\\.."""))
        f.close()

    except Exception as e:
        print(f"Error creating virtual environment: {e}")
def main():
    for i in range(1, n):
        try:
            item = sys.argv[i]
            if item == "-h" or item == "--help":
                print("Usage: nove [name of evnironment]")
            else:
                create_env(item)
            
        except IndexError:
            print("error")

#-- main --
if __name__ == "__main__":
    main()

# written by Pratham 🍂🍁

