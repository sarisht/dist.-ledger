

# create primary keys
# open("public_keys.txt","w").write("\n".join(map(str,range(int(input())))))

#create nodeips
a = map(str,[10,1,20])
b = map(str,[100,10,120])
c = map(str,[10,1,20])
d = map(str,[1,11,12])

n=75

nodeips = []
count = 0
for i in a:
	if count == n:
		break
	for j in b:
		if count == n:
			break
		for k in c:
			if count == n:
				break
			for l in d:
				if count == n:
					break
				nodeips.append(i + "." + j + "." + k + "." + l)
				count+=1

open("nodes.txt","w").write("\n".join(nodeips))