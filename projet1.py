def binarytoint(S):
	somme= 0
	for i in range(len(S)):
		somme*=2
		somme+=S[i]
	return somme
	
"""
1 bit for the sign
8 bits for the Exponent
23 bits for the mantissa
"""
def move(B, i):
	res= [0]*26
	for j in range(i, len(B)):
		res[j]=B[j-i]
	return res

def binarytofloat(R):
	sign= 1	
	if R[0]==1:
		sign= -1
	exponent= binarytoint(R[1:9])-127
	tmp= R[9:32]
	mantissa= 0
	for i in range(0, 23):
		mantissa+= tmp[i]*(2**(-1-i))
	return sign*(1+mantissa)*(2**exponent)

def dectobinary(dec):
	R= [0]*32
	if dec <0:
		R[0]= 1
		dec*=-1
	fl= int(dec)
	val= dec-fl

	tmpfl= [int(x) for x in "{0:b}".format(fl)]
	tmpval=[]
	
	if fl!=0:
		exponent= len(tmpfl)-1
		for i in range(23-exponent):
			val*=2
			if val>=1.0:
				tmpval.append(1)
				val-=1
			else:
				tmpval.append(0)
		for i in range(9, 8+len(tmpfl)):
			R[i]= tmpfl[i-8]
		for i in range(8+len(tmpfl), 32):
			R[i]= tmpval[i-8-len(tmpfl)]
	else:
		exponent= 0
		while exponent > -127:
			val*=2
			exponent-= 1
			if val>=1:
				break
		if exponent!=-127:
			val-=1
			for i in range(23):
				val*=2
				if val>=1.0:
					tmpval.append(1)
					val-=1
				else:
					tmpval.append(0)
		for i in range(9, 32):
			R[i]= tmpval[i-9]

	exp= [int(x) for x in "{0:08b}".format(exponent+127)]
	for i in range(1, 9):
		R[i]= exp[i-1]
	return R

def addone(S):
	for i in range(len(S)-1,-1, -1):
		if S[i]==0:
			S[i]=1
			break
		if S[i]==1:
			S[i]=0
def subone(S):
	for i in range(len(S)-1,-1, -1):
		if S[i]==1:
			S[i]=0
			break
		if S[i]==0:
			S[i]=1

def twoscomplement(C):
	tC=[1-x for x in C]
	addone(tC)
	return tC

def somme(A, B, signA, signB):
	s=[[0]+A, [0]+B]
	if signA == 1:
		s[0]= twoscomplement(s[0])
	if signB == 1:
		s[1]= twoscomplement(s[1])
	r= 0
	res= [0]*27
	for i in range(len(res)-1, -1, -1):
		a= s[0][i]+s[1][i]+r
		r= a//2
		res[i]= a%2
	signe= res[0]
	if signe==1:
		tmp= twoscomplement(res)
		return signe, tmp[1:27]
	return res[0], res[1:27]

class PFU:
	def Init(self):
		self.R= [[0]*32]*8
		self.A= [0]*26
		self.B= [0]*26
		self.C= [0]*26
		self.S= [0]*4

	def Load(self, dec):
		index=binarytoint(self.S)
		if index==8:
			raise ValueError("Stack Full")
		else:
			self.R[index]= dectobinary(dec)
			addone(self.S)

	def Store(self):
		index= binarytoint(self.S)
		if index==0:
			raise ValueError("Stack Empty")
		else:
			return(binarytofloat(self.R[index-1]))

	def Pop(self):
		index= binarytoint(self.S)
		if index == 0:
			raise ValueError("Stack Empty")
		else:
			self.R[index-1]= [0]*32	#not necessary
			subone(self.S)
	def Dup(self):
		index=binarytoint(self.S)
		if index==8:
			raise ValueError("Stack Full")
		elif index==0:
			raise ValueError("Stack Empty")
		else:
			for i in range(32):
				self.R[index]= self.R[index-1].copy()	#deepcopy
			addone(self.S)

	def Add(self):
		index= binarytoint(self.S)
		if index<2:
			raise ValueError("Stack Empty")
		x= binarytoint(self.R[index-1][1:9])
		y= binarytoint(self.R[index-2][1:9])
		if(x>y):
			X= self.R[index-1]
			Y= self.R[index-2]
		else:
			Y= self.R[index-1]
			X= self.R[index-2]
			x,y = y,x
		tmp= [0]*(x-y)+[1]+Y[9:32]
		arrondi=False
		if len(tmp)>25:
			if tmp[25]==1:
				arrondi=True
		self.A[0]= 0
		while(len(tmp)<25):
			tmp.append(0)
		for i in range(1, 26):
			self.A[i]= tmp[i-1]
		if arrondi:
			addone(self.A)
		
		self.B[0]= 0
		self.B[1]= 1
		for i in range(0, 23):
			self.B[i+2]= X[9+i]
		self.B[25]= 0

		signe, self.C= somme(self.A, self.B, Y[0], X[0])
		exponent=X[1:9]
		i= 0
		while(i<len(self.C) and self.C[i]!=1):
			i+=1
		if(i==len(self.C)):
			self.Pop()
			self.Pop()
			self.R[binarytoint(self.S)]= [0]*32
			addone(self.S)
		else:
			last= i+24
			if last<26:
				mantissa= self.C[i+1:last]
				if last!=26 and self.C[last]==1:
					addone(mantissa)
			if last>26:
				mantissa= self.C[i+1:26]
				while(len(mantissa)<23):
					mantissa.append(0)
			if(i>1):
				while(i>1):
					subone(exponent)
					i-=1
			elif(i==0):
				addone(exponent)
			self.Pop()
			self.Pop()
			self.R[binarytoint(self.S)]= [signe]+exponent+mantissa
			addone(self.S)
	def Opp(self):
		index=binarytoint(self.S)
		if index==0:
			raise ValueError("Stack Empty")
		self.R[index-1][0]= 1 -self.R[index-1][0]
	def Sub(self):
		index= binarytoint(self.S)
		if index<2:
			raise ValueError("Stack Empty")
		self.R[index-2][0]= 1 -self.R[index-2][0]
		self.Add()
	def Mul(self):
		index= binarytoint(self.S)
		if index<2:
			raise ValueError("Stack Empty")
		exponent= binarytoint(self.R[index-1][1:9])+binarytoint(self.R[index-2][1:9])-127
		signe= (self.R[index-1][0]+self.R[index-2][0])%2
		A=[0,1]+self.R[index-1][9:32]+[0]
		B=self.R[index-2][9:32]
		self.A= A.copy()
		for i in range(len(B)):
			if B[i]==1:
				self.B= move(A, i+1)
				print(self.A)
				print(self.B)
				signe, self.C= somme(self.A, self.B, 0, 0)
				self.A= self.C.copy()
		mantissa= self.C[1:24]
		if self.C[24]==1:
			addone(mantissa)
		self.Pop()
		self.Pop()
		self.R[binarytoint(self.S)]= [signe]+[int(x) for x in "{0:08b}".format(exponent)]+mantissa
		print(len(mantissa))
		print(len([int(x) for x in "{0:08b}".format(exponent)]))
		print(exponent)
		addone(self.S)

	def PrintReg(self):
		for i in range(8):
			r="0b"
			for k in range(len(self.R[i])):
				r+= str(self.R[i][k])
			print(r)
		"""
		for i in range(8):
			r=str(self.R[i][0])+" "
			for k in range(1, 9):
				r+=str(self.R[i][k])
			r+=" "
			for k in range(9, 32):
				r+=str(self.R[i][k])
			print("R"+str(i)+": "+r)
		a=""
		b=""
		c=""
		s=""
		for i in range(26):
			a+=str(self.A[i])
			b+=str(self.B[i])
			c+=str(self.C[i])
		for i in range(4):
			s+=str(self.S[i])
		print("A: "+ a)
		print("B: "+ b)
		print("C: "+ c)
		print("S: "+ s)
"""

