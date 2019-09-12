import matplotlib as matplt
matplt.use('Agg')

import sys,os
sys.path.insert(0,os.path.abspath('.'))
sys.path.insert(0,os.path.abspath('..'))
sys.path.insert(0,os.path.abspath('../model_pool'))
sys.path.insert(0,os.path.abspath('../mermaid'))
import data_pre.module_parameters as pars
from abc import ABCMeta, abstractmethod
from model_pool.piplines import run_one_task
from data_pre.reg_data_utils import write_list_into_txt, get_file_name, loading_img_list_from_files
import numpy as np

class BaseTask():
    __metaclass__ = ABCMeta
    def __init__(self,name):
        self.name = name

    @abstractmethod
    def save(self):
        pass
 
class DataTask(BaseTask):
    """
    load the data settings from json
    """
    def __init__(self,name,path='../settings/base_data_settings.json'):
        super(DataTask,self).__init__(name)
        self.data_par = pars.ParameterDict()
        self.data_par.load_JSON(path)


    def save(self, path='../settings/data_settings.json'):
        self.data_par.write_ext_JSON(path)

class ModelTask(BaseTask):
    """
    load the task settings from json
    """
    def __init__(self,name,path='../settings/base_task_settings.json'):
        super(ModelTask,self).__init__(name)
        self.task_par = pars.ParameterDict()
        self.task_par.load_JSON(path)

    def save(self,path= '../settings/task_settings.json'):
        self.task_par.write_ext_JSON(path)



def force_setting(dm, tsm,output_path):
    task_full_path = os.path.join(os.path.join(output_path,'reg'),'res')
    dm.data_par['datapro']['dataset']['prepare_data'] = False
    dm.data_par['datapro']['reg']['max_pair_for_loading'] = [1, 1, -1, 1]
    tsm.task_par['tsk_set']['train'] = False
    tsm.task_par['tsk_set']['save_by_standard_label'] = True
    tsm.task_par['tsk_set']['continue_train'] = False
    tsm.task_par['tsk_set']['reg']['mermaid_net']['using_sym'] = False
    data_json_path = os.path.join(task_full_path, 'cur_data_setting.json')
    tsk_json_path = os.path.join(task_full_path, 'cur_task_setting.json')
    tsm.save(tsk_json_path)
    dm.save(data_json_path)



def init_env(task_full_path,output_path, source_path_list, target_path_list, l_source_path_list=None, l_target_path_list=None):
    """
    :param task_full_path:  the path of a completed task
    :param source_path: path of the source image
    :param target_path: path of the target image
    :param l_source: path of the label of the source image
    :param l_target: path of the label of the target image
    :return: None
    """
    dm_json_path = os.path.join(task_full_path, 'cur_data_setting.json')
    tsm_json_path = os.path.join(task_full_path, 'cur_task_setting.json')
    dm = DataTask('task_reg',dm_json_path)
    tsm = ModelTask('task_reg',tsm_json_path)
    file_num = len(source_path_list)
    assert len(source_path_list) == len(target_path_list)
    if l_source_path_list is not None and l_target_path_list is not None:
        assert len(source_path_list) == len(l_source_path_list)
        file_list = [[source_path_list[i], target_path_list[i],l_source_path_list[i],l_target_path_list[i]] for i in range(file_num)]
    else:
        file_list = [[source_path_list[i], target_path_list[i]] for i in range(file_num)]
    os.makedirs(os.path.join(output_path,'reg/test'),exist_ok=True)
    os.makedirs(os.path.join(output_path,'reg/res'),exist_ok=True)
    pair_txt_path =  os.path.join(output_path,'reg/test/pair_path_list.txt')
    fn_txt_path =   os.path.join(output_path,'reg/test/pair_name_list.txt')
    fname_list = [get_file_name(file_list[i][0])+'_'+get_file_name(file_list[i][1]) for i in range(file_num)]
    write_list_into_txt(pair_txt_path,file_list)
    write_list_into_txt(fn_txt_path,fname_list)
    root_path = output_path
    data_task_name = 'reg'
    cur_task_name = 'res'
    dm.data_par['datapro']['dataset']['output_path'] = root_path
    dm.data_par['datapro']['dataset']['task_name'] = data_task_name
    tsm.task_par['tsk_set']['task_name'] = cur_task_name
    return dm, tsm









def do_registration(refering_task_path=None,pair_txt_path=None,registration_pair_list=None,mermaid_setting_file=None,output_path=None,gpu_id=0):
    read_img_list_from_txt= pair_txt_path is not None
    img_list_txt_path = pair_txt_path
    if not read_img_list_from_txt:
        source_path_list,target_path_list,l_source_path_list,l_target_path_list = registration_pair_list
    else:
        source_path_list, target_path_list,l_source_path_list,l_target_path_list = loading_img_list_from_files(img_list_txt_path)

    task_full_path = refering_task_path
    """ the path of the setting from a completed task"""
    dm, tsm = init_env(task_full_path,output_path,source_path_list,target_path_list,l_source_path_list,l_target_path_list)
    optional_setting_on = False
    tsm.task_par['tsk_set']['gpu_ids'] = gpu_id
    tsm.task_par['tsk_set']['reg']['mermaid_net'][
        'mermaid_net_json_pth'] = mermaid_setting_file
    tsm.task_par['tsk_set']['batch_sz'] = 2
    tsm.task_par['tsk_set']['save_3d_img_on'] = False
    tsm.task_par['tsk_set']['save_fig_on'] = False
    if optional_setting_on:
        """ the following settings are optional, if you want do something different than the loaded setting"""
        ############################### general settings ##########################

        tsm.task_par['tsk_set']['network_name'] ='mermaid'
        tsm.task_par['tsk_set']['model'] = 'reg_net'
        tsm.task_par['tsk_set']['batch_sz'] = 2  # multi sample registration is only for mermaid based methods, for other methods should always be 1
        #tsm.task_par['tsk_set']['model_path'] = '/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_intra/train_affine_net_sym_lncc/checkpoints/    epoch_1070_'
            #'/playpen/zyshen/data/croped_for_reg_debug_3000_pair_oai_reg_inter/reg_svf_reg10_old_2step/checkpoints/epoch_130_'
            #'/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_inter/train_intra_mermaid_net_500thisinst_10reg_double_loss_jacobi/checkpoints/epoch_110_'
            #'/playpen/zyshen/data/croped_for_reg_debug_3000_pair_oai_reg_inter/reg_svf_baseline_continue_rk4_old/checkpoints/epoch_100_'
            #'/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_inter/debug_oneadpt_lddmm/checkpoints/epoch_120_'
        #"/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_inter/train_intra_mermaid_net_500thisinst_10reg_double_loss_jacobi/checkpoints/epoch_170_"
            #'/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_intra/vm_miccal_setting_zeroboundary_withbothlambda100sigma002withenlargedflowreg/checkpoints/epoch_270_'
        #'/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_intra/train_intra_mermaid_net_500inst_10reg_double_loss_jacobi/checkpoints/epoch_110_'
            #'/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_inter/vm_cvprwithregfixnccandtraindata_fixedregfixedncc_reg2/checkpoints/epoch_200_'
            #'/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_intra/train_affine_net_sym_lncc/checkpoints/epoch_1070_'

        ###############################  for mermaid network registration ##########################
        tsm.task_par['tsk_set']['reg']['mermaid_net']['optimize_momentum_network']=False
        tsm.task_par['tsk_set']['reg']['mermaid_net']['using_multi_step']=True
        tsm.task_par['tsk_set']['reg']['mermaid_net']['num_step']=3
        tsm.task_par['tsk_set']['reg']['mermaid_net']['using_affine_init']=True

        affine_path = '/playpen/zyshen/data/reg_debug_3000_pair_oai_reg_intra/train_affine_net_sym_lncc/checkpoints/epoch_1070_'
        tsm.task_par['tsk_set']['reg']['mermaid_net']['affine_init_path']=affine_path
        tsm.task_par['tsk_set']['reg']['affine_net']['affine_net_iter']=7


        ################################  for mermaid optimization registration ######################################3
        tsm.task_par['tsk_set']['reg']['mermaid_iter']={}
        """ settings for the mermaid optimization version, we only provide parameter that may different in longitudinal and cross subject task"""
        tsm.task_par['tsk_set']['reg']['mermaid_iter']['affine']={}
        """ settings for the mermaid-affine optimization version"""
        tsm.task_par['tsk_set']['reg']['mermaid_iter']['affine']['sigma'] =np.sqrt(0.5)
        """ for optimization-based mermaid recommand np.sqrt(1./batch_sz) for longitudinal, recommand np.sqrt(0.5/batch_sz) for cross-subject """
        """ for optimization-based mermaid recommand np.sqrt(1.) for longitudinal, recommand np.sqrt(0.5) for cross-subject """
        tsm.task_par['tsk_set']['reg']['mermaid_iter']['mermaid_affine_json'] = '../model_pool/cur_settings_affine_tmp.json'
        tsm.task_par['tsk_set']['reg']['mermaid_iter']['mermaid_nonp_json'] = '../model_pool/cur_settings_svf_dipr.json'


    force_setting(dm, tsm, output_path)
    task_full_path = os.path.join(os.path.join(output_path, 'reg'), 'res')
    dm_json_path = os.path.join(task_full_path, 'cur_data_setting.json')
    tsm_json_path = os.path.join(task_full_path, 'cur_task_setting.json')
    run_one_task(tsm_json_path, dm_json_path)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='implementation of Adaptive vector-momentum-based Stationary Velocity Field Mappinp (AVSM)')

    parser.add_argument('-rt','--refering_task_path', required=False,
                        default='./dl/pretrained/avsm_3step',
                        help='a pretrain task folder including necessary settings')

    parser.add_argument('-txt','--pair_txt_path', required=False, default=None, type=str,
                        help='the txt file recording the pairs to registration')  # 2
    parser.add_argument('-s','--source_list',nargs='+', required=False, default=None,
                        help='the source list,  s1 s2 s3..sn')
    parser.add_argument('-t','--target_list',nargs='+', required=False, default=None,
                        help='the target list,  t1 t2 t3..tn')
    parser.add_argument('-ls','--lsource_list',nargs='+', required=False, default=None,
                        help='the source label list,  ls1,ls2,ls3..lsn')
    parser.add_argument('-lt','--ltarget_list',nargs='+', required=False, default=None,
                        help='the target label list,  lt1,lt2,lt3..ltn')

    parser.add_argument('-ms',"--mermaid_setting_file",required=False,default='./d1/settings/vsvf.json',help='the json file for vsvf settings')
    parser.add_argument('-o',"--output_path",required=False,default='./dl/output', help='the output path')
    parser.add_argument('-g',"--gpu_id",required=False,type=int,default=0,help='gpu_id to use')

    args = parser.parse_args()
    print(args)
    registration_pair_list= [args.source_list, args.target_list, args.lsource_list, args.ltarget_list]
    print(registration_pair_list)

    do_registration(refering_task_path=args.refering_task_path,pair_txt_path=args.pair_txt_path,registration_pair_list=registration_pair_list,
                    mermaid_setting_file=args.mermaid_setting_file,output_path = args.output_path, gpu_id=args.gpu_id)



    """
    python single_pair_atlas_registration.py -rt '/playpen/zyshen/data/reg_debug_labeled_oai_reg_inter/test_intra_mermaid_net_500thisinst_10reg_double_loss_step3_jacobi'\
    -txt  '/playpen/zyshen/data/reg_test_for_atlas/test/pair_path_list.txt' -ms '/playpen/zyshen/reg_clean/mermaid_settings/cur_settings_svf.json'\
    -o '/playpen/zyshen/data/reg_test_for_atlas/debug' -g 2
    
    python single_pair_atlas_registration.py -rt '/playpen/zyshen/data/reg_debug_labeled_oai_reg_inter/test_intra_mermaid_net_500thisinst_10reg_double_loss_step3_jacobi'\
    -s  /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_image.nii.gz  -t /playpen/zyshen/debugs/atlas.nii.gz  -ls /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_prediction_step1_batch6_16_reflect.nii.gz  -lt /playpen/zhenlinx/Code/OAI_analysis/atlas/atlas_60_LEFT_baseline_NMI/atlas_mask_step_10.nii.gz\
    -ms '/playpen/zyshen/reg_clean/mermaid_settings/cur_settings_svf.json'\
    -o '/playpen/zyshen/data/reg_test_for_atlas/debug' -g 2
    
    
    python single_pair_atlas_registration.py -rt '/playpen/zyshen/data/reg_debug_labeled_oai_reg_inter/test_intra_mermaid_net_500thisinst_10reg_double_loss_step3_jacobi'\
    -s  /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_image.nii.gz  -t /playpen/zyshen/debugs/atlas.nii.gz \
    -ms '/playpen/zyshen/reg_clean/mermaid_settings/cur_settings_svf.json'\
    -o '/playpen/zyshen/data/reg_test_for_atlas/debug' -g 2
    
    -rt '/playpen/zyshen/data/reg_debug_labeled_oai_reg_inter/test_intra_mermaid_net_500thisinst_10reg_double_loss_step3_jacobi'     -s  /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_image.nii.gz  -t /playpen/zyshen/debugs/atlas.nii.gz  -ls /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_prediction_step1_batch6_16_reflect.nii.gz  -lt /playpen/zhenlinx/Code/OAI_analysis/atlas/atlas_60_LEFT_baseline_NMI/atlas_mask_step_10.nii.gz     -ms '/playpen/zyshen/reg_clean/mermaid_settings/cur_settings_svf.json'     -o '/playpen/zyshen/data/reg_test_for_atlas/debug' -g 2
    -rt '/playpen/zyshen/OAI_analysis/settings/avsm'     -s  /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_image.nii.gz  -t /playpen/zyshen/debugs/atlas.nii.gz  -ls /playpen/zyshen/debugs/9002116_20060804_SAG_3D_DESS_RIGHT_11269909_prediction_step1_batch6_16_reflect.nii.gz  -lt /playpen/zhenlinx/Code/OAI_analysis/atlas/atlas_60_LEFT_baseline_NMI/atlas_mask_step_10.nii.gz     -ms '/playpen/zyshen/reg_clean/mermaid_settings/cur_settings_svf.json'     -o '/playpen/zyshen/data/reg_test_for_atlas/debug' -g 2

    """
