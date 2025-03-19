import numpy as np 
import pandas as pd 
import joblib 
import pickle as pkl 
import os
import random 
import lightgbm as lgb
from sklearn.metrics import accuracy_score,roc_auc_score, confusion_matrix, classification_report, roc_curve, auc,f1_score

from sklearn import preprocessing
from sklearn.model_selection import train_test_split

from tpf import DataDeal as dt
from tpf.d1 import is_single_label



def pkl_save(data, file_path, use_joblib=False, compress=0):
    """
    data:保存一个列表时直接写列表,多个列表为tuple形式
    """
    if use_joblib:
        joblib.dump(data, filename=file_path, compress=compress)
    else:
        data_dict = {}
        if type(data).__name__ == 'tuple':
            index = 0
            for v in data:
                index = index+1
                key = "k"+str(index)
                data_dict[key]= v 
        else:
            data_dict["k1"] = data 

        # 在新文件完成写入之前，不要损坏旧文件
        tmp_path = file_path+".tmp"
        bak_path = file_path+".bak"

        with open(tmp_path, 'wb') as f:
            # 如果这一步失败，原文件还没有被修改，重新写入即可
            pkl.dump(data_dict, f)

            # 如果这一步失败，.tmp文件已经被成功写入，直接将.tmp去掉就是最新写入的文件
            # 这里并没有测试rename是否被修改文件的内容，从命名上看，rename是不会的，
            if os.path.exists(file_path):
                os.rename(src=file_path,dst=bak_path)
        if os.path.exists(tmp_path):
            # 如果是下面这一步被强制中止，直接将.tmp去掉就是最新写入的文件
            # 也可以通过.bak文件恢复到修改之前的文件
            # 重命后，不会删除备份文件，最坏的结果是丢失当前的写入，但也会保留一份之前的备份
            os.rename(src=tmp_path,dst=file_path)
        

def pkl_load(file_path, use_joblib=False):
    """ 
    与pkl_load配对使用
    """
    if use_joblib:
        data = joblib.load(file_path)
        return data

    try:
        with open(file_path, 'rb') as f:
            data_dict = pkl.load(f)
        data = tuple(list(data_dict.values()))
        if len(data) == 1:
            return data[0]
        return data 
    except Exception as e:
    #     print(repr(e))
        model = joblib.load(file_path)
        return model 


def str_pd(data,cname_date_type):
    """pandas数表列转字符类型"""
    data[cname_date_type] = data[cname_date_type].astype(str)
    data[cname_date_type] = data[cname_date_type].astype("string")
    return data


def null_deal_pandas(data,cname_num_type=[], cname_str_type=[], num_padding=0, str_padding = '<PAD>'):
    """
    params
    ----------------------------------
    - data:pandas数表
    - cname_num_type：数字类型列表
    - cname_str_type：字符类型列表
    - num_padding:数字类型空值填充
    - str_padding:字符类型空值填充
    
    example
    -----------------------------------
    #空值处理
    data = null_deal_pandas(data,cname_num_type=num_type,cname_str_type=str_classification,num_padding=0,str_padding = '<PAD>')

    """
    if len(cname_num_type)>0:
        # 数字置为0
        for col in cname_num_type:
            data.loc[data[col].isna(),col]=num_padding
    
    if len(cname_str_type)>0:
        #object转str，仅处理分类特征，身份认证类特征不参与训练
        data[cname_str_type] = data[cname_str_type].astype(str)
        data[cname_str_type] = data[cname_str_type].astype("string")
        
        for col in cname_str_type:
            data.loc[data[col].isna(),col]=str_padding

        # nan被转为了字符串，但在pandas中仍然是个特殊存在，转为特定字符串，以防Pandas自动处理
        # 创建一个替换映射字典  
        type_mapping = {  
            'nan': str_padding,   
            '': str_padding
        }  
            
        # 使用.replace()方法替换'列的类型'列中的值  
        data[cname_str_type] = data[cname_str_type].replace(type_mapping)  
            
        nu = data[cname_str_type].isnull().sum()
        for col_name,v in nu.items():
            if v > 0 :
                print("存在空值的列:\n")
                print(col_name,v)
        return data

def min_max_scaler(df):  
    return (df - df.min()) / (df.max() - df.min())  

def std7(df, cname_num, means=None, stds=None, set_7mean=True):
    if set_7mean: #将超过7倍均值的数据置为7倍均值
        # 遍历DataFrame的每一列,
        for col in cname_num:  
            # 获取当前列的均值  
            mean_val = means[col]  
            # 创建一个布尔索引，用于标记哪些值超过了均值的7倍  
            mask = df[col] > (7 * mean_val)  
            # 将这些值重置为均值的7倍  
            df.loc[mask, col] = 7 * mean_val  

    df[cname_num] = (df[cname_num] - means)/stds  #标准化
    
    return df  

def get_logical_types(col_type):
    """featuretools逻辑类型处理
    - 主要处理日期与字符串两类，即将日期，字符串类型的字段转换为featuretools的类型
    - 数字不需要处理，因为featuretools会默认把数字形式的字符串当数字处理
    """
    logical_types={}
    for col in col_type.date_type:
        logical_types[col] = 'datetime'
    
    #类别本来不是数字，但onehot编码后，就只剩下0与1这两个数字了
    for col in col_type.str_classification:
        logical_types[col] = 'categorical'

    return logical_types


class ColumnType:
    def __init__(self):
        self.num_type = []          # 数字类
        self.bool_type = []          # 整数类
        self.date_type = []         # 日期类
        self.str_identity= []       # 标识
        self.str_classification=[]  # 类别
        self.feature_names = []     # 特征组合列
        self.feature_names_num= []  # 特征组合列之数字特征
        self.feature_names_str=[]   # 特征组合列之类别特征
        self.feature_logical_types={}


def data_classify_deal(data, col_type, pc,dealnull=False,dealstd=False,deallowdata=False,lowdata=10,deallog=False):
    """数据分类处理
    - 日期处理
    - object转string
    - 空值处理
    - 数字处理
        - 边界：极小-舍弃10￥以下交易，极大-重置超过7倍均值的金额
        - 分布：Log10后标准化
        - 最终的数据值不大，并且是以0为中心的正态分布

    - 处理后的数据类型：数字，日期，字符
    -
    
    params
    --------------------------------
    - dealnull:是否同时处理空值
    - dealstd:是否进行标准化处理
    - deallog:是否对数字列log10处理
    
    example
    ----------------------------------
    data_classify_deal(data,pc.col_type_nolable,pc)
    
    """
    column_all = data.columns
     
     
    ### 日期
    date_type = [col for col in col_type.date_type if col in column_all] 
    data = str_pd(data, date_type)
    for col in date_type:
        data[col] = pd.to_datetime(data[col], errors='coerce')  

    ### 数字
    num_type = [col for col in col_type.num_type if col in column_all] 
    data[num_type] = data[num_type].astype(np.float32)
    
    
    bool_type = [col for col in col_type.bool_type if col in column_all]
    data[bool_type] = (data[bool_type].astype(np.float32)).astype(int)  # 为了处理'0.00000000'

    ### 字符-身份标识类
    cname_str_identity = pc.cname_str_identity 
    str_identity = [col for col in column_all if col in cname_str_identity]
    col_type.str_identity = str_identity
    data = str_pd(data,str_identity)

    ### 字符-分类，用于分类的列，比如渠道，交易类型,商户，地区等
    str_classification = [col for col in data.columns if col not in str_identity and col not in num_type and col not in date_type and col not in bool_type]
    col_type.str_classification = str_classification
    data = str_pd(data,str_classification)

    #空值处理
    if dealnull:
        data = null_deal_pandas(data,cname_num_type=num_type,cname_str_type=str_classification,num_padding=0,str_padding = '<PAD>')

    if len(num_type)>0:
        if deallowdata:
            #数字特征-极小值处理
            #将小于10￥的金额全部置为0，即不考虑10￥以下的交易
            for col_name in num_type:
                data.loc[data[col_name]<lowdata,col_name] = lowdata
        
            #将lowdata以下交易剔除
            data.drop(data[data.CNY_AMT.eq(10)].index, inplace=True)
        if deallog:
            #防止后面特征组合时，两个本来就很大的数据相乘后变为inf
            data[num_type] = np.log10(data[num_type])
    
        if dealstd:
            # 数字特征-归一化及极大值处理
            #需要保存，预测时使用
            means = data[num_type].mean()
            stds = data[num_type].std()
            
            data = std7(data, num_type, means, stds)
    

    return data
    
    
from sklearn import tree
from sklearn.tree import _tree


def Get_Rules(clf,X):
    n_nodes = clf.tree_.node_count
    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    feature = clf.tree_.feature
    threshold = clf.tree_.threshold
    value = clf.tree_.value
    
    node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
    is_leaves  = np.zeros(shape=n_nodes, dtype=bool)
    stack = [(0, 0)]
    
    while len(stack) > 0:
        
        node_id, depth = stack.pop()
        node_depth[node_id] = depth
    
        is_split_node = children_left[node_id] != children_right[node_id]
        
        if is_split_node:
            stack.append((children_left[node_id],  depth+1))
            stack.append((children_right[node_id], depth+1))
        else:
            is_leaves[node_id] = True  
    feature_name = [
            X.columns[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in clf.tree_.feature]
    
    ways  = []
    depth = []
    feat = []
    nodes = []
    rules = []
    for i in range(n_nodes):   
        if  is_leaves[i]: 
            while depth[-1] >= node_depth[i]:
                depth.pop()
                ways.pop()    
                feat.pop()
                nodes.pop()
            if children_left[i-1]==i:#当前节点是上一个节点的左节点，则是小于
                a='{f}<={th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))
                ways[-1]=a              
                last =' & '.join(ways)+':'+str(value[i][0][0])+':'+str(value[i][0][1])
                rules.append(last)
            else:
                a='{f}>{th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))
                ways[-1]=a
                last = ' & '.join(ways)+':'+str(value[i][0][0])+':'+str(value[i][0][1])
                rules.append(last)
               
        else: #不是叶子节点 入栈
            if i==0:
                ways.append(round(threshold[i],4))
                depth.append(node_depth[i])
                feat.append(feature_name[i])
                nodes.append(i)             
            else: 
                while depth[-1] >= node_depth[i]:
                    depth.pop()
                    ways.pop()
                    feat.pop()
                    nodes.pop()
                if i==children_left[nodes[-1]]:
                    w='{f}<={th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))
                else:
                    w='{f}>{th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))              
                ways[-1] = w  
                ways.append(round(threshold[i],4))
                depth.append(node_depth[i]) 
                feat.append(feature_name[i])
                nodes.append(i)
    return rules

from sklearn import tree
from sklearn.tree import _tree

def rules_clf_base(clf,X):
    n_nodes = clf.tree_.node_count
    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    feature = clf.tree_.feature
    threshold = clf.tree_.threshold
    value = clf.tree_.value
    
    node_depth = np.zeros(shape=n_nodes, dtype=np.int64)
    is_leaves  = np.zeros(shape=n_nodes, dtype=bool)
    stack = [(0, 0)]
    
    while len(stack) > 0:
        
        node_id, depth = stack.pop()
        node_depth[node_id] = depth
    
        is_split_node = children_left[node_id] != children_right[node_id]
        
        if is_split_node:
            stack.append((children_left[node_id],  depth+1))
            stack.append((children_right[node_id], depth+1))
        else:
            is_leaves[node_id] = True  
    feature_name = [
            X.columns[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in clf.tree_.feature]
    
    ways  = []
    depth = []
    feat = []
    nodes = []
    rules = []
    for i in range(n_nodes):   
        if  is_leaves[i]: 
            while depth[-1] >= node_depth[i]:
                depth.pop()
                ways.pop()    
                feat.pop()
                nodes.pop()
            if children_left[i-1]==i:#当前节点是上一个节点的左节点，则是小于
                a='{f}<={th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))
                ways[-1]=a              
                last =' & '.join(ways)+':'+str(value[i][0][0])+':'+str(value[i][0][1])
                rules.append(last)
            else:
                a='{f}>{th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))
                ways[-1]=a
                last = ' & '.join(ways)+':'+str(value[i][0][0])+':'+str(value[i][0][1])
                rules.append(last)
               
        else: #不是叶子节点 入栈
            if i==0:
                ways.append(round(threshold[i],4))
                depth.append(node_depth[i])
                feat.append(feature_name[i])
                nodes.append(i)             
            else: 
                while depth[-1] >= node_depth[i]:
                    depth.pop()
                    ways.pop()
                    feat.pop()
                    nodes.pop()
                if i==children_left[nodes[-1]]:
                    w='{f}<={th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))
                else:
                    w='{f}>{th}'.format(f=feat[-1],th=round(threshold[nodes[-1]],4))              
                ways[-1] = w  
                ways.append(round(threshold[i],4))
                depth.append(node_depth[i]) 
                feat.append(feature_name[i])
                nodes.append(i)
    return rules

# 判断对象是否为 DataFrame 类型  

def is_dataframe(obj):  
    return isinstance(obj, pd.DataFrame) 

def rules_clf2(X,y,columns=None,max_depth=5,top_n=None,):
    """二分类问题规则生成
    - 按异常样本的含量排序，
    - 100%是异常样本，与0%是异常样本同样有用，它们都是纯净的数据，看实际需要提取哪个
    """
    if not is_dataframe(X):
        if columns is not None:
            X=pd.DataFrame(X,columns=columns)
            y=pd.DataFrame(y,columns=['label'])
        else:
            return 'X与y非pandas数表时，请指定 columns'

    #训练一个决策树，这里限制了最大深度和最小样本树
    clf = tree.DecisionTreeClassifier(max_depth=max_depth,min_samples_leaf=50)
    clf = clf.fit(X, y)
    rules = rules_clf_base(clf,X)
    
    # 结果格式整理
    df = pd.DataFrame(rules)
    df.columns = ['allrules']
    df['rules']    = df['allrules'].str.split(':').str.get(0)
    df['good']     = df['allrules'].str.split(':').str.get(1).astype(float)
    df['bad']      = df['allrules'].str.split(':').str.get(2).astype(float)
    df['all']      = df['bad']+df['good']
    df['rate'] = df['bad']/df['all']
    df.drop(columns=['good','bad','all'],inplace=True)
    df = df.sort_values(by='rate',ascending=False)
    del df['allrules']
    if top_n:
        return df[:top_n]
    else:
        return df
    

