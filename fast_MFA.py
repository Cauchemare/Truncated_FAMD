# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 18:43:24 2019

@author: luyao.li
"""


from fast_MCA import MCA
from fast_PCA import PCA

import six
import numpy as np
import pandas as pd 
from sklearn.utils import check_array

class MFA(PCA):
    def __init__(self,standard_scaler=True,n_components=2,svd_solver='auto',whiten=False,copy=True,
                 tol=None,iterated_power=2,batch_size =None,random_state=None,groups=None):
        for k,v in locals().items():
            if k!='self':
                setattr(self,k,v)

                
    def fit(self,X,y=None):
        if self.groups is None:
            raise ValueError('Must input group vars')

        check_array(X,dtype=[six.string_types[0],np.number])
        
        if not isinstance(X,(pd.DataFrame,pd.SparseDataFrame)):
            X=pd.DataFrame(X) 
        #determine which group is all_numeric
        self.partial_factor_analysis_={}
        for name, cols in  self.groups.items():
            all_num = all(pd.api.types.is_numeric_dtype(X[c]) for c in cols)
            all_cat = all(pd.api.types.is_string_dtype(X[c]) for c in cols)
            if not (all_num or all_cat):
                raise ValueError('Not all columns in "{}" group are of the same type'.format(name))
        # Run a factor analysis in each group   
       
            if all_num:
                fa = PCA(
                    standard_scaler=self.standard_scaler,
                    n_components=self.n_components,
                    copy=self.copy,
                    random_state=self.random_state,
                    svd_solver=self.svd_solver,
                    whiten=self.whiten,
                    tol=self.tol,
                    iterated_power=self.iterated_power,
                    batch_size=self.batch_size
                
                )
            else:
                fa = MCA(
                            n_components=self.n_components,
                             svd_solver=self.svd_solver,
                             copy=self.copy,
                             tol=self.tol,
                             iterated_power=self.iterated_power,
                             batch_size =self.batch_size,
                             random_state=self.random_state
                )

            self.partial_factor_analysis_[name] = fa.fit(X.loc[:, cols])  
            
        self= super().fit(self._X_global(X))
            
        return self
    
    def _X_global(self,X) :
        for name, cols in  self.groups.items():
            X_globals=[] 
            X_partial= X.loc[:,cols]
            if self.partial_factor_analysis_[name].__class__.__name__ =='PCA':
                X_partial=  pd.DataFrame(self.partial_factor_analysis_[name].scaler_.transform(X_partial),columns =cols)                 
            else:
                X_partial=self.partial_factor_analysis_[name].one_hot.transform(X_partial)
            X_globals.append(X_partial/ self.partial_factor_analysis_[name].singular_values[0] )
                           
        X_global=pd.concat(X_globals,axis=1 )
        return  X_global
    
    def transform(self,X,y =None):
        X_global=self._X_global(X)
        return len(X_global) ** 0.5 *super().transform(X_global)
    
    def column_correlation(self,X,same_input=True):
        X_global=self._X_global(X)
        return super().column_correlation(X_global,same_input=locals()['same_input'])
        
        
'''
Questions：
1)
  File "E:\1113蓝海数据建模\fast_FAMD\fast_MFA.py", line 82, in _X_global
    X_global=pd.concat(X_partial,axis=1)
    TypeError: first argument must be an iterable of pandas objects,
    you passed an object of type "SparseDataFrame
            X_global=pd.concat(X_partial,axis=1) ->  X_global=pd.concat(X_global,axis=1)
2)
          if self.partial_factor_analysis_[name].__class__.__name__ =='PCA':
                X_partial=  self.partial_factor_analysis_[name].scaler_.transform(X_partial) -> np.array
    
 将所有X_partial convert to np.ndarray


'''
                
            
                
                

        
            
            
            
            
            
            
        
        
        