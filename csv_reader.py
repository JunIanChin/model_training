import pandas as pd 
from smart_detection.smart_detection import test_smart_deteciton

def main():
    csv_files = ['node1_msgdatas.csv','node2_msgdatas.csv','node3_msgdatas.csv','node4_msgdatas.csv']
    for csvfiles in csv_files:
        msgdata_df = pd.read_csv(csvfiles,encoding='utf-8')
        msgdata_col = msgdata_df.loc[msgdata_df['data_coding'] != 3]
        msgdata_df_to_list = msgdata_col['msgdata'].tolist()
        msgid_df_to_list = msgdata_col['msgid'].tolist()
        #print(type(msgdata_df_to_list), len(msgdata_df_to_list), len(msgid_df_to_list))
        test_smart_deteciton(msgdata_df_to_list,msgid_df_to_list ,csvfiles)
        print(msgdata_df[msgdata_df.isnull().any(axis=1)])

if __name__ == "__main__":
    main()