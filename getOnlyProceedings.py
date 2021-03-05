import sys
myfile = open(sys.argv[1],'r')
outfile = open(sys.argv[2],'w')
ok = False
for line in myfile.readlines():
    if "<proceedings" in line or ok:
        ok = True
        if "</proceedings" in line and ok:
            if "<proceedings" in line:
                ok = True
                outfile.write(line)
            else:
                outfile.write('</proceedings>\n')
                ok = False
        else:
            try:
                if line[1] == "/":
                    outfile.write(line[line.find('>')+1:])
                else:
                    outfile.write(line)
            except:
                print(line)

myfile.close()
outfile.close()
