
import subprocess


output = subprocess.run('sudo apt update', shell = True , capture_output = True, text = True)
print(output.stdout, output.stderr) 

