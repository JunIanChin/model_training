import os 
from urllib.parse import unquote
import pandas as pd 
import re 

def logs_to_csv():
    subdirs = ['node1','node2','node3', 'node4']
    MAIN_DIR = os.getcwd().replace('\\','/')
    MAIN_DIR += "/smart detection logs"
    result = []
    to_find_pattern = "Got msg data:"
    msgid_string = "msgid"
    data_coding_string="data coding:"
    flagged_word_count_string = "Flagged words count:"

    for dir in subdirs:
        for files in os.scandir(f'{MAIN_DIR}/{dir}'):
            current_file = files.name 
            current_directory = dir 
            current_file_full_path = MAIN_DIR + '/' + current_directory + '/' + current_file
            print('current file',current_directory,current_file, current_file_full_path)
            with open(current_file_full_path, 'r', encoding='utf-8') as f:
                for data in f.readlines():
                    if data.find(flagged_word_count_string) != -1:
                        flagged_word_count = data[(data.index(flagged_word_count_string)+len(flagged_word_count_string))+1:].strip()
                        if flagged_word_count == '0':
                            #print(trimmed_msgdata,msgid,data_coding)
                            if msgdata != "%00":
                                result.append([trimmed_msgdata,'normal',msgid,data_coding])

                    if data.find(to_find_pattern) != -1:
                        start = data.index(to_find_pattern)
                        msgid_index = data.index(msgid_string)
                        data_coding_index = data.index(data_coding_string)
                        msgdata = data[(start+len(to_find_pattern)+1):(msgid_index-2)]
                        msgid = data[(msgid_index+len(msgid_string)+1):(data_coding_index-2)].strip()
                        data_coding = data[(data_coding_index+len(data_coding_string)+1):].strip()
                        decoded_msg = unquote(msgdata,encoding='utf-8')
                        trimmed_msgdata = re.sub(r'[\+\n\r]+', " ", decoded_msg)
                        if msgdata != "%00":
                            pass 
                            #result.append([trimmed_msgdata,'normal',msgid,data_coding])
                        else:
                            print(f'trimmed:{trimmed_msgdata},ascii_trimmed:{ord(trimmed_msgdata)},original:{msgdata},msgid:{msgid},data_coding:{data_coding}')
                        #print(result)

        #write to csv file , reset list after 
        msgdatas = pd.DataFrame(result, columns= ['msgdata','nature','msgid','data_coding'])
        print(f'Writing to file {current_directory}_msgdatas.csv....')
        msgdatas.to_csv(f'{current_directory}_msgdatas.csv', na_rep="", index=False, sep=',',encoding='utf-8')
        print(len(result), result[0], result[-1])
        print(f'Successfully written to file {current_directory}_msgdatas.csv...Cleaning up data')
        result = []


if __name__ == "__main__": 
    logs_to_csv()
