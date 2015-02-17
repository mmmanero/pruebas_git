#! /bin/bash -x
# 
cd /oceano/gmeteo/WORK/ASNA/projects/corwes/02_cmip5_CanESM2_WRF3.4.1/scripts
use netcdf
use cdo
# VARIABLES CORWES
# vars=T2,RAINF,PSFC,MSLP,Q2,SPDUV10,ACSWDNB,ACLWDNB,ACLHF,ACHFX,ACSWUPB,ACLWUPB,SFROFF,UDROFF,MRSO,RAINC,ACLWUPT,ACSWDNT,ACSWUPT,U10ER,V10ER,TSK,PBLH,SNOWH,SNOWNC,SNOW,CLT,ACSNOM,VIM,VIQC,VIQI,QFX,RAINNC,ALBEDO,SST,ACLWDNT,UST,SFCEVP,POTEVP,CLH,CLM,CLL,RH2,MRRO,MRSO
#Variables nuevas que no estan en la tabla: XICEM,P,PB,PH,PHB
#Variables por niveles: UER,VER,TEMP,QVAPOR,GHT,QCLOUD,QICE,RH,CLDFRA
#Variables de suelo: TSLB,SH2O,SMOIS
# ----Introducir las variables que se quiere posprocesar----------
vars=TSLB,SH2O,SMOIS
filetype="out" # Modificar segun las variables a posprocesar, extremas:xtrm, normales:out
#
#---Comentar o descomentar los niveles según se quiera------
levels="1000,975,950,925,900,875,850,700,600,500,400,300,200"
slevels="0.05,0.25,0.7,1.5"
filter="-v ${vars} -l ${levels} -s ${slevels}"
#filter="-v ${vars}"
source ./dirs
export SWPP_TEMPORARY_STORAGE=/localtmp
export SWPP_FULLFILE=${SCRIPTDIR}/wrffull_corwes.nc
export SWPP_GEOFILE=${SCRIPTDIR}/geo_em.d01.nc

export SWPP_WRFNCXNJ_PY=/oceano/gmeteo/WORK/ASNA/WRFtoolbox/wrfncxnj/wrfncxnj.py
export SWPP_WRFNCXNJ_GLOBALATTR=${SCRIPTDIR}/wrfnc_extract_and_join.gattr_CORWES
export SWPP_WRFNCXNJ_TABLE=/oceano/gmeteo/WORK/ASNA/WRFtoolbox/wrfncxnj/wrfncxnj.table

test "${filetype}" == "xtrm" && filter="${filter} -y ${filetype} --dont-check-nofim"

expdir="${BASEDIR}"
# Comentar o descomentar el OUTPUT_PATTERN que corresponda, segun la frecuencia de la variable que vayamos a posprocesar 
export SWPP_OUTPUT_PATTERN=${expdir}/data/post_fullres/'${year}/CWS_CANESM2_3H_${year}${month}_[varcf][level].nc'
#export SWPP_OUTPUT_PATTERN=${expdir}/data/post_fullres/'${year}/CWS_CANESM2_DAM_${year}${month}_[varcf][level].nc'

bash ./swpp_wrfnc2cf.sh ${filter} -i /oceano/gmeteo/WORK/ASNA/projects/corwes/02_cmip5_CanESM2_WRF3.4.1/data/raw/AFRICA_canesm2_WRF3.4.1_nLEAPy/AFRICA_canesm2_WRF3.4.1_nLEAPy/output
