# An Extension Package on Mermaid
The purpose of this package is to provide an easy interface for Mermaid and other popluar registration
package.\
The current support methods include Mermaid-optimization and Mermaid-network. 
We add supports on [AntsPy](https://github.com/ANTsX/ANTsPy), [NiftyReg](http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg) and Demons(embedded in [SimpleITK](http://www.simpleitk.org/SimpleITK/resources/software.html)), though we recommend the usage of official source.


# Installation
```
conda create -n easyreg python=3.6
source activate easyreg
git clone https://github.com/uncbiag/easyreg.git
cd easyreg
gdown https://drive.google.com/open?id=1RjFV0lht4uQFc2jYmBYxmXtRrdYAzk8S
unzip demo_saved_models.zip -d .
git clone https://github.com/uncbiag/mermaid.git
pip install -r requirements.txt
cd mermaid
python setup.py
```

# Paper related
Networks for Joint Affine and Non-parametric Image Registration [[link]](https://arxiv.org/pdf/1903.08811.pdf)\
Region-specific Diffeomorphic Metric Mapping [[link]](https://arxiv.org/pdf/1906.00139.pdf)


# Guide
1 . prepare the data
Though dataset processing examples are provided, we recommend to write your own
code for specific dataset.
And take the following format

* image itself should be normalized into 0-1 and saved as nii.gz
* **train**, **val**,  **test**, **debug** (subset of train data, to check overfit)  folder should be put under **data_folder/data_task_folder**, each of the folder should
   include **'pair_path_list.txt'** and **'pair_name_list.txt'**\
   **'pair_path_list.txt'**: each line of the txt include 4 terms: s_pth t_pth ls_path\
    _s refers to source, t refers to target, ls refers to label of source (string 'None' if not exist)_ \
    **'pair_name_list.txt'**: each line of the txt include 1 term: the pair name
    the file is line to line corresponded with 'pair_path_list.txt'


2 . Training Setting
* general settings for paths\
we assume there is three level folder, data_folder/ data_task_folder/ task_folder 
In data folder, each folder works on different data, i.e. lung, brain, (just for organization, data can be put in other location)
In data_task_folder, each folder refer to different preprocessing strategy, i.e. resampling into different size,\
In task_folder, each folder refer to a specific setting

so the task folder would be created as data_folder/data_task_folder/your_current_task_name\


In the 'your_current_task_name' folder, three folder will be auto created, **log** for tensorboard, **checkpoints** for saving models,
**records** for saving running time results. Besides, two files will also be created. **task_settings.json** for recording settings of current tasks.
**logfile.log** for terminal output ( only flushed when task finished)


* general settings for tasks\
models support list: 'reg_net'  'mermaid_iter'  'ants'  'nifty_reg' 'demons'\
each model supports several methods
methods support by reg_net: 'affine_sym', 'mermaid'\
methods support by mermaid_iter: 'affine','nonp' ( including affine registration first)\
methods support by ants: 'affine','syn' ( including affine registration first)\
methods support by nifty_reg: 'affine','bspline' ( including affine registration first)\
methods support by demons: 'demons' ( including niftyreg affine registration first)\

**reg_net** refers to registration network build on memraid library. 'affine_sym' refers to multi-step affine symmetric network (s-t, t-s),\
**mermaid_iter** refers to optimization methods built on mermaid library, 'nonp' refers to non-parametric method\
**ant** refers to AntsPy, 'syn' refers to 'SyNCC' in AntsPy\
** nifty_reg ** refers NifyReg\
**demons** refers to deformably register two images using a symmetric forces demons  algorithm, which is provided by simple itk

\* Mermaid library ( including various fluid based registration methods, specific method can be set in mermaid setting files)\
The current version only support map-based mermaid methods.


 





    
