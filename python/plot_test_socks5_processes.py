import matplotlib.pyplot as plt
import sys
import re

def do_graph(data):
    plt.ylabel(r'% done')
    for pid in data:
        x = data[pid][0]
        y = data[pid][1]
        plt.plot(x, y, label=str(pid))
    plt.legend()
    plt.show()
    
def main():
    data = get_data(sys.argv[1])
    do_graph(data)

def get_data(file_name):
    data=dict()
    
    with open(file_name,'r') as fd:
        
        rgx = re.compile(r'\d+.+\((\d+\.\d+)\).+\[(\d+)\].+\(done=(\d+.\d+)%\)')
        line = fd.readline()

        while len(line) > 0:
            m = rgx.match(line)

            if not m is None:

                time,pid,percent = m.groups()
                pid = int(pid)
                if not pid in data:
                    data[pid] = ([],[])

                data[pid][0].append(float(time))
                data[pid][1].append(float(percent))
            line = fd.readline()
    
    return data
        
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("no argument provided")