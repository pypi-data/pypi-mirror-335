from .print_fonts import PrintFonts

class DataScience():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = f"""
        ## DATA SCIENCE HELP
        ! Here you can find everything I've studied about Data Science
        
        # Imports:
        -imports_dataframe(): Most used imports to work with DataFrames  
        -imports_machinelearning(): Most used imports for Machine Learning  
        
        # Methods:
        -eda(): Show the step-by-step process for data visualization and plots  
        -operations(): Show the most common DataFrame operations and filters  
        -machinelearning(): Show every machine-learning model
        """
        pf.format(text)


    def imports_dataframe(self):
        """Write imports for dataframes"""
        pf = PrintFonts()

        text = f"""
        ## MOST USED IMPORTS FOR DATAFRAMES
        
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        """
        pf.format(text)


    def import_machinelearning(self):
        """Write imports from machine learning"""
        pf = PrintFonts()

        text = """  
        ## MOST USED IMPORTS FOR MACHINE LEARNING
        
        # Supervised Models - Regressors 
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor  
        from sklearn.ensemble import VotingRegressor
        from sklearn.ensemble import GradientBoostingRegressor
        
        # Supervised Models - Classifiers 
        from sklearn.tree import DecisionTreeClassifier  
        from sklearn.neighbors import KNeighborsClassifier  
        from sklearn.ensemble import VotingClassifier 
        from sklearn.ensemble import AdaBoostClassifier  
        
        # Train / Test and Score  
        from sklearn.model_selection import train_test_split  
        from sklearn.metrics import accuracy_score  
        from sklearn.metrics import mean_squared_error  
        from sklearn.metrics import r2_score  
        from sklearn.metrics import confusion_matrix  
        
        # UnSupervised Models  
        from sklearn.cluster import KMeans  
        from sklearn.model_selection import GridSearchCV  
        from sklearn.model_selection import KFold  
        from sklearn.metrics import silhouette_samples, silhouette_score  
        from sklearn.tree import plot_tree  
        """
        pf.format(text)


    def eda(self):
        """Write about EDA"""
        pf = PrintFonts()

        # Load df - show info - create plots
        text = """  
        ## EXPLORATORY DATA ANALYSIS
        ! EDA is the technique to visualize data and gain insights, using data exploration, plots and statistics.  
        ! Use pandas, matplotlib.pyplot and seaborn  

        # Load file csv as DataFrame  
        df = pd.read_csv('path.csv')  

        # Visualize DataFrame info  
        print(df.info())  
        print(df.describe())  

        # Show na values of each column  
        for column in df.columns:  
            print(df[column].isna().sum())  

        # (optional) Drop na values  
        df = df.dropna()  

        # (optional) Fill na values with mean (single numerical column)  
        df['column'] = df['column'].fillna(df['column'].mean())  

        # CREATE PLOTS  

        # Scatterplot for outliers  
        plt.figure(figsize=(8,4))  
        for column in df.columns:  
            sns.scatterplot(x='column', y=column, data=df)  
        plt.show()  

        # Lineplot for continuous numbers  
        plt.figure(figsize=(8,4))  
        for column in df.columns:  
            sns.lineplot(x='column', y=column, data=df)  
        plt.show()  

        # Regplot for trendlines  
        plt.figure(figsize=(8,4))  
        for column in df.columns:  
            sns.regplot(x='column', y=column, data=df, ci=None)  
        plt.show()  
        """
        pf.format(text)


    def operations(self):
        """Write about DataFrame operations"""
        pf = PrintFonts()

        text = """  
        ## DATAFRAME OPERATIONS
        ! Here you can see some common df operations like add new row or filters using pandas  

        # Add new row  
        df.loc[len(df)] = {'column1': value1, 'column2': value2, ...}  

        # Change a field in a specific column of a specific row  
        df.loc[df['column'] == value_filter, 'column_to_update'] = value_to_update  

        # Filter all the values of a condition  
        df[df['column'] == value_filter]  

        # Group by column(s)  
        df.groupby(['column'])  

        # Do operations on a specific column after a filter  
        df[df['column'] == value_filter]['column2'].mean()  

        # Get the first row of a value of a column in a filter  
        df[df['column'] == value_filter]['column2'].iloc[0]  
        """
        pf.format(text)


    def machinelearning(self):
        """Write about Machine Learning"""
        pf = PrintFonts()

        text = """  
        ## MACHINE LEARNING
        ! Here you can see a quick-guide to each Machine Learning model using Scikit-learn  

        ## SETTING PARAMS

        # Seed is a number to set random_state to a fixed value  
        SEED = 42  
        # X are feature(s) that to use, y is the feature we want to predict  
        X = df[['column1', 'column2', ...]].values  
        y = df['column_to_forecast']  

        # Split the dataset on train and test  
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=SEED)  

        ## SUPERVISED LEARNING for REGRESSION

        # Instantiate Regressors Modules  
        lr = LinearRegression()
        rf = RandomForestRegressor(n_estimators=100, random_state=SEED)
        gr = GradientBoostingRegressor()
        
        # Create a list of regressors  
        estimators = [('lr', lr), ('rf', rf), ('gr', gr)]  
        
        # Create the VotingRegressor with the list  
        vr = VotingRegressor(estimators=estimators)  
        
        # Define the list of regressors  
        regressors = [('Linear Regression', lr), ('Random Forest Regressor', rf), ('Voting Regressor', vr), ('Gradient Boosting Regressor', gr)]  
        
        # Iterate over the pre-defined list of regressors  
        results = []  
        for reg_name, reg in regressors:
            # Fit clf to the training set  
            reg.fit(X_train, y_train) 
        
            # Predict y_pred  
            y_pred = reg.predict(X_test)  
            
            # Calculate mse and r2 and append result  
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            results.append((reg_name, mse))  
            
            # Evaluate clf's mse on the test set  
            print('{:s} Mse: {:.3f} -- R2: {:.2f}'.format(reg_name, mse, r2))  
            print(f'Showing {reg_name} graph: ')  

            # Create a scatter plot with dt predictions and real values  
            plt.figure(figsize=(8, 4))  
            sns.scatterplot(x=df['feature'], y=predicted_labels, label='Predictions', alpha=0.3, s=100)  
            sns.scatterplot(x=df['feature'], y=df['feature to forecast'], label='Real', alpha=1)  
            plt.xlabel('feature')  
            plt.ylabel('feature') 
            plt.show()  

        ## SUPERVISED LEARNING for CLASSIFICATION (0 or 1)

        # Instantiate Classifiers Modules  
        lr = LogisticRegression(random_state=SEED)  
        knn = KNeighborsClassifier(n_neighbors=27)  
        dt = DecisionTreeClassifier(min_samples_leaf=0.13, random_state=SEED)  
        ada = AdaBoostClassifier(estimator=dt, n_estimators=100, random_state=SEED)  

        # Create a list of estimators  
        estimators = [('lr', lr), ('knn', knn), ('dt', dt), ('ada', ada)]  

        # Create the VotingClassifier with the list  
        vc = VotingClassifier(estimators=estimators)  

        # Define the list classifiers  
        classifiers = [('Logistic Regression', lr), ('K Nearest Neighbours', knn), ('Classification Tree', dt), ('Voting Classifier', vc), ('Ada Boost', ada)]  

        # Iterate over the pre-defined list of classifiers  
        results = []  
        for clf_name, clf in classifiers:  
            # Fit clf to the training set  
            clf.fit(X_train, y_train)  

            # Predict y_pred  
            y_pred = clf.predict(X_test)  

            # Calculate accuracy and append result  
            accuracy = accuracy_score(y_test, y_pred)  
            results.append((clf_name, accuracy))  

            # Evaluate clf's accuracy on the test set  
            print('{:s} Accuracy: {:.3f} %'.format(clf_name, accuracy))  

        ## USING KFOLD

        # Define the number of folds  
        kfold = KFold(n_splits=5, shuffle=True, random_state=42)  
        model = LogisticRegression(random_state=SEED)

        # Evaluate using cross-validation  
        accuracies = []  
        for train_index, test_index in kfold.split(X):  
            X_train, X_test = X[train_index], X[test_index]  
            y_train, y_test = y[train_index], y[test_index]  
            model.fit(X_train, y_train)  
            y_pred = model.predict(X_test)  
            accuracy = round(accuracy_score(y_test, y_pred), 2)  
            accuracies.append(accuracy)  

        # Print the average accuracy across folds  
        print('Average accuracy with fixed dimension:', round(np.mean(accuracies), 2))  

        # Create graph with different training set dimensions for both train and test accuracies  
        list_test_dimensions = []  
        list_test_accuracies = []  
        list_train_dimensions = []  
        list_train_accuracies = []  

        for i in range(1, 10):  
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=i/10, random_state=42)  
            model = LogisticRegression()  
            model.fit(X_train, y_train)  
            y_pred = model.predict(X_test)  
            accuracy = round(accuracy_score(y_test, y_pred), 2)  
            list_test_dimensions.append(len(X_test))  
            list_test_accuracies.append(accuracy)  
            print(f'Using train set with dimension {len(X_test)} --- Accuracy is: {accuracy}')  
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=i/10, random_state=42)  
            model = LogisticRegression()  
            model.fit(X_train, y_train)  
            y_pred = model.predict(X_train)  
            accuracy = round(accuracy_score(y_train, y_pred), 2)  
            list_train_dimensions.append(len(X_test))  
            list_train_accuracies.append(accuracy)  
            print(f'Using test set with dimension {len(X_test)} --- Accuracy is: {accuracy}')  

        print('Using either test and train sets to make predictions. The following graph shows how the Accuracy varies changing the sets dimension. Test set is what should be used to predict!')  
        plt.figure(figsize=(8, 4))  
        plt.plot(list_test_dimensions, list_test_accuracies, label='Test set')  
        plt.xlabel('Test & Train set Dimension')  
        plt.ylabel('Accuracy')  
        plt.legend()  
        plt.show()  

        ## UNSUPERVISED MODEL

        # Select clusters and use KMeans  
        n_clusters = 'Select number of clusters'  
        model = KMeans(n_clusters=n_clusters, n_init=10)  
        labels = model.fit_predict(X)  
        unsdf = pd.DataFrame({'labels': labels, 'varieties': df['feature']})  
        ct = pd.crosstab(unsdf['labels'], unsdf['varieties'])  
        """
        pf.format(text)

