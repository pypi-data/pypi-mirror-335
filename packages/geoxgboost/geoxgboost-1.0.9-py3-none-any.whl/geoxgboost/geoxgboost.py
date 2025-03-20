""" This module implements Geographical-XGBoost for spatially local regression.

The module contains the following functions:

- `create_param_grid` - Returns the grid of up to three hyperparameters.
- `nestedCV` - Returns the optimized hyperparameters' values and generalization error of XGBoost.
- `global_xgb` - Returns the global XGBoost model.
- `optimize_bw` - Returns the optimized bandwidth value.
- `gxgb` - Returns geographical XGBoost, local prediction and related statistics.
- `predict_gxgb` - Returns prediction in unseen data.

"""
# Import libs
import numpy as np
import pandas as pd
from numpy import mean
from numpy import std
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from scipy.spatial import distance_matrix

def create_param_grid(Param1, Param1_Values, Param2=None, Param2_Values=None, Param3=None, Param3_Values=None):
    """ Creates a grid of up to three hyperparameters for tuning.

    Examples:
        >>> Param1='n_estimators'
        >>> Param1_Values = [100, 200, 300,500]
        >>> Param2='learning_rate'
        >>> Param2_Values = [0.1, 0.05,0.01]
        >>> Param3='max_depth'
        >>> Param3_Values = [2,3,4,6]
        >>> create_param_grid(Param1,Param1_Values,Param2,Param2_Values,Param3,Param3_Values)

    :param Param1: 1st hyperparameter name e.g., 'n_estimators'
    :param Param1_Values: values for search e.g., [100, 200, 500]
    :param Param2:  2nd hyperparameter name e.g., 'learning_rate'. Default=None.
    :param Param2_Values: values for search e.g., [0.1, 0.05,0.01]. Default=None.
    :param Param3: 3rd hyperparameter name e.g., 'max_depth'. Default=None.
    :param Param3_Values: values for search e.g., [2,3,4,6]. Default=None.
    :return: param_grid.  Can be used in nestedCV function to fine tune hyperparameters

    Change the argument of Param1, Param2, or Param3 with other hyperparamters available to tune XGBoost, such as:
    subsample, colsample_bytree, lambda, alpha etc.

    For example:

    Param1= 'subsmample'

    Param1_Values = [0.5, 0.7, 0.9]

    A complete list of hyperparameters can be found here:
    https://xgboost.readthedocs.io/en/stable/parameter.html

    Tip: This function can be iteratively repeated with different sets of hyperparameters.
    See an example in GXGB_call_demo.py at the DemoGXGBoost in GitHub.
    """
    param_grid = {}  # Create params grid
    if Param1 is not None:
        param_grid[Param1] = Param1_Values
    if Param2 is not None:
        param_grid[Param2] = Param2_Values
    if Param3 is not None:
        param_grid[Param3] = Param3_Values
    return param_grid

def nestedCV(X, y, param_grid, Param1, Param2=None, Param3=None, params=None, path_save=False, n_OuterSplits=5,
             n_InnerSplits=3):
    """ Applies nested cross validation for tuning up to three hyperparameters and calculating model generalization error.

    :param X: dataframe with the independent variables values
    :param y: dataframe with the dependent variable values
    :param params: initial hyperparameter values. Type:dictionary
    :param param_grid: grid values - output of param_grid function
    :param Param1: name of 1st hyperparameter used (same as param_grid function)
    :param Param2: name of 2nd hyperparameter used in param_grid function. Default=None.
    :param Param3: name of 3rd hyperparameter used in param_grid function. Default=None.
    :param path_save: output folder. Default=False.
    :param n_OuterSplits: number of outer splits. Default=5.
    :param n_InnerSplits: number if inner splits Default=3.
    :return: optimized hyperparameters' values and generalization error of model through nestedCV
    """
    # Default values for params for XGBoost and GXGBoost
    defaultparams = {
        'n_estimators': 100,
        'learning_rate': 0.3,
        'max_depth': 6,
        'min_child_weight': 1,
        'gamma': 0,
        'subsample': 1,
        'colsample_bytree': 1,
        'reg_alpha': 0,
        'reg_lambda': 1,
    }

    if params is None:
        params = defaultparams
        print(params)

    Best_Param1 = list()
    Best_Param2 = list()
    Best_Param3 = list()
    count = 0
    # Outer loop
    cv_outer = KFold(n_splits=n_OuterSplits, shuffle=True, random_state=1)
    outer_resultsR2 = list()
    outer_resultsRMSE = list()
    outer_resultsMAE = list()
    print("=================Nested CV process===========================================")
    # Inner loop
    for train_ix, test_ix in cv_outer.split(X):
        # split data
        X_train, X_test = X.iloc[train_ix, :], X.iloc[test_ix, :]
        Y_train, y_test = y[train_ix], y[test_ix]
        # configure the cross-validation procedure for the inner loop
        cv_inner = KFold(n_splits=n_InnerSplits, shuffle=True, random_state=1)
        # define the model
        model = XGBRegressor(**params)
        # execute search
        grid_search = GridSearchCV(model, param_grid, scoring="neg_root_mean_squared_error", n_jobs=-1, cv=cv_inner)
        grid_result = grid_search.fit(X_train, Y_train)
        # get the best performing model fit on the whole training set
        best_model = grid_result.best_estimator_
        # evaluate model on the hold out dataset
        predictions = best_model.predict(X_test)
        R2 = r2_score(y_test, predictions)  # (ytrue,ypredict)
        MAE = mean_absolute_error(y_test, predictions)
        # store the result
        outer_resultsR2.append(R2)
        outer_resultsRMSE.append(grid_result.best_score_)
        outer_resultsMAE.append(MAE)
        # update params based on the number of hyperparameters used
        if Param3 is None:
            if Param2 is not None:
                print('Tuning with 2 hyperparameters')
                Best_Param1.append(grid_result.best_params_[Param1])
                Best_Param2.append(grid_result.best_params_[Param2])
                case = 2
            else:
                Best_Param1.append(grid_result.best_params_[Param1])
                print('Tuning with 1 hyperparameter')
                case = 1
        else:
            print('Tuning with 3 hyperparameters')
            Best_Param1.append(grid_result.best_params_[Param1])
            Best_Param2.append(grid_result.best_params_[Param2])
            Best_Param3.append(grid_result.best_params_[Param3])
            case = 3
        # print progress and results
        count += 1
        progress = count / n_OuterSplits
        print('>Count=%.0f,  R2=%.3f, RMSE=%.3f, MAE=%.3f,cfg=%s, Progress Completed=%.2f%%' % (
        count, R2, grid_result.best_score_, MAE, grid_result.best_params_, progress * 100))
    # End of Inner loop
    # Outer loop: Summarize the estimated performance of the model

    print("=================Nested CV results for hyperparamtre tuning==================")
    print('Generalization error: mean-R2 (stdev): %.3f (%.3f)' % (mean(outer_resultsR2), std(outer_resultsR2)))
    print('Mean MAE: %.3f (%.3f)' % (mean(outer_resultsMAE), std(outer_resultsMAE)))
    print('Mean RMSE: %.3f (%.3f)' % (mean(outer_resultsRMSE), std(outer_resultsRMSE)))
    # Find the best model
    index_max = np.argmax(outer_resultsRMSE)
    print('Best params taken at model with minimum RMSE at count: %.0f ' % (index_max + 1))
    Generalized_NestedCV = pd.DataFrame(index=['Generalized Nested CV'],
                                        columns=['meanR2', 'Std_meanR2', 'meanMAE', 'Std_meanMAE', 'meanRMSE',
                                                 'meanRMSE'])
    Generalized_NestedCV.iloc[0, 0] = mean(outer_resultsR2)
    Generalized_NestedCV.iloc[0, 1] = std(outer_resultsR2)
    Generalized_NestedCV.iloc[0, 2] = mean(outer_resultsMAE)
    Generalized_NestedCV.iloc[0, 3] = std(outer_resultsMAE)
    Generalized_NestedCV.iloc[0, 4] = mean(outer_resultsRMSE)
    Generalized_NestedCV.iloc[0, 5] = std(outer_resultsRMSE)
    print(Generalized_NestedCV)

    # Outer loop generalization results export
    if path_save is False:
        Generalized_NestedCV.to_csv('Generalized_NestedCV_Stats.csv', index=True)
    else:
        Generalized_NestedCV.to_csv(path_save + 'Generalized_NestedCV_Stats.csv', index=True)
    # save tuned params
    if case == 3:
        TunedParams = {
            Param1: Best_Param1[index_max],
            Param2: Best_Param2[index_max],
            Param3: Best_Param3[index_max],
        }
    elif case == 2:
        TunedParams = {
            Param1: Best_Param1[index_max],
            Param2: Best_Param2[index_max],
        }
    else:
        TunedParams = {
            Param1: Best_Param1[index_max],
        }
    params.update(TunedParams)

    result = {}
    result['Params'] = params
    result['TunedParams'] = TunedParams
    result['Stats'] = Generalized_NestedCV
    Output_NestedCV = result

    print('Best hyperparamter values:')
    print(params)
    print('Results have been saved in csv format at the specified path')
    print("=============================================================================")

    return params, Output_NestedCV


def global_xgb(X, y, params, feat_importance='gain', test_size=0.33, seed=7, path_save=False):
    """ Calculates global XGBoost 

    :param X: dataframe with the independent variables values
    :param y: dataframe with the dependent variable values
    :param params: hyperparameter values. Type:dictionary  (NestedCV can be used to produce params)
    :param feat_importance: type of feature importance: 'gain',weight’,cover’,‘total gain’,‘total cover’.Default='gain'
    :param test_size: size test (%). Default=0.33.
    :param seed: seed value.Default=7
    :param path_save: output folder. Default=False.
    :return: global xgboost performance
    """
    eval_metric = ["mae", "rmse"]
    # Split data into train and test sets
    X_train, X_test, Y_train, y_test = train_test_split(X, y, test_size=test_size,
                                                        random_state=seed)
    model = XGBRegressor(**params, importance_type=feat_importance, eval_metric=eval_metric)
    eval_set = [(X_train, Y_train), (X_test, y_test)]
    # Train model
    model.fit(X_train, Y_train, eval_set=eval_set, verbose=False)
    # Importance
    importance = (pd.DataFrame(model.feature_importances_)).T
    importance.columns = X.columns[:]  # (VarNames)
    # Predictions
    Predictions_Test = model.predict(X_test)  # Make predictions for test data
    # evaluate prediction
    R2 = r2_score(y_test, Predictions_Test)  # (ytrue ypredict)
    # Output Results for Test set (OOB)
    y_true = y_test
    y_pred = Predictions_Test
    R2test = r2_score(y_true, y_pred)
    MAEtest = mean_absolute_error(y_true, y_pred)
    RMSEtest = root_mean_squared_error(y_true, y_pred)
    # Output Results for Prediction set [We use complete X to Predict Y - expected overestimations]
    Predictions_Full = model.predict(X)
    y_true = y
    y_pred = Predictions_Full
    R2pred = r2_score(y_true, y_pred)
    GM_Res = y_true - y_pred
    MAEpred = mean_absolute_error(y_true, y_pred)
    RMSEpred = root_mean_squared_error(y_true, y_pred)
    GMDict = {'y': y_true, 'GM_yPred': y_pred, 'GM_Res': GM_Res}
    Global_XGB = pd.DataFrame(GMDict)
    # Output stats
    Global_XGB_Stats = pd.DataFrame(index=['GlobalXGB'],
                                    columns=['R2Pred', 'MAEPred', 'RMSPred', 'R2test', 'MAEtest', 'RMSETest'])
    Global_XGB_Stats.iloc[0, 0] = R2pred
    Global_XGB_Stats.iloc[0, 1] = MAEpred
    Global_XGB_Stats.iloc[0, 2] = RMSEpred
    Global_XGB_Stats.iloc[0, 3] = R2test
    Global_XGB_Stats.iloc[0, 4] = MAEtest
    Global_XGB_Stats.iloc[0, 5] = RMSEtest
    Global_XGB_Stats.reset_index(drop=True, inplace=True)
    importance.reset_index(drop=True, inplace=True)
    importance.columns = X.add_prefix('Imp_').columns[:]
    Global_XGB_Stats = pd.concat([Global_XGB_Stats, importance], axis=1)
    Global_XGB_Stats = Global_XGB_Stats.rename(index={0: 'GlobalXGB'})

    print("=================XGBoost (global) evaluation results ========================")
    print("Global feature importance:")
    print(importance)
    print("Test R2: %.2f%%" % (R2 * 100.0))
    print("===================Stats and importance======================================")
    print(Global_XGB_Stats)
    print('Results have been saved in xlsx format at the specified path')
    print("=============================================================================")

    txt1 = [
        'Pred metrics refer to the full set (after training, prediction using all data). Used only for reference.  | Test metrics refer to the test set. | Imp_ refers to feature importance ']
    Text1 = pd.DataFrame(txt1, columns=['Note:'])
    txt2 = ['Grekousis G. (2025). Geographical-XGBoost: A new ensemble model for spatially local regression based on gradient-boosted trees. Journal of Geographical Systems, https://doi.org/10.1007/s10109-025-00465-4']
    Text2 = pd.DataFrame(txt2, columns=['Citation:'])
    if path_save is False:
        with pd.ExcelWriter('GlobalXGB.xlsx') as writer:
            Global_XGB_Stats.to_excel(writer, sheet_name='Stats', index=True)
            Global_XGB.to_excel(writer, sheet_name='Predict', index=False)
            Text1.to_excel(writer, sheet_name='Stats', startrow=5, index=False)
            Text2.to_excel(writer, sheet_name='Stats', startrow=10, index=False)
    else:
        with pd.ExcelWriter(path_save + 'GlobalXGB.xlsx') as writer:
            Global_XGB_Stats.to_excel(writer, sheet_name='Stats', index=True)
            Global_XGB.to_excel(writer, sheet_name='Predict', index=False)
            Text1.to_excel(writer, sheet_name='Stats', startrow=5, index=False)
            Text2.to_excel(writer, sheet_name='Stats', startrow=10, index=False)

    result = {}
    result['Predictions'] = Global_XGB
    result['Stats'] = Global_XGB_Stats
    result['Importance'] = importance

    Output_GlobalXGBoost = result

    return Output_GlobalXGBoost


def optimize_bw(X, y, Coords, params, bw_min, bw_max, step=1, Kernel='Adaptive', spatial_weights=True, n_splits=3,
                path_save=False):
    """ Finds optimal bandwidth value for defining spatial kernels

    Examples:
        >>> optimize_bw(X,y, Coords, params, bw_min=30, bw_max=100,step=10)

    :param X: dataframe with the independent variables values
    :param y: dataframe with the dependent variable values
    :param Coords: dataframe with the coordinates of spatial units
    :param params: hyperparameter values
    :param bw_min: min bandwidth value
    :param bw_max: max bandwidth value
    :param step: incremental step. Default=1.
    :param Kernel: 'Adaptive' or 'Fixed' kernel type to be used. Default= 'Adaptive'.
    :param spatial_weights: spatial weights matrix. Default= True.
    :param n_splits: k-fold grid CV number of split, Default=3.
    :param path_save: output folder. Default=False.
    :return: optimal bandwidth value
    """
    reg_Alpha = []
    reg_Alpha.insert(0, params['reg_alpha'])
    param_grid = {  # creates a pseudo grid
        'reg_alpha': reg_Alpha
    }
    scoring = ['neg_root_mean_squared_error', 'r2']

    print("=================Calculating optimal bandwidth===============================")
    if spatial_weights is False:
        print('Calculation without spatial weights')
    else:
        print('Calculation with spatial weights')
        if Kernel == 'Adaptive':
            print('Adaptive Kernel used')
        else:
            print('Fixed kernel ')

    bwR2 = []
    bwMAE = []
    bwRMSE = []
    bwIndex = []
    bwCV = []
    num_rows = len(X)  # number of spatial units
    DistanceMatrix_ij = pd.DataFrame(distance_matrix(Coords, Coords))  # Distance matrix nXn

    # loop for bandwidth values
    for b in range(bw_min, bw_max + 1, step):
        print('Calculating bw= %.0i, with bw_max=%.0i and step of %.0i' % (b, bw_max, step))
        bw = b
        listIDs = []
        yt = []  # ytrue value
        LM_yOOB = []  # save central Y oob
        LM_ResOOB = []  # calculate the residual of  ytrue central with yOOB
        # loop for spatial units
        for i in range(num_rows):  # the spatial unit to be calculated
            Neigbours = pd.DataFrame(DistanceMatrix_ij.iloc[:, i])
            Neigbours.columns = ['Distance']
            Data = pd.concat([X, y, Neigbours], axis=1)
            DataSorted = Data.sort_values(by=['Distance'])
            XcentralOOB = pd.DataFrame(DataSorted.iloc[0, : -2])  # For estimating OOB error of the central point
            YcentralOOB = DataSorted.iloc[0, -2]
            # Spatial weights
            if Kernel == 'Adaptive':
                knn = bw
                LocalData = DataSorted.iloc[1:knn + 1, :]  # Local data without the central spatial unit (OOB).
                LocalX = LocalData.iloc[:, : -2]
                LocalY = LocalData.iloc[:, -2]  # Keep only the dependent y
                h = max(LocalData.Distance)
                SpatialWeights = (1 - (LocalData.Distance.pow(2) / h ** 2)).pow(
                    2)  # Adaptive bi-square (when we set number of nearest neighbours)
            else:  # fixed kernel
                LocalData = DataSorted[DataSorted.Distance < bw]
                LocalData = LocalData.iloc[1:, :]  # Removes central spatial unit
                LocalX = LocalData.iloc[:, : -2]
                LocalY = LocalData.iloc[:, -2]
                h = bw
                SpatialWeights = (1 - (LocalData.Distance.pow(2) / h ** 2)).pow(
                    2)  # Fixed bi-square (when we set a distance threshold value)

            # train model through grid CV (used to assign spatial weights if selected)
            model = XGBRegressor(**params)
            kfold = KFold(n_splits=n_splits, shuffle=True, random_state=7)
            grid_search = GridSearchCV(model, param_grid, scoring=scoring, refit='neg_root_mean_squared_error',
                                       return_train_score=True, n_jobs=-1, cv=kfold)
            if spatial_weights is False:
                grid_result = grid_search.fit(LocalX, LocalY)
            else:
                grid_result = grid_search.fit(LocalX, LocalY, sample_weight=SpatialWeights)
            # get the best performing model fit on the whole training set
            best_model = grid_result.best_estimator_

            # Y central OOB
            yOOB = best_model.predict(XcentralOOB.T)
            LM_yOOB.append(yOOB[0])
            ResOOB = YcentralOOB - yOOB[0]
            LM_ResOOB.append(ResOOB)
            listIDs.append(i)
            yt.append(YcentralOOB)
            # end loop for spatial units
        LMDict = {'IDS': listIDs, 'y': yt, 'LM_yOOB': LM_yOOB,
                  'LM_ResOOB': LM_ResOOB}
        LMResults = pd.DataFrame(LMDict)
        y_true = LMResults.iloc[:, 1]
        y_pred = LMResults.iloc[:, 2]
        R2test = r2_score(y_true, y_pred)
        MAEtest = mean_absolute_error(y_true, y_pred)
        RMSEtest = root_mean_squared_error(y_true, y_pred)
        CV = ((LMResults.iloc[:, 3]).pow(2)).sum()  # CV=Σ(ytrue-yoob)^2
        bwR2.append(R2test)
        bwMAE.append(MAEtest)
        bwRMSE.append(RMSEtest)
        bwIndex.append(bw)
        bwCV.append(CV)
        print('bw= %.0i, with CV= %.3f' % (b, CV))
        # end loop for bandwidth value
    # Save data to dataframe end csv
    BWDict = {'BW': bwIndex, 'R2': bwR2, 'MAE': bwMAE, 'RMSE': bwRMSE, 'CV': bwCV}
    BW_results = pd.DataFrame(BWDict)
    CVmin = min(BW_results.CV)
    idx = BW_results[['CV']].idxmin()
    BW_optCV = (BW_results.iloc[idx, 0]).values[0]
    print('Best bandwidth value: %i at min CV= %.3f.' % (BW_optCV, CVmin))
    print('Results have been saved in csv format at the specified path')
    print("=============================================================================")
    if path_save is False:
        BW_results.to_csv('BW_results.csv', index=True)
    else:
        BW_results.to_csv(path_save + 'BW_results.csv', index=True)
    return BW_optCV


def gxgb(X, y, Coords, params, bw, Kernel='Adaptive', spatial_weights=False, feat_importance='gain',
         alpha_wt_type='varying', alpha_wt=1, test_size=0.30, seed=7, n_splits=5, path_save=False):
    """ Implements GeoXGBoost

    :param X: dataframe with the independent variables values
    :param y: dataframe with the dependent variable values
    :param Coords: dataframe with the coordinates of spatial units
    :param params: hyperparameter values
    :param bw: bandwidth value
    :param Kernel: 'Adaptive' or 'Fixed' kernel type to be used. Default= 'Adaptive'.
    :param spatial_weights: spatial weights matrix. Default= True.
    :param feat_importance: type of feature importance. Available methods: 'gain',weight’,cover’,‘total gain’,‘total cover’.Default='gain'
    :param alpha_wt_type: type of alpha_wt. Available methods: 'varying', fixed’. Default='varying'
    :param alpha_wt: aplha weight value. It takes values between 0 and 1. Default=1.
    :param test_size: size test (%). Default=0.33.
    :param seed: seed value. Default=7.
    :param n_splits: k-fold grid CV number of split, Default=5.
    :param path_save: output folder. Default=False.
    :return: local prediction and related statistics

    """
    # Initialize variabes
    reg_Alpha = []
    reg_Alpha.insert(0, params['reg_alpha'])
    param_grid = {  # creates a pseudo grid, needed for spatial weights
        'reg_alpha': reg_Alpha
    }
    listIDs = []
    yt = []  # Saves the y true value
    LM_yPred = []  # Saves the predicted value of central when included in training
    LM_yOOB = []  # Saves Central Y oob
    LM_ResOOB = []  # Calculates the residual of y true central with yOOB
    LocalRsqr = []  # Save local Rsqr of test set
    LM_Best_params = []  # Saves best params of every local model
    LM_Best_score = []  # Saves best score of every local model during training phase
    LM_Best_importance = []  # Importance from best model
    bestLocalModel = []  # Best local model. Used also in PredictGXGB function
    y_G_hat = []  # Saves the prediction of XcentralOOB of the global  model trained without the OOB
    y_comb = []  # Saves the combined of local yhat+ global yhat:  alpha_wt * yOOB + (1-alpha_wt) * yGhat
    LocalAlpha_wt = []  # Saves the alpha_wt per local model
    # caclulate distance matrix
    DistanceMatrix_ij = pd.DataFrame(distance_matrix(Coords, Coords))  # Distance matrix nXn
    # Calculate the number of spatial units and the number of independent variable
    num_rows = len(X)
    num_cols = len(X.columns)
    # Scoring method
    scoring = ['neg_root_mean_squared_error', 'r2']
    # checks
    if spatial_weights is False:
        if alpha_wt < 1:
            raise ValueError('alpha_wt should be 1 and alpha_wt_type should be fixed if spatial_weights is False.')

    print("=================Calculating Geographical XGBOOST============================")

    # ---------------Start loop for every local model ---------
    for i in range(num_rows):
        print('Calculating i= %.0i from a total of %.0i' % (i + 1, num_rows))
        Neigbours = pd.DataFrame(DistanceMatrix_ij.iloc[:, i])
        Neigbours.columns = ['Distance']
        Data = pd.concat([X, y, Neigbours], axis=1)
        DataSorted = Data.sort_values(by=['Distance'])
        XcentralOOB = pd.DataFrame(DataSorted.iloc[0, : -2])  # For estimating OOB error of the cetral point
        YcentralOOB = DataSorted.iloc[0, -2]
        # Kernel weights
        if Kernel == 'Adaptive':
            knn = bw
            LocalData = DataSorted.iloc[1:knn + 1, :]  # Local data without the central spatial unit (OOB).
            LocalX = LocalData.iloc[:, : -2]
            LocalY = LocalData.iloc[:, -2]  # Keep only the dependent y
            # For predict results. All data are used- no OOB
            LocalDataFull = DataSorted.iloc[:knn + 1, :]  # Local data with the central sptatial unit (Pred).
            LocalXFull = LocalDataFull.iloc[:, : -2]
            LocalYFull = LocalDataFull.iloc[:, -2]  # Keep only the dependent y
            # Calculate spatial weights: Adaptive bi-square (for number of nearest neighbours)
            h = max(LocalData.Distance)
            SpatialWeights = (1 - (LocalData.Distance.pow(2) / h ** 2)).pow(2)
            print('Adaptive Kernel used with %i neighbours' % knn)
        else:
            LocalData = DataSorted[DataSorted.Distance < bw]
            LocalData = LocalData.iloc[1:, :]  # Removes central spatial unit
            LocalX = LocalData.iloc[:, : -2]
            LocalY = LocalData.iloc[:, -2]
            # For predict results
            LocalDataFull = DataSorted.iloc[:, :]  # Local data with the central spatial unit (Pred).
            LocalXFull = LocalDataFull.iloc[:, : -2]
            LocalYFull = LocalDataFull.iloc[:, -2]  # Keep only the dependent y
            # Calculate spatial weights: Fixed bi-square (for distance threshold value)
            h = bw
            SpatialWeights = (1 - (LocalData.Distance.pow(2) / h ** 2)).pow(2)
            print('Fixed kernel with distance value %.00f' % bw)

        # ------------------Model run ---------------------
        model = XGBRegressor(**params, importance_type=feat_importance)
        # Run Grid CV
        kfold = KFold(n_splits=n_splits, shuffle=True, random_state=7)
        grid_search = GridSearchCV(model, param_grid, scoring=scoring, refit='neg_root_mean_squared_error',
                                   return_train_score=True, n_jobs=-1, cv=kfold)
        if spatial_weights is False:
            print('Calculation without spatial weights')
            grid_result = grid_search.fit(LocalX, LocalY)
        else:
            print('Calculation with spatial weights')
            grid_result = grid_search.fit(LocalX, LocalY, sample_weight=SpatialWeights)
        # get the best performing model fit on the training set
        best_model = grid_result.best_estimator_
        bestLocalModel.append(best_model)
        LM_Best_params.append(grid_result.best_params_)
        LM_Best_score.append(grid_result.best_score_)
        LM_Best_importance.append(best_model.feature_importances_)
        # calculate LMR2 at the test set of CV
        R2means = np.max(grid_result.cv_results_['mean_test_r2'])
        # Y central OOB
        yOOB = best_model.predict(XcentralOOB.T)
        LM_yOOB.append(yOOB[0])
        ResOOB = YcentralOOB - yOOB[0]
        LM_ResOOB.append(ResOOB)
        # Local Rsq Train
        LocalRsqr.append(R2means)  # Saves the R2  of the (i) local model
        listIDs.append(i)
        yt.append(YcentralOOB)
        # Y central Predict  (for predict statistcs)
        modelFull = XGBRegressor(**params, importance_type=feat_importance)
        modelFull.fit(LocalXFull, LocalYFull)
        yCentralPred = modelFull.predict(XcentralOOB.T)
        LM_yPred.append(yCentralPred[0])

        # ----------------------Ensemble-----------------------
        # Calcluates the Global model without the OOB
        X1 = X.drop(i)  # Creates a set for the global model without the OOB
        y1 = y.drop(i)
        eval_metric = ["mae", "rmse"]
        # Split data into train and test sets
        X_train, X_test, Y_train, y_test = train_test_split(X1, y1, test_size=test_size,
                                                            random_state=seed)
        model1 = XGBRegressor(**params, importance_type=feat_importance, eval_metric=eval_metric)
        eval_set = [(X_train, Y_train), (X_test, y_test)]
        # Train model
        model1.fit(X_train, Y_train, eval_set=eval_set, verbose=False)
        # Prediction of OOB through the global model
        yGhat = model1.predict(XcentralOOB.T)
        resG = YcentralOOB - yGhat[0]
        # check global and local residuals
        if alpha_wt_type == 'fixed':
            Alpha_wt = alpha_wt
            print('Calculation with fixed alpha_wt')
            if alpha_wt == 1:
                print('Calculation without ensemble')
            else:
                print('Calculation with ensemble')
        else:
            if alpha_wt == 1:
                print('Calculation without ensemble')
                Alpha_wt = alpha_wt
            else:
                print('Calculation with ensemble and varying alpha_wt')
            if abs(resG) > abs(ResOOB):
                Alpha_wt = 1
            else:
                Alpha_wt = alpha_wt
        b = 1 - Alpha_wt  # controls the weight of local vs global model. [Alpha_wt] refers to the local model
        print('a= %.2f, b=%.2f' % (Alpha_wt, b))
        ycomb = Alpha_wt * yOOB + b * yGhat  # Combines local and global predictions
        y_G_hat.append(yGhat[0])  # Prediction of OOB through the global model
        y_comb.append(ycomb[0])
        LocalAlpha_wt.append(Alpha_wt)
    # ---------------End loop-------------------------------------------------

    # ------------Local models and local fearure importance -----------------
    LMDict = {'IDS': listIDs, 'y': yt, 'LM_yPred': LM_yPred, 'LM_yOOB': LM_yOOB, 'LM_ResOOB': LM_ResOOB,
              'LMRsqr': LocalRsqr, 'LM_Best_score(RMSE)': LM_Best_score, 'alpha_wt': LocalAlpha_wt, 'yGhat': y_G_hat,
              'y_ensemble': y_comb}
    LM_results = pd.DataFrame(LMDict)
    LM_importance = pd.DataFrame(LM_Best_importance)
    LM_importance.columns = X.add_prefix('Imp_').columns[:]
    # finding the feature with max importance. Used to map later to GIS
    maxValues = LM_importance.max(axis=1)
    MaxValues = pd.DataFrame(maxValues, columns=['MaxImportance'])
    # finds the column position (feature)
    column_id = LM_importance.columns.get_indexer(LM_importance.apply('idxmax', axis=1)) + 1
    Column_id = pd.DataFrame(column_id, columns=['MaxFeatureID'])
    LM_importance = pd.concat([LM_importance, MaxValues, Column_id], axis=1)
    LM_results2Excel = pd.concat([LM_results, LM_importance], axis=1)

    # ----Output results of aggregated local models to compare with global set ---------------
    # Output Results for Predict set (only used for reference)
    y_true = LM_results.iloc[:, 1]
    y_pred = LM_results.iloc[:, 2]
    R2pred = r2_score(y_true, y_pred)
    MAEpred = mean_absolute_error(y_true, y_pred)
    RMSEpred = root_mean_squared_error(y_true, y_pred)
    # Output Results for OOB set (Local Model yOOB)
    y_true = LM_results.iloc[:, 1]
    y_pred = LM_results.iloc[:, 3]
    R2test = r2_score(y_true, y_pred)
    MAEtest = mean_absolute_error(y_true, y_pred)
    RMSEtest = root_mean_squared_error(y_true, y_pred)
    # output results for OOB-1 global set (global model output for OOB  yGhat)
    y_true = LM_results.iloc[:, 1]
    y_pred = LM_results.iloc[:, 8]
    R2oobGl = r2_score(y_true, y_pred)
    MAEoobGl = mean_absolute_error(y_true, y_pred)
    RMSEoobGl = root_mean_squared_error(y_true, y_pred)
    # Output Results for combined set (y_ensemble)
    y_true = LM_results.iloc[:, 1]
    y_pred = LM_results.iloc[:, 9]
    R2ens = r2_score(y_true, y_pred)
    MAEens = mean_absolute_error(y_true, y_pred)
    RMSEens = root_mean_squared_error(y_true, y_pred)

    #  xlsx file naming
    if spatial_weights is False:
        if alpha_wt == 1:
            ind = ['L_GXGB']
    else:
        if alpha_wt == 1:
            ind = ['LW_GXGB']
        else:
            ind = ['GXGB']
    Evaluation_Results = pd.DataFrame(index=[ind],
                                      columns=['R2_Pred', 'MAE_Pred', 'RMS_Pred', 'R2_oob', 'MAE_oob', 'RMS_oob',
                                               'R2oobGl', 'MAEoobGl', 'RMSEoobGl', 'R2ens', 'MAEens', 'RMSEens'])

    Evaluation_Results.iloc[0, 0] = R2pred
    Evaluation_Results.iloc[0, 1] = MAEpred
    Evaluation_Results.iloc[0, 2] = RMSEpred
    Evaluation_Results.iloc[0, 3] = R2test
    Evaluation_Results.iloc[0, 4] = MAEtest
    Evaluation_Results.iloc[0, 5] = RMSEtest
    if alpha_wt == 1:
        pass
    else:
        Evaluation_Results.iloc[0, 6] = R2oobGl
        Evaluation_Results.iloc[0, 7] = MAEoobGl
        Evaluation_Results.iloc[0, 8] = RMSEoobGl
        Evaluation_Results.iloc[0, 9] = R2ens
        Evaluation_Results.iloc[0, 10] = MAEens
        Evaluation_Results.iloc[0, 11] = RMSEens

    print("=============Geographical-XGBoost Evaluation results ================")
    print(Evaluation_Results)
    print('Results have been saved in xlsx format at the specified path')
    print("=====================================================================")
    # saving hyperparameters values
    params_spatial = {'Spatial Units': num_rows, 'Features': num_cols, 'Kernel': Kernel, 'Bandwidth': bw,
                      'Spatial Weights': spatial_weights, 'Alpha Weight type': alpha_wt_type,
                      'Alpha Weight value': alpha_wt, 'Feature Importance': feat_importance,
                      'Test Size': test_size, 'Seed': seed}
    params_full = params | params_spatial
    Params_full = (pd.DataFrame(data=params_full, index=['Value'])).T
    file_name = (ind[0] + '.xlsx')

    txt1 = [
        'Pred metrics refer to the full set (after training, prediction using all data). Used only for reference.  | oob metrics refer to the local model when the central point is not including. | oobGl metrics refer to the global model when the central point is not including. | ens metrics refer to the local model']
    Text1 = pd.DataFrame(txt1, columns=['Notes:'])
    txt3 = ['Grekousis G. (2025). Geographical-XGBoost: A new ensemble model for spatially local regression based on gradient-boosted trees. Journal of Geographical Systems, https://doi.org/10.1007/s10109-025-00465-4']
    Text3 = pd.DataFrame(txt3, columns=['Citation:'])

    Xls_column_labels = {'IDS': 'Spatial unit id', 'y': 'y_true',
                         'LM_yPred': 'Local model prediction including central point',
                         'LM_yOOB': 'Local model prediction excluding central point',
                         'LM_ResOOB': 'Local model OOB residuals', 'LMRsqr': 'Local model Rsqr (oob)',
                         'LM_Best_score(RMSE)': 'Local model best score (oob)', 'alpha_wt': 'alpha weight value',
                         'yGhat': 'Prediction of the global model excluding central point',
                         'y_ensemble': 'prediction  of y through ensemble', 'Imp_': 'Feature local importance',
                         'MaxImportance': 'Maximum feature importance',
                         'MaxFeatureID': 'Feature with  max importance'}
    xls_column_labels = (pd.DataFrame(data=Xls_column_labels, index=['Description'])).T

    # saving hyperparameters, statistics, and local models to xlsx
    if path_save is False:
        with pd.ExcelWriter(file_name) as writer:
            Evaluation_Results.to_excel(writer, sheet_name='Stats', index=True)
            Params_full.to_excel(writer, sheet_name='Stats', startrow=3, index=True)
            Text1.to_excel(writer, sheet_name='Stats', startrow=25, index=False)
            xls_column_labels.to_excel(writer, sheet_name='Stats', startrow=28, index=True)
            Text3.to_excel(writer, sheet_name='Stats', startrow=43, index=False)
            LM_results2Excel.to_excel(writer, sheet_name='LocalModels', index=False)


    else:
        with pd.ExcelWriter(path_save + file_name) as writer:
            Evaluation_Results.to_excel(writer, sheet_name='Stats', index=True)
            Params_full.to_excel(writer, sheet_name='Stats', startrow=3, index=True)
            Text1.to_excel(writer, sheet_name='Stats', startrow=25, index=False)
            xls_column_labels.to_excel(writer, sheet_name='Stats', startrow=28, index=True)
            Text3.to_excel(writer, sheet_name='Stats', startrow=43, index=False)
            LM_results2Excel.to_excel(writer, sheet_name='LocalModels', index=False)

    # output results
    result = {}
    result['Params'] = Params_full
    result['Stats'] = Evaluation_Results
    result['Prediction'] = LM_results2Excel
    result['alpha_wt'] = LocalAlpha_wt
    result['y_G_hat'] = y_G_hat
    result['bestLocalModel'] = bestLocalModel
    Output_GXGB_LocalModel = result

    return Output_GXGB_LocalModel


def predict_gxgb(DataPredict, CoordsPredict, Coords, Output_GXGB_LocalModel, alpha_wt=0.5, alpha_wt_type='varying',
                 path_save=False):
    """ Prediction in unseen data

    :param DataPredict: dataframe containing the values of the independent variables referring to the spatial units in which the prediction will take place.
    :param CoordsPredict: dataframe containing the coordinates of the spatial units in which the prediction will take place.
    :param Coords: dataframe of coordinates of all spatial units that the original GXGB model was trained
    :param Output_GXGB_LocalModel: the trained model that has been created through gxgb function
    :param alpha_wt: the value of alpha weight. It ranges from 0 to 1. Default=0.5
    :param alpha_wt_type: type of alpha_wt. Available methods: 'varying', fixed’. Default='varying'
    :param path_save: output folder. Default=False.
    :return: prediction in unseen data.

    """

    DistanceMatrix_Predict = pd.DataFrame(distance_matrix(CoordsPredict, Coords))  # Distance matrix nXn
    num_rows = len(DataPredict)
    index_min = np.argmin(DistanceMatrix_Predict, axis=1)
    Y_PRED = []
    Alpha_wtDF = pd.DataFrame(Output_GXGB_LocalModel['alpha_wt'])
    y_G_hat = pd.DataFrame(Output_GXGB_LocalModel['y_G_hat'])
    bestLocalModel = Output_GXGB_LocalModel['bestLocalModel']

    for i in range(num_rows):
        index = index_min[i]
        localModel = bestLocalModel[index]
        pred = pd.DataFrame(DataPredict.iloc[i, :])
        # predict y using the local model
        y_predLoc = localModel.predict(pred.transpose())
        # predict y using the global model
        yGhat = y_G_hat.iloc[index]
        # predict final
        if alpha_wt_type == 'fixed':
            Alpha_wt = alpha_wt
            print('Calculation with fixed alpha_wt')
            b = 1 - Alpha_wt  # controls the weight of local vs global model. [Alpha_wt] refers to the local model
            print('a= %.2f, b=%.2f' % (Alpha_wt, b))
        else:
            Alpha_wt = Alpha_wtDF.iloc[index]
            print('Calculation with varying alpha_wt')
            b = 1 - Alpha_wt  # controls the weight of local vs global model. [Alpha_wt] refers to the local model
            print('a= %.2f, b=%.2f' % (Alpha_wt.iloc[0], b.iloc[0]))
        # Combines local and global predictions
        Y_pred = Alpha_wt * y_predLoc + b * yGhat
        Y_PRED.append(Y_pred[0])

    Predict_results = pd.DataFrame(Y_PRED, columns=['Y_PRED'])
    if path_save is False:
        Predict_results.to_csv('Predict_results.csv', index=True)
    else:
        Predict_results.to_csv(path_save + 'Predict_results.csv', index=True)

    print("=============Predict Geographical-XGBoost ==========================")
    print(Predict_results)
    print('Results have been saved in xlsx format at the specified path')
    print("=====================================================================")

    Output_PredictGXGBoost = Predict_results

    return Output_PredictGXGBoost