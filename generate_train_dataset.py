import pandas as pd 
import itertools
from random import sample, shuffle

def main(total_csv_size, increment_size, total_iteration):
    normal_msgdata_csv_list = ['node1_msgdatas.csv', 'node2_msgdatas.csv', 'node3_msgdatas.csv', 'node4_msgdatas.csv']
    creative_msg_csv = "generated_creative_msg_100000.csv"
    cm_csv_df = pd.read_csv(creative_msg_csv, sep= ",", encoding= "utf-8")

    for i in range(total_iteration):
        num_msg_extract_per_nature = (total_csv_size+(i*increment_size))//2 
        output_csv = f"training_set_{total_csv_size+(i*increment_size)}.csv"
        print(f"Process {i+1}/{total_iteration} reading csv....")
        last_file_extra = (num_msg_extract_per_nature % len(normal_msgdata_csv_list))
        nm_csv_msgdata = []
        for normal_msg_csv_file in normal_msgdata_csv_list:
            curr_df = pd.read_csv(normal_msg_csv_file, sep=',', encoding='utf-8')
            if normal_msg_csv_file == normal_msgdata_csv_list[-1]:
                nm_csv_msgdata = list(itertools.chain(nm_csv_msgdata, sample(curr_df['msgdata'].tolist(), (num_msg_extract_per_nature//(len(normal_msgdata_csv_list))) +last_file_extra)))
            else:
               nm_csv_msgdata = list(itertools.chain(nm_csv_msgdata, sample(curr_df['msgdata'].tolist(), (num_msg_extract_per_nature//len(normal_msgdata_csv_list)))))
        print("Done reading csv...")

        cm_csv_msgdata = sample(cm_csv_df['msgdata'].tolist(), num_msg_extract_per_nature)
        cm_csv_nature = sample(cm_csv_df['nature'].tolist(), num_msg_extract_per_nature)
        nm_csv_nature = ['normal'] * len(nm_csv_msgdata)

        if (len(cm_csv_msgdata) < (num_msg_extract_per_nature)):
            print(f'{creative_msg_csv} has only {len(cm_csv_msgdata)} rows of data')

        concat_msgdata_list = list(itertools.chain(cm_csv_msgdata, nm_csv_msgdata))
        concat_nature_list = list(itertools.chain(cm_csv_nature, nm_csv_nature))
        concat_result = [[x,y] for x,y in zip(concat_msgdata_list, concat_nature_list)]
        shuffle(concat_result)
        print(len(concat_result), concat_result[0])
        print(len(concat_msgdata_list), len(concat_nature_list))
        print(len(cm_csv_msgdata), len(cm_csv_nature), len(nm_csv_msgdata), len(nm_csv_nature), "matched len" if len(cm_csv_msgdata) == len(nm_csv_msgdata) else "len mismatched")

        combined_msgdata_df = pd.DataFrame(concat_result, columns=['msgdata', 'nature'])
        print(f'Writing to file {output_csv}....')
        combined_msgdata_df.to_csv(output_csv, na_rep="", index=False, sep=',',encoding='utf-8')
        print(f'Successfully written to file {output_csv}..')

if __name__ == "__main__":
    main(1000, 1000, 100)