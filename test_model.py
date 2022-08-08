import os 
import pickle
import timeit 
import pandas as pd

# def extract_msgdata(dir):
#     #subdirs = ['node1']#,'node2','node3', 'node4']
#     MAIN_DIR = '/'.join([os.getcwd().replace('\\','/'), 'smart detection logs'])
#     result = []
#     to_find_pattern = "Got msg data:"
#     msgid_string = "msgid"
#     data_coding_string="data coding:"

#     for files in os.scandir(f'{MAIN_DIR}/{dir}'):
#         current_file = files.name 
#         current_directory = dir 
#         current_file_full_path = MAIN_DIR + '/' + current_directory + '/' + current_file
#         print('current file',current_directory,current_file, current_file_full_path)
#         with open(current_file_full_path, 'r', encoding='utf-8') as f:
#             for data in f.readlines():
#                 if data.find(to_find_pattern) != -1:
#                     start = data.index(to_find_pattern)
#                     msgid_index = data.index(msgid_string)
#                     data_coding_index = data.index(data_coding_string)
#                     msgdata = data[(start+len(to_find_pattern)+1):(msgid_index-2)]
#                     msgid = data[(msgid_index+len(msgid_string)+1):(data_coding_index-2)].strip()
#                     data_coding = data[(data_coding_index+len(data_coding_string)+1):].strip()
#                     decoded_msg = unquote(msgdata,encoding='utf-8')
#                     trimmed_msgdata = re.sub(r'[\+\n\r]+', " ", decoded_msg)
#                     if msgdata != "%00":
#                         result.append([trimmed_msgdata,'normal',msgid,data_coding])
#                     else:
#                         print(f'trimmed:{trimmed_msgdata},ascii_trimmed:{ord(trimmed_msgdata)},original:{msgdata},msgid:{msgid},data_coding:{data_coding}')
#                     #print(result)


#     return result

def load_msgdata_csv(cur_node):
    cur_node_csv_filename = f'{cur_node}_msgdatas.csv'
    print(f'Reading csv file {cur_node_csv_filename}...')
    cur_node_df = pd.read_csv(cur_node_csv_filename, sep=',', encoding='utf-8')
    #print(cur_node_df.head(5))
    msgdata_list = (cur_node_df['msgdata']).tolist()
    #print(len(msgdata_list))
    return msgdata_list

def do_msgdata_prediction(msgdata_list, current_model):
    # test nb model 
    model_folder = '/'.join([os.getcwd().replace('\\', '/'), f'trained_models_{current_model}'])
    os.chdir(model_folder)
    all_models = os.listdir()
    total_msgdata_for_prediction = len(msgdata_list)
    to_return_result = []

    for model in all_models:
        print(f'Doing prediction using model: {model}')
        model_path = '/'.join([model_folder, model])
        nb_model = pickle.load(open(model_path, 'rb'))
        print(f'Doing prediction....')
        start = timeit.default_timer()
        prediction_result = nb_model.predict(msgdata_list)
        timetaken = timeit.default_timer() - start
        count_normal = 0
        for result in prediction_result:
            if result == 'normal':
                count_normal +=1 

        print(f'Sanity check... {len(msgdata_list) == len(prediction_result)}\n')
        print(f'Total testing result: {len(msgdata_list)}, \
                Prediction result: normal: {count_normal} creative: {len(msgdata_list)-count_normal}, \
                False positive rate:{((len(msgdata_list)-count_normal)/len(msgdata_list))}%, \
                Total took: {timetaken}second\n')

        to_return_result.append([model, count_normal, timetaken])
    
    return total_msgdata_for_prediction, to_return_result

if __name__ == "__main__": 
    current_model = "nb"
    output_analysis_file = f'test_model_prediction_{current_model}.txt'
    DEFAULT_WD = 'C:/Users/junia/Desktop/work'
    start_time = timeit.default_timer() 

    for i in range(4):
        cur_node = f'node{i+1}'
        print(f'Currently extracting data from {cur_node} logs...')
        msgdatas = load_msgdata_csv(cur_node)
        print(f'Finished extracting data from {cur_node}....')
        print(f'Starting to do msg prediction for {cur_node} msgdatas')
        total_records, prediction_results = do_msgdata_prediction(msgdatas, current_model)
        print(f'Finished doing msg prediction for {cur_node} msgdatas')

        os.chdir(DEFAULT_WD)

        with open(output_analysis_file, mode = 'a', encoding = 'utf-8') as f:
            f.write(f'Model Prediction Result Using {cur_node.upper()} MsgDatas on {current_model.upper()} model\n\n')
            for cur_model, normal_count, total_time in prediction_results:
                f.write(f'Current Model: {cur_model}\n')
                f.write(f'Predicted normal count: {normal_count}, Predicted creative count: {total_records-normal_count}\n')
                f.write(f'Total normal message in msgdatas: {total_records}\n')
                f.write(f'False positive rate: {((total_records-normal_count)/total_records)}%\n')
                f.write(f'Total time taken for prediction: {total_time}(s), est time taken to predict one message: {total_time/total_records}(s)\n\n')

        msgdatas = []

    total_time_taken = timeit.default_timer() - start_time
    tt_min =  total_time_taken // 60
    tt_sec = total_time_taken  % 60
    print(f'Finished everything... took {tt_min}min {tt_sec}(s)\n')
