
"""小型数据集，通常是模型自带的数据集
规范:
多个数据集,全部以列表形式返回,格式:
[数据,标签],[数据1,标签2,数据2,标签2,],...

load_hotel

X_train, y_train, X_test, y_test = ds.load_iris()
X_train, y_train = ds.load_iris(split=False)

X,y = load_boston(split=False)
X_train, y_train, X_test, y_test = load_boston(split=True,test_size=0.15) 


"""

import os
import numpy as np 
import pandas as pd 
import torch 
import tpf.d1 as d1 
from tpf.box.base import stp
from tpf import pkl_save,pkl_load 
from tpf.params import TestEnvPath as ep
from tpf.params import dataset_path1 as dp
from tpf.params import TPF_DATADIR
from tpf.params import IMG_CIFAR

ds = d1.DataStat()

BASE_DATA_DIR = "/opt/aisty/data/deal"
BASE_DATA_DIR = "/opt/aisty/data/deal"
# mnist_path="/opt/aisty/data/deep/mnist.npz"



from sklearn.model_selection import train_test_split
from sklearn import datasets




def pd_ruxianai(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
    else:

        # 加载乳腺癌数据集
        data = load_breast_cancer()
        X = pd.DataFrame(data.data, columns=data.feature_names)
        y = pd.DataFrame(data.target,columns=['target'])

        columns = X.columns
        df = pd.concat([X,y],axis=1)
        df.to_csv(file_path,index=False)
    return df



def local_cifar10_train():
    """本地cifar10训练数据集dataset
    """
    c10 = os.path.join(IMG_CIFAR,"c10_train.pkl")
    train_dataset = pkl_load(file_path=c10)
    return train_dataset

def local_cifar10_test():
    """本地cifar10测试数据集dataset
    """
    c10_test = os.path.join(IMG_CIFAR,"c10_test.pkl")
    test_dataset = pkl_load(file_path=c10_test)
    return test_dataset


def load_hotel(return_dict=False, return_Xy=True, dataset_path=dp):
    """酒店评论索引数据集
    - return_dict: 返回 words_set,word2idx
    - return_Xy： 返回 X_train,y_train,X_test,y_test, np.ndarray类型
    """
    BASE_DIR = os.path.join(dataset_path,"hotel_reader")
    dict_file = os.path.join(BASE_DIR,"data_pkl/wordict.pkl")
    file_train = os.path.join(BASE_DIR,"data_pkl/train.pkl")
    file_test = os.path.join(BASE_DIR, "data_pkl/test.pkl")
    if return_dict:
        words_set,word2idx = pkl_load(file_path=dict_file)   # 字典
        return words_set,word2idx 
    if return_Xy:
        X_train,y_train = pkl_load(file_path=file_train)     # 训练集
        X_test,y_test = pkl_load(file_path=file_test)        # 测试集
        X_train = np.array(X_train)
        y_train = np.array(y_train)
        X_test = np.array(X_test)
        y_test = np.array(y_test)
        print("X_train:",X_train.shape)  # X_train: (4800, 85)
        print("y_train:",y_train.shape)  # y_train: (4800,)
        print("X_test:",X_test.shape)    # X_test: (1200, 85)
        print("y_test:",y_test.shape)    # y_test: (1200,)
        return X_train,y_train,X_test,y_test


def load_iris(split=True):
    """
    split:True,拆分数据集为训练集与测试集,False为不拆分
    data_list = ds.load_iris()

    或

    X_train, y_train, X_test, y_test = ds.load_iris()

    或

    X_train, y_train = ds.load_iris(split=False)
    """
    data = datasets.load_iris()
    if split:
        x_train, x_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.20, random_state=73)
        return x_train, y_train, x_test, y_test
    else:
        return data.data, data.target


def load_iris_onehot(split=True):
    """
    返回已经对标签独热编码过的数据集

    split:True,拆分数据集为训练集与测试集,False为不拆分,

    data_list = ds.load_iris_onehot()

    或

    [x_train, y_train, x_test, y_test] = ds.load_iris_onehot()

    或

    [X_train, y_train] = ds.load_iris_onehot(split=False)
    """
    data = datasets.load_iris()
    if split:
        x_train, x_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.33, random_state=42)
        
        y_train  = ds.onehot_pd(y_train)
        y_test  = ds.onehot_pd(y_test)
        return [x_train, y_train, x_test, y_test]
    else:
        lable  = ds.onehot_pd(data.target)
        return [data.data, lable]



def load_boston(split=True, test_size=0.15, reload=False):
    """房价（回归问题）,后续默认加载首次生成的文件 
    X,y = load_boston(split=False)
    X_train, y_train, X_test, y_test = load_boston(split=True,test_size=0.15) 

    print(type(X))   # <class 'numpy.ndarray'>
    print(X.shape)   # (506, 13)
    print(y.shape)   # (506,)
    """
    if not os.path.exists(TPF_DATADIR):
        os.makedirs(TPF_DATADIR, exist_ok=True)
    if split and (not reload):
        tmp_path = os.path.join(TPF_DATADIR,"fangjia_boston_split.pkl")
    else:
        tmp_path = os.path.join(TPF_DATADIR,"fangjia_boston.pkl")
    
    if os.path.exists(tmp_path):
        return pkl_load(tmp_path)

    data_url = "http://lib.stat.cmu.edu/datasets/boston"
    raw_df = pd.read_csv(data_url, sep=r'\s+', skiprows=22, header=None)
    # print(raw_df.info())
    """
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1012 entries, 0 to 1011
Data columns (total 11 columns):
 #   Column  Non-Null Count  Dtype
---  ------  --------------  -----
 0   0       1012 non-null   float64
 1   1       1012 non-null   float64
 2   2       1012 non-null   float64
 3   3       506 non-null    float64
 4   4       506 non-null    float64
 5   5       506 non-null    float64
 6   6       506 non-null    float64
 7   7       506 non-null    float64
 8   8       506 non-null    float64
 9   9       506 non-null    float64
 10  10      506 non-null    float64
dtypes: float64(11)
memory usage: 87.1 KB
    """
    # print(raw_df.describe())
    """
                0            1            2           3           4   ...          6           7           8           9           10
count  1012.000000  1012.000000  1012.000000  506.000000  506.000000  ...  506.000000  506.000000  506.000000  506.000000  506.000000
mean    180.143778    12.008350    16.834792    0.069170    0.554695  ...   68.574901    3.795043    9.549407  408.237154   18.455534
std     188.132839    17.250728     9.912616    0.253994    0.115878  ...   28.148861    2.105710    8.707259  168.537116    2.164946
min       0.006320     0.000000     0.460000    0.000000    0.385000  ...    2.900000    1.129600    1.000000  187.000000   12.600000   
25%       0.257830     0.000000     8.375000    0.000000    0.449000  ...   45.025000    2.100175    4.000000  279.000000   17.400000   
50%      24.021000     7.240000    18.100000    0.000000    0.538000  ...   77.500000    3.207450    5.000000  330.000000   19.050000   
75%     391.435000    16.780000    21.890000    0.000000    0.624000  ...   94.075000    5.188425   24.000000  666.000000   20.200000   
max     396.900000   100.000000    50.000000    1.000000    0.871000  ...  100.000000   12.126500   24.000000  711.000000   22.000000   

[8 rows x 11 columns]
    """

    data = np.hstack([raw_df.values[::2, :], raw_df.values[1::2, :2]])
    target = raw_df.values[1::2, 2]
    if split:
        X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=test_size, random_state=73)
        stp(X_train,"X_train")
        stp(y_train,"y_train")
        pkl_save((X_train,y_train, X_test, y_test),file_path=tmp_path)
        return X_train,y_train, X_test, y_test
    else:
        stp(data, "X")
        stp(target,"y")
        pkl_save((data,target),file_path=tmp_path)
        return data,target


from pprint import pprint as pp

def load_ruxianai(split=True, test_size=0.15, lable2vec=False, random_state=73, file_dir=None):
    """疾病分类(二分类问题)

    params
    ----------------------------------------
    - split:是否拆分为训练集，测试集
    - test_size:测试集占比
    - lable2vec:为True将标签转为列向量，y_train.reshape((-1,1)),标签成为2维数据


    示例
    ------------------------------------------------
    X_train, y_train, X_test, y_test = load_ruxianai()

    或

    X_train, y_train = ruxianai(split=False)


        mean radius  mean texture  mean perimeter  ...  worst concave points  worst symmetry  worst fractal dimension
    count   569.000000    569.000000      569.000000  ...            569.000000      569.000000               569.000000
    mean     14.127292     19.289649       91.969033  ...              0.114606        0.290076                 0.083946
    std       3.524049      4.301036       24.298981  ...              0.065732        0.061867                 0.018061
    min       6.981000      9.710000       43.790000  ...              0.000000        0.156500                 0.055040
    25%      11.700000     16.170000       75.170000  ...              0.064930        0.250400                 0.071460
    50%      13.370000     18.840000       86.240000  ...              0.099930        0.282200                 0.080040
    75%      15.780000     21.800000      104.100000  ...              0.161400        0.317900                 0.092080
    max      28.110000     39.280000      188.500000  ...              0.291000        0.663800                 0.207500

    [8 rows x 30 columns]
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 569 entries, 0 to 568

    Data columns (total 30 columns):
    #   Column                   Non-Null Count  Dtype
    ---  ------                   --------------  -----
    0   mean radius              569 non-null    float64
    1   mean texture             569 non-null    float64
    2   mean perimeter           569 non-null    float64
    3   mean area                569 non-null    float64
    4   mean smoothness          569 non-null    float64
    5   mean compactness         569 non-null    float64
    6   mean concavity           569 non-null    float64
    7   mean concave points      569 non-null    float64
    8   mean symmetry            569 non-null    float64
    9   mean fractal dimension   569 non-null    float64
    10  radius error             569 non-null    float64
    11  texture error            569 non-null    float64
    12  perimeter error          569 non-null    float64
    13  area error               569 non-null    float64
    14  smoothness error         569 non-null    float64
    24  worst smoothness         569 non-null    float64
    25  worst compactness        569 non-null    float64
    26  worst concavity          569 non-null    float64
    27  worst concave points     569 non-null    float64
    28  worst symmetry           569 non-null    float64
    29  worst fractal dimension  569 non-null    float64
    dtypes: float64(30)
    memory usage: 133.5 KB
    """

    if split:
        if file_dir is not None:
            ep.DATA_BREAST_CANCER_PATH = file_dir
        save_path = os.path.join(ep.DATA_BREAST_CANCER_PATH,"train_test.pkl")

        if os.path.exists(save_path):
            X_train, y_train, X_test, y_test = pkl_load(file_path=save_path)
            return X_train, y_train, X_test, y_test 
        data = datasets.load_breast_cancer()
        X = data.data  # numpy 
        y = data.target
        X_train, X_test, y_train,  y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        pkl_save(data=(X_train, y_train, X_test, y_test),file_path=save_path)
        
        if lable2vec:
            # 原始数据的标签，是1维数据，每个样本向量对应一个标量
            # 将标签变成列向量
            y_train = y_train.reshape((-1,1))
            y_test = y_test.reshape((-1,1))
        
        print(f"X_train.shape={X_train.shape}, y_train.shape={y_train.shape}")
        print(f"X_test.shape={X_test.shape}, y_test.shape={y_test.shape}")
        
        return X_train, y_train, X_test, y_test
    else:
        if file_dir is not None:
            ep.DATA_BREAST_CANCER_PATH = file_dir
            
        save_path = os.path.join(ep.DATA_BREAST_CANCER_PATH,"train.pkl")
        
        if os.path.exists(save_path):
            X,y = pkl_load(file_path=save_path)
            if lable2vec:
                y = y.reshape((-1,1))
            return X,y
        data = datasets.load_breast_cancer()
        X = data.data  # numpy 
        y = data.target
        X_train, X_test, y_train,  y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        
        pkl_save(data=(X,y),file_path=save_path)
        if lable2vec:
            y = y.reshape((-1,1))
        return X,y

def load_taitan():
    """
    泰坦尼克求生数据
    """
    data_path = os.path.join(BASE_DATA_DIR,"taitan/train.pkl")
    x,y = d1.pkl_xy_load(data_path)

    # 经处理的测试数据
    data_path = os.path.join(BASE_DATA_DIR,"taitan/test.pkl")
    x2,y2 = d1.pkl_xy_load(data_path) 
    return [x,y,x2,y2]


# def load_breast_cancer(return_X_y=False, test_size=0.2, random_state=1):
#     """
#     示例
#     -------------------
#     X_train, y_train, X_test, y_test = load_breast_cancer()
    
#     """
#     X,y = datasets.load_breast_cancer(return_X_y=True)
#     if return_X_y:
#         print(f"X.shape={X.shape}, y.shape={y.shape}")
#         return X,y 
    
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

#     # 原始数据的标签，是1维数据，每个样本向量对应一个标量
#     # 将标签变成列向量
#     y_train = y_train.reshape((-1,1))
#     y_test = y_test.reshape((-1,1))

#     print(f"X_train.shape={X_train.shape}, y_train.shape={y_train.shape}")
#     print(f"X_test.shape={X_test.shape}, y_test.shape={y_test.shape}")
#     return (X_train, y_train, X_test, y_test)


def batch_loader(file_dir=None, presfx="batch_", return_torch = False):
    """
    所有数据全部以numpy格式存储;
    不管原来数据什么格式，统统以列表存放；
    读取文件时，再做数据类型转换；
    或者自行修改本方法，以适应特别数据结构与类型
    """
    if not os.listdir(file_dir):
        print(file_dir,'目录为空！')
    else:
        for i in os.listdir(file_dir):
            path_file = os.path.join(file_dir,i)  #取文件绝对路径
            data = d1.pkl_load(file_path=path_file)

            yield data 




def batch_save_set(datasets, batch_size=32, file_dir=None, presfx="batch_"):
    """
    将datasets按批次存储；
    所有数据全部以numpy格式存储;
    """
    data = []
    count = 0
    for v in datasets:
        count += 1
        data.append(v)

        if count % batch_size == 0:
            save_path = os.path.join(file_dir,"{}{}.pkl".format(presfx,count)) 
            pkl_save(data=data,file_path=save_path)
            data = []

def batch_save_Xy(X, y, batch_size=32, file_dir=None, presfx="batch_"):
    """
    每batch_size条(X,y)存储为一个文件；
    numpy格式存储;
    """
    data_X = []
    data_y = []
    max_len = len(y)
    count = 0
    for label in y:
        count += 1
        x = X[count-1]

        if isinstance(x,torch.Tensor):
            x = x.numpy().tolist()
            label = label.numpy().tolist()
        else: # 反之按numpy类型处理
            x = x.tolist()
            label = label.tolist()
        data_X.append(x)
        data_y.append(label)

        if count % batch_size == 0 or count == max_len:
            save_path = os.path.join(file_dir,"{}{}.pkl".format(presfx,count)) 
            data_X = np.array(data_X)
            data_y = np.array(data_y)
            pkl_save(data=(data_X,data_y),file_path=save_path)
            data_X = []
            data_y = []

def batch_loader_Xy(file_dir=None, presfx="batch_", return_torch = False, show_file=False,gray=False):
    """
    批次加载数据，默认一个文件记录一个批次的(X,y)数据

    return_torch：
    为True返回torch.Tensor格式数据，反之返回numpy.ndarray；

    """
    if not os.path.exists(file_dir):
        return 
    if not os.listdir(file_dir):
        print(file_dir,'目录为空！')
    else:
        for i in os.listdir(file_dir):
            path_file = os.path.join(file_dir,i)  #取文件绝对路径
            if show_file:
                print(path_file)
                
            data = d1.pkl_load(file_path=path_file)

            x = data[0]
            label = data[1]
            if gray:  # 模拟图像灰度处理
                x = np.mean(x,axis=1,keepdims=True)
            if return_torch:
                data = (torch.Tensor(x),torch.Tensor(label).long())
            else:
                data = (x,label)
            yield data

def sample_from_dataset(datasets, label_list_key, max_count_one_label = 300):
    """
    按指定的label_list_key从datasets中提取数据，每个label最多提取max_count_one_label条数据；
    原数据集中每个元素为一个(x,y)，现将之拆解为x,y两个列表，然后返回；
    """
    key_count = len(label_list_key)
    label_list_count = [0 for i in range(key_count)]
    sample_dict = dict(zip(label_list_key,label_list_count))  # {0: 300, 1: 300, 2: 300, 3: 300, 4: 300, 5: 300, 6: 300, 7: 300, 8: 300, 9: 300}

    label_key_full = 0
    img_list = []
    train_len = len(datasets)
    label_add = [key for key in sample_dict.keys()]
    labels = []

    for i in range(train_len):
        x,label = datasets[i]
        if label in label_add:
            if sample_dict[label] < max_count_one_label:
                img_list.append(x.numpy().tolist())
                labels.append(label)
                sample_dict[label] += 1

            else:
                label_add.remove(label)
                label_key_full += 1

        if label_key_full == key_count:
            break

        
    img_list = torch.Tensor(img_list)
    labels = torch.Tensor(labels)
    return img_list,labels



def test_batch_save_Xy():
    
    from torchvision import datasets
    from torchvision.transforms import Compose
    from torchvision.transforms import Resize
    from torchvision.transforms import ToTensor
    from torchvision.transforms import Normalize

    """
        打包数据
    """

    # 定义数据预处理
    transforms = Compose(transforms=[Resize(size=(224, 224)), 
                                        ToTensor(),
                                        Normalize(mean=[0.5, 0.5, 0.5], 
                                                    std=[0.5, 0.5, 0.5])])

    data_name = "cifar100"
    train_dataset = datasets.CIFAR100(root=data_name, train=True, transform=transforms, download=True)
    test_dataset = datasets.CIFAR100(root=data_name, train=False, transform=transforms, download=True)


    label_list_key   = [i for i in range(10)] # label列表
    max_count_one_label = 500  # 每个类别取多少条数据


    # imgs,labels = sample_from_dataset(datasets=train_dataset, label_list_key=label_list_key,max_count_one_label=max_count_one_label)
    # print("begin batch save-------")

    # # 这里更好的应该在加载的时候，加载完一批就存一批，而不加载完所有的，再批次保存
    # batch_save_Xy(X=imgs, y=labels, batch_size=32, file_dir="/source/data/tmp/ci100", presfx="batch_")


    imgs,labels = sample_from_dataset(datasets=test_dataset, label_list_key=label_list_key,max_count_one_label=100)
    print("begin batch save test-------")
    batch_save_Xy(X=imgs, y=labels, batch_size=32, file_dir="/source/data/tmp/ci100_test", presfx="batch_")


def test_batch_loader_Xy():

    file_dir="/source/data/tmp/ci100"
    data_loader = batch_loader_Xy(file_dir=file_dir, return_torch=True)

    count = 0
    for X,y in data_loader:
        count += 1
        print(f"count={count}, X.shape={X.shape}, y.shape={y.shape},y.dtype={type(y)}")

if __name__=="__main__":
    # test_batch_loader_Xy()
    # load_breast_cancer()
    # X_train, y_train, X_test, y_test = ruxianai()
    # print(X_train.shape,X_test.shape)

    X_train, y_train, X_test, y_test = load_iris()
    print(X_train.shape,X_test.shape)
