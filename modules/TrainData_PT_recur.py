from TrainData import TrainData_fullTruth
from TrainData import TrainData,fileTimeOut

class TrainData_PT_recur_Test(TrainData_fullTruth):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        TrainData_fullTruth.__init__(self)
        
        
        self.addBranches(['jet_pt', 'jet_eta','nCpfcand','nNpfcand','nsv','npv'])
       
        self.addBranches([
                          'Cpfcan_ptrel', #not the same as btv ptrel!
                          #'Cpfcan_erel',
                          'Cpfcan_phirel',
                          'Cpfcan_etarel',
                          'Cpfcan_pt', 
                          'Cpfcan_puppiw',
#                          'Cpfcan_quality'
                              ],
                             25)
        
        
        self.addBranches(['Npfcan_ptrel', #not the same as btv ptrel!
                          #'Cpfcan_erel',
                          'Npfcan_phirel',
                          'Npfcan_etarel',
                          'Npfcan_pt', 
                          'Npfcan_puppiw',
 #                         'Npfcan_quality'
                              ],
                             25)
        
  
        
       
    def readFromRootFile(self,filename,TupleMeanStd, weighter):
        from preprocessing import MeanNormApply, MeanNormZeroPad, MeanNormZeroPadParticles
        import numpy
        from stopwatch import stopwatch
        
        sw=stopwatch()
        swall=stopwatch()
        
        import ROOT
        
        fileTimeOut(filename,120) #give eos a minute to recover
        rfile = ROOT.TFile(filename)
        tree = rfile.Get("deepntuplizer/tree")
        self.nsamples=tree.GetEntries()
        
        print('took ', sw.getAndReset(), ' seconds for getting tree entries')
        
        
        # split for convolutional network
        
        x_global = MeanNormZeroPad(filename,TupleMeanStd,
                                   [self.branches[0]],
                                   [self.branchcutoffs[0]],self.nsamples)
        
        x_cpf = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[1],
                                   self.branchcutoffs[1],self.nsamples)
        
        x_npf = MeanNormZeroPadParticles(filename,TupleMeanStd,
                                   self.branches[2],
                                   self.branchcutoffs[2],self.nsamples)
        
     
        
        print('took ', sw.getAndReset(), ' seconds for mean norm and zero padding (C module)')
        
        Tuple = self.readTreeFromRootToTuple(filename)
        
        if self.remove:
            notremoves=weighter.createNotRemoveIndices(Tuple)
            undef=Tuple['isUndefined']
            notremoves-=undef
            print('took ', sw.getAndReset(), ' to create remove indices')
        
        if self.weight:
            weights=weighter.getJetWeights(Tuple)
        elif self.remove:
            weights=notremoves
        else:
            print('neither remove nor weight')
            weights=numpy.empty(self.nsamples)
            weights.fill(1.)
        
        
        truthtuple =  Tuple[self.truthclasses]
        #print(self.truthclasses)
        alltruth=self.reduceTruth(truthtuple)
        NPfCands = Tuple[['nCpfcand','nNpfcand']]
     #   print(x_cpf.shape)
        allpf = numpy.concatenate((x_cpf,x_npf),axis=1)
      #  print ('and now ', allpf.shape)
     
        for i in range (0,allpf.shape[0]):
            myI = allpf[i][:]
     #       print( myI, ' this is the initial row, the shape is ',myI.shape)
            myI = myI[myI[:,0].argsort()]
      #      print( myI, ' this is the initial PT sorted row, the shape is ',myI.shape, ' ' , NPfCands[i][0], ' ' , NPfCands[i][1])
            
            nPF = int(NPfCands[i][0]+NPfCands[i][1])
            # 50 is hardcoded, it is the maximun number of candidates
            if (nPF>50): nPF=50
            myI = myI[0:nPF]
            zeroI = numpy.zeros(((50-nPF),5))
       #     print (myI.shape, ' ' , zeroI.shape)
            thisJet = numpy.concatenate((myI,zeroI))
        #    print ('concated' ,thisJet.shape )
        #    print( thisJet, ' this is the initial PT sorted row with zeros padded, the shape is ',thisJet.shape)
            allpf[i]= thisJet



        #print(alltruth.shape)
        if self.remove:
            print('remove')
            weights=weights[notremoves > 0]
            x_global=x_global[notremoves > 0]
            x_allpf=x_cpf[notremoves > 0]
           # x_npf=x_npf[notremoves > 0]
            alltruth=alltruth[notremoves > 0]
   
      
        
        newnsamp=x_global.shape[0]
        print('reduced content to ', int(float(newnsamp)/float(self.nsamples)*100),'%')
        self.nsamples = newnsamp
        
        print(x_global.shape,self.nsamples)

        self.w=[weights]
        self.x=[x_global,x_allpf]
        self.y=[alltruth]
        
