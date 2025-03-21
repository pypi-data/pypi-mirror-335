from .common import *
from kcw import kcw
def cill_start(fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr='kcweb'):
    "脚本入口"
    cmd_par=kcw.get_cmd_par(fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr=fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr)
    if cmd_par and not cmd_par['project']:
        cmd_par['project']='kcweb'
    if cmd_par and cmd_par['install'] and not cmd_par['help']:#插入 应用、模块、插件
        if cmd_par['appname']:
            remppath=os.path.split(os.path.realpath(__file__))[0]
            if not os.path.exists(cmd_par['project']+'/'+cmd_par['appname']) and not os.path.exists(cmd_par['appname']):
                shutil.copytree(remppath+'/tempfile/kcweb',cmd_par['project'])
                print('项目创建成功')
            else:
                return kcw.cill_start(fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr=fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr)
        else:
            return kcw.cill_start(fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr=fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr)
    elif cmd_par:
        return kcw.cill_start(fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr=fdgrsgrsegsrsgrsbsdbftbrsbfdrtrtbdfsrsgr)