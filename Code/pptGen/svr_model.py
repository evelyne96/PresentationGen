from sklearn.svm import SVR


def regressor_model(features, target):
    regressor=SVR(kernel = 'rbf', C= 1e3, gamma= 0.1)
    regressor.fit(features, target)

    return regressor

def tune_svm_parameters(features, target):
        # parameters gamma and C of the Radial Basis Function (RBF) kernel SVM.
        # Intuitively, the gamma parameter defines how far the influence of a single training example
        #  reaches, with low values meaning ‘far’ and high values meaning ‘close’. The gamma parameters 
        #  can be seen as the inverse of the radius of influence of samples selected by the model as support vectors.
        # The C parameter trades off misclassification of training examples against simplicity of the decision surface. 
        # A low C makes the decision surface smooth, while a high C aims at classifying all training examples correctly 
        # by giving the model freedom to select more samples as support vectors.

        regressor_model = regressor_model(features, target)

        C_range = numpy.logspace(-3, 10, 13)
        gamma_range = numpy.logspace(-9, 3, 12)
        param_grid = dict(gamma=gamma_range, C=C_range)

        cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)

        grid = GridSearchCV(regressor_model, param_grid=param_grid, cv=cv, return_train_score=True, verbose=10)
        # grid = GridSearchCV(SVC(kernel='linear'), param_grid=param_grid, cv=cv, return_train_score=True)
        grid.fit(features, target)
        print("best params ", grid.best_params_, "best score ", grid.best_score_)
        return grid.best_params_, grid.best_score_


