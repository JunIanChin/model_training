import matplotlib.pyplot as plt 
import numpy as np
import re 

ml_model = 'nb'
model_training_result_filelist = [f'ratio_0.2_{ml_model}.txt', f'ratio_0.3_{ml_model}.txt']
check_file_word = re.compile('^File: training_set_')
check_accuracy_word = re.compile('^Accuracy:')
for file in model_training_result_filelist:
    dataset_size = []
    accuracy = []
    with open(file, mode='r', encoding='utf-8') as f:
        for data in f.readlines():
            if (check_file_word.match(data) is not None): 
                dataset_size.append(int(data[check_file_word.match(data).end():-5]))
            elif (check_accuracy_word.match(data) is not None):
                accuracy.append(float(data[check_accuracy_word.match(data).end()+1:].strip()))
            else:
                continue 
        f.close()
    dataset_size = np.array(dataset_size)
    accuracy = np.array(accuracy)

    plt.xlabel('Dataset Size')
    plt.ylabel('Accuracy')
    plt.title(f'Dataset size vs Accuracy ({file[:-4]})')
    plt.xticks(dataset_size)
    #plt.yticks(np.round(accuracy, decimals=5))
    plt.grid(True)
    plt.plot(dataset_size, accuracy)
    plt.savefig(f'{file[:-4]}_{dataset_size[0]}_{dataset_size[-1]}_{ml_model}.png')
    plt.show()
    

# dataset_size = np.array([4000, 5000, 6000, 7000, 8000])
# accuracy = np.array([0.9225, 0.916, 0.9241666666666667, 0.9385714285714286, 0.9375])

# #dataset_size = np.array([])
# #accuracy = np.array([0.9133333333333333, 0.9133333333333333, 0.9205555555555556, 0.9361904761904762, 0.93625])

# plt.xlabel('Dataset Size')
# plt.ylabel('Accuracy')
# plt.title('Dataset size vs Accuracy (0.2)')
# plt.xticks(dataset_size)
# plt.grid(True)
# plt.plot(dataset_size, accuracy)
# plt.show()