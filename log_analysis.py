from concurrent.futures import ProcessPoolExecutor
from email import header
from gzip import READ
import multiprocessing
from classes.file_controller import FileController as fc 
from classes.config_controller import ConfigController as cc
import pandas as pd 
import os 
from urllib.parse import unquote
import re 
import promptlib
from datetime import datetime 
import time 
import logging 

CURRENT_DATETIME = datetime.today().strftime("%Y-%m-%d")
CURRENT_CWD = os.getcwd().replace('\\','/')
OUTPUT_CSV_PATH = '/'.join([CURRENT_CWD, f'log_to_csv/{CURRENT_DATETIME}/'])
OUTPUT_QUARANTINE_DC3_TRUE_CSV = '/'.join([OUTPUT_CSV_PATH, f'quarantine_dc3_true_{CURRENT_DATETIME}.csv'])
OUTPUT_QUARANTINE_DC3_FALSE_CSV = '/'.join([OUTPUT_CSV_PATH, f'quarantine_dc3_false_{CURRENT_DATETIME}.csv'])
OUTPUT_QUARANTINE_TRUE_CSV = '/'.join([OUTPUT_CSV_PATH, f'quarantine_true_{CURRENT_DATETIME}.csv'])
OUTPUT_QUARANTINE_FALSE_CSV = '/'.join([OUTPUT_CSV_PATH, f'quarantine_false_{CURRENT_DATETIME}.csv'])
OUTPUT_CSV_FILENAME = 'combined_data.csv'
OUTPUT_CSV_FULL_PATH = ''.join([OUTPUT_CSV_PATH, OUTPUT_CSV_FILENAME]).replace('//','/')
CONFIG_FILE_PATH  = '/'.join([CURRENT_CWD, 'cfg/training_cfg.ini'])
MSGDATA_STR = 'Msgdata'
DATA_CODING_STR = 'data coding'
RESULT_STR = 'result'
MSGID_STR = 'msgid'
CPU_COUNT = multiprocessing.cpu_count()-2
CSV_HEADER = ['msgdata', 'data_coding', 'result', 'msgid']
READ_DTYPE = {'msgdata': 'unicode', 'data_coding': 'str', 'result': 'str', 'msgid': 'str'}
LOG_FILE = ''.join([CURRENT_CWD, '/', CURRENT_DATETIME, '_logger.log'])
LOG_FORMAT = "%(asctime)s :: %(levelname)s :: %(message)s"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, encoding='utf-8', format=LOG_FORMAT, handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

def parseData(data:str, logs):
    msgdata = None 
    data_coding = None 
    result = None 
    msgid = None

    msgdata_start_idx = data.find(MSGDATA_STR) + len(MSGDATA_STR) +1
    data_coding_start_idx = data.find(DATA_CODING_STR) + len(DATA_CODING_STR) +1
    result_start_idx = data.find(RESULT_STR) + len(RESULT_STR)+1
    msgid_start_idx = data.find(MSGID_STR) + len(MSGID_STR) +1
    msgdata_end_idx = data.find(',', msgdata_start_idx, msgid_start_idx)
    data_coding_end_idx = data.find(',', data_coding_start_idx, result_start_idx)

    if (msgdata_end_idx == -1 or data_coding_end_idx == -1):
        return 

    msgdata = data[msgdata_start_idx:msgdata_end_idx].strip()
    decoded_msg = unquote(msgdata,encoding='utf-8')
    trimmed_msgdata = re.sub(r'[\+\n\r\;]+', " ", decoded_msg)
    data_coding = data[data_coding_start_idx:data_coding_end_idx].strip()
    msgid = data[msgid_start_idx: data_coding_start_idx-len(DATA_CODING_STR)-1].strip().strip(',')
    result=data[result_start_idx:].strip()

    # if trimmed_msgdata[:len('SMSOveride: RequestID')] == 'SMSOveride: RequestID':
    #     print(msgdata)
    # if trimmed_msgdata[:12] == 'REG-RESP?v=3':
    #     print(trimmed_msgdata)
    
    # if trimmed_msgdata[:len('https://secure.booking.com/apps.html?action=confirmation')] == 'https://secure.booking.com/apps.html?action=confirmation':
    #     print(trimmed_msgdata)

    logs.append([trimmed_msgdata,data_coding,result,msgid])
    return 

def prompt_user_log_directory():
    log_dir = promptlib.Files().dir()
    return log_dir 

def process_file(file:str, count):
    logs = []
    print('Im process:', count)
    OUTPUT_CSV_PATH_file = ''.join([OUTPUT_CSV_PATH, f'{file[file.find(".log")+5:]}', str(file[69:95]).replace('/','_').replace('.log', '.csv')])
    logger.debug(f'Processing current file:{file}')
    with open(file, mode='r', encoding='utf-8') as f:   
        for data in f.readlines():
            parseData(data, logs)

        #print(len(logs))
        if len(logs) > 0:
            #print(logs[0])
            msgdatas = pd.DataFrame(data=logs)
            logger.debug(f'Writing to file {OUTPUT_CSV_PATH_file}')
            msgdatas.to_csv(f'{OUTPUT_CSV_PATH_file}', mode='w', header=None, na_rep="", index=False, sep=',',encoding='utf-8')              
            logger.debug(f'Successfully written to file {OUTPUT_CSV_PATH_file}')

    return 

def log_to_csv_multi():
    LOG_PATH = prompt_user_log_directory()
    logs_data = fc(LOG_PATH)

    start = time.perf_counter()
    try:
        with ProcessPoolExecutor(max_workers=CPU_COUNT) as executor:
            count = 0
            for file in logs_data.available_logs:
                executor.submit(process_file, file, count)
                count +=1
    except:
        logging.error('Something went wrong while converting log file to csv file')
    end = time.perf_counter()
    logger.info(f'Log_to_csv: time elapsed: {(end-start) // 60:.0f} minute {((end-start) % 60):.2f} second(s)')
    return 

def log_to_csv_single():
    LOG_PATH = prompt_user_log_directory()
    logs_data = fc(LOG_PATH)

    start = time.perf_counter()
    try:
        for file in logs_data.available_logs:
            process_file(file)
    except:
        logging.error('Something went wrong while converting log file to csv file')
    end = time.perf_counter()
    logger.info(f'Log_to_csv: time elapsed: {(end-start) // 60:.0f} minute {((end-start) % 60):.2f} second(s)')
    return 

def combine_csv():
    all_logs = fc(OUTPUT_CSV_PATH)
    start_combine = time.perf_counter()
    try:
        for i in range(len(all_logs.available_logs)):
            current_file = str(all_logs.available_logs[i]).replace('//', '/') # fullfile path
            if current_file[-4:] != '.csv' or current_file == OUTPUT_CSV_FULL_PATH:
                continue 
            logger.debug(f'Combining current file: {current_file}')
            current_df = pd.read_csv(current_file, sep=',', engine="c", dtype=READ_DTYPE, names=CSV_HEADER, on_bad_lines='skip', encoding='utf-8').drop_duplicates(subset=['msgdata']).dropna()
            pd.DataFrame(data=current_df).to_csv(OUTPUT_CSV_FULL_PATH, mode='a', sep=",", na_rep="", index=False, encoding='utf-8')
        
    except: 
        logging.error('Something went wrong while combining csv files')
    end_combine = time.perf_counter()
    combine_time_taken = end_combine-start_combine
    logger.info(f'[Combine csv]: time elapsed: {(combine_time_taken) // 60:.0f} minute {((combine_time_taken) % 60):.2f} second(s)')

    return  

def data_coding_csv_split():
    split_start = time.perf_counter()
    logger.debug(f'Spltting based on data_coding, filepath:{OUTPUT_CSV_FULL_PATH}')
    pd_df = pd.read_csv(OUTPUT_CSV_FULL_PATH, engine="c", sep=",", dtype=READ_DTYPE, names=CSV_HEADER, chunksize=300000, on_bad_lines="skip", encoding="utf-8")
    #false_msg = pd_df[pd_df['result'] == 'False']
    for chunks_df in pd_df:
        chunks_df = chunks_df.dropna()
        try:
            msg_dc3_true = chunks_df[(chunks_df['data_coding'] == '3') & (chunks_df['result'] == 'True')]
            msg_dc3_false = chunks_df[(chunks_df['data_coding'] == '3') & (chunks_df['result'] == 'False')]
            msg_others_true = chunks_df[(chunks_df['data_coding'] != '3') & (chunks_df['result'] == 'True')]
            msg_others_false = chunks_df[(chunks_df['data_coding'] != '3') & (chunks_df['result'] == 'False')]
            msg_dc3_true.to_csv(OUTPUT_QUARANTINE_DC3_TRUE_CSV, header=None, mode='a', sep=',', na_rep="", index=False, encoding='utf-8')
            msg_dc3_false.to_csv(OUTPUT_QUARANTINE_DC3_FALSE_CSV, header=None, mode='a', sep=',', na_rep="", index=False, encoding='utf-8')
            msg_others_true.to_csv(OUTPUT_QUARANTINE_TRUE_CSV, header=None, mode='a', sep=',', na_rep="", index=False, encoding='utf-8')
            msg_others_false.to_csv(OUTPUT_QUARANTINE_FALSE_CSV, header=None, mode='a', sep=',', na_rep="", index=False, encoding='utf-8')
        except:
            logger.error('Something went wrong reading dataframe chunks')

    logger.debug(f'Successfully split csv based on data_coding')
    split_end = time.perf_counter() 
    split_time_taken = split_end - split_start
    logger.info(f'[Split csv]: time elapsed: {(split_time_taken) // 60:.0f} minute {((split_time_taken) % 60):.2f} second(s)')
    return 

def dir_checker():
    if not os.path.isdir(OUTPUT_CSV_PATH):
        os.mkdir(OUTPUT_CSV_PATH)
        logger.debug(f'{OUTPUT_CSV_PATH} was created.')
    return 

def preprocess_log(is_multi):
    dir_checker()
    start = time.perf_counter()
    try:
        if is_multi: log_to_csv_multi()
        else: log_to_csv_single()
        combine_csv()
        data_coding_csv_split()
    except:
        logging.error('Ooops something went wrong..')
    end = time.perf_counter() 
    logger.info(f'Preprocessing: time elapsed: {(end-start) // 60:.0f} minute {((end-start) % 60):.2f} second(s)')

if __name__ == '__main__':
    #data_coding_csv_split()
    preprocess_log(True)
    # test = cc(CONFIG_FILE_PATH)
    # print(test)
    #print('Writing quarantine file')
    #csv_analysis() 