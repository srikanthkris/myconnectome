

import os,sys
from alff import alff
import numpy
import ctypes
_old_rtld=sys.getdlopenflags()
sys.setdlopenflags(_old_rtld|ctypes.RTLD_GLOBAL)
import sklearn.decomposition
sys.setdlopenflags(_old_rtld)

network_names=['1 Default','2 Second Visual','3 Frontal-Parietal','4.5 First Visual (V1+)','5 First Dorsal Attention','6 Second Dorsal Attention','7 Ventral Attention/Language','8 Salience','9 Cingulo-opercular','10 Somatomotor','11.5 Frontal-Parietal Other','15 Parietal Episodic Retrieval','16 Parieto-Occipital']

datadir='/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/subdata_scrubbed'
outdir_modeig='/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/modeig_data'
outdir_bwmod='/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/bwmod_corr_data'
outdir_winmod='/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/winmod_corr_data'
outdir_alff='/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/module_alff'

#subcode='sub014'
subcodes=[i.strip() for i in open('/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/subcodes.txt').readlines()]

#subcodes=[subcodes[0]]
for subcode in subcodes:
    datafile=os.path.join(datadir,subcode+'.txt')
    datafile_unscrubbed=os.path.join(datadir.replace('_scrubbed',''),subcode+'.txt')
    assert os.path.exists(datafile)

    data=numpy.loadtxt(datafile)
    data_unscrubbed=numpy.loadtxt(datafile_unscrubbed)


    f=open('/corral-repl/utexas/poldracklab/data/selftracking/analyses/rsfmri_analyses/module_assignments.txt')
    roinum=[]
    hemis=[]
    parcelnum=[]
    modulenum=[]
    for l in f.readlines():
        l_s=l.strip().split()
        roinum.append(int(l_s[0]))
        hemis.append(l_s[1])
        parcelnum.append(int(l_s[2]))
        modulenum.append(float(l_s[3]))
    f.close()

    modulenum=numpy.array(modulenum)
    modules=numpy.unique(modulenum)
    modules=modules[modules>0]
    modctr=0
    modrois={}
    modeig=numpy.zeros((data.shape[0],len(modules)))
    modeig_unscrubbed=numpy.zeros((data_unscrubbed.shape[0],len(modules)))

    modmeancorr_within=numpy.zeros(len(modules))
                            
    for m in modules:
        modrois[m]=numpy.where(modulenum==m)[0]
        moddata=data[:,modrois[m]]
        moddata_unscrubbed=data_unscrubbed[:,modrois[m]]
        modcorr=numpy.corrcoef(moddata.T)
        modutr=numpy.triu_indices(modcorr.shape[0],1)
        modmeancorr_within[modctr]=numpy.mean(modcorr[modutr])
        pca=sklearn.decomposition.PCA(1)
        modeig[:,modctr]=pca.fit(moddata).transform(moddata)[:,0]
        modeig_unscrubbed[:,modctr]=pca.fit(moddata_unscrubbed).transform(moddata_unscrubbed)[:,0]
        modctr+=1
    a,modeig_falff=alff(modeig_unscrubbed,1.16)
    numpy.savetxt(os.path.join(outdir_alff,subcode+'.txt'),modeig_falff)
    numpy.savetxt(os.path.join(outdir_modeig,subcode+'.txt'),modeig)

    modeig_corr=numpy.corrcoef(modeig.T)
    modeig_corr_utr=modeig_corr[numpy.triu_indices(modeig_corr.shape[0],1)]
    
    numpy.savetxt(os.path.join(outdir_winmod,subcode+'.txt'),modmeancorr_within)
    numpy.savetxt(os.path.join(outdir_bwmod,subcode+'.txt'),modeig_corr_utr)


f=open('bwmod_corr_labels.txt','w')
utr=numpy.triu_indices(modeig_corr.shape[0],1)
for i in range(utr[0].shape[0]):
    f.write('%s\t%s\n'%(network_names[utr[0][i]],network_names[utr[1][i]]))
f.close()