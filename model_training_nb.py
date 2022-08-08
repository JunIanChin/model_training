from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import itertools
import pickle
import os 

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
        """
        This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`.
        """
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')

        print(cm)

        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)

        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fmt),
                    horizontalalignment="center",
                    color="white" if cm[i, j] > thresh else "black")

        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout()

def train_nb_model(split_ratio):

    training_csvs = []
    model_output_path = '/'.join([os.getcwd().replace('\\','/'),'trained_models_nb',''])
    cf_output_path = '/'.join([os.getcwd().replace('\\','/'), 'confusion_matrix', ''])
    output_text_file_path = '/'.join([os.getcwd().replace('\\', '/'), ''])
    cf_matrix_to_file_list = []
    cf_report_to_file_list = []
    accuracy_list = []
    print(model_output_path)

    all_csv_files = os.listdir(os.getcwd())
    training_csvs = [csv_file for csv_file in all_csv_files if csv_file.startswith('training_set') and csv_file.endswith('.csv')]

    for train_csv in training_csvs:
        train_df = pd.read_csv(train_csv, sep=',', encoding='utf-8')
        print(train_df.info())
        X = train_df['msgdata']
        y = train_df['nature']
        model_output_name = f'{model_output_path}{train_csv[:-4]}_{split_ratio}'
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split_ratio, stratify=y, random_state=1000)
        tfidf=TfidfVectorizer()

        X_train_tfidf_vect = tfidf.fit_transform(X_train)
        print(X_train_tfidf_vect)
        print(X_train_tfidf_vect.shape)
        text_mnb=Pipeline([('tfidf',TfidfVectorizer()),('mnb',MultinomialNB())])
        text_mnb.fit(X_train,y_train)
        Pipeline(steps=[('tfidf',TfidfVectorizer()),('mnb',MultinomialNB())])
        y_preds_mnb= text_mnb.predict(X_test)
        print(y_preds_mnb)
        print(text_mnb.score(X_test,y_test))
        accuracy_list.append(text_mnb.score(X_test, y_test))
        pickle.dump(text_mnb, open(f'{model_output_name}.sav', 'wb'))

        print('Confusion matrix')
        cnf_matrix = confusion_matrix(y_test, y_preds_mnb)
        plt.figure()
        plot_confusion_matrix(cnf_matrix, classes=['Creative','Normal'], normalize=False,
                            title='Confusion matrix')
        plt.savefig(f'{cf_output_path}{model_output_name[len(model_output_path):]}_nb_cf.png')
        cf_matrix = confusion_matrix(y_test,y_preds_mnb)
        cf_report = classification_report(y_test,y_preds_mnb)
        cf_matrix_to_file_list.append(cf_matrix)
        cf_report_to_file_list.append(cf_report)
        print(cf_matrix)
        print(cf_report)

        test_msg = ["RM0 Your Lazada return #333487303178820 has been cancelled by you or as per Lazada policy. Visit ""My Account"" on the Lazada app or website for more information.",
                    "RM0 My§ejæhtêrÂ: NRIç/PA§S xxxxxxxx5401, k¢putµsaÑ ujìáÑ aÑÐÁ ada1ah ñ¢gatìf. SiÍÂ $émÂk hÅlÆmân Prof!Í Mÿ§¢jÂh÷8rÆ añÐa uÑtuk méï¡ha± máklÜma± ÷¢rkìÑi."]

        print('Prediction',text_mnb.predict(test_msg))

    with open(f'{output_text_file_path}ratio_{split_ratio}_nb.txt', mode='w') as f:
        for (train_file, matrix, cf_report, accuracy) in zip(training_csvs, cf_matrix_to_file_list, cf_report_to_file_list, accuracy_list):
            f.write(f'File: {train_file}\nMatrix:\n{matrix}\nAccuracy: {accuracy}\nClassification_Report:\n{cf_report}\n')

    f.close()

if __name__ == "__main__":
    split_ratios = [0.2, 0.3]
    for ratio in split_ratios:
        train_nb_model(ratio)