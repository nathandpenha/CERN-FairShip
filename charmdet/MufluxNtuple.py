import ROOT,os,time,operator,subprocess
import rootUtils as ut
from argparse import ArgumentParser
PDG = ROOT.TDatabasePDG.Instance()
cuts = {}
cuts['muTrackMatchX']= 5.
cuts['muTrackMatchY']= 10.
zTarget = -370.       # start of target: -394.328, mean z for mu from Jpsi in MC = -375cm, for all muons: -353cm

cuts['zRPC1']  = 878.826706
cuts['xLRPC1'] =-97.69875
cuts['xRRPC1'] = 97.69875
cuts['yBRPC1'] =-41.46045
cuts['yTRPC1'] = 80.26905

sqrt2 = ROOT.TMath.Sqrt(2.)

Debug = False

host = os.uname()[1]
if host=="ubuntu":
    gPath = "/media/truf/disk2/home/truf/ShipSoft/ship-ubuntu-1710-32/"
elif host=='ship-ubuntu-1710-32':
    gPath = "/home/truf/muflux/"
else:
    gPath = "/home/truf/ship-ubuntu-1710-32/"

hData   = {}
hMC     = {}
h0      = {}
h = {}

parser = ArgumentParser()
parser.add_argument("-f", "--files", dest="listOfFiles", help="list of files comma separated", default=False)
parser.add_argument("-d", "--dir", dest="directory", help="directory", default=False)
parser.add_argument("-c", "--cmd", dest="command", help="command to execute", default="")
parser.add_argument("-p", "--path", dest="path", help="path to ntuple", default="")
parser.add_argument("-t", "--type", dest="MCType", help="version of MC", default="final") # other versions: "0", "multHits", "noDeadChannels", "withDeadChannels"
parser.add_argument("-A", "--with1GeV",  dest="with1GeV", help="1GeV MC",              default="False")
parser.add_argument("-C", "--withcharm", dest="withCharm", help="charm 1GeV MC",       default="False")
parser.add_argument("-B", "--with10GeV", dest="with10GeV", help="10GeV MC",            default="False")
parser.add_argument("-D", "--withData",  dest="withData", help="use default data set", default="False")
parser.add_argument("-J", "--withJpsi",  dest="withJpsi", help="use Jpsi data set",    default="False")
parser.add_argument("-8", "--withJpsiP8",  dest="withJpsiP8", help="use Jpsi pythia8 data set",    default="False")
parser.add_argument("-x", dest="ncpus", help="number of parallel jobs", default=False)
parser.add_argument("-s", dest="nseq", help="sequence of parallel job", default=0)
parser.add_argument("-r", dest="refit", help="use refitted ntuples", required=False, action="store_true")

options = parser.parse_args()

MCType    =  options.MCType
with1GeV  =  options.with1GeV  == "True"
withCharm =  options.withCharm == "True"
with10GeV =  options.with10GeV == "True"
withData  =  options.withData  == "True"
withJpsi  =  options.withJpsi  == "True"
withJpsiP8  =  options.withJpsiP8  == "True"
if options.path != "": gPath = options.path+'/'
fdir = options.directory

Nfiles = 0
if not fdir:
    Nfiles = 2000
    fdir   = "/eos/experiment/ship/user/truf/muflux-reco/RUN_8000_2403"
if not options.listOfFiles:
    sTreeData = ROOT.TChain('tmuflux')
    if withData:
     path = gPath + fdir
     countFiles=[]
     if fdir.find('eos')<0:
        for x in os.listdir(path):
            if x.find('ntuple-SPILL')<0: continue
            if x.find('refit')<0 and options.refit or x.find('refit')>0 and not options.refit: continue
            countFiles.append(path+'/'+x)
     else:
        temp = subprocess.check_output("xrdfs "+os.environ['EOSSHIP']+" ls "+fdir,shell=True)
        for x in temp.split('\n'):
            if x.find('ntuple-SPILL')<0: continue
            if x.find('refit')<0 and options.refit or x.find('refit')>0 and not options.refit: continue
            countFiles.append(os.environ["EOSSHIP"]+"/"+x)
     for x in countFiles:
        tmp = ROOT.TFile.Open(x)
        if not tmp.Get('tmuflux'):
           print "Problematic file:",x
           continue
        sTreeData.Add(x)
        Nfiles-=1
        if Nfiles==0: break

    sTreeMC = ROOT.TChain('tmuflux')

    if with1GeV:
        path = os.environ["EOSSHIP"]+"/eos/experiment/ship/user/truf/muflux-sim/1GeV-"+MCType+"/pythia8_Geant4_1.0_cXXXX_mu/"
        for k in range(0,20000,1000):
            for m in range(5):
                fname = path.replace('XXXX',str(k))+"ntuple-ship.conical.MuonBack-TGeant4_dig_RT-"+str(m)+".root"
                try:
                    test = ROOT.TFile.Open(fname)
                    if test.tmuflux.GetEntries()>0:   sTreeMC.Add(fname)
                except:
                    print "file not found",fname
                    continue
    if withCharm:
        fdir = fdir+'-charm'
        path = os.environ["EOSSHIP"]+"/eos/experiment/ship/user/truf/muflux-sim/1GeV-"+MCType+"/pythia8_Geant4_charm_0-19_1.0_mu/"
        for m in range(5):
            fname = path+"ntuple-ship.conical.MuonBack-TGeant4_dig_RT-"+str(m)+".root"
            try:
                test = ROOT.TFile.Open(fname)
                if test.tmuflux.GetEntries()>0:   sTreeMC.Add(fname)
            except:
                print "file not found",fname
                continue

    if with10GeV:
        path = os.environ["EOSSHIP"]+"/eos/experiment/ship/user/truf/muflux-sim/10GeV-"+MCType+"/pythia8_Geant4_10.0_withCharmandBeautyXXXX_mu/"
        for k in range(0,67000,1000):
            for m in range(10):
                fname = path.replace('XXXX',str(k))+"ntuple-ship.conical.MuonBack-TGeant4_dig_RT-"+str(m)+".root"
                try:
                    test = ROOT.TFile.Open(fname)
                    if test.tmuflux.GetEntries()>0:   sTreeMC.Add(fname)
                except:
                    print "file not found",fname
                    continue

    if withJpsi:
        path = os.environ["EOSSHIP"]+"/eos/experiment/ship/user/truf/muflux-sim/JpsiProduction/"
        for k in range(16):
            fname = "ntuple-pythia8_Geant4_"+str(k)+"_10.0_dig_RT.root"
            sTreeMC.Add(path+fname)
    if withJpsiP8:
        path = os.environ["EOSSHIP"]+"/eos/experiment/ship/user/truf/muflux-sim/JpsiProduction_P8/"
        for k in range(16):
            fname = "ntuple-pythia8_Geant4_"+str(k)+"_10.0_dig_RT.root"
            sTreeMC.Add(path+fname)
# small problem here when merging 1GeV and 10GeV, due to different p cutoff, px and pt cannot be used directly. 

# temp hack
#nfile = "/media/truf/disk2/home/truf/ShipSoft/ship-ubuntu-1710-48/simulation1GeV-withDeadChannels/pythia8_Geant4_1.0_c3000_mu/ship.conical.MuonBack-TGeant4_dig_RT-0.root"
#sTreeMC.Add("ntuple-ship.conical.MuonBack-TGeant4_dig_RT-0.root")
    case = {'MC':[sTreeMC,hMC,ROOT.kRed,'hist same'],'Data':[sTreeData,hData,ROOT.kBlue,'hist']}

s_SQRT2i = 1./ROOT.TMath.Sqrt( 2.0 )
sqrt2pi  = ROOT.TMath.Sqrt( 2*ROOT.TMath.Pi() )
cb=ROOT.TF1("cb","crystalball",0,6.)
def TwoCrystalBall(x,par):
   bw = par[0] # should be fixed
   cb.SetParameters(par[1]*bw,par[2],par[3],par[4],par[5])
   highMass = cb.Eval(x[0])
   cb.SetParameters(par[6]*bw,par[7],par[8],par[9],par[10])
   lowMass = cb.Eval(x[0])
   Psi2s = 0
   if abs(par[13])>0:
     cb.SetParameters(par[13]*bw,3.6871+par[2]- 3.0969,par[3],par[4],par[5])
     Psi2s = cb.Eval(x[0])
   Y = highMass + lowMass + par[11] + par[12]*x[0] + Psi2s
   return Y
def CrystalBall(x,par):
   bw = par[0] # should be fixed
   cb.SetParameters(par[1]*bw,par[2],par[3],par[4],par[5])
   highMass = cb.Eval(x[0])
   lowMass = par[6]*bw/(abs(par[8])*sqrt2pi)*ROOT.TMath.Exp(-0.5*( (x[0]-par[7])/par[8])**2)
   Y = highMass + lowMass + par[9] + par[10]*x[0]
   return Y

def IP(OnlyDraw = False):
    if not OnlyDraw:
        for c in case:
            sTree = case[c][0]
            h = case[c][1]
            ut.bookHist(h,'IP','transv distance to z-axis at target',100,0.,250.)
            ut.bookHist(h,'IPx','x distance to z-axis at target',100,-100.,100.)
            ut.bookHist(h,'IPmu','transv distance to z-axis at target',100,0.,250.)
            ut.bookHist(h,'IPxmu','x distance to z-axis at target',100,-100.,100.)
            ut.bookHist(h,'IPxy','xy distance to z-axis at target',100,-100.,100.,100,-100.,100.)
            for n in range(sTree.GetEntries()):
                rc = sTree.GetEvent(n)
                for t in range(sTree.nTr):
                    if sTree.GoodTrack[t]<0: continue
                    P = ROOT.TMath.Sqrt(sTree.Px[t]**2+sTree.Py[t]**2+sTree.Pz[t]**2)
                    if P<5. : continue
                    l = (sTree.z[t] - zTarget)/sTree.Pz[t]
                    x = sTree.x[t]+l*sTree.Px[t]
                    y = sTree.y[t]+l*sTree.Py[t]
                    r = ROOT.TMath.Sqrt(x*x+y*y)
                    rc = h['IP'].Fill(r)
                    rc = h['IPx'].Fill(x)
                    rc = h['IPxy'].Fill(x,y)
                    if abs(sTree.Delx[t])<cuts['muTrackMatchX']:
                        rc = h['IPxmu'].Fill(x)
                    if abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']:
                        rc = h['IPmu'].Fill(r)
    for proj in ['','x']:
        ut.bookCanvas(hData,'TIP'+proj,'IP'+proj,1600,1200,2,2)
        ic = 1
        for mu in ['','mu']:
            tc = hData['TIP'+proj].cd(ic)
            tc.SetLogy()
            hData['MCIP'+proj+mu]=hMC['IP'+proj+mu].Clone('MCIP'+proj+mu)
            hData['MCIP'+proj+mu].Scale( hData['IP'+proj+mu].GetEntries()/hMC['IP'+proj+mu].GetEntries())
            for k in [0,2]:
                if proj=='x':      hData['leg'+proj+str(ic+k)]=ROOT.TLegend(0.33,0.17,0.67,0.24)
                else:             hData['leg'+proj+str(ic+k)]=ROOT.TLegend(0.43,0.77,0.88,0.88)
            for c in case:
                x = ''
                if c=='MC': x=c
                for k in [0,2]:
                    tc = hData['TIP'+proj].cd(ic+k)
                    hData[x+'IP'+proj+mu].SetLineColor(case[c][2])
                    hData[x+'IP'+proj+mu].Draw(case[c][3])
                    hData[x+'IP'+proj+mu].SetLineColor(case[c][2])
                    hData[x+'IP'+proj+mu].Draw(case[c][3])
                    mean = hData[x+'IP'+proj+mu].GetMean()
                    rms = hData[x+'IP'+proj+mu].GetRMS()
                    hData[x+'IP'+proj+mu].SetStats(0)
                    txt = "%s  Mean=%5.2F  Std Dev=%5.2F"%(c,mean,rms)
                    rc = hData['leg'+proj+str(ic+k)].AddEntry(hData[x+'IP'+proj+mu],txt,'PL')
            for k in [0,2]:
                tc = hData['TIP'+proj].cd(ic+k)
                hData['leg'+proj+str(ic+k)].Draw()
            ic+=1
        myPrint(hData['TIP'+proj],'IP'+proj)

def RPCextrap(OnlyDraw = False,pxMin=3.,pMin=10.,station1Occ=100,station1OccLow=0):
    if not OnlyDraw:
        for c in case:
            sTree = case[c][0]
            h = case[c][1]
            for l in range(1,7):
                if l<5:  txt ="x station "+str(l)+" Occupancy"
                if l==5: txt ="u station 1 Occupancy"
                if l==6: txt ="v station 2 Occupancy"
                ut.bookHist(h,'stationOcc'+str(l),txt,50,-0.5,49.5)
            ut.bookHist(h,'upStreamOcc',"station 1&2",200,-0.5,199.5)
            ut.bookHist(h,'upStreamOccwithTrack',"station 1&2",200,-0.5,199.5)
            ut.bookHist(h,'upStreamOccMuonTagged',"station 1&2",200,-0.5,199.5)
            ut.bookHist(h,'xy',   'xy at RPC',100,-150.,150.,100,-150.,150.)
            ut.bookHist(h,'xyIn', 'xy at RPC in acceptance',100,-150.,150.,100,-150.,150.)
            ut.bookHist(h,'xyInX','xy at RPC in acceptance',100,-150.,150.,100,-150.,150.)
            ut.bookHist(h,'xyTagged', 'xy at RPC for muons',100,-150.,150.,100,-150.,150.)
            ut.bookHist(h,'xyTaggedX','xy at RPC for muons',100,-150.,150.,100,-150.,150.)
            for x in ['-Tagged','-nonTagged']:
                ut.bookHist(h,'chi2Dof'+x,'chi2 per DoF',100,0.,10.)
                ut.bookHist(h,'p/pt'+x,'momentum vs Pt (GeV);#it{p} [GeV/c]; #it{p}_{T} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,'pz/Abspx'+x,'Pz vs Px (GeV);#it{p} [GeV/c]; #it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
            for n in range(sTree.GetEntries()):
                rc = sTree.GetEvent(n)
                upStreamOcc = sTree.stationOcc[1]+sTree.stationOcc[5]+sTree.stationOcc[2]+sTree.stationOcc[6]
                rc = h['upStreamOcc'].Fill(upStreamOcc)
                if sTree.nTr>0:
                    for l in range(1,7):
                        rc = h['stationOcc'+str(l)].Fill(sTree.stationOcc[l])
                        if sTree.stationOcc[l]>40: print l,sTree.stationOcc[l],sTree.evtnr,sTree.spillnrA,sTree.spillnrB,sTree.spillnrC ,sTree.GetCurrentFile().GetName()
                    rc = h['upStreamOccwithTrack'].Fill(upStreamOcc)
                if sTree.stationOcc[1] > station1Occ or sTree.stationOcc[1] < station1OccLow: continue
                for t in range(sTree.nTr):
                    if sTree.GoodTrack[t]<0: continue
                    Pvec = ROOT.TVector3(sTree.Px[t],sTree.Py[t],sTree.Pz[t])
                    P = Pvec.Mag()
                    if abs(sTree.Px[t])<pxMin : continue
                    if P<pMin                 : continue
                    rc = h['xy'].Fill(sTree.RPCx[t],sTree.RPCy[t])
                    if sTree.RPCx[t]>cuts['xLRPC1'] and sTree.RPCx[t]<cuts['xRRPC1']: 
                        rc = h['xyInX'].Fill(sTree.RPCx[t],sTree.RPCy[t])
                        if abs(sTree.Delx[t])<cuts['muTrackMatchX']:
                            rc = h['xyTaggedX'].Fill(sTree.RPCx[t],sTree.RPCy[t])
                            rc = h['pz/Abspx-Tagged'].Fill(Pvec[2],Pvec[0])
                        else:
                            rc = h['pz/Abspx-nonTagged'].Fill(Pvec[2],Pvec[0])
                        if sTree.RPCy[t]>cuts['yBRPC1'] and sTree.RPCy[t]<cuts['yTRPC1']:
                            rc = h['xyIn'].Fill(sTree.RPCx[t],sTree.RPCy[t])
                        if abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']:
                            rc = h['xyTagged'].Fill(sTree.RPCx[t],sTree.RPCy[t])
                            rc = h['chi2Dof-Tagged'].Fill(sTree.Chi2[t])
                            rc = h['p/pt-Tagged'].Fill(P,Pvec.Pt())
                            rc = h['upStreamOccMuonTagged']
                        else:
                            rc = h['chi2Dof-nonTagged'].Fill(sTree.Chi2[t])
                            rc = h['p/pt-nonTagged'].Fill(P,Pvec.Pt())
    effDataIn = hData['xyTagged'].GetEntries()/hData['xyIn'].GetEntries()*100.
    effMCIn   = hMC['xyTagged'].GetEntries()/hMC['xyIn'].GetEntries()*100.
    effData = hData['xyTagged'].GetEntries()/hData['xy'].GetEntries()*100.
    effMC   = hMC['xyTagged'].GetEntries()/hMC['xy'].GetEntries()*100.
    print "eff xy data: %5.2F (%5.2F)  MC: %5.2F (%5.2F)"%(effDataIn,effData,effMCIn,effMC)
    effDataIn = hData['xyTaggedX'].GetEntries()/hData['xyInX'].GetEntries()*100.
    effMCIn   = hMC['xyTaggedX'].GetEntries()/hMC['xyInX'].GetEntries()*100.
    effData = hData['xyTaggedX'].GetEntries()/hData['xy'].GetEntries()*100.
    effMC   = hMC['xyTaggedX'].GetEntries()/hMC['xy'].GetEntries()*100.
    print "eff x  data: %5.2F (%5.2F)  MC: %5.2F (%5.2F)"%(effDataIn,effData,effMCIn,effMC)
    keys = ['upStreamOcc','upStreamOccwithTrack','upStreamOccMuonTagged']
    for l in range(1,7):
        keys.append('stationOcc'+str(l))
    for key in keys:
        hData['MC'+key] = hMC[key].Clone('MC'+key)
        hData['MC'+key].SetLineColor(ROOT.kRed)
        if key.find('upStreamOcc')==0:
            norm = (hMC[key].GetBinContent(15))/(hData[key].GetBinContent(15))
        else:  
            norm = (hMC[key].GetBinContent(4)+hMC[key].GetBinContent(5))/(hData[key].GetBinContent(4)+hData[key].GetBinContent(5))
        hData['MC'+key].Scale(1./norm)

def MCRPCextrap(OnlyDraw = False):
    if not OnlyDraw:
        c = 'MC'
        sTree = case[c][0]
        h = case[c][1]
        ut.bookHist(h,'P','true momentum muReconstructible;[GeV/c]',400,0.,400.)
        ut.bookHist(h,'Pt','true momentum muReconstructible;[GeV/c]',80,0.,4.)
        ut.bookHist(h,'Px','true momentum muReconstructible;[GeV/c]',80,0.,4.)
        ut.bookHist(h,'Preco1','true momentum reco track matched;[GeV/c]',400,0.,400.)
        ut.bookHist(h,'Ptreco1','true momentum reco track matched;[GeV/c]',100,0.,10.)
        ut.bookHist(h,'Pxreco1','true momentum reco track matched;[GeV/c]',100,0.,10.)
        ut.bookHist(h,'Preco2','true momentum reco track matched, good track p/pt;[GeV/c]',400,0.,400.)
        ut.bookHist(h,'Preco3','true momentum reco track matched, good track pz/px;[GeV/c]',400,0.,400.)
        for x in ['','mu']:
            ut.bookHist(h,'delP'+x,'true momentum - reco vs true P;[GeV/c]',100,-10.,10.,80,0.,400.)
            ut.bookHist(h,'delPx'+x,'true Px - reco vs true P;[GeV/c]',100,-2.,2.,80,0.,400.)
            ut.bookHist(h,'delPt'+x,'true Pt - reco vs true P;[GeV/c]',100,-2.,2.,80,0.,400.)
        for n in range(sTree.GetEntries()):
            rc = sTree.GetEvent(n)
            if sTree.MCRecoDT.size() != 1: continue # look at simple events for the moment 
            for m in sTree.MCRecoRPC:
                i = -1
                for d in sTree.MCRecoDT:
                    i+=1
                    if m!=d: continue  # require same MCTrack
                    P  = ROOT.TVector3(sTree.MCRecoDTpx[i],sTree.MCRecoDTpy[i],sTree.MCRecoDTpz[i])
                    rc = h['P'].Fill(P.Mag())
                    rc = h['Px'].Fill(abs(P.X()))
                    rc = h['Pt'].Fill(P.Pt())
                    for t in range(sTree.nTr):
                        if sTree.nTr>1: continue
                        Preco  = ROOT.TVector3(sTree.Px[t],sTree.Py[t],sTree.Pz[t])
                        delP = P.Mag()-Preco.Mag()
                        delPx = P.X()-Preco.X()
                        delPt = P.Pt()-Preco.Pt()
                        rc = h['delP'].Fill(delP,P.Mag())
                        rc = h['delPx'].Fill(delPx,P.Mag())
                        rc = h['delPt'].Fill(delPt,P.Mag())
                        if abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']:
                            rc = h['Preco1'].Fill(P.Mag())
                            rc = h['Pxreco1'].Fill(abs(P.X()))
                            rc = h['Ptreco1'].Fill(P.Pt())
                            rc = h['delPmu'].Fill(delP,P.Mag())
                            rc = h['delPxmu'].Fill(delPx,P.Mag())
                            rc = h['delPtmu'].Fill(delPt,P.Mag())
        for x in ['P','Pt','Px']:
            h['tagEff'+x]=ROOT.TEfficiency(h[x+'reco1'],h[x])

def makeProjectionRMS(h,hname,proj):
    pname = hname+proj
    if not proj.find('x')<0: h[pname] = h[hname].ProjectionX(pname)
    else:                    h[pname] = h[hname].ProjectionY(pname)
    for n in range(1,h[pname].GetNbinsX()+1):
        if not proj.find('x')<0: temp = h[hname].ProjectionY('p'+str(n),n,n)
        else:                    temp = h[hname].ProjectionX('p'+str(n),n,n)
        RMS = temp.GetRMS()
        h[pname].SetBinContent(n,RMS)

def clones(OnlyDraw = False,noClones=False):
    if not OnlyDraw:
        for c in case:
            sTree = case[c][0]
            h = case[c][1]
            ut.bookHist(h,'cos alpha','cosine of angle between two tracks;cos[#alpha]',10000,0.95,1.01)
            for n in range(sTree.GetEntries()):
                rc = sTree.GetEvent(n)
                for a in range(sTree.nTr-1):
                    if sTree.GoodTrack[a]<0: continue
                    if noClones and sTree.GoodTrack[a]>1000: continue
                    A = ROOT.TVector3(sTree.Px[a],sTree.Py[a],sTree.Pz[a])
                    for b in range(a,sTree.nTr):
                        if sTree.GoodTrack[b]<0: continue
                        if noClones and sTree.GoodTrack[b]>1000: continue
                        if sTree.Sign[b]*sTree.Sign[a]>0: continue
                        B = ROOT.TVector3(sTree.Px[b],sTree.Py[b],sTree.Pz[b])
                        rc = h['cos alpha'].Fill(A.Dot(B)/(A.Mag()*B.Mag()))
    hData['cos alpha'].GetXaxis().SetRangeUser(0.999,1.0001)
    hMC['cos alpha'].SetLineColor(ROOT.kRed)
    hData['MCcos alpha'] = hMC['cos alpha'].Clone('MCcos alpha')
    hData['MCcos alpha'].Scale(hData['cos alpha'].GetEntries()/hMC['cos alpha'].GetEntries())
    hData['MCcos alpha'].SetStats(0)
    hData['cos alpha'].SetStats(0)
    ut.bookCanvas(hData,'clones','Clones',1200,900,1,1)
    hData['cos alpha'].Draw()
    hData['MCcos alpha'].Draw('same')
    hData['leg']=ROOT.TLegend(0.24,0.50,0.54,0.61)
    rc = hData['leg'].AddEntry(hData["cos alpha"],"Data",'PL')
    rc = hData['leg'].AddEntry(hData["MCcos alpha"],"MC",'PL')
    hData['leg'].Draw()
    lmax = hData['cos alpha'].GetMaximum()
    h['lcut'] =  ROOT.TArrow(0.99995,0.,0.99995,lmax*0.2,0.05,"<")
    h['lcut'].SetLineColor(ROOT.kMagenta)
    h['lcut'].SetLineWidth(2)
    h['lcut'].Draw()
    myPrint(hData['clones'],'MC-Comparison-Clones') 
    ff = ROOT.TFile('Clones.root','recreate')
    hData['clones'].Write('Clones.root')

def tails(OnlyDraw = False):
    if not OnlyDraw:
        for c in case:
            sTree = case[c][0]
            h = case[c][1]
            ut.bookHist(h,'momentum','momentum',1000,0.0,1000.)
            for n in range(sTree.GetEntries()):
                rc = sTree.GetEvent(n)
                for t in range(sTree.nTr):
                    if sTree.GoodTrack[t]<0: continue
                    P = ROOT.TVector3(sTree.Px[t],sTree.Py[t],sTree.Pz[t])
                    rc = h['momentum'].Fill(P.Mag())
        hData['MCmomentum'] = hMC['momentum'].Clone('MCmomentum')
        norm = hData['momentum'].Integral(5,100)/hMC['momentum'].Integral(5,100)
        hData['MCmomentum'].SetLineColor(ROOT.kRed)
        hData['MCmomentum'].Scale(norm)

deadChannels4MC = [10112001,11112012,20112003,30002042,30012026,30102021,30102025,30112013,30112018,40012014]

def reconstructible(OnlyDraw = False):
    if not OnlyDraw:
        #for c in case:
        c = 'MC'
        sTree = case[c][0]
        h = case[c][1]
        ut.bookHist(h,'reconstructibleP',"reconstructible P",400,0.0,400.)
        ut.bookHist(h,'reconstructedP',"reconstructed P",400,0.0,400.)
        for x in ['','_mu']:
            ut.bookHist(h,'delPzR'+x,"reconstructed Pz - true / true",1000,-5.,5.)
            ut.bookHist(h,'delPtR'+x,"reconstructed Pt - true / true",1000,-5.,5.)
            ut.bookHist(h,'delPz'+x,"reconstructed Pz - true ",1000,-50.,50.)
            ut.bookHist(h,'delPx'+x,"reconstructed Px - true ",1000,-1.,1.)
            ut.bookHist(h,'delPt'+x,"reconstructed Pt - true ",1000,-1.,1.)
        ut.bookHist(h,'upStreamOcc',"station 1&2",200,-0.5,199.5)
        ut.bookHist(h,'upStreamOcc-nonReco',"station 1&2",200,-0.5,199.5)
        ut.bookHist(h,'upStreamOcc-badRecoP',"station 1&2",200,-0.5,199.5)
        ut.bookHist(h,'upStreamOcc-badRecoPx',"station 1&2",200,-0.5,199.5)
        ut.bookHist(h,'upStreamOcc-reconstructible',"station 1&2",200,-0.5,199.5)
        ut.bookHist(h,'stationOcc1x1u',"station 1",50,-0.5,49.5,50,-0.5,49.5)
        ut.bookHist(h,'stationOcc2x2v',"station 2",50,-0.5,49.5,50,-0.5,49.5)
        for n in range(sTree.GetEntries()):
            rc = sTree.GetEvent(n)
            rc = h['stationOcc1x1u'].Fill(sTree.stationOcc[1],sTree.stationOcc[5])
            rc = h['stationOcc2x2v'].Fill(sTree.stationOcc[2],sTree.stationOcc[6])
            upStreamOcc = sTree.stationOcc[1]+sTree.stationOcc[5]+sTree.stationOcc[2]+sTree.stationOcc[6]
            rc = h['upStreamOcc'].Fill(upStreamOcc)
            if sTree.MCRecoDT.size()==1:
                rc = h['upStreamOcc-reconstructible'].Fill(upStreamOcc)
                m = 0
                P  = ROOT.TVector3(sTree.MCRecoDTpx[m],sTree.MCRecoDTpy[m],sTree.MCRecoDTpz[m])
                rc = h['reconstructibleP'].Fill(P.Mag())
                if sTree.nTr==1: 
                    rc = h['reconstructedP'].Fill(P.Mag())
                    Preco  = ROOT.TVector3(sTree.Px[0],sTree.Py[0],sTree.Pz[0])
                    delPz  = (sTree.Pz[0]-sTree.MCRecoDTpz[0])
                    delPx = (sTree.Px[0]-sTree.MCRecoDTpx[0])
                    delPzR = (sTree.Pz[0]-sTree.MCRecoDTpz[0])/sTree.MCRecoDTpz[0]
                    rc = h['delPz'].Fill(delPz)
                    rc = h['delPx'].Fill(delPx)
                    rc = h['delPzR'].Fill(delPzR)
                    delPt  = Preco.Pt()-P.Pt()
                    delPtR = (Preco.Pt()-P.Pt()/P.Pt())
                    rc = h['delPt'].Fill(delPt)
                    rc = h['delPtR'].Fill(delPtR)
                    if abs(sTree.Delx[0])<cuts['muTrackMatchX'] and abs(sTree.Dely[0])<cuts['muTrackMatchY']:
                        x='_mu'
                        rc = h['delPz'+x].Fill(delPz)
                        rc = h['delPx'+x].Fill(delPx)
                        rc = h['delPzR'+x].Fill(delPzR)
                        rc = h['delPt'+x].Fill(delPt)
                        rc = h['delPtR'+x].Fill(delPtR)
                    if abs(delPz)>10.: rc = h['upStreamOcc-badRecoP'].Fill(upStreamOcc)
                    if abs(delPx)>2.: rc = h['upStreamOcc-badRecoPx'].Fill(upStreamOcc)
#        if abs(delPt)>2. :                                        print "bad reco pt",n,upStreamOcc,sTree.MCRecoDT.size(),delPt,P.Pt()
#        if abs( abs(sTree.Px[0])-abs(sTree.MCRecoDTpx[0]))>2. :   print "bad reco px",n,upStreamOcc,sTree.MCRecoDT.size(),delPx,sTree.MCRecoDTpx[0]
                if sTree.nTr <1:
                    rc = h['upStreamOcc-nonReco'].Fill(upStreamOcc)
                    # print "non reco",n,upStreamOcc,sTree.MCRecoDT.size(),sTree.MCRecoDTpx[0],sTree.MCRecoDTpy[0],sTree.MCRecoDTpz[0]
        h['ineff-upStreamOcc-reconstructible']=ROOT.TEfficiency(h['upStreamOcc-nonReco'],h['upStreamOcc-reconstructible'])
        h['effP']=ROOT.TEfficiency(h['reconstructedP'],h['reconstructibleP'])
from array import array
def RecoEffFunOfOcc(OnlyDraw = False,Nevents = -1):
    pMin = 5.
    if not OnlyDraw:
        c = 'Data'
        sTree = case[c][0]
        h = case[c][1]
        if Nevents<0: Nevents=sTree.GetEntries()
        ut.bookHist(h,'Occ','N',50,0.,200.)
        ut.bookHist(h,'OccAllEvents','N',50,0.,200.)
        for n in range(Nevents):
            rc = sTree.GetEvent(n)
            upStreamOcc = sTree.stationOcc[1]+sTree.stationOcc[5]+sTree.stationOcc[2]+sTree.stationOcc[6]
            if sTree.nTr>0: rc = h['OccAllEvents'].Fill(upStreamOcc)
            for t in range(sTree.nTr):
                if sTree.GoodTrack[t]<0: continue
                Pvec = ROOT.TVector3(sTree.Px[t],sTree.Py[t],sTree.Pz[t])
                P = Pvec.Mag()
                if P<pMin                 : continue
                if abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']:
                    rc = h['Occ'].Fill(upStreamOcc)
        ut.writeHists(h,'histos-DataOcc.root')
        c = 'MC'
        sTree = case[c][0]
        h = case[c][1]
# variable bin size
        paxis = []
        xv = 0.
        for x in range(100): 
            paxis.append(xv)
            xv+=1.
        for x in range(20): 
            paxis.append(xv)
            xv+=5.
        for x in range(5): 
            paxis.append(xv)
            xv+=50.
        dpaxis = array('d',paxis)
        ut.bookHist(h,'Ptrue', 'true momentum muReconstructible;[GeV/c];N',500,0.,500.)
        ut.bookHist(h,'P', 'true momentum muReconstructible;[GeV/c];N',dpaxis,50,0.,200.)
        ut.bookHist(h,'Pz','true momentum muReconstructible;[GeV/c];N',dpaxis,50,0.,200.)
        ut.bookHist(h,'Preco', 'true momentum reconstructed;[GeV/c];N',dpaxis,50,0.,200.)
        ut.bookHist(h,'Pfailed', 'true momentum no reco;[GeV/c];N',dpaxis,50,0.,200.)
        ut.bookHist(h,'Pzreco','true momentum reconstructed;[GeV/c];N',dpaxis,50,0.,200.)
        ut.bookHist(h,'Pt','true momentum muReconstructible;[GeV/c];N',80,0.,4.,50,0.,200.)
        ut.bookHist(h,'Px','true momentum muReconstructible;[GeV/c];N',80,0.,4.,50,0.,200.)
        ut.bookHist(h,'Ptreco','true momentum reconstructed;[GeV/c];N',80,0.,4.,50,0.,200.)
        ut.bookHist(h,'Pxreco','true momentum reconstructed;[GeV/c];N',80,0.,4.,50,0.,200.)
        ut.bookHist(h,'delx/y','delx vs dely;cm;cm',100,0.,20,100,0.,50.)
        ut.bookHist(h,'OccAllEvents','N',50,0.,200.)
        for x in ['','_mu']:
            ut.bookHist(h,'delP'+x,"reconstructed P - true ",1000,-50.,50.)
            ut.bookHist(h,'delPt'+x,"reconstructed Pt - true ",1000,-1.,1.)
            ut.bookHist(h,'delPx'+x,"reconstructed Px - true ",1000,-1.,1.)
        for n in range(sTree.GetEntries()):
            rc = sTree.GetEvent(n)
            upStreamOcc = sTree.stationOcc[1]+sTree.stationOcc[5]+sTree.stationOcc[2]+sTree.stationOcc[6]
            if sTree.nTr>0: rc = h['OccAllEvents'].Fill(upStreamOcc)
            if sTree.MCRecoDT.size() != 1: continue # look at 1 Track events for the moment 
            # require reco RPC tracks, otherwise cannot compare to zero field data which starts with RPC tracks
            if sTree.nRPC%10 == 0 or sTree.nRPC/10 == 0 : continue
            # starting with reconstructible RPC track, check that same MCTrack is reconstructible in DT
            for m in sTree.MCRecoRPC:
                i = -1
                for d in sTree.MCRecoDT:
                    i+=1
                    if m!=d: continue  # require same MCTrack
                    P  = ROOT.TVector3(sTree.MCRecoDTpx[i],sTree.MCRecoDTpy[i],sTree.MCRecoDTpz[i])
                    rc = h['P'].Fill(P.Mag(),upStreamOcc)
                    rc = h['Ptrue'].Fill(P.Mag())
                    rc = h['Px'].Fill(abs(P.X()),upStreamOcc)
                    rc = h['Pz'].Fill(P.Z(),upStreamOcc)
                    rc = h['Pt'].Fill(P.Pt(),upStreamOcc)
                    found = False  # avoid double counting
                    if sTree.nTr<1:
                        rc = h['Pfailed'].Fill(P.Mag(),upStreamOcc)
                        if Debug: print "no reco track  event nr ",n,sTree.GetCurrentFile().GetName(),P.Mag(),upStreamOcc
                    for t in range(sTree.nTr):
                        Preco  = ROOT.TVector3(sTree.Px[t],sTree.Py[t],sTree.Pz[t])
                        delP   = P.Mag() - Preco.Mag()
                        delPx  = P.X() -   Preco.X()
                        delPt  = P.Pt() -  Preco.Pt()
                        rc = h['delP'].Fill(delP,P.Mag())
                        rc = h['delPx'].Fill(delPx,P.Mag())
                        rc = h['delPt'].Fill(delPt,P.Mag())
                        rc = h['delx/y'].Fill(sTree.Delx[t],sTree.Dely[t])
                        # if there is no muon track in event, sTree.Delx[t] = 9999. and sTree.Dely[t] = 9999.
                        if Debug and (sTree.Delx[t]>9998 or sTree.Dely[t] > 9998): print "no reco RPC track in RPC reconstructible event" 
                        if abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']:
                            if found: continue
                            rc = h['delP_mu'].Fill(delP,P.Mag())
                            rc = h['delPx_mu'].Fill(delPx,P.Mag())
                            rc = h['delPt_mu'].Fill(delPt,P.Mag())
                            rc = h['Preco'].Fill(P.Mag(),upStreamOcc)
                            rc = h['Pxreco'].Fill(abs(P.X()),upStreamOcc)
                            rc = h['Pzreco'].Fill(P.Z(),upStreamOcc)
                            rc = h['Ptreco'].Fill(P.Pt(),upStreamOcc)
                            found = True
                    if not found and sTree.nTr==1 and Debug:
                        dec = abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']
                        print "event nr ",n,P.Mag(),sTree.nTr,upStreamOcc,abs(sTree.Delx[t]),abs(sTree.Dely[t]),dec
        ut.writeHists(h,'histos-MCRecoEffFunOfOcc'+'-'+fdir+'.root')
        return
    if not hMC.has_key('P'): 
        ut.readHists(hMC,'histos-MCRecoEffFunOfOcc.root')
    if not hData.has_key('Occ'): 
        ut.readHists(hData,'histos-DataOcc.root')
        hData['Occ'].Scale(1./hData['Occ'].GetMaximum())
    # now take occupancy from zero field
    if not hMC.has_key("hDTEff"):
        hMC["hDTEff"] = {}
        hDTEff=hMC["hDTEff"]
        interestingHistos=[]
        for k in range(1,5):
            interestingHistos.append("upStreamOccWithTrack"+str(k))
            interestingHistos.append("upStreamOcc"+str(k))
        ut.readHists(hDTEff,'DTEff.root',interestingHistos)
        hDTEff['upStreamOccWithTrack']=hDTEff['upStreamOccWithTrack1'].Clone('upStreamOccWithTrack')
        hDTEff['upStreamOccWithTrack'].Add(hDTEff['upStreamOccWithTrack2'])
        hDTEff['upStreamOccWithTrack'].Add(hDTEff['upStreamOccWithTrack3'])
        hDTEff['upStreamOccWithTrack'].Add(hDTEff['upStreamOccWithTrack4'])

        hDTEff['upStreamOcc']=hDTEff['upStreamOcc1'].Clone('upStreamOcc')
        hDTEff['upStreamOcc'].Add(hDTEff['upStreamOcc2'])
        hDTEff['upStreamOcc'].Add(hDTEff['upStreamOcc3'])
        hDTEff['upStreamOcc'].Add(hDTEff['upStreamOcc4'])

        hMC['zeroFieldOcc']=hDTEff['upStreamOccWithTrack'].Rebin(4,'zeroFieldOcc')
        hMC['zeroFieldOcc'].Scale(1./hMC['zeroFieldOcc'].GetMaximum())
        hMC['zeroFieldOcc'].SetLineColor(ROOT.kGreen)
        hMC['zeroFieldOcc'].SetMarkerColor(ROOT.kGreen)
        hMC['zeroFieldOcc'].SetMarkerStyle(24)
    h = hMC
    tmp = h['P'].ProjectionY()
    T = ROOT.TLatex()
    T.SetTextColor(ROOT.kMagenta)
    ut.bookCanvas(h,'upStreamOcc','upstream occupancy',900,600,1,1)
    tc = hMC['upStreamOcc'].cd(1)
    tc.SetLogy(1)
    hData['OccAllEvents'].SetTitle('upstream occupancy;Number of hits;arbitrary scale')
    hData['OccAllEvents'].SetStats(0)
    hData['OccAllEvents'].Draw()
    hmax = hData['OccAllEvents'].GetMaximum()
    hMC['OccAllEvents'].SetLineColor(ROOT.kMagenta)
    hMC['OccAllEvents_scaled']=hMC['OccAllEvents'].Clone('OccAllEvents_scaled')
    hMC['OccAllEvents_scaled'].Scale(hmax/hMC['OccAllEvents'].GetMaximum())
    hMC['OccAllEvents_scaled'].SetStats(0)
    hMC['OccAllEvents_scaled'].Draw('same hist')
    myPrint(h['upStreamOcc'],'upstreamOcc')
    variables = ['P','Px','Pz','Pt']
    fun = {}
    for var in variables:
        xmin = tmp.GetBinLowEdge(1)
        xmax = tmp.GetBinLowEdge(tmp.GetNbinsX())+tmp.GetBinWidth(tmp.GetNbinsX())
        ut.bookHist(h,'effFun'+var,'eff as function of occupancy '+var,tmp.GetNbinsX(),xmin,xmax)
        ut.bookCanvas(h,'eff'+var,'Efficiencies '+var,1200,900,5,4)
        if var=='P' or var=='Pz': fun[var] = ROOT.TF1('pol0'+var,'[0]',12.,200.)
        else:                     fun[var] = ROOT.TF1('pol0'+var,'[0]',0.,2.5)
        j=1
        for o in range(1,tmp.GetNbinsX()+1):
            h[var+'eff'+str(o)] =  ROOT.TEfficiency(h[var+'reco'].ProjectionX(var+'reco'+str(o),o,o),h[var].ProjectionX(var+str(o),o,o))
            if j<20:
                tc = h['eff'+var].cd(j)
                j+=1
                h[var+'eff'+str(o)].Draw()
                tc.Update()
                if h[var+'eff'+str(o)].GetTotalHistogram().GetEntries() == 0: continue
                g = h[var+'eff'+str(o)].GetPaintedGraph()
                x = h[var+'eff'+str(o)].GetEfficiency(20) # just to have a decent scale
                g.SetMinimum(x*0.8)
                g.SetMaximum(1.02)
                if var=='P' or var=='Pz':
                    g.GetXaxis().SetRangeUser(0.,200.)
                t = str(int(tmp.GetBinLowEdge(o)))+"-"+str(int(tmp.GetBinLowEdge(o)+tmp.GetBinWidth(o)))
                rc = T.DrawLatexNDC(0.5,0.9,t)
                rc = h[var+'eff'+str(o)].Fit(fun[var],'SRQ')
                fitResult = rc.Get()
                if fitResult:
                    eff = fitResult.Parameter(0)
                    rc = T.DrawLatexNDC(0.2,0.9,"eff=%5.2F%%"%(eff*100.))
                    h['effFun'+var].SetBinContent(o,eff)
                tc.Update()
        myPrint(h['eff'+var],'MCEfficienciesOcc'+var)
    ut.bookCanvas(h,'eff final','Efficiencies ',1200,900,2,2)
    j=1
    h['occ']=hMC['OccAllEvents'].Clone('occ') # want to have MC efficiency for all events, not only 1 track
    h['occ'].Scale(1./h['occ'].GetMaximum())
    h['occ'].SetLineColor(ROOT.kMagenta)
    for var in variables:
        h['eff final'].cd(j)
        j+=1
        h['effFun'+var].SetStats(0)
        h['effFun'+var].SetMarkerStyle(20)
        h['effFun'+var].SetMarkerColor(h['effFun'+var].GetLineColor())
        h['effFun'+var].GetXaxis().SetRangeUser(0.,100.)
        h['effFun'+var].Draw('P')
        h['effFun'+var].Draw('hist same')
        h['occ'].SetMarkerStyle(8)
        h['occ'].SetMarkerColor(h['occ'].GetLineColor())
        h['occ'].Draw('same P')
        h['occ'].Draw('same hist')
    var = 'P'
    ut.bookCanvas(h,'eff final P','Efficiencies ',900,600,1,1)
    h['eff final P'].cd(1)
    h['effFun'+var].SetTitle('Tracking efficiency as function of occupancy; N hits in upstream stations;efficiency')
    h['effFun'+var].GetXaxis().SetRangeUser(0.,100.)
    h['effFun'+var].Draw('P')
    h['effFun'+var].Draw('hist same')
    h['occ'].Draw('same P') 
    h['occ'].Draw('same hist')
    h['zeroFieldOcc'].Draw('P same')
    h['zeroFieldOcc'].Draw('same hist')
    hData['Occ'].Draw('same hist')
    hData['Occ'].Draw('P same')
    rc = T.DrawLatexNDC(0.28,0.40,"upstream station occupancy MC")
    T.SetTextColor(h['zeroFieldOcc'].GetLineColor())
    rc = T.DrawLatexNDC(0.28,0.28,"upstream station occupancy zero field Data")
    T.SetTextColor(hData['Occ'].GetLineColor())
    rc = T.DrawLatexNDC(0.28,0.34,"upstream station occupancy Data")
    T.SetTextColor(ROOT.kBlue)
    rc = T.DrawLatexNDC(0.35,0.8,"tracking efficiency")
    myPrint(h['eff final P'],"MCTrackEffFunOcc")
    finalEff  = 0
    sumEvents = 0
    for o in range(1,h['occ'].GetNbinsX()+1):
        finalEff+=h['occ'].GetBinContent(o)*h['effFun'+var].GetBinContent(o)
        sumEvents+=h['occ'].GetBinContent(o)
    finalEff=finalEff/sumEvents
    print "and the final answer is for MC: %5.2F%%"%(finalEff*100)
    finalEff  = 0
    sumEvents = 0
    for o in range(1,hData['Occ'].GetNbinsX()+1):
        finalEff+=hData['Occ'].GetBinContent(o)*h['effFun'+var].GetBinContent(o)
        sumEvents+=hData['Occ'].GetBinContent(o)
    finalEff=finalEff/sumEvents
    print "and the prediction for Data: %5.2F%%"%(finalEff*100)
    finalEff  = 0
    sumEvents = 0
    for o in range(1,h['zeroFieldOcc'].GetNbinsX()+1):
        finalEff+=h['zeroFieldOcc'].GetBinContent(o)*h['effFun'+var].GetBinContent(o)
        sumEvents+=h['zeroFieldOcc'].GetBinContent(o)
    finalEff=finalEff/sumEvents
    print "and the prediction for zeroField Data: %5.2F%%"%(finalEff*100)

def plotOccExample():
    ut.bookCanvas(h,'Occexample',' ',1200,600,1,1)
    for n in range(3,7):
        x = hMC['effP'].GetListOfPrimitives()[n]
        x.GetListOfPrimitives()[1].Draw()
        t = x.GetListOfPrimitives()[2].Clone('t2'+str(n))
        tmp = t.GetTitle().split('-')
        t.SetTitle(tmp[0]+'-'+str(int(tmp[1])-1))
        t.SetTextSize(0.09)
        t.Draw()
        t2 = x.GetListOfPrimitives()[3].Clone('t3'+str(n))
        t2.SetTextSize(0.09)
        t2.Draw()
        myPrint(h['Occexample'],x.GetName())

def trueMomPlot(Nevents=-1,onlyPlotting=False):
    ROOT.gStyle.SetTitleStyle(0)
    h     = hMC
    sTree = sTreeMC
    MCStats    = 1.8E9
    sim10fact  = MCStats/(65.E9*(1.-0.016)) # normalize 10GeV to 1GeV stats, 1.6% of 10GeV stats not processed.
    charmNorm  = {1:0.176,10:0.424}
    beautyNorm = {1:0.,   10:0.01218}
    if not onlyPlotting:
        for x in ['charm','10GeV','1GeV']:
            for c in ['','charm','beauty']:
                ut.bookHist(h,'trueMom-'+x+c,'true MC momentum;#it{p} [GeV/c];#it{p}_{T} [GeV/c]',500,0.,500.,200,0.,10.)
                ut.bookHist(h,'recoMom-'+x+c,'reco MC momentum;#it{p} [GeV/c];#it{p}_{T} [GeV/c]',500,0.,500.,200,0.,10.)
        if Nevents<0: Nevents = sTree.GetEntries()
        for n in range(Nevents):
            rc = sTree.GetEvent(n)  
            fname = sTree.GetCurrentFile().GetName()
            x = '1GeV'
            if not fname.find('charm')<0: x = 'charm'
            elif not fname.find('pythia8_Geant4_10.0')<0: 
              x = '10GeV'
              if sTree.channel==5: x+='charm'
              if sTree.channel==6: x+='beauty'
            if sTree.MCRecoDT.size() != 1: continue # look at 1 Track events for the moment
            for d in sTree.MCRecoDT:
                i = 0
                P  = ROOT.TVector3(sTree.MCRecoDTpx[i],sTree.MCRecoDTpy[i],sTree.MCRecoDTpz[i])
                found = False
                for t in range(sTree.nTr):
                    Preco  = ROOT.TVector3(sTree.Px[t],sTree.Py[t],sTree.Pz[t])
                    if abs(sTree.Delx[t])<cuts['muTrackMatchX'] and abs(sTree.Dely[t])<cuts['muTrackMatchY']:
                        rc = h['trueMom-'+x].Fill(P.Mag(),P.Pt())
                        rc = h['recoMom-'+x].Fill(Preco.Mag(),Preco.Pt())
                        break
        for x in ['trueMom-','recoMom-']:
            h[x+'10GeVnorm']=h[x+'10GeV'].Clone(x+'10GeVnorm')
            h[x+'10GeVnorm'].Add(h[x+'10GeVcharm'],charmNorm[10])
            h[x+'10GeVnorm'].Add(h[x+'10GeVbeauty'],beautyNorm[10])
            h[x+'10GeVnorm'].Scale(sim10fact)
            h[x+'1GeVnorm']=h[x+'1GeV'].Clone(x+'1GeVnorm')
            h[x+'1GeVnorm'].Add(h[x+'charm'],charmNorm[1])
            h[x+'P1GeVnorm'] =h[x+'1GeVnorm'].ProjectionX(x+'P1GeVnorm')
            h[x+'P10GeVnorm']=h[x+'10GeVnorm'].ProjectionX(x+'P10GeVnorm')
            h[x+'P']=h[x+'P10GeVnorm'].Clone(x+'P')
            for i in range(1,20): 
                h[x+'P'].SetBinContent(i,h[x+'P1GeVnorm'].GetBinContent(i))
                h[x+'P'].SetBinError(i,h[x+'P1GeVnorm'].GetBinError(i))
            for i in range(20,401): 
                h[x+'P'].SetBinContent(i,h[x+'P10GeVnorm'].GetBinContent(i))
                h[x+'P'].SetBinError(i,h[x+'P10GeVnorm'].GetBinError(i))
            h[x+'Pt1GeVnorm'] =h[x+'1GeVnorm'].ProjectionY(x+'Pt1GeVnorm',1,20)
            h[x+'Pt10GeVnorm']=h[x+'10GeVnorm'].ProjectionY(x+'Pt10GeVnorm',21,400)
            h[x+'Pt']=h[x+'Pt10GeVnorm'].Clone(x+'Pt')
            h[x+'Pt'].Add(h[x+'Pt1GeVnorm'])
        ut.writeHists(h,'trueMoms-'+MCType+'.root')
    else:
        ut.readHists(h,'trueMoms-repro.root')
        ut.readHists(h0,'trueMoms-0.root')
        for k in ['P','Pt']:
            t = "true Mom "+k
            if not h.has_key(t): ut.bookCanvas(h,t,'true and reco momentum',900,600,1,1)
            tc=h[t].cd(1)
            tc.SetLogy()
            h['trueMom-'+k].SetStats(0)
            #h['trueMom-'+k].Draw()
            h['rebinned-trueMom-'+k]=h['trueMom-'+k].Clone('rebinned-trueMom-'+k)
            h['rebinned-trueMom-'+k].Rebin(5)
            h['rebinned-trueMom-'+k].Scale(1./5.)
            h['rebinned-trueMom-'+k].SetMarkerStyle(21)
            h['rebinned-trueMom-'+k].SetMarkerColor(h['rebinned-trueMom-'+k].GetLineColor())
            if k=='P': 
                 h['rebinned-trueMom-'+k].GetXaxis().SetRangeUser(5.,400.)
                 h['rebinned-trueMom-'+k].SetTitle(';#it{p} [GeV/c]' )
            else: 
                 h['rebinned-trueMom-'+k].SetTitle(';#it{p}_{T} [GeV/c]' )
            h['rebinned-trueMom-'+k].Draw()
            h['recoMom-'+k].SetLineColor(ROOT.kMagenta)
            h['recoMom-'+k].SetStats(0)
            #h['recoMom-'+k].Draw('same')
            h['rebinned-recoMom-'+k]=h['recoMom-'+k].Clone('rebinned-recoMom-'+k)
            h['rebinned-recoMom-'+k].Rebin(5)
            h['rebinned-recoMom-'+k].Scale(1./5.)
            h['rebinned-recoMom-'+k].SetMarkerStyle(23)
            h['rebinned-recoMom-'+k].SetMarkerColor(h['rebinned-recoMom-'+k].GetLineColor())
            h['rebinned-recoMom-'+k].Draw('P same')
            h0['recoMom-'+k].SetLineColor(ROOT.kGreen)
            h0['recoMom-'+k].SetStats(0)
            #h0['recoMom-'+k].Draw('same')
            h0['0rebinned-recoMom-'+k]=h0['recoMom-'+k].Clone('0rebinned-recoMom-'+k)
            # bypass issue with different number of tracks in sim files with 270mu, -0 and 350mu -repro
            rescale = h['recoMom-'+k].GetSumOfWeights()/h0['recoMom-'+k].GetSumOfWeights()
            print "rescale ",'0rebinned-recoMom-'+k,rescale,h['recoMom-'+k].GetSumOfWeights(),h0['recoMom-'+k].GetSumOfWeights()
            h0['0rebinned-recoMom-'+k].Scale( rescale )
            h0['0rebinned-recoMom-'+k].Rebin(5)
            h0['0rebinned-recoMom-'+k].Scale(1./5.)
            h0['0rebinned-recoMom-'+k].SetMarkerStyle(22)
            h0['0rebinned-recoMom-'+k].SetMarkerColor(h0['0rebinned-recoMom-'+k].GetLineColor())
            h0['0rebinned-recoMom-'+k].Draw('P same')
            h['leg'+t]=ROOT.TLegend(0.31,0.67,0.85,0.85)
            h['leg'+t].SetEntrySeparation(0.35)
            h['leg'+t].AddEntry(h['rebinned-trueMom-'+k],'true momentum ','PL')
            h['leg'+t].AddEntry(h0['0rebinned-recoMom-'+k],'reconstructed momentum #sigma_{hit}=270#mum','PL')
            h['leg'+t].AddEntry(h['rebinned-recoMom-'+k],'reconstructed momentum #sigma_{hit}=350#mum','PL')
            h['leg'+t].Draw()
            myPrint(h[t],'True-Reco'+k)
def yBeam():
    Mproton = 0.938272081
    pbeam   = 400.
    Ebeam   = ROOT.TMath.Sqrt(400.**2+Mproton**2)
    beta    = 400./Ebeam # p/E 
    sqrtS   = ROOT.TMath.Sqrt(2*Mproton**2+2*Ebeam*Mproton)
    y_beam  = ROOT.TMath.Log(sqrtS/Mproton)   # Carlos Lourenco, private communication
    return y_beam
def mufluxReco(sTree,h,nseq=0,ncpus=False):
    y_beam = yBeam()
    cuts = {'':0,'Chi2<':0.7,'Dely<':5,'Delx<':2,'All':1}
    ut.bookHist(h,'Trscalers','scalers for track counting',20,0.5,20.5)
    for c in cuts:
        for x in ['','mu']:
            for s in ["","Decay","Hadronic inelastic","Lepton pair","Positron annihilation","charm","beauty","Di-muon P8","invalid"]:
                ut.bookHist(h,c+'p/pt'+x+s,'momentum vs Pt (GeV);#it{p} [GeV/c]; #it{p}_{T} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'y'+x+s,'rapidity cm; y_{CM}',500,-1.,5.,100,0.,500.,50,0.,10.)
                ut.bookHist(h,c+'p/px'+x+s,'momentum vs Px (GeV);#it{p} [GeV/c]; #it{p}_{X}[GeV/c]',500,0.,500.,200,-10.,10.)
                ut.bookHist(h,c+'p/Abspx'+x+s,'momentum vs Px (GeV);#it{p}_{T} [GeV/c]; #it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'pz/Abspx'+x+s,'Pz vs Px (GeV);#it{p} [GeV/c]; #it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'p/pxy'+x+s,'momentum vs Px (GeV);#it{p} [GeV/c]; #it{p}_{X} [GeV/c]',500,0.,500.,200,-10.,10.)
                ut.bookHist(h,c+'p/Abspxy'+x+s,'momentum vs Px (GeV) tagged RPC X;#it{p} [GeV/c]; #it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'pz/Abspxy'+x+s,'Pz vs Px (GeV) tagged RPC X;#it{p} [GeV/c]; #it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'TrackMult'+x+s,'track multiplicity',10,-0.5,9.5)
                ut.bookHist(h,c+'chi2'+x+s,'chi2/nDoF',100,0.,10.)
                ut.bookHist(h,c+'Nmeasurements'+x+s,'number of measurements used',25,-0.5,24.5)
                ut.bookHist(h,c+'xy'+x+s,'xy of first state;x [cm];y [cm]',100,-30.,30.,100,-30.,30.)
                ut.bookHist(h,c+'pxpy'+x+s,'px/pz py/pz of first state',100,-0.2,0.2,100,-0.2,0.2)
                ut.bookHist(h,c+'p1/p2'+x+s,'momentum p1 vs p2;#it{p} [GeV/c]; #it{p} [GeV/c]',500,0.,500.,500,0.,500.)
                ut.bookHist(h,c+'pt1/pt2'+x+s,'P_{T} 1 vs P_{T} 2;#it{p} [GeV/c]; #it{p} [GeV/c]',100,0.,10.,100,0.,10.)
                ut.bookHist(h,c+'p1/p2s'+x+s,'momentum p1 vs p2 same sign;#it{p} [GeV/c]; #it{p} [GeV/c]',500,0.,500.,500,0.,500.)
                ut.bookHist(h,c+'pt1/pt2s'+x+s,'P_{T} 1 vs P_{T} 2 same sign;#it{p} [GeV/c]; #it{p} [GeV/c]',100,0.,10.,100,0.,10.)
                ut.bookHist(h,c+'Chi2/DoF'+x+s,'Chi2/DoF',100,0.,5.,100,0.,500.)
                ut.bookHist(h,c+'DoF'+x+s,     'DoF'     ,30,0.5,30.5,100,0.,500.)
                ut.bookHist(h,c+'R'+x+s,'rpc match',100,0.,10.,100,0.,500.)
                ut.bookHist(h,c+'RPCResX/Y'+x+s,'RPC residuals',200,0.,200.,200,0.,200.)
                ut.bookHist(h,c+'RPCMatch'+x+s,'RPC matching',100,0.,10.,100,0.,10.)
                ut.bookHist(h,c+'trueMom'+x+s,'true MC momentum;#it{p} [GeV/c];#it{p}_{T} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'recoMom'+x+s,'reco MC momentum;#it{p} [GeV/c];#it{p}_{T} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'truePz/Abspx'+x+s,'true MC momentum;#it{p} [GeV/c];#it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'recoPz/Abspx'+x+s,'reco MC momentum;#it{p} [GeV/c];#it{p}_{X} [GeV/c]',500,0.,500.,100,0.,10.)
                ut.bookHist(h,c+'momResol'+x+s,'momentum resolution function of momentum;#it{p} [GeV/c];#sigma P/P', 200,-0.5,0.5,40,0.,400.)
#
    MCdata = False
    if sTree.FindBranch("MCRecoDT"): MCdata = True
#
    Ntotal = sTree.GetEntries()
    nStart = 0
    if ncpus:
      ncpus = int(ncpus)
      nseq = int(nseq)
      deltaN = (sTree.GetEntries()+0.5)//ncpus
      nStart = int(nseq*deltaN)
      Ntotal = int(min(sTree.GetEntries(),nStart+deltaN))
    for n in range(nStart,Ntotal):
        rc = sTree.GetEvent(n)
        if n%500000==0: print 'now at event ',n,'of',Ntotal,time.ctime()
        h['Trscalers'].Fill(1)
        if len(sTree.GoodTrack)>0: h['Trscalers'].Fill(2)
        tchannel = sTree.channel
        source = ''
        if MCdata:
            if (tchannel == 1):  source = "Decay"
            if (tchannel == 7):  source = "Di-muon P8"
            if (tchannel == 2):  source = "Hadronic inelastic"
            if (tchannel == 3):  source = "Lepton pair"
            if (tchannel == 4):  source = "Positron annihilation"
            if (tchannel == 5):  source = "charm"
            if (tchannel == 6):  source = "beauty"
            if (tchannel == 13): source = "invalid"
        muonTaggedTracks = {}
        for k in range(len(sTree.GoodTrack)):
            h['Trscalers'].Fill(3)
            if sTree.GoodTrack[k]<0: continue
            h['Trscalers'].Fill(4)
            muTagged  = False
            muTaggedX = False
            clone     = False
            if sTree.GoodTrack[k]%2==1: 
                muTaggedX = True
                if int(sTree.GoodTrack[k]/10)%2==1: muTagged = True
            if sTree.GoodTrack[k]>999:  clone = True
            if clone: continue
            R = (sTree.Dely[k]/3.)**2+(sTree.Delx[k]/1.5)**2
            p = ROOT.TVector3(sTree.Px[k],sTree.Py[k],sTree.Pz[k])
            rc = h['R'].Fill(R,p.Mag())
            rc = h['RPCMatch'].Fill(sTree.Delx[k],sTree.Dely[k])
            okCuts = ['']
            muonTaggedTracks['']=[]
            if sTree.Chi2[k]<cuts['Chi2<']: okCuts.append('Chi2<')
            if sTree.Dely[k]<cuts['Dely<']: okCuts.append('Dely<')
            if sTree.Delx[k]<cuts['Delx<']: okCuts.append('Delx<')
            if sTree.Chi2[k]<cuts['Chi2<'] and sTree.Dely[k]<cuts['Dely<'] and sTree.Delx[k]<cuts['Delx<']: okCuts.append('All')
            for c in okCuts:
                LV = ROOT.Math.PxPyPzMVector(p.X(),p.Y(),p.Z(),0.105658)
                y  = LV.Rapidity()-y_beam
                h[c+"p/pt"].Fill(p.Mag(),p.Pt())
                h[c+"y"].Fill(y,p.Mag(),p.Pt())
                h[c+"p/Abspx"].Fill(p.Mag(),abs(p.x()))
                h[c+"pz/Abspx"].Fill(p.z(),abs(p.x()))
                h[c+"xy"].Fill(sTree.x[k],sTree.y[k])
                h[c+"pxpy"].Fill(p.x()/p.z(),p.y()/p.z())
                h[c+'Chi2/DoF'].Fill(sTree.Chi2[k],p.Mag())
                h[c+'DoF'].Fill(sTree.nDoF[k],p.Mag())
                if p.Mag()>300. and Debug: 
                    occ = sTree.stationOcc[1]+sTree.stationOcc[2]+sTree.stationOcc[5]+sTree.stationOcc[6]
                    print n, p.Mag(),occ,sTree.GoodTrack[k],sTree.Chi2[k],sTree.nDoF[k]
                if source != '':
                    h[c+"p/pt"+source].Fill(p.Mag(),p.Pt())
                    h[c+"y"+source].Fill(y,p.Mag(),p.Pt())
                    h[c+"p/px"+source].Fill(p.Mag(),p.x())
                    h[c+"p/Abspx"+source].Fill(p.Mag(),abs(p.x()))
                    h[c+"pz/Abspx"+source].Fill(p.z(),abs(p.x()))
                    h[c+"xy"+source].Fill(sTree.x[k],sTree.y[k])
                    h[c+"pxpy"+source].Fill(p.x()/p.z(),p.y()/p.z())
                    h[c+'R'+source].Fill(R,p.Mag())
                    h[c+'Chi2/DoF'+source].Fill(sTree.Chi2[k],p.Mag())
                    h[c+'DoF'+source].Fill(sTree.nDoF[k],p.Mag())
                h[c+'RPCResX/Y'].Fill(sTree.Delx[k],sTree.Dely[k])
                if (muTaggedX): # within ~3sigma  X from mutrack
                    h[c+"p/pxmu"].Fill(p.Mag(),p.x())
                    h[c+"p/Abspxmu"].Fill(p.Mag(),abs(p.x()))
                    h[c+"pz/Abspxmu"].Fill(p.z(),abs(p.x()))
                    if source != '':
                        h[c+"p/pxmu"+source].Fill(p.Mag(),p.x())
                        h[c+"p/Abspxmu"+source].Fill(p.Mag(),abs(p.x()))
                        h[c+"pz/Abspxmu"+source].Fill(p.z(),abs(p.x()))
                if (muTagged): #  within ~3sigma  X,Y from mutrack
                    if c=='': muonTaggedTracks[''].append(k)
                    h[c+"p/ptmu"].Fill(p.Mag(),p.Pt())
                    h[c+"ymu"].Fill(y,p.Mag(),p.Pt())
                    h[c+"p/pxymu"].Fill(p.Mag(),p.x())
                    h[c+"p/Abspxymu"].Fill(p.Mag(),abs(p.x()))
                    h[c+"pz/Abspxymu"].Fill(p.z(),abs(p.x()))
                    h[c+"xymu"].Fill(sTree.x[k],sTree.y[k])
                    h[c+"pxpymu"].Fill(p.x()/p.z(),p.y()/p.z())
                    h[c+'Rmu'].Fill(R,p.Mag())
                    h[c+'Chi2/DoFmu'].Fill(sTree.Chi2[k],p.Mag())
                    h[c+'DoFmu'].Fill(sTree.nDoF[k],p.Mag())
                    if source != '':
                        h[c+"p/ptmu"+source].Fill(p.Mag(),p.Pt())
                        h[c+"ymu"+source].Fill(y,p.Mag(),p.Pt())
                        h[c+"p/pxymu"+source].Fill(p.Mag(),p.x())
                        h[c+"p/Abspxymu"+source].Fill(p.Mag(),abs(p.x()))
                        h[c+"pz/Abspxymu"+source].Fill(p.z(),abs(p.x()))
                        h[c+"xymu"+source].Fill(sTree.x[k],sTree.y[k])
                        h[c+"pxpymu"+source].Fill(p.x()/p.z(),p.y()/p.z())
                        h[c+'Rmu'+source].Fill(R,p.Mag())
                        h[c+'Chi2/DoFmu'+source].Fill(sTree.Chi2[k],p.Mag())
                        h[c+'DoFmu'+source].Fill(sTree.nDoF[k],p.Mag())
#
                if len(muonTaggedTracks[''])==2:
                    a,b=muonTaggedTracks[''][0],muonTaggedTracks[''][1]
                    pA=ROOT.TVector3(sTree.Px[a],sTree.Py[a],sTree.Pz[a])
                    pB=ROOT.TVector3(sTree.Px[b],sTree.Py[b],sTree.Pz[b])
                    prodSign = sTree.Sign[a]*sTree.Sign[b]
                    if prodSign<0:
                        h["p1/p2"].Fill(pA.Mag(),pB.Mag())
                        h["pt1/pt2"].Fill(pA.Pt(),pB.Pt())
                        if source != '':
                            h["p1/p2"+source].Fill(pA.Mag(),pB.Mag())
                            h["pt1/pt2"+source].Fill(pA.Pt(),pB.Pt())
                    else:
                        h["p1/p2s"].Fill(pA.Mag(),pB.Mag())
                        h["pt1/pt2s"].Fill(pA.Pt(),pB.Pt())
                        if source != '':
                            h["p1/p2s"+source].Fill(pA.Mag(),pB.Mag())
                            h["pt1/pt2s"+source].Fill(pA.Pt(),pB.Pt())
# mom resolution
                if MCdata and len(sTree.GoodTrack)==1 and len(sTree.MCRecoDTpx)==1:
                    trueMom = ROOT.TVector3(sTree.MCRecoDTpx[0],sTree.MCRecoDTpy[0],sTree.MCRecoDTpz[0])
                    h["trueMom"].Fill(trueMom.Mag(),trueMom.Pt())
                    h["recoMom"].Fill(p.Mag(),p.Pt())
                    h["truePz/Abspx"].Fill(trueMom[2],ROOT.TMath.Abs(trueMom[0]))
                    h["recoPz/Abspx"].Fill(p[2],ROOT.TMath.Abs(p[0]))
                    h["momResol"].Fill((p.Mag()-trueMom.Mag())/trueMom.Mag(),trueMom.Mag())
                    if source != '':
                        h["trueMom"+source].Fill(trueMom.Mag(),trueMom.Pt());
                        h["recoMom"+source].Fill(p.Mag(),p.Pt());
                        h["truePz/Abspx"+source].Fill(trueMom[2],ROOT.TMath.Abs(trueMom[0]));
                        h["recoPz/Abspx"+source].Fill(p[2],ROOT.TMath.Abs(p[0]));
                        h["momResol"+source].Fill((p.Mag()-trueMom.Mag())/trueMom.Mag(),trueMom.Mag());
    if not MCdata : tmp = 'RUN_8000'+fdir.split('RUN_8000')[1]
    else : 
      tmp = fdir
      if withCharm : tmp+='-charm'
    outFile = 'sumHistos-'+'-'+tmp+'.root'
    if options.refit: outFile = 'sumHistos-'+'-'+tmp+'_refit.root'
    if ncpus:
       outFile=outFile.replace('.root','-'+str(nseq)+'.root')
    ut.writeHists( h,outFile)
    print "I have finished. ",outFile
def dEdxCorrection(p):
 # +7.3    # most probably ~7.5, mean 6.9.
 # -8.1 - 0.045 *p + 0.00017 *p*p fit without cut
 dE = -7.63907  -0.0315131  * p + 0.000168569 * p*p
 return -dE*(1-0.085)  # fudge factor reversed engineering
def invMass(sTree,h,nseq=0,ncpus=False):
    ut.bookHist(h,'invMassSS','inv mass ',100,0.0,10.0)
    ut.bookHist(h,'invMassOS','inv mass ',100,0.0,10.0)
    ut.bookHist(h,'invMassJ','inv mass from Jpsi',100,0.0,10.0)
    ut.bookHist(h,'p/pt','p/pt',100,0.0,400.0,100,0.0,10.0)
    ut.bookHist(h,'p/ptJ','p/pt of Jpsi',100,0.0,400.0,100,0.0,10.0)
    ut.bookHist(h,'p/ptmu','p/pt of mu',100,0.0,400.0,100,0.0,10.0)
    ut.bookHist(h,'p/ptmuJ','p/pt of mu from Jpsi',100,0.0,400.0,100,0.0,10.0)
    MCdata = False
    if sTree.FindBranch("MCRecoDT"): MCdata = True
    if MCdata:
       name = "ntuple-invMass-MC.root"
       if ncpus:
          name = name.replace('.root','-'+str(nseq)+'.root')
    else:      
       name = "ntuple-invMass-"+fdir.split('/')[7]+'.root'
    if options.refit: name = name.replace('.root','_refit.root')
    h['fntuple']  = ROOT.TFile.Open(name, 'RECREATE')
    variables = "mult:m:mcor:mcor2:y:ycor:p:pcor:pt:ptcor:p1:pt1:p1cor:pt1cor:p2:pt2:p2cor:pt2cor:Ip1:Ip2:chi21:chi22:cosTheta:cosCSraw:cosCScor:\
prec1x:prec1y:prec1z:prec2x:prec2y:prec2z:rec1x:rec1y:rec1z:rec2x:rec2y:rec2z"
    if MCdata:
      variables += ":Jpsi:PTRUE:PtTRUE:YTRUE:p1True:p2True:dTheta1:dTheta2:dMults1:dMults2:originZ1:originZ2:p1x:p1y:p1z:p2x:p2y:p2z:ox:oy:oz:Pmother"
    h['nt']  = ROOT.TNtuple("nt","dimuon",variables) 
#
    sTreeFullMC = None
    Ntotal = sTree.GetEntries()
    nStart = 0
    if ncpus:
      ncpus = int(ncpus)
      nseq = int(nseq)
      deltaN = (sTree.GetEntries()+0.5)//ncpus
      nStart = int(nseq*deltaN)
      Ntotal = int(min(sTree.GetEntries(),nStart+deltaN))
    currentFile = ''
    for n in range(0,Ntotal):
        rc = sTree.GetEvent(n)
        # if n%500000==0: print 'now at event ',n,'of',Ntotal,time.ctime()
        if sTree.GetCurrentFile().GetName()!=currentFile:
            currentFile = sTree.GetCurrentFile().GetName()
            nInFile = n
        if n<nStart: continue
        tchannel = sTree.channel
        source = ''
        if MCdata:
            if (tchannel == 1):  source = "Decay"
            if (tchannel == 7):  source = "Di-muon P8"
            if (tchannel == 2):  source = "Hadronic inelastic"
            if (tchannel == 3):  source = "Lepton pair"
            if (tchannel == 4):  source = "Positron annihilation"
            if (tchannel == 5):  source = "charm"
            if (tchannel == 6):  source = "beauty"
            if (tchannel == 13): source = "invalid"
        P     = {-1:ROOT.Math.PxPyPzMVector()}
        IP    = {-1:-999.}
        Pcor  = {-1:ROOT.Math.PxPyPzMVector()}
        Pcor2 = {-1:ROOT.Math.PxPyPzMVector()}
        for k in range(len(sTree.GoodTrack)):
            if sTree.GoodTrack[k]<0: continue
            if sTree.GoodTrack[k]%2!=1 or  int(sTree.GoodTrack[k]/10)%2!=1: continue
            if sTree.GoodTrack[k]>999:  continue
            P[k] = ROOT.Math.PxPyPzMVector(sTree.Px[k],sTree.Py[k],sTree.Pz[k],0.105658)
            l = (sTree.z[k] - zTarget)/(sTree.Pz[k]+ 1E-19)
            x = sTree.x[k]+l*sTree.Px[k]
            y = sTree.y[k]+l*sTree.Py[k]
            IP[k] = ROOT.TMath.Sqrt(x*x+y*y)
# make dE correction plus direction from measured point
            dline   = ROOT.TVector3(sTree.x[k],sTree.y[k],sTree.z[k]-zTarget)
            Ecor = P[k].E()+dEdxCorrection(P[k].P())
            norm = dline.Mag()
            Pcor[k]  = ROOT.Math.PxPyPzMVector(Ecor*dline.X()/norm,Ecor*dline.Y()/norm,Ecor*dline.Z()/norm,0.105658)
            Pcor2[k] = ROOT.Math.PxPyPzMVector(P[k].P()*dline.X()/norm,P[k].P()*dline.Y()/norm,P[k].P()*dline.Z()/norm,0.105658)
# now we have list of selected tracks, P.keys()
        if len(P)<2 and not withJpsi: continue
        X      =  {0:ROOT.Math.PxPyPzMVector()}
        Xcor   =  {0:ROOT.Math.PxPyPzMVector()}
        Xcor2  =  {0:ROOT.Math.PxPyPzMVector()}
        jpsi   =  {0:-1}
        pTrue  =  {0:[ROOT.TVector3(0,0,-9999.),ROOT.TVector3(0,0,-9999.)]}
        dTheta =  {0:[-9999.,-9999.]}
        dMults =  {0:[-9999.,-9999.]}
        originZ = {0:[-9999.,-9999.]}
        PTRUE  =  {0:-1}
        PtTRUE =  {0:-1}
        YTRUE  =  {0:-999}
        costheta = {0:-999.}
        chi2     = {0:[-999.,-999.]}
        nComb    = {0:[-1,-1]}
        Pmother  = {0:0}
        j = 0
        pDict = P.keys()
        pDict.remove(-1)
        for l1 in range(len(pDict)-1):
         for l2 in range(l1+1,len(pDict)):
          n1 = pDict[l1]
          n2 = pDict[l2]
# for jpsi MC only take truth matched combinations
          if withJpsi:
            if sTreeMC.MCID[n1]<0 or sTreeMC.MCID[n2]<0: continue
          X[j]    = P[n1]+P[n2]
          Xcor[j] = Pcor[n1]+Pcor[n2]
          Xcor2[j] = Pcor2[n1]+Pcor2[n2]
# angle between two tracks in Jpsi rest frame
          b = X[j].BoostToCM()
          moth_boost = ROOT.Math.Boost(b.x(),b.y(),b.z())
          Pcms = moth_boost*P[n1]
          v0=ROOT.TVector3(Pcms.X(),Pcms.Y(),Pcms.Z())
          v1=ROOT.TVector3(X[j].X(),X[j].Y(),X[j].Z())
          costheta[j] = v0.Dot(v1)/( v0.Mag()*v1.Mag() + 1E-19)
          if sTree.Sign[n1]*sTree.Sign[n2]<0:  rc = h["invMassOS"].Fill(X[j].M())
          else:                                rc = h["invMassSS"].Fill(X[j].M())
          chi2[j] = [sTree.Sign[n1]*sTree.Chi2[n1],sTree.Sign[n2]*sTree.Chi2[n2]]
          if X[j].M()>2.5 and X[j].M()<4.0:
             rc = h["p/pt"].Fill(X[j].P(),X[j].Pt())
             rc = h["p/ptmu"].Fill(P[n1].P(),P[n2].Pt())
             rc = h["p/ptmu"].Fill(P[n1].P(),P[n2].Pt())
          jpsi[j] = -1
          originZ[j]  = [-9999.,-9999.]
          pTrue[j]    = [ROOT.TVector3(0,0,-9999.),ROOT.TVector3(0,0,-9999.)]
          dTheta[j] = [-9999.,-9999.]
          dMults[j] = [-9999.,-9999.]
          PTRUE[j]  = -1.
          PtTRUE[j] = -1.
          YTRUE[j]  = -999.
          nComb[j]=[n1,n2]
          j+=1
#check truth
        eospathSim = os.environ['EOSSHIP']+'/eos/experiment/ship/user/truf/muflux-sim/'
        fname = sTree.GetCurrentFile().GetName().replace('ntuple-','')
        if sTreeFullMC:
            if sTreeFullMC.GetCurrentFile().GetName().find(fname)<0:
                fMC = ROOT.TFile.Open(fname)
                sTreeFullMC = fMC.cbmsim
        else: 
            fMC = ROOT.TFile.Open(fname)
            sTreeFullMC = fMC.cbmsim
        rc = sTreeFullMC.GetEvent(n-nInFile)

        for j in nComb:
            mothers = []
            mJpsi  =  -1
            if withJpsi:
               for m in sTreeFullMC.MCTrack:
                  mJpsi += 1
                  if m.GetPdgCode()==443:
                     PTRUE[j]  = m.GetP()
                     PtTRUE[j] = m.GetPt()
                     YTRUE[j]  = m.GetRapidity()
                     Pmother[j]  = sTreeFullMC.MCTrack[m.GetMotherId()].GetP()
            if nComb[j][0]<0: continue  # no reco Jpsi
            kx = 0
            for k in [nComb[j][0],nComb[j][1]]:
                if sTreeMC.MCID[k]<0: continue
                trueMu = sTreeFullMC.MCTrack[sTreeMC.MCID[k]]
                mother = sTreeFullMC.MCTrack[trueMu.GetMotherId()]
                mothers.append(mother.GetPdgCode())
                if withJpsi and mJpsi != mother and j==0:
# mu mu combination does not point to correct Jpsi, don't overwrite true one
                    PTRUE[j]=-PTRUE[j]
                else:
                    PTRUE[j]  = mother.GetP()
                    PtTRUE[j] = mother.GetPt()
                    YTRUE[j]  = mother.GetRapidity()
                    if not mother.GetMotherId()<0:
                        Pmother[j]  = sTreeFullMC.MCTrack[mother.GetMotherId()].GetP()
# check multiple scattering
                trueMu.GetMomentum(pTrue[j][kx])
                originZ[j][kx] = trueMu.GetStartZ()
                dline   = ROOT.TVector3(sTree.x[k],sTree.y[k],sTree.z[k]-zTarget)
                dTheta[j][kx]  = pTrue[j][kx].Dot(dline)/(pTrue[j][kx].Mag()*dline.Mag())
                prec = ROOT.TVector3(P[k].Px(),P[k].Py(),P[k].Pz())
                dMults[j][kx]  = pTrue[j][kx].Dot(prec)/(pTrue[j][kx].Mag()*prec.Mag())
                kx+=1
            if len(mothers)==2: 
             if mothers[0]==mothers[1]: jpsi[j] = mothers[0]
            if jpsi[j] == 443:
                rc = h["invMassJ"].Fill(X[j].M())
                rc = h["p/ptJ"].Fill(X[j].P(),X[j].Pt())
                rc = h["p/ptmuJ"].Fill(P[n1].P(),P[n1].Pt())
                rc = h["p/ptmuJ"].Fill(P[n2].P(),P[n2].Pt())
                if Debug:
                 trueMu = sTreeFullMC.MCTrack[sTreeMC.MCID[n1]]
                 mother = sTreeFullMC.MCTrack[trueMu.GetMotherId()]
                 print X[j].M(),n,n-nInFile,sTree.GetCurrentFile()
                 print 'origin',mother.GetStartX(),mother.GetStartY(),mother.GetStartZ()
# now we have all combinations, j
        for j in nComb:
          n1 = nComb[j][0]
          n2 = nComb[j][1]
          if n1<0:
            cosCSraw,cosCScor       = -999.,-999.
            Y,Ycor                  = -999.,-999.
            xn1,yn1,zn1,xn2,yn2,zn2 = 0,0,0,0,0,0
          else:
            if chi2[j][0] < 0: 
              nlep      = n1
              nantilep  = n2
            else: 
              nlep = n2
              nantilep  = n1
            P1pl = P[nlep].E()+P[nlep].Pz()
            P2pl = P[nantilep].E()+P[nantilep].Pz()
            P1mi = P[nlep].E()-P[nlep].Pz()
            P2mi = P[nantilep].E()-P[nantilep].Pz()
            cosCSraw = X[j].Pz()/abs(X[j].Pz()) * 1./X[j].M()/ROOT.TMath.Sqrt(X[j].M2()+X[j].Pt()**2)*(P1pl*P2mi-P2pl*P1mi)
            P1pl = Pcor[nlep].E()+Pcor[nlep].Pz()
            P2pl = Pcor[nantilep].E()+Pcor[nantilep].Pz()
            P1mi = Pcor[nlep].E()-Pcor[nlep].Pz()
            P2mi = Pcor[nantilep].E()-Pcor[nantilep].Pz()
            cosCScor = Xcor[j].Pz()/abs(Xcor[j].Pz()) * 1./Xcor[j].M()/ROOT.TMath.Sqrt(Xcor[j].M2()+Xcor[j].Pt()**2)*(P1pl*P2mi-P2pl*P1mi)
            Y    = X[j].Rapidity()
            Ycor = Xcor[j].Rapidity()
            xn1 = sTree.x[n1]
            yn1 = sTree.y[n1] 
            zn1 = sTree.z[n1]
            xn2 = sTree.x[n2]
            yn2 = sTree.y[n2]
            zn2 = sTree.z[n2] 
          nrOfComb = float(len(nComb))
          if nComb[j][0]<0 : nrOfComb-=1
          theArray = [nrOfComb,X[j].M(),Xcor[j].M(),Xcor2[j].M(),Y,Ycor,X[j].P(),Xcor[j].P(),X[j].Pt(),Xcor[j].Pt(),\
                     P[n1].P(),P[n1].Pt(),Pcor[n1].P(),Pcor[n1].Pt(),P[n2].P(),P[n2].Pt(),Pcor[n2].P(),Pcor[n2].Pt(),\
                     IP[n1],IP[n2],chi2[j][0],chi2[j][1],costheta[j],cosCSraw,cosCScor,\
                     P[n1].X(),P[n1].Y(),P[n1].Z(),P[n2].X(),P[n2].Y(),P[n2].Z(),\
                     xn1,yn1,zn1,xn2,yn2,zn2]
          if MCdata:
             if n1<0: kTrueMu = -1
             else:    kTrueMu = sTreeMC.MCID[n1]
             if kTrueMu>0:
              ox,oy,oz = sTreeFullMC.MCTrack[kTrueMu].GetStartX(),sTreeFullMC.MCTrack[kTrueMu].GetStartY(),sTreeFullMC.MCTrack[kTrueMu].GetStartZ()
             else:
              ox,oy,oz = -9999.,9999.,-9999.
             theArray += [float(jpsi[j]),PTRUE[j],PtTRUE[j],YTRUE[j],pTrue[j][0].Mag(),pTrue[j][1].Mag(),\
                     dTheta[j][0],dTheta[j][1],dMults[j][0],dMults[j][1],originZ[j][0],originZ[j][1],\
                     pTrue[j][0].X(),pTrue[j][0].Y(),pTrue[j][0].Z(),pTrue[j][1].X(),pTrue[j][1].Y(),pTrue[j][1].Z(),ox,oy,oz,Pmother[j]]
          theTuple = array('f',theArray)
          h['nt'].Fill(theTuple)
    h['fntuple'].cd()
    h['nt'].Write()
    hname = name.replace('ntuple-','')
    ut.writeHists(h,hname)
    print "I have finished. ",hname
def myDraw(variable,cut,ntName='10GeV'):
 hMC[ntName].Draw(variable,cut)
 # too complicated to combine 1GeV
 # hMC['10GeV'].Draw(variable,str(hMC['weights']['1GeV'])+'*('+cut+')')
 # hMC['10eV'].Draw(variable.replace(">>",">>+"),str(hMC['weights']['1GeV'])+'*('+cut+')')
 
jpsiCascadeContr = 7./33.
InvMassPlots = [160,0.,8.]

# The elastic proton proton cross section at ~27GeV is about 7mbar. The inelastic cross section is about 33mbar. 
# Since we have a thick target, any proton from the elastic scattering will interact inelastic somewhere else.
# last cascade production of Eric shows even larger contribution, but momentum distribution not clear.
def loadNtuples():
 if options.refit :
  hData['f']     = ROOT.TFile('ntuple-InvMass-refitted.root')  # ROOT.TFile('ntuple-InvMass-refitted_intermediateField.root')
  hMC['f1']      = ROOT.TFile('ntuple-invMass-MC-1GeV-repro.root')
  hMC['f10']     = ROOT.TFile('ntuple-invMass-MC-10GeV-repro.root')
  hMC['fJpsi']   = ROOT.TFile('ntuple-invMass-MC-Jpsi.root')
  hMC['fJpsiP8'] = ROOT.TFile('ntuple-invMass-MC-JpsiP8.root')
  hMC['fJpsiP8_Primary'] = ROOT.TFile.Open(os.environ['EOSSHIP']+'/eos/experiment/ship/user/truf/muflux-sim/JpsiProduction_P8/Jpsi-Pythia8_21788000000_0-3074.root')
  hMC['fJpsiP8_PrimaryMu'] = ROOT.TFile.Open(os.environ['EOSSHIP']+'/eos/experiment/ship/user/truf/muflux-sim/JpsiProduction_P8/Jpsi-Pythia8_385000000_10000-11000.root')
  hMC['fJpsiCascade']  = ROOT.TFile.Open(os.environ['EOSSHIP']+'/eos/experiment/ship/data/jpsicascade/cascade_MSEL61_20M.root')
  # hMC['fJpsiCascade'] needs to be scaled by 0.9375, since 1 file not being used in simulation
  hMC['scalingFactor']={}
  hMC['scalingFactor']['fJpsiCascade']=0.9375
  hMC['fJpsi10GeV'] = ROOT.TFile('JpsifromBackground.root')
  hMC['fJpsi1GeV']  = ROOT.TFile('JpsifromBackground-1GeV.root')
 else:
  hData['f'] = ROOT.TFile('ntuple-InvMass.root')
  hMC['f1']  = ROOT.TFile('ntuple-invMass-MC-1GeV.root')
  hMC['f10'] = ROOT.TFile('ntuple-invMass-MC-10GeV.root')
 hMC['1GeV']        = hMC['f1'].nt
 hMC['10GeV']       = hMC['f10'].nt
 hMC['Jpsi']        = hMC['fJpsi'].nt
 hMC['JpsiP8']      = hMC['fJpsiP8'].nt
 hMC['JpsiCascade'] = hMC['fJpsiCascade'].pythia6
 hMC['JpsiP8_Primary'] = hMC['fJpsiP8_Primary'].pythia6
 hMC['JpsiP8_PrimaryMu'] = hMC['fJpsiP8_PrimaryMu'].pythia6
 hMC['Jpsi10GeV']   = hMC['fJpsi10GeV'].pythia8
 hMC['Jpsi1GeV']   = hMC['fJpsi1GeV'].pythia8
 ut.bookCanvas(hMC,'dummy',' ',900,600,1,1)
def JpsiAcceptance(withCosCSCut=True):
   y_beam = yBeam()
   bw = (InvMassPlots[2]-InvMassPlots[1])/InvMassPlots[0]
   hMC['myGauss'] = ROOT.TF1('gauss','abs([0])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-[1])/[2])**2)\
            +abs([3])*'+str(bw)+'/(abs([5])*sqrt(2*pi))*exp(-0.5*((x-[4])/[5])**2)+abs( [6]+[7]*x+[8]*x**2 )\
            +abs([9])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-(3.6871 + [1] - 3.0969))/[2])**2)',10)
   category = {}
   category['_Cascade']     = {'nt':hMC['Jpsi'],  'ntOriginal':hMC['JpsiCascade'],   'cut':'id==443',            'cutrec':'&&Jpsi==443'}
   category['_Cascadeprim'] = {'nt':hMC['Jpsi'],  'ntOriginal':hMC['JpsiCascade'],   'cut':'id==443&&mE>399.999','cutrec':'&&Jpsi==443&&Pmother>399.999'}
   category['_P8prim']      = {'nt':hMC['JpsiP8'],'ntOriginal':hMC['JpsiP8_Primary'],'cut':'id==443',            'cutrec':'&&Jpsi==443'}
   colors = {}
   colors['_Cascade']=ROOT.kMagenta
   colors['_Cascadeprim']=ROOT.kRed
   colors['_P8prim']=ROOT.kGreen
   colors['Data'] = ROOT.kBlue
   v='mcor'
   ptCut = 1.4
   sptCut = str(ptCut)
   theCut =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1<300&&p2<300&&p1>20&&p2>20&&mcor>0.20'
   if v=='mcor': 
      theCut = theCut.replace('pt1','pt1cor')
      theCut = theCut.replace('pt2','pt2cor')
   theCutcosCS = theCut
   if withCosCSCut: theCutcosCS = theCut+'&&cosCScor>-0.5&&cosCScor<0.5'
   for z in category:
     ut.bookHist(hMC,'PandPt'+z,'P and Pt Jpsi '                     ,60,0.,300.,60,0.,6.)
     ut.bookHist(hMC,'PandPt'+z+'_rec','P and Pt Jppsi reconstructed',60,0.,300.,60,0.,6.)
     ut.bookHist(hMC,'YandPt'+z,'rapidity of original ',              100,-2.,2., 60, 0.,6.)
     ut.bookHist(hMC,'YandPt'+z+'_rec','rapidity of reconstructed ',  100,-2.,2., 60, 0.,6.)
#
   ROOT.gROOT.cd()
   hMC['dummy'].cd()
   variables = {'Ypt':'sqrt(px*px+py*py):0.5*log((E+pz)/(E-pz))-'+str(y_beam),
                'ppt':'sqrt(px*px+py*py):sqrt(px*px+py*py+pz*pz)'}
   for z in category:
     category[z]['ntOriginal'].Draw(variables['ppt']+'>>PandPt'+z,                  category[z]['cut'])
     category[z]['nt'].Draw('PtTRUE:PTRUE>>PandPt'+z+'_rec',theCutcosCS+category[z]['cutrec'])
     category[z]['ntOriginal'].Draw(variables['Ypt']+'>>YandPt'+z,category[z]['cut'])
     category[z]['nt'].Draw('PtTRUE:(YTRUE-'+str(y_beam)+')>>YandPt'+z+'_rec',theCutcosCS+category[z]['cutrec'])
#
     # divide all MC true distributions by factor 0.5 due to cosCS cut only applied at reco level
     # TEfficiency does not like weights, change entries and errors by hand
     if withCosCSCut:
        for x in [hMC['PandPt'+z],hMC['YandPt'+z]]:
           for nx in range(1,x.GetNbinsX()+1):
              for ny in range(1,x.GetNbinsY()+1):
                x.SetBinContent(nx,ny,x.GetBinContent(nx,ny)/2.)
             # x.SetBinError(nx,ny,x.GetBinError(nx,ny)/2.)
# make projections
     hMC['P'+z]        = hMC['PandPt'+z].ProjectionX('P'+z)
     hMC['P'+z+'_rec'] = hMC['PandPt'+z+'_rec'].ProjectionX('P'+z+'_rec')
     print "make eff ",'PEff'+z
     hMC['PEff'+z]=ROOT.TEfficiency(hMC['P'+z+'_rec'],hMC['P'+z])
     hMC['Y'+z]     = hMC['YandPt'+z].ProjectionX('Y'+z)
     hMC['Y'+z+'_rec'] = hMC['YandPt'+z+'_rec'].ProjectionX('Y'+z+'_rec')
     print "make eff ",'YEff'+z
     hMC['YEff'+z]=ROOT.TEfficiency(hMC['Y'+z+'_rec'],hMC['Y'+z])
     hMC['YEff'+z].Draw()
     hMC['dummy'].Update()
     hMC['YEff'+z+'_graph']= hMC['YEff'+z].GetPaintedGraph()
     hMC['YEff'+z+'_graph'].GetXaxis().SetRangeUser(0.,2.)
     hMC['YEff'+z+'_graph'].GetYaxis().SetRangeUser(0.,0.8)
     hMC['YEff'+z].Draw()
   for z in category:
        hMC['YEff'+z].SetLineColor(colors[z])
        hMC['YEff'+z].Draw('same')
   myPrint(hMC['dummy'],'JpsiEfficiencies')

# problem, how to apply to data, where there is prec and multiple scattering, dE/dx
# check how much is the ycor different from ytrue, sigma y-ycor = 0.1
   makeProjection('ycor',0.,2.,'y_{CMS}',theCutcosCS,nBins=20,ntName='JpsiP8',printout=False,fixSignal=False)
   cases = {'dataJpsi':hData["Jpsiycor"],'MCJpsiP8':hMC["mc-Jpsiycor"]}
   for c in cases: 
     for z in category:
       hMC[c+"ycor_effCorrected"+z]  = cases[c].Clone(c+"ycor_effCorrected"+z)
       hjpsi   = hMC[c+"ycor_effCorrected"+z]
       for n in range(1,cases[c].GetNbinsX()+1): 
          x = cases[c].GetBinCenter(n)
          y = cases[c].GetBinContent(n)
          yerr = cases[c].GetBinError(n)
          e = hMC['YEff'+z+'_graph'].Eval(x)
          if e>0.01:
           hjpsi.SetBinContent(n,y/e)
           hjpsi.SetBinError(n,yerr/e)
          else:
           hjpsi.SetBinContent(n,0.)
           hjpsi.SetBinError(n,0.)
       hMC['dummy'].cd()
       hjpsi.Draw()
     for z in category:
         hjpsi = hMC[c+"ycor_effCorrected"+z]
         hjpsi.SetLineColor(colors[z])
         hjpsi.Draw('same')
     myPrint(hMC['dummy'],c+'YieldsEffCorrected')
   lumi  = 30.7 # pb-1
   elumi = 0.7
   ylimits= [0.4,0.6]
   frac = hMC['etaNA50'].Integral(ylimits[0],ylimits[1])/hMC['etaNA50'].Integral(-0.425,0.575)
   NA50fraction  = frac * 3.994
   eNA50fraction = frac * 0.087
   hMC['mix']=hMC["dataJpsiycor_effCorrected_P8prim"]
   hMC['mix'].Add(hMC["dataJpsiycor_effCorrected_Cascade"])
   hMC['mix'].Scale(0.5)
   for z in category:
        print "results with "+z
        hjpsi = hMC["dataJpsiycor_effCorrected"+z]
        bw = hjpsi.GetBinWidth(1)/2.
        NsignalNA50 = hjpsi.Integral(hjpsi.FindBin(ylimits[0]+bw),hjpsi.FindBin(ylimits[1]-bw))
        Nsignal     = hjpsi.Integral(hjpsi.FindBin(ylimits[0]+bw),hjpsi.FindBin(1.8-bw))
        print "N in "+str(ylimits[0])+"<y<1.8: %5.1F   Xsection=%5.2Fnb"%(Nsignal,Nsignal/lumi/1000.)
        print "N in "+str(ylimits[0])+"<y<0.6: %5.1F   Xsection=%5.2Fnb  Muflux/NA50=%5.2F"%(NsignalNA50,NsignalNA50/lumi/1000.,NsignalNA50/lumi/1000./NA50fraction)
#
   hMC['etaNA50'].SetParameter(0,9000.)
   hMC['etaNA50'].SetParameter(1,hMC['etaNA50'].GetParameter(1))
   hMC['etaNA50'].SetParameter(2,hMC['etaNA50'].GetParameter(2))
   hMC['mix'].Fit(hMC['etaNA50'],'','',0.3,1.8)
   c = "dataJpsi"
   hMC[c+"ycor_effCorrected_Cascade"].SetMinimum(0)
   hMC[c+"ycor_effCorrected_Cascade"].Draw()
   for z in category:
         hjpsi = hMC[c+"ycor_effCorrected"+z]
         hjpsi.SetLineColor(colors[z])
         hjpsi.Draw('same')
   myPrint(hMC['dummy'],"JpsiYieldsEffCorrectedWithNA50")
   for z in ['_Cascade','_P8prim']:
     ntname = 'Jpsi'
     if z=='_P8prim': ntname = 'JpsiP8'
     ROOT.gROOT.cd()
     makeProjection('cosCScor',-1.,1.,'cosCScor',theCut,nBins=20,ntName=ntname,printout=False,fixSignal=False)
     hMC['mc-JpsicosCScor'+z]=hMC['mc-JpsicosCScor'].Clone('mc-JpsicosCScor'+z)
   hMC['dummy'].cd()
   hData['JpsicosCScor'].SetLineColor(colors['Data'])
   hData['JpsicosCScor'].Draw()
   for z in ['_Cascade','_P8prim']:
      scale(hMC['mc-JpsicosCScor'+z],hData['JpsicosCScor'])
      hMC['mc-JpsicosCScor'+z].SetLineColor(colors[z])
      hMC['mc-JpsicosCScor'+z].Draw('same')
      hMC['JpsicosCScorEffcorrected'+z]=hData['JpsicosCScor'].Clone('JpsicosCScorEffcorrected'+z)
      hMC['JpsicosCScorEffcorrected'+z].Divide(hMC['mc-JpsicosCScor'+z])
      hMC['JpsicosCScorEffcorrected'+z].SetLineColor(colors[z])
   myPrint(hMC['dummy'],'cosCScorDataMC')
   hMC['JpsicosCScorEffcorrected_Cascade'].Draw()
   hData['polFun'] = ROOT.TF1('polFun','[0]*(1+x**2*[1])',2)
   T = ROOT.TLatex()
   dy = 0.15
   for z in ['_Cascade','_P8prim']:   
       hMC['JpsicosCScorEffcorrected'+z].Draw('same')
       rc = hMC['JpsicosCScorEffcorrected'+z].Fit(hData['polFun'],'S','',-0.8,0.8)
       fitResult = rc.Get()
       txt  = "%s: polarization CS #Lambda=%5.2F +/- %5.2F"%(z,fitResult.Parameter(1),fitResult.ParError(1))
       T.SetTextColor(colors[z])
       T.DrawLatexNDC(0.2,dy,txt)
       hMC['JpsicosCScorEffcorrected'+z].GetFunction('polFun').SetLineColor(colors[z])
       dy+=0.08
   hMC['dummy'].Update()
   myPrint(hMC['dummy'],'cosCScorDataEffCorrected')

def diMuonAnalysis():
 y_beam = yBeam()
 loadNtuples()
 sTreeData  = hData['f'].nt
# make normalization
    # covered cases: cuts = '',      simpleEffCor=0.024, simpleEffCorMu=0.024
    # covered cases: cuts = 'Chi2<', simpleEffCor=0.058, simpleEffCorMu=0.058
    # covered cases: cuts = 'All', simpleEffCor=0.058,   simpleEffCorMu=0.129
    # 1GeV mbias,      1.806 Billion PoT 
    # 10GeV MC,       66.02 Billion PoT 
    # using 626 POT/mu-event and preliminary counting of good tracks -> 12.63 -> pot factor 7.02
    # using 710 POT/mu-event, full field
# 
 simpleEffCor = 0.024
 MCStats = {'1GeV': 1.806E9,'10GeV':66.02E9}
 mcSysError = 0.03
 daSysError = 0.021
 dataStats  = 324.75E9
 hMC['weights'] = {'1GeV': MCStats['1GeV']/dataStats/(1+simpleEffCor*2),'10GeV':MCStats['10GeV']/dataStats/(1+simpleEffCor*2)}
#
 ptCutList = [0.0,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]
 hData['fitResult'] = {}
 hMC['fitResult'] = {}
 sptCut = 'XYZ'
 theCutTemplate =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1<300&&p2<300&&p1>20&&p2>20&&mcor>0.20'
 ut.bookHist(hMC, 'mc_theta','cos theta mother - daughter1',100,-1,1.)
 ut.bookHist(hMC, 'mc_thetaJ','cos theta mother - daughter1 Jpsi',100,-1,1.)
 ut.bookHist(hData, 'theta','cos theta mother - daughter1',100,-1,1.)
 ut.bookCanvas(hMC,'tTheta','costheta',900,600,1,1)
 ut.bookCanvas(hMC,'tMass','mass',900,600,1,1)
 hMC['mc_theta'].SetLineColor(ROOT.kRed)
 hMC['mc_thetaJ'].SetLineColor(ROOT.kMagenta)
 theCut = theCutTemplate.replace('XYZ','0')
 ROOT.gROOT.cd()
 myDraw('cosTheta>>mc_thetaJ',theCut+'&&Jpsi==443')
 myDraw('cosTheta>>mc_theta',theCut)
 sTreeData.Draw('cosTheta>>theta',theCut)
 hMC['tTheta'].cd(1)
 hMC['mc_theta'].Scale(1./hMC['mc_theta'].GetEntries())
 hMC['mc_thetaJ'].Scale(1./hMC['mc_thetaJ'].GetEntries())
 hData['theta'].Scale(1./hData['theta'].GetEntries())
 hMC['mc_theta'].Draw()
 hMC['mc_thetaJ'].Draw('same')
 hData['theta'].Draw('same')
 myPrint(hMC['tTheta'],'dimuon-theta')
 ut.bookHist(hMC, 'mc_IP','IP',100,0.,100.)
 ut.bookHist(hMC, 'mc_IPJ','IP',100,0.,100.)
 ut.bookHist(hData, 'IP','IP',100,0.,100.)
 ut.bookCanvas(hMC,'tIP','distance to target',900,600,1,1)
 hMC['mc_IP'].SetLineColor(ROOT.kRed)
 hMC['mc_IPJ'].SetLineColor(ROOT.kMagenta)
 myDraw('Ip1>>mc_IPJ',theCut+'&&Jpsi==443')
 myDraw('Ip1>>mc_IP',theCut)
 sTreeData.Draw('Ip1>>IP',theCut)
 myDraw('Ip2>>+mc_IPJ',theCut+'&&Jpsi==443')
 myDraw('Ip2>>+mc_IP',theCut)
 sTreeData.Draw('Ip2>>+IP',theCut)
 hMC['tIP'].cd()
 hMC['mc_IP'].Scale(1./hMC['mc_IP'].GetEntries())
 hMC['mc_IPJ'].Scale(1./hMC['mc_IPJ'].GetEntries())
 hData['IP'].Scale(1./hData['IP'].GetEntries())
 hMC['mc_IP'].Draw()
 hMC['mc_IPJ'].Draw('same')
 hData['IP'].Draw('same')
 myPrint(hMC['tIP'],'dimuon-IP')
 ut.bookHist(hMC, 'm_MC','inv mass;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
 ut.bookHist(hMC, 'm_MClow','inv mass;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
 hMC['dummy'].cd()
 colors = {221:ROOT.kBlue,223:ROOT.kCyan,113:ROOT.kGreen,331:ROOT.kOrange,333:ROOT.kRed,443:ROOT.kMagenta}
 nmax = 0
 for j in colors:
   pname = PDG.GetParticle(j).GetName()
   hname = 'Mass_'+pname.replace('/','')
   hMC[hname]=hMC['m_MClow'].Clone(hname)
   hMC[hname].SetTitle('inv mass '+PDG.GetParticle(j).GetName()+' ;M [GeV/c^{2}]')
   hMC[hname].SetLineColor(colors[j])
   hMC[hname].SetStats(0)
   myDraw('m>>'+hname,'Jpsi=='+str(j))
   if hMC[hname].GetMaximum()>nmax: nmax = hMC[hname].GetMaximum()
   hname = 'Masscor_'+pname.replace('/','')
   hMC[hname]=hMC['m_MClow'].Clone(hname)
   hMC[hname].SetTitle('inv mass '+PDG.GetParticle(j).GetName()+' ;M [GeV/c^{2}]')
   hMC[hname].SetLineColor(colors[j])
   hMC[hname].SetStats(0)
   myDraw('mcor>>'+hname,'Jpsi=='+str(j))
   if hMC[hname].GetMaximum()>nmax: nmax = hMC[hname].GetMaximum()
 for z in ['','cor']:
  first = True
  hMC['lMassMC'+z]=ROOT.TLegend(0.7,0.7,0.95,0.95)
  for j in colors:
    pname = PDG.GetParticle(j).GetName()
    hname = 'Mass'+z+'_'+pname.replace('/','')
    hMC[hname].SetStats(0)
    if first:
       first = False
       hMC[hname].SetMaximum(nmax*1.1)
       hMC[hname].SetTitle(';M [GeV/c^{2}]')
       hMC[hname].Draw()
    else:
       hMC[hname].Draw('same')
    hMC['lMassMC'+z].AddEntry(hMC[hname],pname,'PL')
  hMC['lMassMC'+z].Draw()
  myPrint(hMC['dummy'],'MCdiMuonMass'+z)


 bw = hMC['m_MC'].GetBinWidth(1)
 hMC['myGauss'] = ROOT.TF1('gauss','abs([0])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-[1])/[2])**2)\
            +abs([3])*'+str(bw)+'/(abs([5])*sqrt(2*pi))*exp(-0.5*((x-[4])/[5])**2)+abs( [6]+[7]*x+[8]*x**2 )\
            +abs([9])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-(3.6871 + [1] - 3.0969))/[2])**2)',10)
 myGauss = hMC['myGauss']
 # doesn't help really theCutTemplate +=  '&&abs(cosTheta)<0.8' 
 vText={'m':'inv mass and fits','mcor':'inv mass, dE and direction corrected, and fits','mcor2':'inv mass, direction corrected, and fits'}
 for v in vText:
  for ptCut in ptCutList:
   sptCut = str(ptCut)
   ut.bookHist(hMC, 'mc-'+v+'_'+sptCut,'inv mass MC;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
   ut.bookHist(hMC, 'mc-'+v+'_Jpsi_'+sptCut,'inv mass Jpsi MC matched;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
   ut.bookHist(hData,v+'_'+sptCut,'inv mass DATA;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
   ut.bookHist(hData,'SS-'+v+'_'+sptCut,'SS inv mass DATA;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
   ut.bookHist(hMC, 'SS-mc-'+v+'_'+sptCut,'SS inv mass MC;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
   hData['SS-'+v+'_'+sptCut].SetLineColor(ROOT.kRed)
   hMC['SS-mc-'+v+'_'+sptCut].SetLineColor(ROOT.kRed)
#
   theCut =  theCutTemplate.replace('XYZ',sptCut)
   if v=='mcor': 
      theCut = theCut.replace('pt1','pt1cor')
      theCut = theCut.replace('pt2','pt2cor')
   ROOT.gROOT.cd()
   hMC['dummy'].cd()
   sTreeData.Draw(v+'>>'+v+'_'+sptCut,theCut)
   sTreeData.Draw(v+'>>SS-'+v+'_'+sptCut,theCut.replace('chi21*chi22<0','chi21*chi22>0'))
   myDraw(v+'>>mc-'+v+'_'+sptCut ,theCut)
   myDraw(v+'>>SS-mc-'+v+'_'+sptCut ,theCut.replace('chi21*chi22<0','chi21*chi22>0'))
   myDraw(v+'>>mc-'+v+'_Jpsi_'+sptCut ,theCut+"&&Jpsi==443")

  ut.bookCanvas(hMC,'fits'+v,vText[v],1800,800,5,4)
  j = 1
  for ptCut in  ptCutList:
   sptCut = str(ptCut)
   tc = hMC['fits'+v].cd(j)
   init_Gauss(myGauss)
   rc = hMC['mc-'+v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
   fitResult = rc.Get()
   if fitResult.Parameter(0)+fitResult.Parameter(3)>hMC['mc-'+v+'_'+sptCut].GetEntries()*1.5:
     myGauss.FixParameter(3,0)
     myGauss.FixParameter(4,1.)
     myGauss.FixParameter(5,1.)
     rc = hMC['mc-'+v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
     fitResult = rc.Get()
   hMC['fitResult'][ptCut] = {}
   for n in range(10):
    hMC['fitResult'][ptCut][myGauss.GetParName(n)] = [fitResult.Parameter(n),fitResult.ParError(n)]
   if v=='mcor':
    myGauss.FixParameter(1,fitResult.Parameter(1))
    myGauss.FixParameter(2,fitResult.Parameter(2))
    myGauss.ReleaseParameter(9)
    rc = hMC['mc-'+v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
    myGauss.ReleaseParameter(1)
    myGauss.ReleaseParameter(2)
    rc = hMC['mc-'+v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
    fitResult = rc.Get()
    hMC['fitResult'][ptCut][myGauss.GetParName(9)] = [fitResult.Parameter(9),fitResult.ParError(9)]
   hMC['mc-'+v+'_Jpsi_'+sptCut].SetLineColor(ROOT.kMagenta)
   hMC['mc-'+v+'_Jpsi_'+sptCut].Draw('same')
   hMC['SS-mc-'+v+'_'+sptCut].Draw('same')
   tc.Update()
   stats = tc.GetPrimitive('stats')
   stats.SetOptFit(10111)
   stats.SetFitFormat('5.4g')
   stats.SetX1NDC(0.41)
   stats.SetY1NDC(0.41)
   stats.SetX2NDC(0.99)
   stats.SetY2NDC(0.84)
   tc.Update()
# data
   tc = hMC['fits'+v].cd(j+5)
   rc = hData[v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
   fitResult = rc.Get()
   hData['fitResult'][ptCut] = {}
   for n in range(10):
    hData['fitResult'][ptCut][myGauss.GetParName(n)] = [fitResult.Parameter(n),fitResult.ParError(n)]
   if v=='mcor':
# psi(2S) 
    myGauss.FixParameter(1,fitResult.Parameter(1))
    myGauss.FixParameter(2,fitResult.Parameter(2))
    myGauss.ReleaseParameter(9)
    rc = hData[v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
    myGauss.ReleaseParameter(1)
    myGauss.ReleaseParameter(2)
    rc = hData[v+'_'+sptCut].Fit(myGauss,'S','',0.5,5.)
    fitResult = rc.Get()
    hData['fitResult'][ptCut][myGauss.GetParName(9)] = [fitResult.Parameter(9),fitResult.ParError(9)]
   hData['SS-'+v+'_'+sptCut].Draw('same')
   tc.Update()
   stats = tc.GetPrimitive('stats')
   stats.SetOptFit(10011)
   stats.SetFitFormat('5.4g')
   stats.SetX1NDC(0.41)
   stats.SetY1NDC(0.41)
   stats.SetX2NDC(0.99)
   stats.SetY2NDC(0.84)
   tc.Update()
   j+=1
   if j==6: j+=5
   hMC['tMass'].cd()
   hMC['mc-'+v+'_'+sptCut].Draw()
   hMC['SS-mc-'+v+'_'+sptCut].Draw('same')
   myPrint(hMC['tMass'],'mc_dimuon_'+v+sptCut)
   hData[v+'_'+sptCut].Draw()
   hData['SS-'+v+'_'+sptCut].Draw('same')
   myPrint(hMC['tMass'],'m_dimuon_'+v+sptCut)
  hMC['fits'+v].Update()
  myPrint(hMC['fits'+v],v+'_dimuon_all')
#
  param = {0:'Signal',1:'Mass',2:'Sigma'}
  txt   = {0:'; #it{p}_{T}>X GeV/c; Nsignal',1:'; #it{p}_{T}>X GeV/c; M [GeV/c^{2}]',2:';#it{p}_{T}>X GeV/c; #sigma [GeV/c^{2}]'}
  choices = {'MC':hMC,'Data':hData}
  for c in choices:
   h=choices[c]
   for p in range(3):
    hname = 'evolution'+v+param[p]+c
    ut.bookHist(h,hname,v+' evolution of '+param[p]+txt[p],20,0., 2.)
    for ptCut in ptCutList:
        k = h[hname].FindBin(ptCut)
        h[hname].SetBinContent(k,h['fitResult'][ptCut][myGauss.GetParName(p)][0])
        h[hname].SetBinError(k,h['fitResult'][ptCut][myGauss.GetParName(p)][1])
        k+=1
  ut.bookCanvas(hMC,'evolutionC'+v,'evolution',1600,500,3,1)
  for p in range(3):
   tc = hMC['evolutionC'+v].cd(p+1)
   hname = 'evolution'+v+param[p]
   resetMinMax(hMC[hname+'MC'])
   resetMinMax(hData[hname+'Data'])
   hMC[hname+'MC'].SetLineColor(ROOT.kRed)
   hMC[hname+'MC'].GetXaxis().SetRangeUser(0.9,2.0)
   hData[hname+'Data'].GetXaxis().SetRangeUser(0.9,2.0)
   hMC[hname+'MC'].SetMaximum(1.1*max(hMC[hname+'MC'].GetMaximum(),hData[hname+'Data'].GetMaximum()))
   if p==1: 
        hMC[hname+'MC'].SetMaximum(3.5)
        hMC[hname+'MC'].SetMinimum(2.)
   if p==2: 
        hMC[hname+'MC'].SetMaximum(0.6)
        hMC[hname+'MC'].SetMinimum(0.3)
   hMC[hname+'MC'].Draw()
   hData[hname+'Data'].Draw('same')
  myPrint(hMC['evolutionC'+v],'EvolutionOfCuts_dimuon'+v)
# truth momentum
 ut.bookCanvas(hMC,'kin','Jpsi kinematics',1800,1000,3,2)
 ut.bookHist(hMC, 'pt','pt',100,0.,5.)
 ut.bookHist(hMC, 'ptTrue','pt vs ptTrue',100,0.,5.,100,0.,5.)
 ut.bookHist(hMC, 'pTrue' ,'p vs pTrue',100,0.,400.,100,0.,400.)
 ut.bookHist(hMC, 'delpTrue' ,'pTrue - p',100,-20.,70.)
 ut.bookHist(hMC, 'delptTrue' ,'ptTrue - pt',100,-2.,2.)
 tc = hMC['kin'].cd(1)
 myDraw('p:PTRUE>>pTrue','Jpsi==443')
 myDraw('pt:PtTRUE>>ptTrue','Jpsi==443')
 myDraw('PTRUE-p>>delpTrue','Jpsi==443')
 myDraw('PtTRUE-pt>>delptTrue','Jpsi==443')
 ROOT.gROOT.cd()
 tc = hMC['kin'].cd(1)
 hMC['pTrue'].Draw('colz')
 tc = hMC['kin'].cd(4)
 hMC['delpTrue'].Fit('gaus')
 tc.Update()
 stats = tc.GetPrimitive('stats')
 stats.SetOptFit(10011)
 stats.SetFitFormat('5.4g')
 stats.SetX1NDC(0.50)
 stats.SetY1NDC(0.41)
 stats.SetX2NDC(0.99)
 stats.SetY2NDC(0.84)
 tc.Update()
 tc = hMC['kin'].cd(2)
 hMC['ptTrue'].Draw('colz')
 tc = hMC['kin'].cd(5)
 hMC['delptTrue'].Fit('gaus')
 tc.Update()
 stats = tc.GetPrimitive('stats')
 stats.SetOptFit(10011)
 stats.SetFitFormat('5.4g')
 tc.Update()
 tc = hMC['kin'].cd(3)
 hMC['ptTrue_x']=hMC['ptTrue'].ProjectionX('ptTrue_x')
 hMC['ptTrue_y']=hMC['ptTrue'].ProjectionY('ptTrue_y')
 hMC['pTrue_x']=hMC['pTrue'].ProjectionX('pTrue_x')
 hMC['pTrue_y']=hMC['pTrue'].ProjectionY('pTrue_y')
 hMC['ptTrue_x'].SetLineColor(ROOT.kRed)
 hMC['pTrue_x'].SetLineColor(ROOT.kRed)
 hMC['pTrue_x'].Draw()
 hMC['pTrue_y'].Draw('same')
 tc = hMC['kin'].cd(6)
 hMC['ptTrue_x'].Draw()
 hMC['ptTrue_y'].Draw('same')
 myPrint(hMC['kin'],'JpsiKinematics')
# low mass
 ut.bookCanvas(hMC,'lkin','low mass kinematics',1800,1000,3,2)
 ut.bookHist(hMC, 'lpt','pt',100,0.,5.)
 ut.bookHist(hMC, 'lptTrue','pt vs ptTrue',100,0.,5.,100,0.,5.)
 ut.bookHist(hMC, 'lpTrue' ,'p vs pTrue',100,0.,400.,100,0.,400.)
 ut.bookHist(hMC, 'ldelpTrue' ,'pTrue - p',100,-20.,70.)
 ut.bookHist(hMC, 'ldelptTrue' ,'ptTrue - pt',100,-2.,2.)
 tc = hMC['lkin'].cd(1)
 select=""
 for c in colors:
  if c==443: continue
  select+="||Jpsi=="+str(c)
 select = select[2:]
 myDraw('p:PTRUE>>lpTrue',select)
 myDraw('pt:PtTRUE>>lptTrue',select)
 myDraw('PTRUE-p>>ldelpTrue',select)
 myDraw('PtTRUE-pt>>ldelptTrue',select)
 tc = hMC['lkin'].cd(1)
 hMC['lpTrue'].Draw('colz')
 tc = hMC['lkin'].cd(4)
 hMC['ldelpTrue'].Fit('gaus')
 tc.Update()
 stats = tc.GetPrimitive('stats')
 stats.SetOptFit(10011)
 stats.SetFitFormat('5.4g')
 stats.SetX1NDC(0.50)
 stats.SetY1NDC(0.41)
 stats.SetX2NDC(0.99)
 stats.SetY2NDC(0.84)
 tc.Update()
 tc = hMC['lkin'].cd(2)
 hMC['lptTrue'].Draw('colz')
 tc = hMC['lkin'].cd(5)
 hMC['ldelptTrue'].Fit('gaus')
 tc.Update()
 stats = tc.GetPrimitive('stats')
 stats.SetOptFit(10011)
 stats.SetFitFormat('5.4g')
 tc.Update()
 tc = hMC['lkin'].cd(3)
 hMC['lptTrue_x']=hMC['lptTrue'].ProjectionX('lptTrue_x')
 hMC['lptTrue_y']=hMC['lptTrue'].ProjectionY('lptTrue_y')
 hMC['lpTrue_x']=hMC['lpTrue'].ProjectionX('lpTrue_x')
 hMC['lpTrue_y']=hMC['lpTrue'].ProjectionY('lpTrue_y')
 hMC['lptTrue_x'].SetLineColor(ROOT.kRed)
 hMC['lpTrue_x'].SetLineColor(ROOT.kRed)
 hMC['lpTrue_x'].Draw()
 hMC['lpTrue_y'].Draw('same')
 tc = hMC['lkin'].cd(6)
 hMC['lptTrue_x'].Draw()
 hMC['lptTrue_y'].Draw('same')
 myPrint(hMC['lkin'],'LowMassKinematics')

# muon dEdx
 ut.bookCanvas(hMC,'TdEdx','dEdx',1800,1200,1,3)
 tc = hMC['TdEdx'].cd(1)
 ut.bookHist(hMC, 'delpTrue2' ,'p-pTrue vs p',40,0.,400.,50,-50.,50.)
 ut.bookHist(hMC, 'delpTrue2True' ,'p-pTrue vs pTrue',40,0.,400.,50,-50.,50.)
 myDraw('(p1-p1True):p1>>delpTrue2','')
 myDraw('(p2-p2True):p2>>+delpTrue2','') # applying cuts does not make a difference
 myDraw('(p1-p1True):p1True>>delpTrue2True','')
 myDraw('(p2-p2True):p2True>>+delpTrue2True','')
 ROOT.gROOT.cd()
 hMC['meanLoss']=hMC['delpTrue2'].ProjectionX('meanLoss')
 hMC['meanLossTrue']=hMC['delpTrue2True'].ProjectionX('meanLossTrue')
 for n in range(1,hMC['delpTrue2'].GetXaxis().GetNbins()+1):
   tmp = hMC['delpTrue2'].ProjectionY('tmp',n,n)
   # hMC['meanLoss'].SetBinContent(n, tmp.GetBinCenter(ut.findMaximumAndMinimum(tmp)[3]))
   hMC['meanLoss'].SetBinContent(n, tmp.GetMean())
   hMC['meanLoss'].SetBinError(n,tmp.GetRMS())
   tmp = hMC['delpTrue2True'].ProjectionY('tmp',n,n)
   hMC['meanLossTrue'].SetBinContent(n, tmp.GetMean())
   hMC['meanLossTrue'].SetBinError(n,tmp.GetRMS())
 hMC['meanLoss'].Draw()
 hMC['meanLoss'].Fit('pol2','S','',20.,300.)
 tc =hMC['TdEdx'].cd(2)
 hMC['meanLossTrue'].Draw()
 hMC['meanLossTrue'].Fit('pol2','S','',20.,300.)
 tc =hMC['TdEdx'].cd(3)
 ut.bookHist(hMC, 'delp' ,'p-pTrue',50,-50.,50.)
 hMC['delpFunOfPtCut']=ROOT.TGraph()
 dp = 0.1
 ptCut = 0.0
 for k in range(20):
  myDraw('(p1-p1True)>>delp','Jpsi==443&&pt1>'+str(ptCut+dp/2.)+'&&pt1<'+str(ptCut-dp/2.))
  myDraw('(p2-p2True)>>+delp','Jpsi==443&&pt2>'+str(ptCut+dp/2.)+'&&pt1<'+str(ptCut-dp/2.))
  dE = hMC['delp'].GetMean()
  hMC['delpFunOfPtCut'].SetPoint(k,ptCut,dE)
  ptCut+=dp
 ut.bookHist(hMC, 'delpt' ,'delpt',20,0.,2.)
 hMC['delpt'].SetMaximum(0.0)
 hMC['delpt'].SetMinimum(-10.0)
 hMC['delpt'].Draw()
 hMC['delpFunOfPtCut'].Draw()
# -7.97  -1.52 * ptCut + 0.93 * ptCut**2

 v='mcor'
 ptCut = 1.4
 sptCut = str(ptCut)
 theCut =  theCutTemplate.replace('XYZ',sptCut)
 if v=='mcor': 
      theCut = theCut.replace('pt1','pt1cor')
      theCut = theCut.replace('pt2','pt2cor')
# yield as function of pt
 makeProjection('ptcor',0.,2.,'#it{p}_{T} [GeV/c^{2}]',theCut)
# yield as function of y
 makeProjection('ycor',0.,2.,'y_{CMS}',theCut)
# yield as function of p
 makeProjection('pcor',20.,220.,'#it{p} [GeV/c^{2}]',theCut)
# polarization
 makeProjection('cosCScor',-1.,1.,'cos{theta}CS',theCut)
 # fit for polarization
 hData['polFun'] = ROOT.TF1('polFun','[0]*(1+x**2*[1])',2)
 rc = hData['JpsicosCScor'].Fit(hData['polFun'],'S','',-1.,1.)
 fitResult = rc.Get()
 print "polarization CS #Lambda=%5.2F +/- %5.2F"%(fitResult.Parameter(1),fitResult.ParError(1))
 makeProjection('cosTheta',-1.,1.,'cos{theta}',theCut)
 rc = hData['JpsicosTheta'].Fit(hData['polFun'],'S','',-1.,1.)
 fitResult = rc.Get()
 print "polarization CS #Lambda=%5.2F +/- %5.2F"%(fitResult.Parameter(1),fitResult.ParError(1))

# low mass in bins of p and pt
 ut.bookHist(hMC, 'mc-lowMassppt','low mass pt vs p;#it{p} [GeV/c];#it{p}_{T} [GeV/c]',50,0.,400.,50,0.,5.)
 ut.bookHist(hData, 'lowMassppt','low mass pt vs p;#it{p} [GeV/c];#it{p}_{T} [GeV/c]',50,0.,400.,50,0.,5.)
 sptCut = '0'
 theCut =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1>20&&p2>20'
 if v=='mcor': 
      theCut = theCut.replace('pt1','pt1cor')
      theCut = theCut.replace('pt2','pt2cor')
 ut.bookHist(hMC, 'mc-lowMassAll','low mass ;M [GeV/c^[2]]',100,0.,5.)
 ut.bookHist(hData, 'lowMassAll', 'low mass ;M [GeV/c^[2]]',100,0.,5.)
 myDraw('mcor>>mc-lowMassAll',theCut)
 sTreeData.Draw('mcor>>lowMassAll',theCut)
 hMC['mc-lowMassAll'].Scale(1./hMC['weights']['10GeV'])
 tc=hMC['dummy'].cd()
 hMC['mc-lowMassAll'].SetLineColor(ROOT.kMagenta)
 hData['lowMassAll'].Draw()
 hMC['mc-lowMassAll'].Draw('same')
 myPrint(hMC['dummy'],'lowMassAll')
 theCut =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1>20&&p2>20&&mcor>0.4&&mcor<2.0'
 if v=='mcor': 
      theCut = theCut.replace('pt1','pt1cor')
      theCut = theCut.replace('pt2','pt2cor')
 myDraw('ptcor:pcor>>mc-lowMassppt',theCut)
 sTreeData.Draw('pt:p>>lowMassppt',theCut)
 hMC['mc-lowMassppt'].Scale(1./hMC['weights']['10GeV'])
 ut.bookCanvas(hData,'lowMass','lowMass summary',1600,1200,1,2)
 hData['lowMass1'] = hData['lowMass'].cd(1)
 hData['lowMass1'].Divide(2,1)
 tc = hData['lowMass1'].cd(1)
 tc.SetLogy(1)
 hData['lowMassppt_projx'] = hData['lowMassppt'].ProjectionX('lowMassppt_projx')
 hData['lowMassppt_projx'].GetXaxis().SetRangeUser(40.,400.)
 hData['lowMassppt_projx'].SetStats(0)
 hData['lowMassppt_projx'].SetTitle('')
 hData['lowMassppt_projx'].Draw()
 hMC['mc-lowMassppt_projx'] = hMC['mc-lowMassppt'].ProjectionX('mc-lowMassppt_projx')
 hMC['mc-lowMassppt_projx'].SetLineColor(ROOT.kMagenta)
 hMC['mc-lowMassppt_projx'].Draw('same')
 tc = hData['lowMass1'].cd(2)
 tc.SetLogy(1)
 hData['lowMassppt_projy'] = hData['lowMassppt'].ProjectionY('lowMassppt_projy')
 hData['lowMassppt_projy'].SetStats(0)
 hData['lowMassppt_projy'].SetTitle('')
 hData['lowMassppt_projy'].Draw()
 hMC['mc-lowMassppt_projy'] = hMC['mc-lowMassppt'].ProjectionY('mc-lowMassppt_projy')
 hMC['mc-lowMassppt_projy'].SetLineColor(ROOT.kMagenta)
 hMC['mc-lowMassppt_projy'].Draw('same')
 hMC['mc-ratioLowMass'] = hMC['mc-lowMassppt'].Clone('mc-ratioLowMass')
 hData['ratioLowMass']  = hData['lowMassppt'].Clone('ratioLowMass')
 hMC['mc-ratioLowMass'].Rebin2D(5,5)
 hData['ratioLowMass'].Rebin2D(5,5)
 asymVersion = False
 for mx in range(1,hMC['mc-ratioLowMass'].GetNbinsX()+1):
  for my in range(1,hMC['mc-ratioLowMass'].GetNbinsY()+1):
    Nmc = hMC['mc-ratioLowMass'].GetBinContent(mx,my)
    Nda = hData['ratioLowMass'].GetBinContent(mx,my)
    eNmc = hMC['mc-ratioLowMass'].GetBinError(mx,my)
    eNda = hData['ratioLowMass'].GetBinError(mx,my)
    if Nmc>10 and Nda>10:
         if asymVersion:
          R = (Nda-Nmc)/(Nda+Nmc)
          sig_data = ROOT.TMath.Sqrt(eNda**2+(Nda*daSysError)**2)
          sig_MC   = ROOT.TMath.Sqrt(eNmc**2+(Nmc*mcSysError)**2)
          e1 = 2*Nda/(Nda+Nmc)**2
          e2 = 2*Nmc/(Nda+Nmc)**2
          eR = ROOT.TMath.Sqrt( (e1*sig_MC)**2+(e2*sig_data)**2 )
         else: # ratio  version
          R = (Nda/Nmc)
          eR = ROOT.TMath.Sqrt( (R/Nmc*eNmc)**2+(R/Nda*eNda)**2 )
    else:      
         R  = 0. # -1      # R = 0
         eR = 0.
    hData['ratioLowMass'].SetBinContent(mx,my,R)
    hData['ratioLowMass'].SetBinError(mx,my,eR)
 tc = hData['lowMass'].cd(2)
 ROOT.gStyle.SetPaintTextFormat("5.2f")
 hData['ratioLowMass'].GetXaxis().SetRangeUser(40.,400.)
 hData['ratioLowMass'].SetStats(0)
 if asymVersion: hData['ratioLowMass'].SetTitle('data - MC / data + MC')
 else: hData['ratioLowMass'].SetTitle('data/MC')
 hData['ratioLowMass'].GetYaxis().SetRangeUser(0,3.)
 hData['ratioLowMass'].SetMarkerSize(1.8)
 hData['ratioLowMass'].Draw('texte')
 myPrint(hData['lowMass'],'lowMassSummary')

def makeProjection(proj,projMin,projMax,projName,theCut,nBins=9,ntName='10GeV',printout=True,fixSignal=False):
   y_beam = yBeam()
   v='mcor'
   fitOption = 'SQ'
   if printout: fitOption='S'
   sTreeData  = hData['f'].nt
   myGauss = hMC['myGauss']
   for k in ['MCbins'+proj,'mc-Jpsi'+proj]:
      if hMC.has_key(k): hMC.pop(k)
   for k in ['bins'+proj,'Jpsi'+proj]:
      if hData.has_key(k): hData.pop(k)
   ut.bookHist(hMC, 'mc-Jpsi'+proj, ' N J/#psi ;'+projName, nBins,projMin,projMax)
   ut.bookHist(hData,  'Jpsi'+proj, ' N J/#psi ;'+projName, nBins,projMin,projMax)
   N1 = int(ROOT.TMath.Sqrt(nBins))
   N2 = N1
   while(N2*N1<nBins): N2+=1
   ut.bookCanvas(hMC,'MCbins'+proj,'mass in bins '+projName,1800,1200,N1,N2)
   ut.bookCanvas(hData,'bins'+proj,'mass in bins '+projName,1800,1200,N1,N2)
   pmin = projMin
   delp = (projMax-projMin)/float(nBins)
   par={"MC":[],"Data":[]}
   for k in range(nBins):
     pmax = pmin+delp
     if hMC.has_key('mc-'+proj+str(k)): hMC.pop('mc-'+proj+str(k)).Delete()
     if hData.has_key(proj+str(k)): hData.pop(proj+str(k)).Delete()
     ut.bookHist(hMC,  'mc-'+proj+str(k),'inv mass MC '   +str(pmin)+'<'+proj+'<'+str(pmax)+';M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
     ut.bookHist(hData,proj+str(k),      'inv mass DATA ' +str(pmin)+'<'+proj+'<'+str(pmax)+';M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
     hMC['dummy'].cd()
     if proj=='ycor': cutExp = "ycor-"+str(y_beam)
     else:            cutExp = proj
# find initial fit parameters
     for m in par: 
       if m=='MC': 
           myDraw(v+'>>mc-'+proj+str(0),     theCut,ntName)
           histo = hMC['mc-'+proj+str(0)]
       else:       
           sTreeData.Draw(v+'>>'+proj+str(0),theCut)
           histo = hData[proj+str(0)]
       init_Gauss(myGauss)
       myGauss.FixParameter(1,3.1)
       myGauss.FixParameter(2,0.35)
       myGauss.FixParameter(4,1.1)
       myGauss.FixParameter(5,0.35)
       rc = histo.Fit(myGauss,fitOption,'',0.5,5.)
       myGauss.ReleaseParameter(1)
       myGauss.ReleaseParameter(2)
       myGauss.ReleaseParameter(4)
       myGauss.ReleaseParameter(5)
       histo.Draw()
       rc = histo.Fit(myGauss,fitOption,'',0.5,5.)
       fitResult = rc.Get()
       for n in range(11): par[m].append(fitResult.Parameter(n))
#
     sTreeData.Draw(v+'>>'+proj+str(k),theCut+'&&'+cutExp+'<'+str(pmax)+'&&'+cutExp+'>'+str(pmin))
     myDraw(v+'>>mc-'+proj+str(k),     theCut+'&&'+cutExp+'<'+str(pmax)+'&&'+cutExp+'>'+str(pmin),ntName)
     pmin = pmin+delp
     cases = {'MC':hMC['mc-'+proj+str(k)],'Data':hData[proj+str(k)]}
     for c in cases:
       histo = cases[c]
       if c=='MC': tc=hMC['MCbins'+proj].cd(k+1)
       else: tc=hData['bins'+proj].cd(k+1)
       init_Gauss(myGauss)
       for n in [1,2,4,5]:  myGauss.FixParameter(n,par[c][n])
       histo.Draw()
       if histo.GetEntries()>10:
        rc = histo.Fit(myGauss,fitOption,'',0.5,5.)
        if not fixSignal:
          myGauss.ReleaseParameter(1)
          myGauss.ReleaseParameter(2)
        myGauss.ReleaseParameter(4)
        myGauss.ReleaseParameter(5)
        rc = histo.Fit(myGauss,fitOption,'',0.5,5.)
        fitResult = rc.Get()
        N = fitResult.Parameter(0)
        if N<0: 
          myGauss.SetParameter(0,abs(N))
          rc = histo.Fit(myGauss,fitOption,'',0.5,5.)
          fitResult = rc.Get()
        N = fitResult.Parameter(0)
        E = fitResult.ParError(0)
        if fitResult.Parameter(1)>4 or fitResult.Parameter(1)<2: 
          N=0
          E=0
       else:
        N=0
        E=0
       tc.Update()
       stats = tc.GetPrimitive('stats')
       stats.SetOptFit(10011)
       stats.SetFitFormat('5.4g')
       stats.SetX1NDC(0.41)
       stats.SetY1NDC(0.41)
       stats.SetX2NDC(0.99)
       stats.SetY2NDC(0.84)
       tc.Update()
       if c=='MC': 
          hMC['mc-Jpsi'+proj].SetBinContent(k+1,N)
          hMC['mc-Jpsi'+proj].SetBinError(k+1,E)
       else: 
          hData['Jpsi'+proj].SetBinContent(k+1,N)
          hData['Jpsi'+proj].SetBinError(k+1,E)
   if printout:
     myPrint(hData['bins'+proj],'diMuonBins'+proj)
     myPrint(hMC['MCbins'+proj],'MC-diMuonBins'+proj)
     hMC['dummy'].cd()
     hMC['mc-Jpsi'+proj].SetLineColor(ROOT.kMagenta)
     hmax = 1.1*max(hMC['mc-Jpsi'+proj].GetMaximum(),hData['Jpsi'+proj].GetMaximum())
     hMC['mc-Jpsi'+proj].SetMaximum(hmax)
     hMC['mc-Jpsi'+proj].Draw()
     hData['Jpsi'+proj].Draw('same')
     myPrint(hMC['dummy'],'diMuonBins'+proj+'Summary')

import math
def init_twoCB(myCB,bw,ptCut,h,fromPrevFit=False):
   myCB.FixParameter(0,bw)
   myCB.SetParName(0,'binwidth')
   myCB.SetParName(1,'psi(1S)')
   myCB.SetParName(2,'Mass')
   myCB.SetParName(3,'Sigma')
   myCB.SetParName(4,'alpha')
   myCB.SetParName(5,'n')
   myCB.SetParName(6,'SignalLow')
   myCB.SetParName(7,'MeanLow')
   myCB.SetParName(8,'SigmaLow')
   myCB.SetParName(9,'alphaLow')
   myCB.SetParName(10,'nLow')
   myCB.SetParName(11,'p0')
   myCB.SetParName(12,'p1')
   myCB.SetParName(13,'psi(2S)')
   if not fromPrevFit:
    myCB.SetParameter(1,h['fitResult'][ptCut]['psi(1S)'][0])
    myCB.SetParameter(2,h['fitResult'][ptCut]['Mean'][0])
    myCB.SetParameter(3,h['fitResult'][ptCut]['Sigma'][0])
    myCB.SetParameter(4,0.3)
    myCB.SetParameter(5,3.5)
    myCB.SetParameter(6,h['fitResult'][ptCut]['SignalLow'][0])
    myCB.SetParameter(7,h['fitResult'][ptCut]['MeanLow'][0])
    myCB.SetParameter(8,h['fitResult'][ptCut]['SigmaLow'][0])
    myCB.SetParameter(9,0.3)
    myCB.SetParameter(10,3.5)
    myCB.SetParameter(11,h['fitResult'][ptCut]['p1'][0])
    myCB.SetParameter(12,h['fitResult'][ptCut]['p2'][0])
    myCB.FixParameter(13,0.)
   else:
    myCB.SetParameter(1,h['fitResultCB'][ptCut]['psi(1S)'][0])
    myCB.SetParameter(2,h['fitResultCB'][ptCut]['Mass'][0])
    myCB.FixParameter(3,h['fitResultCB'][ptCut]['Sigma'][0])
    myCB.FixParameter(4,h['fitResultCB'][ptCut]['alpha'][0])
    myCB.FixParameter(5,h['fitResultCB'][ptCut]['n'][0])
    myCB.SetParameter(6,h['fitResultCB'][ptCut]['SignalLow'][0])
    myCB.SetParameter(7,h['fitResultCB'][ptCut]['MeanLow'][0])
    myCB.FixParameter(8,h['fitResultCB'][ptCut]['SigmaLow'][0])
    myCB.FixParameter(9,h['fitResultCB'][ptCut]['alphaLow'][0])
    myCB.FixParameter(10,h['fitResultCB'][ptCut]['nLow'][0])
    myCB.SetParameter(11,h['fitResultCB'][ptCut]['p0'][0])
    myCB.SetParameter(12,h['fitResultCB'][ptCut]['p1'][0])
    myCB.FixParameter(12,0.)
    myCB.FixParameter(13,0.)
    myCB.ReleaseParameter(2)
    myCB.ReleaseParameter(7)

def fitWithTwoCB():
 hMC['dummy'].cd()
 ptCutList = [0.0,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]
 bw = hMC['m_MC'].GetBinWidth(1)
 cases = {'':hData,'mc-':hMC}
 v = 'mcor'
 for c in cases:
  h=cases[c]
  h['fitResultCB']={}
  for ptCut in ptCutList:
   h['myCB2'+str(ptCut)+c] = ROOT.TF1('2CB'+str(ptCut)+c,TwoCrystalBall,0,10,14)
   myCB = h['myCB2'+str(ptCut)+c]
   init_twoCB(myCB,bw,ptCut,h)
   hname = c+v+'_'+str(ptCut)
   print "+++++ Fit",hname
   myCB.FixParameter(9,10.) # alpha positive and large -> gauss part only
   myCB.FixParameter(5,10.) # alpha positive and large -> gauss part only
   rc = h[hname].Fit(myCB,'S','',0.5,5.)
   myCB.ReleaseParameter(5)
   rc = h[hname].Fit(myCB,'SE','',0.5,5.)
   myCB.ReleaseParameter(9)
   rc = h[hname].Fit(myCB,'SE','',0.5,5.)
   fitResult=rc.Get()
   if math.isnan(fitResult.ParError(1)) or math.isnan(fitResult.ParError(6)):
      myCB.FixParameter(4,10.)
      rc = h[hname].Fit(myCB,'S','',0.5,5.)
      myCB.ReleaseParameter(4)
      rc = h[hname].Fit(myCB,'SE','',0.5,5.)
      fitResult=rc.Get()
      if math.isnan(fitResult.ParError(1)) or math.isnan(fitResult.ParError(6)):
        myCB.FixParameter(4,10.)
        rc = h[hname].Fit(myCB,'SE','',0.5,5.)
        fitResult=rc.Get()
   h['fitResultCB'][ptCut]={}
   for n in range(1,13):
       h['fitResultCB'][ptCut][myCB.GetParName(n)] = [fitResult.Parameter(n),fitResult.ParError(n)]
   myCB.ReleaseParameter(13)
   rc = h[hname].Fit(myCB,'SE','',0.5,5.)
   fitResult=rc.Get()
   n=13
   h['fitResultCB'][ptCut][myCB.GetParName(n)] = [fitResult.Parameter(n),fitResult.ParError(n)]
   myCB.FixParameter(13,0.)
   rc = h[hname].Fit(myCB,'SE','',0.5,5.)
 for j in range(1,21): hMC['fits'+v].cd(j).Update()
 hMC['fits'+v].Update()
 myPrint(hMC['fits'+v],v+'_CBdimuon_all')
# p/pt
# try Jpsi p,pt based on ptmu > 1.4
 fillProjectionCB('ptcor',1.4,nBins=9)
 fillProjectionCB('pcor', 1.4,nBins=9)
 fillProjectionCB('ycor', 1.4,nBins=9)
# make ratio data / mc with lumi weighted:
 hData['ratios']={}
 for ptCut in ptCutList:
   hData['ratios'][ptCut]={}
   for fit in ['','CB']:
    hData['ratios'][ptCut][fit]={}
    for M in ['psi(1S)','SignalLow']:
     N = hData['fitResult'+fit][ptCut][M][0]
     E = hData['fitResult'+fit][ptCut][M][1]
     fudgeFactor = 1.
     if M=='psi(1S)': fudgeFactor = (1.+jpsiCascadeContr)
     MCN = hMC['fitResult'+fit][ptCut][M][0]*fudgeFactor
     MCE = hMC['fitResult'+fit][ptCut][M][1]*fudgeFactor
# '10GeV':MCStats['10GeV']/dataStats/(1+simpleEffCor*2)
     R = N/MCN * hMC['weights']['10GeV']
     ER = ROOT.TMath.Sqrt( (R/N*E)**2 + (R/MCN*MCE)**2)
     hData['ratios'][ptCut][fit][M]=[R,ER]
 for M in ['psi(1S)','SignalLow']:
    print "results for ",M
    for ptCut in ptCutList:
      r = "%5.2F +/- %5.2F"%(hData['ratios'][ptCut][''][M][0],hData['ratios'][ptCut][''][M][1])
      rCB = "%5.2F +/- %5.2F"%(hData['ratios'][ptCut]['CB'][M][0],hData['ratios'][ptCut]['CB'][M][1])
      print "Ratio Data/MC with pt cut %3.2F: gauss  %s  crystalball %s"%(ptCut,r,rCB)
 print "results for mass difference Jpsi low"
 cases = {'':hData,'mc-':hMC}
 for c in cases:
   h=cases[c]
   h['delm']={}
   for ptCut in ptCutList:
     h['delm'][ptCut]={}
     for fit in ['','CB']:
       m = 'Mass'
       if fit=='': m = "Mean"
       Delm  = h['fitResult'+fit][ptCut][m][0] - h['fitResult'+fit][ptCut]['MeanLow'][0]
       eDelm = ROOT.TMath.Sqrt(h['fitResult'+fit][ptCut][m][1]**2+h['fitResult'+fit][ptCut]['MeanLow'][1]**2)
       h['delm'][ptCut][fit]=[Delm,eDelm]
 for ptCut in ptCutList:
    r1 = "%5.2F +/- %5.2F"%(hData['delm'][ptCut][''][0],hData['delm'][ptCut][''][1])
    r2 = "%5.2F +/- %5.2F"%(hData['delm'][ptCut]['CB'][0],hData['delm'][ptCut]['CB'][1])
    r3 = "%5.2F +/- %5.2F"%(hMC['delm'][ptCut][''][0],hMC['delm'][ptCut][''][1])
    r4 = "%5.2F +/- %5.2F"%(hMC['delm'][ptCut]['CB'][0],hMC['delm'][ptCut]['CB'][1])
    print "Dm high-low pt cut: %3.2F: gauss  %s  crystalball %s ||MC gauss  %s  crystalball %s  "%(ptCut,r1,r2,r3,r4)
 ptCut = 1.4
 fit = 'CB'
 m = 'Mass'
 for c in cases:
   h=cases[c]
   print "Jpsi mass measured - PDG %5s %5.3F +/-%5.3F "%(c,h['fitResult'+fit][ptCut][m][0]-3.0969,h['fitResult'+fit][ptCut][m][1])
 v = "mcor"
 param = {1:'Signal',2:'Mass',3:'Sigma'}
 txt   = {1:'; #it{p}_{T}>X GeV/c; Nsignal',2:'; #it{p}_{T}>X GeV/c; M [GeV/c^{2}]',3:'; #it{p}_{T}>X GeV/c; #sigma [GeV/c^{2}]'}
 choices = {'MC':hMC,'Data':hData}
 for c in choices:
   h=choices[c]
   for p in range(1,4):
    hname = 'evolutionCB'+v+param[p]+c
    ut.bookHist(h,hname,v+' evolution of '+param[p]+txt[p],20,0., 2.)
    for ptCut in ptCutList:
        k = h[hname].FindBin(ptCut)
        h[hname].SetBinContent(k,h['fitResultCB'][ptCut][myCB.GetParName(p)][0])
        h[hname].SetBinError(k,h['fitResultCB'][ptCut][myCB.GetParName(p)][1])
        k+=1
 for p in range(1,4):
   tc = hMC['evolutionC'+v].cd(p)
   hname = 'evolutionCB'+v+param[p]
   resetMinMax(hMC[hname+'MC'])
   resetMinMax(hData[hname+'Data'])
   hMC[hname+'MC'].SetLineColor(ROOT.kRed)
   hMC[hname+'MC'].GetXaxis().SetRangeUser(0.9,2.0)
   hData[hname+'Data'].GetXaxis().SetRangeUser(0.9,2.0)
   hMC[hname+'MC'].SetMaximum(1.1*max(hMC[hname+'MC'].GetMaximum(),hData[hname+'Data'].GetMaximum()))
   if p==2: 
        hMC[hname+'MC'].SetMaximum(3.5)
        hMC[hname+'MC'].SetMinimum(3.)
   if p==3: 
        hMC[hname+'MC'].SetMaximum(0.4)
        hMC[hname+'MC'].SetMinimum(0.3)
   hMC[hname+'MC'].Draw()
   hData[hname+'Data'].Draw('same')
 myPrint(hMC['evolutionC'+v],'EvolutionOfCuts_dimuonCB'+v)

def fillProjectionCB(proj,ptCut,nBins=9):
 hMC['dummy'].cd()
 bw = hMC['m_MC'].GetBinWidth(1)
 cases = {'':hData,'mc-':hMC}
 for k in range(nBins):
   for c in cases:
    h=cases[c]
    histo = h[c+proj+str(k)]
    tc = h[c.replace('mc-','MC')+'bins'+proj].cd(k+1)
    myCB = h['myCB2'+str(ptCut)+c]
    init_twoCB(myCB,bw,ptCut,h,True)
    rc = histo.Fit(myCB,'SQ','',0.5,5.)
    myCB.ReleaseParameter(3)
    myCB.ReleaseParameter(4)
    rc = histo.Fit(myCB,'SQ','',0.5,5.)
    fitResult = rc.Get()
    if not fitResult:
        N=0
        E=0
    elif fitResult.Parameter(2)>4. or fitResult.Parameter(2)<2.: 
       myCB.FixParameter(2,3.1)
       myCB.FixParameter(3,0.35)
       rc = histo.Fit(myCB,'SQ','',0.5,5.)
       fitResult = rc.Get()
    if fitResult and histo.GetEntries()>10 and fitResult.Parameter(2)<4.:
     N = fitResult.Parameter(1)
     E = fitResult.ParError(1)
     tc.Update()
     stats = tc.GetPrimitive('stats')
     stats.SetOptFit(10011)
     stats.SetFitFormat('5.4g')
     stats.SetX1NDC(0.41)
     stats.SetY1NDC(0.41)
     stats.SetX2NDC(0.99)
     stats.SetY2NDC(0.84)
     tc.Update()
     h[c+'Jpsi'+proj].SetBinContent(k+1,N)
     h[c+'Jpsi'+proj].SetBinError(k+1,E)
 myPrint(hData['bins'+proj],'diMuonBins'+proj+'CB')
 myPrint(hMC['MCbins'+proj],'MC-diMuonBins'+proj+'CB')
 hMC['mc-Jpsi'+proj].SetLineColor(ROOT.kMagenta)
 hMC['mc-Jpsi'+proj+'_scaled']=hMC['mc-Jpsi'+proj].Clone('mc-Jpsi'+proj+'_scaled')
 hMC['mc-Jpsi'+proj+'_scaled'].Scale(1./hMC['mc-Jpsi'+proj].GetSumOfWeights())
 hData['Jpsi'+proj+'_scaled']=hData['Jpsi'+proj].Clone('Jpsi'+proj+'_scaled')
 hData['Jpsi'+proj+'_scaled'].Scale(1./hData['Jpsi'+proj].GetSumOfWeights())
 hmax = 1.1*max(ut.findMaximumAndMinimum(hData['Jpsi'+proj+'_scaled'])[1],ut.findMaximumAndMinimum(hMC['mc-Jpsi'+proj+'_scaled'])[1])
 hData['Jpsi'+proj+'_scaled'].SetMaximum(hmax)
 hMC['dummy'].cd()
 hData['Jpsi'+proj+'_scaled'].Draw()
 hMC['mc-Jpsi'+proj+'_scaled'].Draw('same')
 myPrint(hMC['dummy'],'diMuonBins'+proj+'CBSummary')

def MCmigration():
 sptCut = '1.4'
 theCutTemplate =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1<200&&p2<200&&p1>20&&p2>20&&mcor>0.5'
 Nbins = 25
 ut.bookHist(hMC, 'pMigration' ,'p vs pTrue',Nbins,0.,400.,Nbins,0.,400.)
 tc = hMC['kin'].cd(1)
 myDraw('p:PTRUE>>pTrue',theCutTemplate+'&&Jpsi==443') # x axis = Ptrue, y axis Preco
 hMC['pRec'] = hMC['pMigration'].ProjectionY('pRec')
 hMC['pTRUE'] = hMC['pMigration'].ProjectionX('pTRUE')
 Prec2True = {}
 for j in range(1,Nbins+1):
  tmp = hMC['pMigration'].ProjectionX(str(j),j,j)
  if tmp.GetEntries()>0: tmp.Scale(1./tmp.GetEntries())
  Prec2True[j]={}
  for l in range(1,Nbins+1): Prec2True[j][l]=tmp.GetBinContent(l)
# cross check
 ut.bookHist(hMC, 'ptrueTest' ,'pTrue from pRec',Nbins,0.,400.)
 for j in range(1,Nbins):
    nRec = hMC['pRec'].GetBinContent(j)
    eRec = hMC['pRec'].GetBinError(j)
    for l in range(1,Nbins+1):
      nTrue = nRec*Prec2True[j][l]
      eTrue = (nRec*eRec)**2
      N,E = hMC['ptrueTest'].GetBinContent(l),hMC['ptrueTest'].GetBinError(l)
      rc = hMC['ptrueTest'].SetBinContent(l,N+nTrue)
      rc = hMC['ptrueTest'].SetBinError(l,E+eTrue)
 for l in range(1,Nbins+1):
   eTrue = (nRec*eRec)**2
   E = hMC['ptrueTest'].GetBinContent(l)
   rc = hMC['ptrueTest'].SetBinError(l,ROOT.TMath.Sqrt(E))


def fitWithCB():
 hMC['myCB'] = ROOT.TF1('CB',CrystalBall,0,10,11)
 myCB = hMC['myCB']
 myCB.SetParName(0,'binwidth')
 myCB.SetParName(1,'psi(1S)')
 myCB.SetParName(2,'Mass')
 myCB.SetParName(3,'Sigma')
 myCB.SetParName(4,'alpha')
 myCB.SetParName(5,'n')
 myCB.SetParName(6,'SignalLow')
 myCB.SetParName(7,'MeanLow')
 myCB.SetParName(8,'SigmaLow')
 myCB.SetParName(9,'p0')
 myCB.SetParName(10,'p1')
 hMC['dummy'].cd()
 ptCutList = [0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]
 bw = hMC['m_MC'].GetBinWidth(1)
 myCB.FixParameter(0,bw)
 cases = {'':hData,'mc-':hMC}
 for c in cases:
  h=cases[c]
  h['fitResultCB']={}
  for ptCut in ptCutList:
   myCB.SetParameter(1,h['fitResult'][ptCut]['psi(1S)'][0])
   myCB.SetParameter(2,h['fitResult'][ptCut]['Mean'][0])
   myCB.SetParameter(3,h['fitResult'][ptCut]['Sigma'][0])
   myCB.SetParameter(4,0.3)
   myCB.SetParameter(5,3.5)
   myCB.SetParameter(6,h['fitResult'][ptCut]['SignalLow'][0])
   myCB.SetParameter(7,h['fitResult'][ptCut]['MeanLow'][0])
   myCB.SetParameter(8,h['fitResult'][ptCut]['SigmaLow'][0])
   myCB.SetParameter(9,h['fitResult'][ptCut]['p1'][0])
   myCB.SetParameter(10,h['fitResult'][ptCut]['p2'][0])
   hname = c+'mcor_'+str(ptCut)
   rc = h[hname].Fit(myCB,'S','',0.5,6.)
   fitResult=rc.Get()
   h['fitResultCB'][ptCut] = []
   for n in range(1,11):
      h['fitResultCB'][ptCut][myCB.GetParName(n)] = [fitResult.Parameter(n),fitResult.ParError(n)]
def resetMinMax(x):
  x.SetMinimum(-1111)
  x.SetMaximum(-1111)
def plotOccupancy(sTree):
    ut.bookHist(h,'upStreamOcc',"station 1&2 function of track mom",50,-0.5,199.5,100,0.,500.)
    for n in range(sTree.GetEntries()):
        rc = sTree.GetEvent(n)
        for k in range(len(sTree.GoodTrack)):
            if sTree.GoodTrack[k]<0: continue
            p=ROOT.TVector3(sTree.Px[k],sTree.Py[k],sTree.Pz[k])
            occ = sTree.stationOcc[1]+sTree.stationOcc[2]+sTree.stationOcc[5]+sTree.stationOcc[6]
            rc=h['upStreamOcc'].Fill(occ,p.Mag())

myExpo = ROOT.TF1('expo','abs([0])*exp(-abs([1]*x))+abs([2])*exp(-abs([3]*x))+[4]',5)
myExpo.SetParName(0,'Signal1')
myExpo.SetParName(1,'tau1')
myExpo.SetParName(2,'Signal2')
myExpo.SetParName(3,'tau2')
myExpo.SetParName(4,'const')

def myPrint(obj,aname):
    name = aname.replace('/','')
    obj.Print(name+'.root')
    obj.Print(name+'.pdf')
    obj.Print(name+'.png')

def fitExpo(h,hname):
    myExpo.SetParameter(0,12.)
    myExpo.SetParameter(1,-0.027)
    myExpo.FixParameter(2,0.)
    myExpo.FixParameter(3,-0.030)
    myExpo.SetParameter(4,1.)
    rc = h[hname].Fit(myExpo,'S','',250.,500.)
    fitresult = rc.Get()
    back = fitresult.Parameter(4)
    hnameb=hname+'_backsubtr'
    h[hnameb]= h[hname].Clone(hnameb)
    for n in range(1,h[hname].GetNbinsX()+1):
        h[hnameb].SetBinContent(n,h[hname].GetBinContent(n)-back)

def studyGhosts():
    sTree = sTreeMC
    h = hMC
    ut.bookHist(h,'gfCurv',             'ghost fraction vs curvature',100,0.,100.,100,0.,0.1)
    ut.bookHist(h,'gf',             'ghost fraction',100,0.,100.,100,0.,500.)
    ut.bookHist(h,'gftrue',         'ghost fraction',100,0.,100.,100,0.,500.)
    ut.bookHist(h,'gfDiff',         'ghost fraction vs reco - true mom',100,0.,100.,500,0.,500.)
    ut.bookHist(h,'RPCMatch',       'RPC matching no ghost',100,0.,10.,100,0.,10.)
    ut.bookHist(h,'RPCMatch_ghosts','RPC matching ghost>33',100,0.,10.,100,0.,10.)
    ut.bookHist(h,'R','rpc match',100,0.,100.,100,0.,10.)
    ut.bookHist(h,'Chi2/DoF','Chi2/DoF',100,0.,100.,100,0.,5.)
    ut.bookHist(h,'DoF','DoF',100,0.,100.,30,0.5,30.5)
    for n in range(sTree.GetEntries()):
        if n%500000==0:
            curFile = sTree.GetCurrentFile().GetName()
            tmp = curFile.split('/')
            print "now at event ",n,tmp[len(tmp)-2],'/',tmp[len(tmp)-1],time.ctime()
        rc = sTree.GetEvent(n)
        if not sTreeMC.FindBranch("MCghostfraction") : continue
        for k in range(sTree.nTr):
            muTagged  = False
            muTaggedX = False
            clone     = False
            if sTree.GoodTrack[k]<0: continue
            if sTree.GoodTrack[k]%2==1:
                muTaggedX = True
                if int(sTree.GoodTrack[k]/10)%2==1: muTagged = True
            if sTree.GoodTrack[k]>999:  clone = True
            if clone: continue
            if not muTagged: continue
            gf    = sTree.MCghostfraction[k]*100
            R = (sTree.Dely[k]/3.)**2+(sTree.Delx[k]/1.5)**2
            rc =   h['Chi2/DoF'].Fill(gf,sTree.Chi2[k])
            rc = h['DoF'].Fill(gf,sTree.nDoF[k])
            rc = h['R'].Fill(gf,R)
            # if R>5: continue
            if gf<1:  
                rc =   h['RPCMatch'].Fill(sTree.Delx[k],sTree.Dely[k])
            if gf>33: 
                rc =   h['RPCMatch_ghosts'].Fill(sTree.Delx[k],sTree.Dely[k])
            p     =ROOT.TVector3(sTree.Px[k],sTree.Py[k],sTree.Pz[k])
            pTrue =ROOT.TVector3(sTree.MCTruepx[k],sTree.MCTruepy[k],sTree.MCTruepz[k])
            rc    = h['gfDiff'].Fill(gf,p.Mag() - pTrue.Mag())
            rc    = h['gftrue'].Fill(gf, pTrue.Mag())
            rc    = h['gf'].Fill(gf,p.Mag() )
            rc = h['gfCurv'].Fill(gf,1./p.Mag() )
    h['P']       =h['gf'].ProjectionY('P')
    h['Ptrue']   =h['gftrue'].ProjectionY('Ptrue')
    h['Ptrue'].SetLineColor(ROOT.kMagenta)
    for x in ['gf','gftrue','Chi2/DoF','R','DoF']:
        if x.find('true')>0: h[x].SetLineColor(ROOT.kGreen)
        else:   h[x].SetLineColor(ROOT.kBlue)
        h[x+'_perfect']      =h[x].ProjectionY(x+'_perfect',1,1)
        h[x+'_ghosts']       =h[x].ProjectionY(x+'_ghosts',33,100)
        h[x+'_ghosts'].SetLineColor(ROOT.kRed)
    h['gf_perfect'].SetTitle(' ;#it{p} [GeV/c];N/5GeV')
    h['gf_perfect'].SetLineColor(ROOT.kGreen)
    h['gf_ghosts'].SetTitle('ghost > 33;#it{p} [GeV/c];N/5GeV')
    ut.writeHists(h,'ghostStudy.root')
def init_Gauss(myGauss):
 myGauss.SetParName(0,'psi(1S)')
 myGauss.SetParName(1,'Mean')
 myGauss.SetParName(2,'Sigma')
 myGauss.SetParName(3,'SignalLow')
 myGauss.SetParName(4,'MeanLow')
 myGauss.SetParName(5,'SigmaLow')
 myGauss.SetParName(6,'p0')
 myGauss.SetParName(7,'p1')
 myGauss.SetParName(8,'p2')
 myGauss.SetParName(9,'psi(2S)')
 myGauss.SetParameter(0,1000.)
 myGauss.SetParameter(1,3.1)
 myGauss.SetParameter(2,0.35)
 myGauss.SetParameter(3,1000.)
 myGauss.SetParameter(4,1.0)
 myGauss.SetParameter(5,0.1)
 myGauss.SetParameter(6,10.)
 myGauss.SetParameter(7,1.)
 myGauss.FixParameter(8,0.)
 myGauss.FixParameter(9,0.)
def stupidCopy():
 for x in os.listdir('.'):
  if x.find('dimuon_all.p')<0: continue
  os.system('cp '+x+' '+ x.replace('all','AND_all'))

def analzyeMuonScattering():
  if not hMC.has_key('10GeV'): loadNtuples()
  nt   = hMC['10GeV']
  ntD  = hData['f'].nt
  ut.bookHist(hMC, 'dEdx','dE;dE [GeV/c^{2}]',100,-50.,25.,20,0.,200.)
  ut.bookHist(hMC, 'scatteringX',   '; #theta^{true}_{X} - #theta^{reco}_{X}         [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC, 'scatteringXcor','; #theta^{true}_{X} - #theta^{cor}_{X}          [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC, 'scatteringY'   ,'; #theta^{true}_{Y} - #theta^{reco}_{Y}         [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC, 'scatteringYcor','; #theta^{true}_{Y} - #theta^{cor}_{Y}          [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC, 'scatteringT',    '; #theta^{true} - #theta^{reco}                [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC, 'scatteringTcor', '; #theta^{true} - #theta^{reco}                [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hData, 'XcorData','; #theta^{reco}_{X} - #theta^{cor}_{X}              [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC,     'XcorMC','; #theta^{reco}_{X} - #theta^{cor}_{X}              [rad]'    ,100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hData, 'YcorData','; #theta^{reco}_{Y} - #theta^{cor}_{Y}              [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC,     'YcorMC','; #theta^{reco}_{Y} - #theta^{cor}_{Y}              [rad]'    ,100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hData, 'TcorData','; #theta^{reco}  - #theta^{cor}               [rad]',100,-0.05,0.05,20,0.,200.)
  ut.bookHist(hMC,     'TcorMC','; #theta^{reco}  - #theta^{cor}               [rad]'    ,100,-0.05,0.05,20,0.,200.)

  ROOT.gROOT.cd()
  nt.Draw('p1:(p1-p1True)>>dEdx','')
  nt.Draw('p2:(p2-p2True)>>+dEdx','')
  ptCut1 = 'pt1>0'
  ptCut2 = 'pt2>0'
  nt.Draw('p1:p1x/p1z-prec1x/prec1z>>scatteringX',ptCut1 )
  nt.Draw('p2:p2x/p2z-prec2x/prec2z>>+scatteringX',ptCut2 )
  nt.Draw('p1:p1x/p1z-rec1x/(rec1z- '+str(zTarget)+')>>scatteringXcor',ptCut1 )
  nt.Draw('p2:p2x/p2z-rec2x/(rec2z- '+str(zTarget)+')>>+scatteringXcor',ptCut2 )

  nt.Draw('p1:p1y/p1z-prec1y/prec1z>>scatteringY','')
  nt.Draw('p2:p2y/p2z-prec2y/prec2z>>+scatteringY','')
  nt.Draw('p1:p1y/p1z-rec1y/(rec1z- '+str(zTarget)+')>>scatteringYcor')
  nt.Draw('p2:p2y/p2z-rec2y/(rec2z- '+str(zTarget)+')>>+scatteringYcor')

  nt.Draw('p1:sqrt(p1x*p1x+p1y*p1y)/p1z-sqrt(prec1y*prec1y+prec1x*prec1x)/prec1z>>scatteringT','')
  nt.Draw('p2:sqrt(p2x*p2x+p2y*p2y)/p2z-sqrt(prec2y*prec2y+prec2x*prec2x)/prec2z>>+scatteringT','')
  nt.Draw('p1:sqrt(p1x*p1x+p1y*p1y)/p1z-sqrt(rec1y*rec1y+rec1x*rec1x)/(rec1z- '+str(zTarget)+')>>scatteringTcor')
  nt.Draw('p2:sqrt(p2x*p2x+p2y*p2y)/p2z-sqrt(rec2y*rec2y+rec2x*rec2x)/(rec2z- '+str(zTarget)+')>>+scatteringTcor')
# look at applied angle correction
  nt.Draw('p1:prec1x/prec1z-rec1x/(rec1z- '+str(zTarget)+')>>XcorMC',ptCut1 )
  nt.Draw('p2:prec2x/prec2z-rec2x/(rec2z- '+str(zTarget)+')>>XcorMC',ptCut2)
  ntD.Draw('p1:prec1x/prec1z-rec1x/(rec1z- '+str(zTarget)+')>>XcorData',ptCut1 )
  ntD.Draw('p2:prec2x/prec2z-rec2x/(rec2z- '+str(zTarget)+')>>XcorData',ptCut2)

  nt.Draw('p1:prec1y/prec1z-rec1y/(rec1z- '+str(zTarget)+')>>YcorMC',ptCut1 )
  nt.Draw('p2:prec2y/prec2z-rec2y/(rec2z- '+str(zTarget)+')>>YcorMC',ptCut2)
  ntD.Draw('p1:prec1y/prec1z-rec1y/(rec1z- '+str(zTarget)+')>>YcorData',ptCut1 )
  ntD.Draw('p2:prec2y/prec2z-rec2y/(rec2z- '+str(zTarget)+')>>YcorData',ptCut2)

  nt.Draw('p1:sqrt(prec1y*prec1y+prec1x*prec1x)/prec1z-sqrt(rec1y*rec1y+rec1x*rec1x)/(rec1z- '+str(zTarget)+')>>TcorMC',ptCut1 )
  nt.Draw('p2:sqrt(prec2y*prec2y+prec2x*prec2x)/prec2z-sqrt(rec2y*rec2y+rec2x*rec2x)/(rec2z- '+str(zTarget)+')>>TcorMC',ptCut2)
  ntD.Draw('p1:sqrt(prec1y*prec1y+prec1x*prec1x)/prec1z-sqrt(rec1y*rec1y+rec1x*rec1x)/(rec1z- '+str(zTarget)+')>>TcorData',ptCut1 )
  ntD.Draw('p2:sqrt(prec2y*prec2y+prec2x*prec2x)/prec2z-sqrt(rec2y*rec2y+rec2x*rec2x)/(rec2z- '+str(zTarget)+')>>TcorData',ptCut2)

  hMC['dEdxMean']=hMC['dEdx'].ProjectionY('dEdxMean')
  hMC['dEdxMean'].Reset()
  for n in range(1,hMC['dEdxMean'].GetNbinsX()+1):
    tmp = hMC['dEdx'].ProjectionX('tmp',n,n)
    hMC['dEdxMean'].SetBinContent(n,tmp.GetMean())
    hMC['dEdxMean'].SetBinError(n,tmp.GetRMS())
  hMC['dEdxMean'].Fit('pol2','S','',10.,190.)
#
  ut.bookCanvas(hMC,'scattering','scattering X and Y',1600,900,3,3)
  ut.bookCanvas(hMC,'singlePlot',' ',900,1200,1,1)
  j=1
  for x in ['scatteringX','scatteringY','scatteringT','scatteringXcor','scatteringYcor','scatteringTcor']:
    hMC[x+'Mean']=hMC[x].ProjectionX(x+'Mean')
    tc=hMC['scattering'].cd(j)
    hMC[x].Draw('colz')
    j+=1
  for tc in [hMC['scattering'].cd(5),hMC['singlePlot'].cd()]:
   hMC['scatteringXcorMean'].SetLineColor(ROOT.kGreen)
   hMC['scatteringXcorMean'].Draw()
   hMC['scatteringXMean'].Draw('same')
  myPrint(tc,'scatteringX')
  for tc in [hMC['scattering'].cd(6),hMC['singlePlot'].cd()]:
   hMC['scatteringYcorMean'].SetLineColor(ROOT.kGreen)
   hMC['scatteringYcorMean'].Draw()
   hMC['scatteringYMean'].Draw('same')
  myPrint(tc,'scatteringY')
  for tc in [hMC['scattering'].cd(7),hMC['singlePlot'].cd()]:
   hMC['scatteringTcorMean'].SetLineColor(ROOT.kGreen)
   hMC['scatteringTcorMean'].Draw()
   hMC['scatteringTMean'].Draw('same')
  myPrint(tc,'scatteringT')

  ut.bookCanvas(hMC,'scatteringDataMC','scattering Data vs MC',1600,900,2,3)
  hMC['scatteringDataMC'].cd(1)
  for proj in ['X','Y','T']:
   for x in ['RMS','Mean']:
    hMC['scatt'+proj+'cor'+x+'_MC']=hMC[proj+'corMC'].ProjectionY('scatt'+proj+'cor'+x+'_MC')
    hMC['scatt'+proj+'cor'+x+'_MC'].Reset()
    hMC['scatt'+proj+'cor'+x+'_MC'].GetYaxis().SetTitle('[rad]')
    hData['scatt'+proj+'cor'+x+'_Data']=hData[proj+'corData'].ProjectionY('scatt'+proj+'cor'+x+'_Data')
    hData['scatt'+proj+'cor'+x+'_Data'].GetYaxis().SetTitle('[rad]')
    hData['scatt'+proj+'cor'+x+'_Data'].Reset()
   for n in range(1,hMC['scatt'+proj+'corRMS_MC'].GetNbinsX()+1):
    tmp = hMC[proj+'corMC'].ProjectionX('tmp',n,n)
    rc = tmp.Fit('gaus','SQ')
    fitresult = rc.Get()
    hMC['scatt'+proj+'corRMS_MC'].SetBinContent(n,fitresult.Parameter(2))
    hMC['scatt'+proj+'corMean_MC'].SetBinContent(n,fitresult.Parameter(1))
    tmp = hData[proj+'corData'].ProjectionX('tmp',n,n)
    rc = tmp.Fit('gaus','SQ')
    fitresult = rc.Get()
    hData['scatt'+proj+'corRMS_Data'].SetBinContent(n,fitresult.Parameter(2))
    hData['scatt'+proj+'corMean_Data'].SetBinContent(n,fitresult.Parameter(1))
    hData['scatt'+proj+'corMean_Data'].SetTitle('Mean; #it{p} [GeV/c]; mean correction [rad]')
    hData['scatt'+proj+'corRMS_Data'].SetTitle('RMS; #it{p} [GeV/c]; sigma of correction [rad]')
  j = 1
  for proj in ['X','Y','T']:
    for x in ['RMS','Mean']:
      for tc in [hMC['scatteringDataMC'].cd(j),hMC['singlePlot'].cd()]:
       hData['scatt'+proj+'cor'+x+'_Data'].SetMinimum( min(hData['scatt'+proj+'cor'+x+'_Data'].GetMinimum(),hMC['scatt'+proj+'cor'+x+'_MC'].GetMinimum()))
       hData['scatt'+proj+'cor'+x+'_Data'].SetMaximum( max(hData['scatt'+proj+'cor'+x+'_Data'].GetMaximum(),hMC['scatt'+proj+'cor'+x+'_MC'].GetMaximum()))
       hData['scatt'+proj+'cor'+x+'_Data'].SetMinimum(0)
       hData['scatt'+proj+'cor'+x+'_Data'].SetStats(0)
       hData['scatt'+proj+'cor'+x+'_Data'].Draw()
       hMC['scatt'+proj+'cor'+x+'_MC'].SetLineColor(ROOT.kMagenta)
       hMC['scatt'+proj+'cor'+x+'_MC'].Draw('same')
       if proj=='T': myPrint(tc,'scatteringDataMC_'+x)
      j+=1

def JpsiAcceptance0():
    hMC['f0']=ROOT.TFile.Open(os.environ['EOSSHIP']+"/eos/experiment/ship/data/jpsicascade/cascade_MSEL61_20M.root")
    nt=hMC['f0'].nt
    two = f.Get('2').Clone('2')
    primJpsi  = two.GetBinContent(1)
    totalJpsi = two.GetSumOfWeights() # = nt.GetEntries()
    print "primary: %5.2F%%,  cascade: %5.2F%% "%(primJpsi/totalJpsi*100.,100.-primJpsi/totalJpsi*100.)
#
    ut.bookHist(hMC,'Jpsi_p/pt','momentum vs Pt (GeV);#it{p} [GeV/c]; #it{p}_{T} [GeV/c]',500,0.,500.,100,0.,10.)
    ut.bookHist(hMC,'Jpsi_y',   'rapidity cm; y_{CM}',100,-1.,5.,25,0.,500.,10,0.,10.)
    for event in nt:
       mom = ROOT.TLorentzVector(event.px,event.py,event.pz,event.E)
       rc = hMC['Jpsi_p/pt'].Fill(mom.P(),mom.Pt())
       rc = hMC['Jpsi_y'].Fill(mom.Rapidity(),mom.P(),mom.Pt())

def analyzeInvMassBias():
  if not hMC.has_key('f10'):
    hMC['f10'] = ROOT.TFile('ntuple-invMass-MC-10GeV.root')
    hMC['10GeV']=hMC['f10'].nt
    hData['f'] = ROOT.TFile('ntuple-InvMass-refitted.root')
  InvMassPlots = [160,0.,8.]
  ptCutList = [0.0,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6]
  nt = hMC['10GeV']
  ut.bookHist(hMC,'deltaXY','diff xy muon1 and muon2;x [cm]; y [cm]',100,0.,20.,100,0.,20.)
  nt.Draw('abs(prec1x-prec2x):abs(prec1y-prec2y)>>deltaXY','mcor<0.25')
# muon dEdx
  ut.bookHist(hMC, 'delpTrue2' ,'p-pTrue vs pTrue',20,0.,400.,50,-50.,50.)
  nt.Draw('(p1-p1True):p1>>delpTrue2','Jpsi==443&&pt1>1.4')
  nt.Draw('(p2-p2True):p2>>+delpTrue2','Jpsi==443&&pt2>1.4') # applying cuts does not make a difference
# inv mass from true mom
  for x in ['','_truePt']:
   ut.bookHist(hMC, 'm_MCtrue'+x, 'inv mass;M [GeV/c^{2}];#it{p}_{Tmin} [GeV/c]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2],10,0.,2.)
   ut.bookHist(hMC, 'm_MCdEdx'+x, 'inv mass;M [GeV/c^{2}];#it{p}_{Tmin} [GeV/c]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2],10,0.,2.)
   ut.bookHist(hMC, 'm_MCmult'+x, 'inv mass;M [GeV/c^{2}];#it{p}_{Tmin} [GeV/c]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2],10,0.,2.)
   ut.bookHist(hMC, 'm_MCcor'+x,  'inv mass;M [GeV/c^{2}];#it{p}_{Tmin} [GeV/c]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2],10,0.,2.)
   ut.bookHist(hMC, 'm_MCcor2'+x, 'inv mass;M [GeV/c^{2}];#it{p}_{Tmin} [GeV/c]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2],10,0.,2.)
   ut.bookHist(hMC, 'm_MCtrueSigma'+x, '#sigma_{M} ;M [GeV/c^{2}]',10,0.,2.)
   ut.bookHist(hMC, 'm_MCdEdxSigma'+x, '#sigma_{M} ;M [GeV/c^{2}]',10,0.,2.)
   ut.bookHist(hMC, 'm_MCmultSigma'+x, '#sigma_{M} ;M [GeV/c^{2}]',10,0.,2.)
   ut.bookHist(hMC, 'm_MCcorSigma'+x,  '#sigma_{M} ;M [GeV/c^{2}]',10,0.,2.)
   ut.bookHist(hMC, 'm_MCcor2Sigma'+x, '#sigma_{M} ;M [GeV/c^{2}]',10,0.,2.)
  Ptrue = {}
  Prec  = {}
  Pcor  = {}
  Pcor2  = {}
  x = '_truePt'
  for event in nt:
   if event.Jpsi!=443: continue
   Ptrue[1] = ROOT.Math.PxPyPzMVector(event.p1x,event.p1y,event.p1z,0.105658)
   Ptrue[2] = ROOT.Math.PxPyPzMVector(event.p2x,event.p2y,event.p2z,0.105658)
   Prec[1]  = ROOT.Math.PxPyPzMVector(event.prec1x,event.prec1y,event.prec1z,0.105658)
   Prec[2]  = ROOT.Math.PxPyPzMVector(event.prec2x,event.prec2y,event.prec2z,0.105658)
   tdir = ROOT.TVector3(event.rec1x,event.rec1y,event.rec1z-zTarget)
   cor = Prec[1].P()/tdir.Mag()
   Pcor[1]  = ROOT.Math.PxPyPzMVector(tdir.X()*cor,tdir.Y()*cor,tdir.Z()*cor,0.105658)
   cor = Ptrue[1].P()/tdir.Mag()
   Pcor2[1]  = ROOT.Math.PxPyPzMVector(tdir.X()*cor,tdir.Y()*cor,tdir.Z()*cor,0.105658)
   tdir = ROOT.TVector3(event.rec2x,event.rec2y,event.rec2z-zTarget)
   cor = Prec[2].P()/tdir.Mag()
   Pcor[2]  = ROOT.Math.PxPyPzMVector(tdir.X()*cor,tdir.Y()*cor,tdir.Z()*cor,0.105658)
   cor = Ptrue[2].P()/tdir.Mag()
   Pcor2[2]  = ROOT.Math.PxPyPzMVector(tdir.X()*cor,tdir.Y()*cor,tdir.Z()*cor,0.105658)
   P=Ptrue[1]+Ptrue[2]
   PtMinTrue = min(Ptrue[1].Pt(),Ptrue[2].Pt())
   PtMin = min(Prec[1].Pt(),Prec[2].Pt())
   rc = hMC['m_MCtrue'].Fill(P.M(),PtMin)
   rc = hMC['m_MCtrue'+x].Fill(P.M(),PtMinTrue)
   P=Pcor[1]+Pcor[2]
   PtMin = min(Pcor[1].Pt(),Pcor[2].Pt())
   rc = hMC['m_MCcor'].Fill(P.M(),PtMin)
   rc = hMC['m_MCcor'+x].Fill(P.M(),PtMinTrue)
   P=Pcor2[1]+Pcor2[2]
   PtMin = min(Pcor2[1].Pt(),Pcor2[2].Pt())
   rc = hMC['m_MCcor2'].Fill(P.M(),PtMin)
   rc = hMC['m_MCcor2'+x].Fill(P.M(),PtMinTrue)
   PdEloss = {}
   Pmult   = {}
   for j in range(1,3): 
       dEloss=Prec[j].P()/Ptrue[j].P()
       PdEloss[j]= ROOT.Math.PxPyPzMVector(Ptrue[j].X()*dEloss,Ptrue[j].Y()*dEloss,Ptrue[j].Z()*dEloss,0.105658)
       Pmult[j]= ROOT.Math.PxPyPzMVector(Prec[j].X()/dEloss,Prec[j].Y()/dEloss,Prec[j].Z()/dEloss,0.105658)
   P=PdEloss[1]+PdEloss[2]
   PtMin = min(PdEloss[1].Pt(),PdEloss[2].Pt())
   rc = hMC['m_MCdEdx'].Fill(P.M(),PtMin)
   rc = hMC['m_MCdEdx'+x].Fill(P.M(),PtMinTrue)
   P=Pmult[1]+Pmult[2]
   PtMin = min(Pmult[1].Pt(),Pmult[2].Pt())
   rc = hMC['m_MCmult'].Fill(P.M(),PtMin)
   rc = hMC['m_MCmult'+x].Fill(P.M(),PtMinTrue)
  for z in ['','_truePt']:
   for x in ['m_MCdEdx','m_MCmult','m_MCtrue','m_MCcor','m_MCcor2']:
    hname = x+'Mean'+z
    hMC[hname] = hMC[x+z].ProjectionY(hname)
    hMC[hname].Reset()
    hMC[hname].SetStats(0)
    hMC[hname.replace('Mean','Sigma')].SetStats(0)
    Nmax = hMC[hname].GetNbinsX()
    for k in range(Nmax):
     tmp = hMC[x+z].ProjectionX('tmp',k,Nmax)
     if x.find('true')>0:
      hMC[hname].SetBinContent(k,tmp.GetMean())
      hMC[hname].SetBinError(k,0.01)
     else:
      rc = tmp.Fit('gaus','S')
      fitresult = rc.Get()
      hMC[hname].SetBinContent(k,fitresult.Parameter(1))
      hMC[hname].SetBinError(k,fitresult.ParError(1))
      hMC[hname.replace('Mean','Sigma')].SetBinContent(k,fitresult.Parameter(2))
      hMC[hname.replace('Mean','Sigma')].SetBinError(k,fitresult.ParError(2))
   ut.bookCanvas(hMC,'TinvMassBiasMean'+z,'inv mass bias, mean',1900,650,1,1)
   ut.bookCanvas(hMC,'TinvMassBiasSigma'+z,'inv mass bias, sigma',1900,650,1,1)
   for tt in ['Mean','Sigma']:
    t=tt+z
    hMC['TinvMassBias'+t].cd()
    if tt=='Mean':
     hMC['m_MCdEdx'+t].SetMinimum(2.)
     hMC['m_MCdEdx'+t].SetMaximum(4.5)
    else:
     hMC['m_MCdEdx'+t].SetMinimum(0.)
     hMC['m_MCdEdx'+t].SetMaximum(1.0)
    hMC['m_MCdEdx'+t].SetMarkerStyle(21)
    hMC['m_MCdEdx'+t].SetLineColor(ROOT.kRed)
    hMC['m_MCmult'+t].SetLineColor(ROOT.kMagenta)
    hMC['m_MCmult'+t].SetMarkerStyle(20)
    hMC['m_MCcor'+t].SetLineColor(ROOT.kBlue)
    hMC['m_MCcor'+t].SetMarkerStyle(29)
    hMC['m_MCcor'+t].SetMarkerSize(1.8)
    hMC['m_MCcor2'+t].SetLineColor(ROOT.kGreen)
    hMC['m_MCcor2'+t].SetMarkerStyle(28)
    hMC['m_MCcor2'+t].SetMarkerSize(1.8)
    hMC['m_MCdEdx'+t].Draw()
    hMC['m_MCmult'+t].Draw('same')
    hMC['m_MCtrue'+t].Draw('same')
    hMC['m_MCcor'+t].Draw('same')
    hMC['m_MCcor2'+t].Draw('same')
    hMC['legInvMassBias'+t]=ROOT.TLegend(0.11,0.66,0.48,0.92)
    rc = hMC['legInvMassBias'+t].AddEntry(hMC['m_MCdEdx'+t],'effect of dEdx','PL')
    rc = hMC['legInvMassBias'+t].AddEntry(hMC['m_MCmult'+t],'effect of multiple scattering','PL')
    rc = hMC['legInvMassBias'+t].AddEntry(hMC['m_MCcor2'+t],'true momentum, correction of direction','PL')
    rc = hMC['legInvMassBias'+t].AddEntry(hMC['m_MCcor'+t], 'reco momentum, correction of direction','PL')
    rc = hMC['legInvMassBias'+t].AddEntry(hMC['m_MCtrue'+t],'true mass','PL')
    hMC['legInvMassBias'+t].Draw()
    myPrint(hMC['TinvMassBias'+t],'invMassBias'+t)

def debug():
    Nstat = {}
    for n in range(sTreeMC.GetEntries()):
        rc = sTreeMC.GetEvent(n)  
        fname = sTreeMC.GetCurrentFile().GetName()
        if not Nstat.has_key(fname): Nstat[fname]=[sTreeMC.GetEntries(),0,0,0]
        rc = sTreeMC.GetEvent(n)
        Nstat[fname][1]+=sTreeMC.nTr
        Nstat[fname][2]+=sTreeMC.MCRecoRPC.size()
        Nstat[fname][3]+=sTreeMC.MCRecoDT.size()
    return Nstat

def debugInvMass(sTree,nMax=1000):
    stats = {}
    currentFile=""
    N=0
    for n in range(0,sTree.GetEntries()):
        rc = sTree.GetEvent(n)
        if sTree.GetCurrentFile().GetName()!=currentFile:
          currentFile = sTree.GetCurrentFile().GetName()
          nInFile = n
        P    = {}
        IP   = {}
        Pcor = {}
        Pcor2 = {}
        for k in range(len(sTree.GoodTrack)):
            if sTree.GoodTrack[k]<0: continue
            if sTree.GoodTrack[k]%2!=1 or  int(sTree.GoodTrack[k]/10)%2!=1: continue
            if sTree.GoodTrack[k]>999:  continue
            P[k] = ROOT.Math.PxPyPzMVector(sTree.Px[k],sTree.Py[k],sTree.Pz[k],0.105658)
            l = (sTree.z[k] - zTarget)/(sTree.Pz[k]+ 1E-19)
            x = sTree.x[k]+l*sTree.Px[k]
            y = sTree.y[k]+l*sTree.Py[k]
            IP[k] = ROOT.TMath.Sqrt(x*x+y*y)
# make dE correction plus direction from measured point
            dline   = ROOT.TVector3(sTree.x[k],sTree.y[k],sTree.z[k]-zTarget)
            Ecor = P[k].E()+dEdxCorrection(P[k].P())
            norm = dline.Mag()
            Pcor[k]  = ROOT.Math.PxPyPzMVector(Ecor*dline.X()/norm,Ecor*dline.Y()/norm,Ecor*dline.Z()/norm,0.105658)
            Pcor2[k] = ROOT.Math.PxPyPzMVector(P[k].P()*dline.X()/norm,P[k].P()*dline.Y()/norm,P[k].P()*dline.Z()/norm,0.105658)
# now we have list of selected tracks, P.keys()
        if len(P)<2: continue
        shortName = currentFile.split('/')[11]
        if not stats.has_key(shortName): stats[shortName]=[]
        stats[shortName].append(n-nInFile)
        N+=1
        if N>nMax: break
    return stats
def JpsiPrimary():
    y_beam = yBeam()
    ut.bookHist(hMC,'Y','Y of Jpsi     ;y_{CMS}',100,-2.,2.)
    ut.bookHist(hMC,'Yprim','Y of primary Jpsi     ;y_{CMS}',100,-2.,2.)
    ut.bookHist(hMC,'Ysec','Y of Jpsi from cascasde;y_{CMS}', 100,-2.,2.)
    ut.bookHist(hMC,'Y_rec','Y of Jpsi ;y_{CMS}',100,-2.,2.)
    ut.bookHist(hMC,'Yprim_rec','Y of primary Jpsi ;y_{CMS}',100,-2.,2.)
    ut.bookHist(hMC,'Ysec_rec','Y of Jpsi from cascasde;y_{CMS}', 100,-2.,2.)
    ut.bookHist(hMC,'deltaYcor','ycor-YTRUE;#Delta y', 100,-1.,1.)
#
    ROOT.gROOT.cd()
#
    bw = (InvMassPlots[2]-InvMassPlots[1])/InvMassPlots[0]
    hMC['myGauss'] = ROOT.TF1('gauss','abs([0])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-[1])/[2])**2)\
            +abs([3])*'+str(bw)+'/(abs([5])*sqrt(2*pi))*exp(-0.5*((x-[4])/[5])**2)+abs( [6]+[7]*x+[8]*x**2 )\
            +abs([9])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-(3.6871 + [1] - 3.0969))/[2])**2)',10)
#
    T = ROOT.TLatex()
    T.SetTextColor(ROOT.kBlue)
#
    tc = hMC['dummy'].cd()
    tc.SetLogy(0)
    hMC['Jpsi'].Draw('YTRUE-'+str(y_beam)+'>>Y')
    hMC['Jpsi'].Draw('YTRUE-'+str(y_beam)+'>>Yprim','Pmother==400')
    hMC['Jpsi'].Draw('YTRUE-'+str(y_beam)+'>>Ysec','Pmother>10&&Pmother<400')
    hMC['Yprim'].SetLineColor(ROOT.kRed)
    hMC['Yprim'].SetTitle('')
    hMC['Yprim'].SetStats(0)
    hMC['Ysec'].SetStats(0)
    hMC['Yprim'].Draw()
    hMC['Ysec'].Draw('same')
    hMC['lyprim']=ROOT.TLegend(0.6,0.75,0.95,0.85)
    l1 = hMC['lyprim'].AddEntry(hMC['Yprim'],'from primary production','PL')
    l1.SetTextColor(hMC['Yprim'].GetLineColor())
    l2 = hMC['lyprim'].AddEntry(hMC['Ysec'],'from cascade production','PL')
    l2.SetTextColor(hMC['Ysec'].GetLineColor())
    hMC['lyprim'].Draw()
    NA50 = hMC['Yprim'].Integral(hMC['Yprim'].FindBin(-0.425 ),hMC['Yprim'].FindBin(0.575))
    Acc_NA50 = NA50/hMC['Yprim'].GetSumOfWeights()
    rc = T.DrawLatexNDC(0.29,0.15,"NA50: -0.425<y<0.575:%5.1F%%"%(Acc_NA50*100))
    tc.Update()
    myPrint(tc,'YJpsiPrimAndSec')
#
    sptCut = '1.4'
    theCut =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1<300&&p2<300&&p1>20&&p2>20&&mcor>0.20'
    theCut = theCut.replace('pt1','pt1cor')
    theCut = theCut.replace('pt2','pt2cor')
    makeProjection('cosCScor',-1.0,1.0,'cosCScor',theCut,nBins=10,ntName='Jpsi',printout=False)
    dataAcc = hData['JpsicosCScor'].Integral(hData['JpsicosCScor'].FindBin(-0.5),hData['JpsicosCScor'].FindBin(0.5))
    dataAcc = dataAcc/hData['JpsicosCScor'].GetSumOfWeights()
    MCAcc = hMC['mc-JpsicosCScor'].Integral(hMC['mc-JpsicosCScor'].FindBin(-0.5),hMC['mc-JpsicosCScor'].FindBin(0.5))
    MCAcc = MCAcc/hMC['mc-JpsicosCScor'].GetSumOfWeights()
    print "JUST FOR INFORMATION:  -0.5<cosCScor<0.5,  acceptance:  data=%5.2F%%,  MC=%5.2F%%  "%(dataAcc*100,MCAcc*100)

    tc = hMC['dummy'].cd()
    theCut+= '&&cosCScor>-0.5&&cosCScor<0.5'
    hMC['Jpsi'].Draw('YTRUE-'+str(y_beam)+'>>Y_rec',               'mcor>2.0&&mcor<4.&&'+theCut)
    hMC['Jpsi'].Draw('YTRUE-'+str(y_beam)+'>>Yprim_rec',           'Pmother==400&&mcor>2.0&&mcor<4.&&'+theCut)
    hMC['Jpsi'].Draw('YTRUE-'+str(y_beam)+'>>Ysec_rec', 'Pmother>10&&Pmother<400&&mcor>2.0&&mcor<4.&&'+theCut)
    hMC['Y10GeV_rec'] = hMC['Yprim_rec'].Clone('Y10GeV_rec')
    hMC['10GeV'].Draw('0.5*log((sqrt(PTRUE**2+3.10**2)+sqrt(PTRUE**2-PtTRUE**2))/(sqrt(PTRUE**2+3.10**2)-sqrt(PTRUE**2-PtTRUE**2)))-'+str(y_beam)+'>>Y10GeV_rec','Jpsi==443&&mcor>2.0&&mcor<4.&&'+theCut)
    hMC['Y10GeV'] = hMC['Yprim_rec'].Clone('Y10GeV')
    hMC['10GeV'].Draw('0.5*log((sqrt(PTRUE**2+3.10**2)+sqrt(PTRUE**2-PtTRUE**2))/(sqrt(PTRUE**2+3.10**2)-sqrt(PTRUE**2-PtTRUE**2)))-'+str(y_beam)+'>>Y10GeV','Jpsi==443')
    hMC['Eff10GeV']=ROOT.TEfficiency(hMC['Y10GeV_rec'],hMC['Y10GeV'])

    for x in ['','prim','sec']:
        hMC[x+'Eff']=ROOT.TEfficiency(hMC['Y'+x+'_rec'],hMC['Y'+x])
        hMC[x+'Eff'].Draw()
        tc.Update()
        hMC[x+'Effgraph'] = hMC[x+'Eff'].GetPaintedGraph()
        hMC[x+'Effgraph'].SetMinimum(0.0)
        hMC[x+'Effgraph'].SetMaximum(0.4)
        hMC[x+'Effgraph'].GetXaxis().SetRangeUser(-2.,2.)
    hMC['primEff'].SetLineColor(ROOT.kRed)
    hMC['primEff'].Draw()
    hMC['secEff'].Draw('same')
    ypos = 0.8
    Eff_Muflux={}
    for xx in ['Y','Yprim','Ysec ']:
     x=xx.replace(' ','')
     Muflux     = hMC[x].Integral(hMC['Yprim'].FindBin(0.4),hMC['Yprim'].FindBin(1.5))
     Muflux_rec = hMC[x+'_rec'].Integral(hMC['Yprim'].FindBin(0.4),hMC['Yprim'].FindBin(1.5))
     Eff_Muflux[x] = Muflux_rec/Muflux
     rc = T.DrawLatexNDC(0.18,ypos,xx.replace('Y','')+": 0.4<y<1.5:%5.1F%%"%(Eff_Muflux[x]*100))
     ypos-=0.1
    tc.Update()
    myPrint(tc,'YEffJpsiPrimAndSec')
    hMC['Yprim'].Draw()
    hMC['Ysec'].Draw('same')
    hMC['lyprim'].Draw()
    ypos = 0.4
    Acc_Muflux={}
    for xx in ['Y','Yprim','Ysec ']:
     x=xx.replace(' ','')
     Muflux     = hMC[x].Integral(hMC['Yprim'].FindBin(0.4),hMC['Yprim'].FindBin(1.5))
     total      = hMC[x].GetSumOfWeights()
     Acc_Muflux[x] = Muflux/total
     rc = T.DrawLatexNDC(0.18,ypos,xx.replace('Y','')+": 0.4<y<1.5/total:%5.1F%%"%(Acc_Muflux[x]*100))
     ypos-=0.1
    tc.Update()
    myPrint(tc,'YAccJpsiPrimAndSec')
#  ycor resolution
    hMC['Jpsi'].Draw('ycor-YTRUE>>deltaYcor',theCut)
    hMC['deltaYcor'].Fit('gaus')
    tc.Update()
    stats = tc.GetPrimitive('stats')
    stats.SetOptFit(10111)
    stats.SetX1NDC(0.60)
    stats.SetY1NDC(0.60)
    stats.SetX2NDC(0.98)
    stats.SetY2NDC(0.93)
    tc.Update()
    myPrint(tc,'YcorResolution')
#
    makeProjection('ycor',0.4,1.5,'y_{CMS}',theCut,nBins=1,ntName='Jpsi',printout=False)
    fitFun = hData['ycor0'].GetFunction('gauss')
    Ndata = fitFun.GetParameter(0)
    Edata = fitFun.GetParError(0)
    Nsignal = Ndata/Eff_Muflux['Y']
    Esignal = Edata/Eff_Muflux['Y']
    print "Ndata fitted: %5.2F +/- %5.2F"%(Ndata,Edata)
    print "Ndata eff corrected: %5.2F +/- %5.2F"%(Nsignal,Esignal)
#
    makeProjection('ycor',0.,2.,'y_{CMS}',theCut,nBins=20,ntName='Jpsi',printout=False)
    hData['Jpsiycor_effCorrected']  = hData['Jpsiycor'].Clone('Jpsiycor_effCorrected')
    hMC['mc-Jpsiycor_effCorrected'] = hMC['mc-Jpsiycor'].Clone('mc-Jpsiycor_effCorrected')
    nSteps = 11
    binWidth = hData['Jpsiycor'].GetBinWidth(1)/float(nSteps)
    for X in [ [hData['Jpsiycor'],hData["Jpsiycor_effCorrected"]],[hMC['mc-Jpsiycor'],hMC["mc-Jpsiycor_effCorrected"]] ]:
      for n in range(1,hData['Jpsiycor'].GetNbinsX()+1): 
         x    = X[0].GetBinLowEdge(n)
         y    = X[0].GetBinContent(n)
         yerr = X[0].GetBinError(n)
         meanEff = 0
         for k in range(nSteps):
           meanEff += hMC['Effgraph'].Eval(x)
           x+=binWidth
         e = meanEff/float(nSteps)
         if e>0.01:
          X[1].SetBinContent(n,y/e)
          X[1].SetBinError(n,yerr/e)
         else:
          X[1].SetBinContent(n,0.)
          X[1].SetBinError(n,0.)

# y distrib from cascade
    ut.readHists(hMC,'Ydistributions.root')
    hMC['YP8'] = hMC['Ypt_P8'].ProjectionX('YP8')
    hMC['dummy'].cd()
    a,b = hData["Jpsiycor_effCorrected"].FindBin(0.3),hData["Jpsiycor_effCorrected"].FindBin(1.4)
    c,d = hMC["Y"].FindBin(0.3),hMC["Y"].FindBin(1.4)
    sbin = hData["Jpsiycor_effCorrected"].GetBinWidth(1)/hMC['Y'].GetBinWidth(1)
    hMC['Y'].Scale(hData["Jpsiycor_effCorrected"].Integral(a,b)/hMC["Y"].Integral(c,d))
    hMC['Y'].Scale(sbin)
    hMC['YP8'].Scale(hData["Jpsiycor_effCorrected"].Integral(a,b)/hMC["YP8"].Integral(c,d))
    hMC['YP8'].Scale(sbin)
    hData["Jpsiycor_effCorrected"].SetStats(0)
    hData["Jpsiycor_effCorrected"].SetLineColor(ROOT.kBlue)
    hMC['mc-Jpsiycor_effCorrected'].SetLineColor(ROOT.kMagenta)
    hMC['Y'].SetLineColor(ROOT.kMagenta)
    hMC['YP8'].SetLineColor(ROOT.kCyan)
    hMC['Y'].SetStats(0)
    hMC['YP8'].SetStats(0)
    hMC['mc-Jpsiycor_effCorrected'].SetStats(0)
    hData["Jpsiycor_effCorrected"].SetMinimum(0.)
    hData["Jpsiycor_effCorrected"].SetMaximum(20000.)
    hData["Jpsiycor_effCorrected"].Draw()
    hMC['Y'].Draw('same')
    hMC['YP8'].Draw('same')
# cross check, take efficiency, apply to Yrec and compare with Ytrue
    hMC['mc-Jpsiycor_effCorrected'].Scale(hData["Jpsiycor_effCorrected"].Integral(a,b)/hMC["mc-Jpsiycor_effCorrected"].Integral(a,b))
    hMC['mc-Jpsiycor_effCorrected'].Draw('same')
    hMC['lyeffcor']=ROOT.TLegend(0.48,0.63,0.95,0.85)
    l1 = hMC['lyeffcor'].AddEntry(hData["Jpsiycor_effCorrected"],'data eff corrected','PL')
    l1.SetTextColor(hData["Jpsiycor_effCorrected"].GetLineColor())
    l2 = hMC['lyeffcor'].AddEntry(hMC['mc-Jpsiycor_effCorrected'],'MC cascade eff corrected','PL')
    l2.SetTextColor(hMC['mc-Jpsiycor_effCorrected'].GetLineColor())
    l3 = hMC['lyeffcor'].AddEntry(hMC['Y'],'MC cascade truth','PL')
    l3.SetTextColor(hMC['Y'].GetLineColor())
    l4 = hMC['lyeffcor'].AddEntry(hMC['YP8'],'MC Pythia8 truth','PL')
    l4.SetTextColor(hMC['YP8'].GetLineColor())
    hMC['lyeffcor'].Draw()
    myPrint(hMC['dummy'],'YeffCorrectedXcheck')
#
    cases = {'Y':ROOT.kMagenta,'Yprim':ROOT.kRed,'Ysec':ROOT.kGreen}
    for x in cases:
     hMC[x+'_rec_arbNorm'] = hMC[x+'_rec'].Clone(x+'_rec_arbNorm')
     hMC[x+'_rec_arbNorm'].Scale(hData['Jpsiycor'].GetSumOfWeights()/hMC['Y_rec'].GetSumOfWeights())
     sbin = hMC[x+'_rec_arbNorm'].GetBinWidth(1)/hData['Jpsiycor'].GetBinWidth(1)
     hMC[x+'_rec_arbNorm'].Scale(1./sbin)
     hMC[x+'_rec_arbNorm'].SetLineColor(cases[x])
     hMC[x+'_rec_arbNorm'].SetTitle('')
     hMC[x+'_rec_arbNorm'].SetStats(0)
    hMC['mc-Jpsiycor_arbNorm'] = hMC['mc-Jpsiycor'].Clone('mc-Jpsiycor_arbNorm')
    hMC['mc-Jpsiycor_arbNorm'].SetLineColor(cases['Y'])
    hMC['mc-Jpsiycor_arbNorm'].SetStats(0)
    hMC['mc-Jpsiycor_arbNorm'].Scale(hData['Jpsiycor'].GetSumOfWeights()/hMC['mc-Jpsiycor_arbNorm'].GetSumOfWeights())
    hData['Jpsiycor'].SetStats(0)
    hMC['Y_rec_arbNorm'].GetYaxis().SetTitle('arbitrary units')
    tc = hMC['dummy'].cd()
    hMC['Y_rec_arbNorm'].Draw()
    hMC['Ysec_rec_arbNorm'].Draw('same')
    hMC['Yprim_rec_arbNorm'].Draw('same')
    hMC['mc-Jpsiycor_arbNorm'].Draw('same')
    hData['Jpsiycor'].Draw('same')
    T.SetTextSize(0.04)
    rc = T.DrawLatexNDC(0.12,0.835,"efficiency corrected events: %5.1F #pm %5.1F"%(Nsignal,Esignal))
    rc = T.DrawLatexNDC(0.12,0.935,"efficiency and acceptance corrected events: %5.1F #pm %5.1F"%(\
                        Nsignal/Acc_Muflux['Y'],Esignal/Acc_Muflux['Y']))
    tc.Update()
    myPrint(tc,'YJpsiData')
    Ilumi = 30.7 # pb-1.  N = sigma * lumi
    Ilumi_error = 0.7 #  
    sigma = Nsignal/Acc_Muflux['Y'] / Ilumi
    E1 = Esignal/Acc_Muflux['Y'] / Ilumi
    E2 = sigma / Ilumi * Ilumi_error
    sigma_error = ROOT.TMath.Sqrt(E1*E1+E2*E2)
    print "sigma = %5.2F +/-%5.2F nb "%(sigma/1000.,sigma_error/1000.)
    print "sigma_prim = %5.2F +/-%5.2F nb "%(sigma/1000.*0.55,sigma_error/1000.*0.55)
def JpsiPrimaryUpdate():
    for x in ['PmotherJpsi','PmotherJpsi_zoom','YJpsiPrimAndSec','YEffJpsiPrimAndSec','YAccJpsiPrimAndSec','YJpsiData','YcorResolution']:
         os.system('cp '+x+'.p* /mnt/hgfs/Images/VMgate/Jpsi/')

hMC['etaNA50'] = ROOT.TF1('etaNA50','abs([0])*exp(-0.5*((x-[1])/[2])**2)',-2.,2.)
hMC['etaNA50'].SetParameter(0,1.)
hMC['etaNA50'].SetParameter(1,-0.2)
hMC['etaNA50'].SetParameter(2,0.85)

def fiducialJpsi(onlyPlot=True):
  hMC['ptHard']  = ROOT.TF1('ptHard','[0]*(1+x/[1])**(-6)')
  y_beam = yBeam()
  variables = {'Ypt':'sqrt(px*px+py*py):0.5*log((E+pz)/(E-pz))-'+str(y_beam),
                 'ppt':'sqrt(px*px+py*py+pz*pz):sqrt(px*px+py*py)'}
  prods = {'10GeV':hMC['Jpsi10GeV'],'1GeV':hMC['Jpsi1GeV'],'P8':hMC['JpsiP8_Primary'],'Cascade':hMC['JpsiCascade']}
  prodsColour = {'10GeV':ROOT.kBlue,'1GeV':ROOT.kCyan,'P8':ROOT.kGreen,'Cascade':ROOT.kMagenta}
  projections = ['P','Pt','Y']
  ut.bookHist(hMC,'pMother',  'p of mother;[GeV/c];[GeV/c]', 1000,0.,400.)
  ut.bookHist(hMC,'pMotherZoom',  'p of mother;[GeV/c];[GeV/c]', 100,399.,400.)
  if not onlyPlot:
    ut.bookHist(hMC,'ppt',  'p vs pt;[GeV/c];[GeV/c]', 100,0.,10., 100,0.,400.)
    ut.bookHist(hMC,'Ypt',  'Y of Jpsi;y_{CMS}', 100,-2.,2., 100,0.,10.)
#
    for p in prods:
      y='pMother'
      hMC[y+'_'+p]=hMC[y].Clone(y+'_'+p)
      y='pMotherZoom'
      hMC[y+'_'+p]=hMC[y].Clone(y+'_'+p)
      for y in ['ppt','Ypt']:
         for x in ['','prim','sec']:
            hMC[y+'_'+x+p]=hMC[y].Clone(y+'_'+x+p)
    for p in prods:
        prods[p].Draw('sqrt(mpx*mpx+mpy*mpy+mpz*mpz)>>pMother_'+p)
        prods[p].Draw('sqrt(mpx*mpx+mpy*mpy+mpz*mpz)>>pMotherZoom_'+p)
        for v in variables: 
           hMC[v+'_'+p].SetStats(0)
           prods[p].Draw(variables[v]+'>>'+v+'_'+p)
           prods[p].Draw(variables[v]+'>>'+v+'_sec'+p,'sqrt(mpx*mpx+mpy*mpy+mpz*mpz)<399.999')
           prods[p].Draw(variables[v]+'>>'+v+'_prim'+p,'sqrt(mpx*mpx+mpy*mpy+mpz*mpz)>399.999')
    hadronAbsorber(Pmin=20.)
    hMC['Yacc_10GeV'] = hMC['Yacc'].Clone('Yacc_10GeV')
    hadronAbsorber(Pmin=10.)
    hMC['Yacc_1GeV'] = hMC['Yacc'].Clone('Yacc_1GeV')
    ut.writeHists(hMC,'Ydistributions.root')
  if onlyPlot: ut.readHists(hMC,'Ydistributions.root')
  tc = hMC['dummy'].cd()
  tc.SetLogy(1)
  hMC['pMother_Cascade'].Draw()
  myPrint(hMC['dummy'],'PmotherJpsi')
  hMC['pMotherZoom_Cascade'].Draw()
  myPrint(hMC['dummy'],'PmotherJpsi_zoom')
  ut.bookCanvas(hMC,'MCprodComp','Jpsi MC productions',1600,900,3,2)
  for p in prods:
       hMC['Pt_'+p]=hMC['ppt_'+p].ProjectionX('Pt_'+p)
       hMC['Pt_'+p].SetTitle(';Pt [GeV/c]')
       hMC['Y_'+p]=hMC['Ypt_'+p].ProjectionX('Y_'+p)
       hMC['Y_'+p].SetTitle(';Y  ')
       hMC['P_'+p]=hMC['ppt_'+p].ProjectionY('P_'+p)
       hMC['P_'+p].SetTitle(';P  [GeV/c]')
  for v in projections:
    for p in prods:
      if p=='10GeV': continue
      scale(hMC[v+'_'+p],hMC[v+'_10GeV'])
  j=1
  for v in projections:
     hMC['l'+v]=ROOT.TLegend(0.59,0.75,0.95,0.87)
     for p in prods:
        hMC[v+'_'+p].SetLineColor(prodsColour[p])
     tc = hMC['MCprodComp'].cd(j)
     j+=1
     p='10GeV'
     hMC[v+'_'+p].SetStats(0)
     if v=='P': hMC[v+'_'+p].SetMaximum(1.1*hMC[v+'_Cascade'].GetMaximum())
     hMC[v+'_'+p].Draw()
     x = hMC['l'+v].AddEntry(hMC[v+'_'+p],p,'PL')
     x.SetTextColor(prodsColour[p])
     for p in prods:
        if p=='10GeV': continue
        hMC[v+'_'+p].SetStats(0)
        hMC[v+'_'+p].Draw('same')
        x = hMC['l'+v].AddEntry(hMC[v+'_'+p],p,'PL')
        x.SetTextColor(prodsColour[p])
     hMC['l'+v].Draw()
  tc = hMC['MCprodComp'].cd(j)
  p='10GeV'
  scale(hMC['Yacc_'+p],hMC['Y_'+p])
  hMC['Y_10GeV'].Draw()
  hMC['Y_P8'].Draw('same')
  hMC['Yacc_10GeV'].Draw('same')
  hMC['l10Y']=ROOT.TLegend(0.59,0.75,0.95,0.87)
  hMC['l10Y'].AddEntry(hMC['Y_P8'],'Pythia8 primary','PL')
  hMC['l10Y'].AddEntry(hMC['Yacc_10GeV'],'Pythia8 E_{#mu}>20GeV','PL')
  hMC['l10Y'].AddEntry(hMC['Y_10GeV'],'Pythia8 from SHiP background simulation','PL')
  hMC['l10Y'].Draw()
  tc = hMC['MCprodComp'].cd(j+1)
  p='1GeV'
  scale(hMC['Yacc_'+p],hMC['Y_'+p])
  hMC['Y_1GeV'].Draw()
  hMC['Y_P8'].Draw('same')
  hMC['Yacc_1GeV'].Draw('same')
  hMC['l1Y']=ROOT.TLegend(0.59,0.75,0.95,0.87)
  hMC['l1Y'].AddEntry(hMC['Y_P8'],'Pythia8 primary','PL')
  hMC['l1Y'].AddEntry(hMC['Yacc_1GeV'],'Pythia8 E_{#mu}>10GeV','PL')
  hMC['l1Y'].AddEntry(hMC['Y_1GeV'],'Pythia8 from SHiP background simulation','PL')
  hMC['l1Y'].Draw()
  myPrint(hMC['MCprodComp'],'JpsiProductionComparison')

def scale(A,B):
     A.Scale(B.GetSumOfWeights()/A.GetSumOfWeights())
     sbin = A.GetBinWidth(1)/B.GetBinWidth(1)
     A.Scale(sbin)

def hadronAbsorberEffect(Pmin=20.):
    Mmu = ROOT.TDatabasePDG.Instance().GetParticle(13).Mass()
    y_beam = yBeam()
    nt = hMC['JpsiP8_Primary']
    ut.bookHist(hMC,'Emu','E of mu',100,0.,100.)
    ut.bookHist(hMC,'Yacc','Y',100,-2.,2.)
    ut.bookHist(hMC,'Y0','Y',100,-2.,2.)
    for event in nt:
       PJpsi = ROOT.TMath.Sqrt(event.px*event.px+event.py*event.py+event.pz*event.pz)
       EJpsi = event.E
       MJpsi = event.M
       gamma = PJpsi/MJpsi
       beta  = PJpsi/EJpsi
       pmu = ROOT.TMath.Sqrt( (MJpsi/2.)**2 - Mmu**2)
       phi = ROOT.gRandom.Rndm()*2.*ROOT.TMath.Pi()
       pmuParallel = abs(pmu * ROOT.TMath.Cos(phi))
       Emu = gamma*MJpsi/2.+beta*gamma*pmuParallel
       rc = hMC['Emu'].Fill(Emu)
       y  = 0.5*ROOT.TMath.Log((EJpsi+event.pz)/(EJpsi-event.pz))-y_beam
       rc = hMC['Y0'].Fill(y)
       if Emu>Pmin:
          rc = hMC['Yacc'].Fill(y)

def JpsiPtinBinsOfY(ntName='Jpsi'):
    y_beam = yBeam()
    ut.bookHist(hMC, 'm_MC','inv mass;M [GeV/c^{2}]',InvMassPlots[0],InvMassPlots[1],InvMassPlots[2])
    bw = hMC['m_MC'].GetBinWidth(1)
    hMC['myGauss'] = ROOT.TF1('gauss','abs([0])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-[1])/[2])**2)\
             +abs([3])*'+str(bw)+'/(abs([5])*sqrt(2*pi))*exp(-0.5*((x-[4])/[5])**2)+abs( [6]+[7]*x+[8]*x**2 )\
             +abs([9])*'+str(bw)+'/(abs([2])*sqrt(2*pi))*exp(-0.5*((x-(3.6871 + [1] - 3.0969))/[2])**2)',10)
    sptCut = '1.4'
    theCut =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1<300&&p2<300&&p1>20&&p2>20&&mcor>0.20'
    theCut = theCut.replace('pt1','pt1cor')
    theCut = theCut.replace('pt2','pt2cor')
    ut.bookCanvas(hMC,'ptVSy','Jpsi pt distribution for different y ranges',1600,1200,2,2)
    ROOT.gROOT.cd()
#
    yranges = ['0.4-0.7','0.7-1.0','1.0-1.3','1.3-1.6']
    for y in yranges:
      ycuts = y.split('-')
      theCuty = theCut+"&&ycor<"+ycuts[1]+'+'+str(y_beam)+"&&ycor>"+ycuts[0]+"+"+str(y_beam)
      makeProjection('ptcor',0.,5.,'ptcor',    theCuty,nBins=20,ntName=ntName,printout=False,fixSignal=True)
      hData['Jpsiptcor'+y]=hData['Jpsiptcor'].Clone('Jpsiptcor'+y)
      hMC['mc-Jpsiptcor'+y]=hMC['mc-Jpsiptcor'].Clone('mc-Jpsiptcor'+y)
    j=1
    for y in yranges:
        hMC['ptVSy'].cd(j)
        j+=1
        hData['Jpsiptcor'+y].SetLineColor(ROOT.kBlue)
        hData['Jpsiptcor'+y].SetMinimum(0.)
        hData['Jpsiptcor'+y].Draw()
        hMC['mc-Jpsiptcor'+y].SetLineColor(ROOT.kMagenta)
        scale(hMC['mc-Jpsiptcor'+y],hData['Jpsiptcor'+y])
        hMC['mc-Jpsiptcor'+y].Draw('same')
    myPrint(hMC['ptVSy'],ntName+'-pt-distribution4different-y-ranges')

def compareJpsiProds():
    y_beam = yBeam()
    sptCut = '1.4'
    theCut =  '('+sptCut+'<pt1||'+sptCut+'<pt2)&&chi21*chi22<0&&abs(chi21)<0.9&&abs(chi22)<0.9&&p1<300&&p2<300&&p1>20&&p2>20&&mcor>0.20'
    theCut = theCut.replace('pt1','pt1cor')
    theCut = theCut.replace('pt2','pt2cor')
    cases = {'10GeV':'Jpsi==443&&mcor>2.0&&mcor<4.&&'+theCut,'Jpsi':'Pmother==400.&&Jpsi==443&&mcor>2.0&&mcor<4.&&'+theCut}
    ut.bookCanvas(hMC,'MCprodComp','Jpsi MC productions',1600,1200,2,2)
#
    makeProjection('ptcor',0.,5.,'ptcor',    theCut,nBins=20,ntName='Jpsi',printout=False)
    makeProjection('pcor',0.,400.,'pcor',    theCut,nBins=20,ntName='Jpsi',printout=False)
    makeProjection('ycor',0.,2.,'ycor',      theCut,nBins=20,ntName='Jpsi',printout=False)
#
    variables = {'ycor':'ycor-'+str(y_beam),'pcor':'pcor', 'ptcor':'ptcor'}
    for nt in cases:
        ut.bookHist(hMC,'ycor_'+nt,'ycor_'+nt+';y',100,0.,2.)
        ut.bookHist(hMC,'pcor_'+nt,'pcor_'+nt+';[GeV/c]',100,0.,400.)
        ut.bookHist(hMC,'ptcor_'+nt,'ptcor_'+nt+';[GeV/c]',100,0.,10.)
        for var in variables:
            hMC[var+'_'+nt].SetStats(0)
            hMC[nt].Draw(variables[var]+'>>'+var+'_'+nt,cases[nt])
    k=1
    for nt in cases:
        for var in variables:
            hMC[var+'_'+nt+'_scaled']=hMC[var+'_'+nt].Clone(var+'_'+nt+'_scaled')
    for var in variables:
        tc = hMC['MCprodComp'].cd(k)
        k+=1
        hMC['l'+var]=ROOT.TLegend(0.59,0.75,0.95,0.87)
        hData['Jpsi'+var].SetLineColor(ROOT.kRed)
        norm = hData['Jpsi'+var].GetSumOfWeights()
        sbin = hData['Jpsi'+var].GetBinWidth(1)/hMC[var+'_10GeV'+'_scaled'].GetBinWidth(1)
        hMC[var+'_10GeV'+'_scaled'].Scale(norm/hMC[var+'_10GeV'].GetEntries())
        hMC[var+'_10GeV'+'_scaled'].Scale(sbin)
        hMC[var+'_10GeV'+'_scaled'].SetLineColor(ROOT.kMagenta)
        hMC[var+'_10GeV'+'_scaled'].SetTitle(var)
        hMC[var+'_Jpsi'+'_scaled'].Scale(norm/hMC[var+'_Jpsi'].GetEntries())
        hMC[var+'_Jpsi'+'_scaled'].Scale(sbin)
        hMC[var+'_Jpsi'+'_scaled'].SetMinimum(0)
        hMC[var+'_Jpsi'+'_scaled'].SetMaximum(1.1*max( hMC[var+'_Jpsi'+'_scaled'].GetMaximum(),
                          hMC[var+'_10GeV'+'_scaled'].GetMaximum(),hData['Jpsi'+var].GetMaximum()))
        hMC[var+'_Jpsi'+'_scaled'].Draw()
        hData['Jpsi'+var].SetStats(0)
        hData['Jpsi'+var].Draw('same')
        hMC[var+'_10GeV'+'_scaled'].Draw('same')
        hMC['l'+var].AddEntry(hData['Jpsi'+var],'Data','PL')
        hMC['l'+var].AddEntry(hMC[var+'_10GeV'+'_scaled'],'Pythia8','PL')
        hMC['l'+var].AddEntry(hMC[var+'_Jpsi'+'_scaled'],'Pythia6 cascade only primary','PL')
        hMC['l'+var].Draw()
    myPrint(hMC['MCprodComp'],'JpsiProdComparison')
def trueCosCS1():
# problem, only has info for reconstructed muons
    ut.bookHist(hMC,'trueCosCS','true Cos CStheta',100,-1.,1.)
    nt = hMC['JpsiP8']
    for n in range(nt.GetEntries()):
          rc=nt.GetEvent(n)
          if nt.Jpsi!=443: continue
          if nt.chi21 < 0: 
            PLepton     = ROOT.Math.PxPyPzMVector(nt.p1x,nt.p1y,nt.p1z,0.105658)
            PAntilepton = ROOT.Math.PxPyPzMVector(nt.p2x,nt.p2y,nt.p2z,0.105658)
          else: 
            PLepton     = ROOT.Math.PxPyPzMVector(nt.p2x,nt.p2y,nt.p2z,0.105658)
            PAntilepton = ROOT.Math.PxPyPzMVector(nt.p1x,nt.p1y,nt.p1z,0.105658)
          P1pl = PLepton.E()+PLepton.Pz()
          P2pl = PAntilepton.E()+PAntilepton.Pz()
          P1mi = PLepton.E()-PLepton.Pz()
          P2mi = PAntilepton.E()-PAntilepton.Pz()
          PJpsi = PLepton+PAntilepton
          cosCSraw = PJpsi.z()/abs(PJpsi.z()) * 1./PJpsi.M()/ROOT.TMath.Sqrt(PJpsi.M2()+PJpsi.Pt()**2)*(P1pl*P2mi-P2pl*P1mi)
          rc = hMC['trueCosCS'].Fill(cosCSraw)
def trueCosCS2():
# try to mimick distribution using jpsi directly
    ut.bookHist(hMC,'trueCosCS','true Cos CStheta',100,-1.,1.)
    ut.bookHist(hMC,'JpsiPtvsY','pt vs y Jpsi',100,-2.,2.,100,0.,5.)
    ut.bookHist(hMC,'JpsiIPtvsY','pt vs y Jpsi intermediate',100,-2.,2.,100,0.,5.)
    y_beam = yBeam()
    for nt in hMC['JpsiP8_PrimaryMu']:
       PJpsi = ROOT.Math.PxPyPzMVector(nt.px,nt.py,nt.pz,nt.M)
       if nt.p1x==nt.p2x and nt.p1y==nt.p2y and nt.p1z==nt.p2z:
          rc = hMC['JpsiIPtvsY'].Fill(PJpsi.Rapidity()-y_beam,PJpsi.Pt())
          continue
       rc = hMC['JpsiPtvsY'].Fill(PJpsi.Rapidity()-y_beam,PJpsi.Pt())
       PLepton     = ROOT.Math.PxPyPzMVector(nt.p1x,nt.p1y,nt.p1z,0.105658)
       PAntilepton = ROOT.Math.PxPyPzMVector(nt.p2x,nt.p2y,nt.p2z,0.105658)
       P1pl = PLepton.E()+PLepton.Pz()
       P2pl = PAntilepton.E()+PAntilepton.Pz()
       P1mi = PLepton.E()-PLepton.Pz()
       P2mi = PAntilepton.E()-PAntilepton.Pz()
       cosCSraw = PJpsi.z()/abs(PJpsi.z()) * 1./PJpsi.M()/ROOT.TMath.Sqrt(PJpsi.M2()+PJpsi.Pt()**2)*(P1pl*P2mi-P2pl*P1mi)
       rc = hMC['trueCosCS'].Fill(cosCSraw)

def plots4AnalysisNote():
 tc = hMC['dummy'].cd()
 hMC['meanLossTrue'].SetStats(0)
 hMC['meanLossTrue'].SetTitle(' ; true momentum [GeV/c]; mean energy loss [GeV/c]')
 hMC['meanLossTrue'].GetXaxis().SetRangeUser(10.,300.)
 hMC['meanLossTrue'].Fit('pol2','S','',20.,300.)
 hMC['meanLossTrue'].Draw()
 myPrint(tc,'meanLossTrue')
 #
 tc.SetLogy(1)
 for ptcut in ["0.0","1.0"]:
  hMC['mc-mcor_'+ptcut].Draw()
  hMC['mc-mcor_Jpsi_'+ptcut].Draw('same')
  hMC['SS-mc-mcor_'+ptcut].Draw('same')
  myCB = hMC['mc-mcor_'+ptcut].GetFunction("2CB"+ptcut+"mc-")
  myCB.FixParameter(9,10.) # alpha positive and large -> gauss part only
  myCB.FixParameter(10,0.)  
  myCB.FixParameter(4,10.) # alpha positive and large -> gauss part only
  myCB.FixParameter(5,0.)  
  rc=hMC['mc-mcor_'+ptcut].Fit(myCB,'SQ','',0.35,4.75)
  stats = hMC['mc-mcor_'+ptcut].FindObject('stats')
  stats.SetX1NDC(0.63)
  stats.SetY1NDC(0.36)
  stats.SetX2NDC(0.99)
  stats.SetY2NDC(0.96)
  hMC['lnormegmc-mcor_'+ptcut]=ROOT.TLegend(0.63,0.20,0.99,0.32)
  l1 = hMC['legmc-mcor_'+ptcut].AddEntry(hMC['mc-mcor_'+ptcut],'opposite sign muons','PL')
  l1.SetTextColor(hMC['mc-mcor_'+ptcut].GetLineColor())
  l2 = hMC['legmc-mcor_'+ptcut].AddEntry(hMC['SS-mc-mcor_'+ptcut],'same sign muons','PL')
  l2.SetTextColor(hMC['SS-mc-mcor_'+ptcut].GetLineColor())
  l3 = hMC['legmc-mcor_'+ptcut].AddEntry(hMC['mc-mcor_Jpsi_'+ptcut],'from J/#psi','PL')
  l3.SetTextColor(hMC['mc-mcor_Jpsi_'+ptcut].GetLineColor())
  hMC['legmc-mcor_'+ptcut].Draw()
  tc.Update()
  myPrint(tc,'dimuon-MC-'+ptcut+'GeVptlog')
#
 tc.SetLogy(0)
 ptcut = "1.4"
 norm  = hData['mcor_'+ptcut].GetMaximum()
 fun = hData['Nmcor_'+ptcut].GetFunction('2CB1.4')
 hMC['Nmc-mcor_'+ptcut] = hMC['mc-mcor_'+ptcut].Clone('Nmc-mcor_'+ptcut)
 norm = 1./hMC['weights']['10GeV']
 hMC['Nmc-mcor_'+ptcut].Scale(norm)
 hMC['Nmc-mcor_'+ptcut].SetLineColor(ROOT.kMagenta)
 hData['mcor_'+ptcut].Draw()
 funMC = hMC['Nmc-mcor_'+ptcut].GetFunction('2CB1.4mc-')
 funMC.SetParameter(1,funMC.GetParameter(1)*norm)
 funMC.SetParameter(6,funMC.GetParameter(6)*norm)
 funMC.SetParameter(11,funMC.GetParameter(11)*norm)
 funMC.SetParameter(12,funMC.GetParameter(12)*norm)
 hMC['Nmc-mcor_'+ptcut].Draw('same')

 for x in ['CB']:
  hn2 = 'YieldMCoverData'+x
  hMC[hn2]= hMC['evolution'+x+'mcorSignalMC'].Clone(hn2)
  hMC[hn2].Divide(hData['evolution'+x+'mcorSignalData'])
  hMC[hn2].GetYaxis().SetRangeUser(0.5,2.0)
  hMC[hn2].GetXaxis().SetRangeUser(0.0,1.7)
  hMC[hn2].GetYaxis().SetTitle("Yield MC/data not normalized")
  hMC[hn2].SetLineColor(ROOT.kBlue)
  hMC[hn2].SetStats(0)
  hMC[hn2].Fit('pol0','Q','',0.0,1.7)
  myPrint(tc,'dimuon-evolptcut-yieldratio'+x)
#
  hn2 = 'evolution'+x+'mcorMassMC'
  hMC[hn2].SetStats(0)
  hMC[hn2].GetYaxis().SetRangeUser(2.9,3.4)
  hMC[hn2].GetXaxis().SetRangeUser(0.9,1.7)
  hMC[hn2].Draw()
  hData['evolution'+x+'mcorMassData'].Draw('same')
  myPrint(tc,'dimuon-evolptcut-Mass'+x)
#
  hn2 = 'evolution'+x+'mcorSigmaMC'
  hMC[hn2].SetStats(0)
  hMC[hn2].GetYaxis().SetRangeUser(0.2,0.5)
  hMC[hn2].GetXaxis().SetRangeUser(0.9,1.7)
  hMC[hn2].Draw()
  hData['evolution'+x+'mcorSigmaData'].Draw('same')
  myPrint(tc,'dimuon-evolptcut-Sigma'+x)
# 
def synchFigures():
  for x in ['meanLossTrue','scatteringX','scatteringY','scatteringT','scatteringDataMC_Mean','scatteringDataMC_RMS',
           'dimuon-evolptcut-yieldratioCB','dimuon-evolptcut-MassCB','dimuon-evolptcut-SigmaCB']: 
     os.system('cp '+x+'.pdf   /mnt/hgfs/Images/VMgate/dimuflux/ ')

if options.command=='MufluxReco':
    curFile = ''
    if sTreeMC: 
          sTreeMC.GetEvent(0)
          curFile = sTreeMC.GetCurrentFile().GetName()
    if fdir.find('simulation')==0 or curFile.find('sim')>0: mufluxReco(sTreeMC,hMC,nseq=options.nseq,ncpus=options.ncpus)
    else: mufluxReco(sTreeData,hData)
if options.command=='RecoEffFunOfOcc':
    RecoEffFunOfOcc()
if options.command=='invMass':
    if sTreeMC: sTreeMC.GetEvent(0)
    if fdir.find('simulation')==0 or sTreeMC.GetCurrentFile().GetName().find('sim')>0:
      invMass(sTreeMC,hMC,nseq=options.nseq,ncpus=options.ncpus)
    else:
      invMass(sTreeData,hData)
