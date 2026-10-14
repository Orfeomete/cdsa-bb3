"""Ek 6 kaniti: Faz A merkezi kolunun yeniden uretim denemesi, E0 semasiyla kaydedilir.
faz_a_results.json / faz_a_curves.json DEGISTIRILMEZ (bu betik onlara yazmaz)."""
import sys, json, time
from pathlib import Path
KOK=Path("/home/claude/cdsa/CDSA-BB3/12_GitHub_Repo/cdsa-bb3")
sys.path.insert(0,str(KOK)); sys.path.insert(0,str(KOK/"experiments"))
import numpy as np
import faz_a_staged as fs
from faz_a_config import PILLAR, N_ACTIONS, ACTION_LABELS, INFO_TRUE_KEY, CRITICAL_ACTIONS, make_env
from faz_e_kayit import KosuKaydi, makro_f1

t0=time.time()
rng=np.random.default_rng(fs.SEED); rnd=fs.evaluate(None,rng=rng)
central=fs.new_agent(fs.SEED); envs=fs.make_client_envs(fs.SEED); curve=[]
for r in range(fs.ROUNDS):
    for e in envs: fs.train_local(e,central)
    if (r+1)%fs.PROBE_EVERY==0: curve.append(fs.evaluate(central,steps=fs.PROBE_STEPS)[0])
# faz_a_staged.evaluate ile BIREBIR ayni protokol, ek olarak tahminler toplanir
env=make_env(fs.SEED+900); s=fs.env_reset(env,seed=2026)
yt,yp,tot=[],[],0.0
for _ in range(fs.EVAL_STEPS):
    a=central.act(s,deterministic=True)[0]
    s2,r,done,info=fs.env_step(env,a); tot+=r
    if isinstance(info,dict) and INFO_TRUE_KEY in info:
        yt.append(int(info[INFO_TRUE_KEY])); yp.append(int(a))
    s=fs.env_reset(env) if done else s2
mr=round(tot/fs.EVAL_STEPS,2)
acc=round(100*sum(int(a==b) for a,b in zip(yt,yp))/len(yt),1)
kt=[i for i,c in enumerate(yt) if c in CRITICAL_ACTIONS]
crit=round(sum(int(yp[i]==yt[i]) for i in kt)/len(kt),3)

kayitli=json.loads((KOK/"experiments/results/faz_a_results.json").read_text())
kayitli_egri=json.loads((KOK/"experiments/results/faz_a_curves.json").read_text())["central_ppo"]
ayrisan=[i for i,(x,y) in enumerate(zip(kayitli_egri,curve)) if x!=y]

k=KosuKaydi(damar=PILLAR, deney="E0", kol="faz_a_merkezi_yeniden_uretim", tohum=fs.SEED)
k.yapilandirma_koddan("faz_a_config",["PILLAR","N_ACTIONS","STATE_DIM","NEW_STEP_API",
                                      "INFO_TRUE_KEY","ACTION_LABELS","CRITICAL_ACTIONS"])
k.yapilandirma_koddan("faz_a_staged",["ROUNDS","LOCAL_ROLLOUTS","ROLLOUT_LEN","PROBE_EVERY",
                                      "PROBE_STEPS","EVAL_STEPS","SEED"])
k.veri_uretilmis(f"{PILLAR} faz_a_staged 'base' merkezi kolu: make_client_envs(42), "
                 f"{fs.ROUNDS} tur; degerlendirme make_env(942).reset(seed=2026), "
                 f"{fs.EVAL_STEPS} adim", n_kayit=len(yt))
cm=k.tahminler(yt,yp,n_sinif=N_ACTIONS,etiketler=list(ACTION_LABELS))
m=makro_f1(cm)
k.metrik(mean_reward=mr, accuracy_pct=acc, critical_recall=crit,
         random_kolu={"mean_reward":rnd[0],"accuracy_pct":rnd[1],"critical_recall":rnd[2]})
k.not_(amac="Ek 6 — tarihsel Faz A merkezi kaydinin yeniden uretim denemesi",
       komut="python3 faz_a_staged.py base (tohum 42, 100 tur, 600 adim degerlendirme)",
       kayitli_deger={"mean_reward":kayitli["central_ppo"]["mean_reward"],
                      "accuracy_pct":kayitli["central_ppo"]["accuracy_pct"],
                      "critical_recall":kayitli["central_ppo"]["critical_recall"],
                      "kayit_tarihi":kayitli.get("date")},
       yeniden_uretilen={"mean_reward":mr,"accuracy_pct":acc,"critical_recall":crit},
       random_kolu_birebir_mi=(rnd[0]==kayitli["random"]["mean_reward"]
                               and rnd[1]==kayitli["random"]["accuracy_pct"]
                               and rnd[2]==kayitli["random"]["critical_recall"]),
       ogrenme_egrisi_ilk_ayrisan_prob=(ayrisan[0] if ayrisan else None),
       ogrenme_egrisi_ayrisan_prob_sayisi=len(ayrisan),
       ogrenme_egrisi_prob_sayisi=len(kayitli_egri),
       kayitli_egri=kayitli_egri, yeniden_egri=curve,
       faz_a_results_json_degistirilmedi=True)
p=k.yaz()
print(json.dumps({"kayitli":[kayitli["central_ppo"]["mean_reward"],kayitli["central_ppo"]["accuracy_pct"],kayitli["central_ppo"]["critical_recall"]],
                  "yeniden":[mr,acc,crit],
                  "makro_f1":m["makro_f1"],"random_birebir":rnd,
                  "ilk_ayrisan_probe":ayrisan[0] if ayrisan else None,
                  "kayit":str(p),"sure_sn":round(time.time()-t0,1)},ensure_ascii=False,indent=1))
