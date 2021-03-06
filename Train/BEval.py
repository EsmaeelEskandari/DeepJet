import sys, os
from argparse import ArgumentParser
                                                                                                                                  
# Options 
parser = ArgumentParser(description ='Script to run the training and evaluate it')
parser.add_argument("--multi", action='store_true', default=False, help="Binary or categorical crossentropy")
#parser.add_argument("-g", "--gpu", default=1, help="Run on gpu's (Need to be in deepjetLinux3_gpu env)", const=1)
parser.add_argument("-i", help="Training dataCollection.dc", default=None, metavar="FILE")
parser.add_argument("-t", help="Testing dataCollection.dc", default=None, metavar="FILE")
parser.add_argument("-d",  help="Training output dir", default=None, metavar="PATH")
parser.add_argument("-o",  help="Eval output dir", default=None, metavar="PATH")
parser.add_argument("--batch",  help="Batch size, default = 2000", default=2000, metavar="INT")
parser.add_argument("--epochs",  help="Epochs, default = 50", default=50, metavar="INT")
opts=parser.parse_args()

sampleDatasets_pf_cpf_sv = ["db","pf","cpf","sv"]
sampleDatasets_cpf_sv = ["db","cpf","sv"]
sampleDatasets_sv = ["db","sv"]

#select model and eval functions
from models.DeepJet_models_final import conv_model_final as trainingModel
from DeepJetCore.training.training_base import training_base
from funcs import loadModel, evaluate

inputDataset = sampleDatasets_pf_cpf_sv
trainDir = opts.d
inputTrainDataCollection = opts.t
inputTestDataCollection = opts.i
LoadModel = True
removedVars = None

if True:
    evalModel = loadModel(trainDir,inputTrainDataCollection,trainingModel,LoadModel,inputDataset,removedVars)
    evalDir = opts.o

    from DeepJetCore.DataCollection import DataCollection
    testd=DataCollection()
    testd.readFromFile(inputTestDataCollection)

    if os.path.isdir(evalDir):
        raise Exception('output directory: %s must not exists yet' %evalDir)
    else:
        os.mkdir(evalDir)

    df = evaluate(testd, evalModel, evalDir)
    
