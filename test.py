import projet as sim
sim.Init()
prec = 1/3.0
sim.Load(prec)
encore = True
while encore:
	sim.PrintReg()
	sim.Load(prec)
	sim.Dup()
	sim.Mul()
	nouv = sim.Store()
	sim.Add()
	encore = (nouv != prec)
	prec = nouv
print("La série converge vers " + str(sim.Store()))
