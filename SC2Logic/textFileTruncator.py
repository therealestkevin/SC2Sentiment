
f = open('ValidMapRotationCopy.txt').readlines()
print(f[0])
open('ValidMapRotationCopy.txt', 'w').writelines(f[1:])
