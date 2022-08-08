from random import choice, sample
import json 
import sys 
import re 
import pandas as pd
from itertools import chain

#https://www.rapidtables.com/code/text/ascii-table.html 
#turn normal msg into creative messages 

# 33-47 
# 58-64 
# 91-96
# 123-126 

# This is a sample message 
# Th1s 1s @ s@mp13 m3ss@g3 
# a->@ , l/i -> 1!
# t^is is ; s:m@le m:}sag?


def is_numeric(char):
    if 48 <= ord(char) <= 57:
        return True 
    return False

def is_lowercase(char):
    if  97 <= ord(char) <= 122:
        return True    
    return False 

def is_uppercase(char): 
    if  65 <= ord(char) <= 90:
        return True    
    return False

def word_sub(word, mapping_list):
    result_sub_word = ""
    for char in word:
        to_sub = choice([True, False])
        #print(to_sub, char)
        if to_sub:
            if is_numeric(char):
                pass 
            elif is_lowercase(char):
                sub_chars = mapping_list[ord(char)-97]
                if len(sub_chars) > 0:
                    subbed_char = choice(sub_chars)
                    #print(subbed_char,chr(subbed_char))
                    result_sub_word += chr(subbed_char)
                else:
                    result_sub_word += char
                continue
            elif is_uppercase(char):
                sub_chars = mapping_list[ord(char)-65]
                if len(sub_chars) > 0:
                    subbed_char = choice(sub_chars)
                    #print(subbed_char,chr(subbed_char))
                    result_sub_word += chr(subbed_char)
                else:
                    result_sub_word += char
                continue
            else:
                pass 
            result_sub_word += char
        else:
            result_sub_word += char
    
    return result_sub_word
  
def hardcode_map_char_to_creative():
    char_to_creative = [[]] * 26 

    f = open('hardcoded_alpha_mapping.json')
    data = json.load(f)

    for i in range(26):
       char_to_creative[i] = data[str(chr(i+97))]

    f.close() 

    return char_to_creative

def get_msg_from_csv(num, csv_file_list):
    result_list = []
    
    for csv_file in csv_file_list:
        print(f'Extracting data from {csv_file}')
        msgdata_df = pd.read_csv(csv_file, sep = ",", encoding="utf-8")
        tmp_list = sample(msgdata_df['msgdata'].tolist(), num)
        result_list = list(chain(result_list, tmp_list))

    return result_list
    
# def pseudo_num_generator(start,end):
#     #inclusive
#     return random.randint(start,end)

# def get_random_char():
#     # based on known ascii value for non caps and caps 
#     # A = 65 , Z = 90 ,a = 97 , z = 122 
#     pseudo_generated_char_1 =  pseudo_num_generator(65,90)
#     pseudo_generated_char_2 =  pseudo_num_generator(97,122)

#     return random.choice([pseudo_generated_char_1, pseudo_generated_char_2]) 

def main(num_msg_to_extract_per_csv, increment_size_per_csv, total_sample_to_generate): 

    # normal_msgs = ["RM0.00 MyFundAction : Betul ke tahun ni raya dua kali? Klik untuk baca cerita penuh https://ezy.la/Qurban_Daftar",
    #              "RM0 [Lalamove] Hello! Lalamove is handling your delivery (Order ID: 147296311073). Track it here: https://sg-d.lalamove.com/0bOSri",
    #              "RM0 Your Nike verification code is: 964862",
    #              "MFM Securities: Your withdrawal has been approved. Kindly check the below withdrawal details: Name: Muhammad Sani Abdul Ghani Account: 364098 Amount: -20 USD",
    #              "RM0.00 MyFundAction : Betul ke tahun ni raya dua kali? Klik untuk baca cerita penuh https://ezy.la/Qurban_Daftar"]
 
    csv_file_list = ['node1_msgdatas.csv', 'node2_msgdatas.csv', 'node3_msgdatas.csv', 'node4_msgdatas.csv']
    char_to_creative = hardcode_map_char_to_creative()
    url_regex = re.compile('((http|https|ftp|ftps):\\/\\/(www.)?)?[a-zA-Z0-9@:%-\\._+~#=]{1,256}\\.[a-z]{2,24}([-a-zA-Z0-9@:%_+\\.~#?&\\/\\/=]*)')

    for i in range(total_sample_to_generate):
        print(f'Process {i+1}/{total_sample_to_generate}...')
        output_csv = f"generated_creative_msg_{(num_msg_to_extract_per_csv+(i*increment_size_per_csv))*len(csv_file_list)}.csv"
        result_list = []

        print('Reading messages from csv file...')
        normal_msgs = get_msg_from_csv(num_msg_to_extract_per_csv+(i*increment_size_per_csv), csv_file_list)
        print(len(normal_msgs))

        #print(len(char_to_creative), char_to_creative)

        if (len(char_to_creative) <= 0):
            sys.exit() 

        else: 
            print('Generating creative messages...')
            for messages in normal_msgs:
                generated_msg = ""
                for word in messages.split():
                    #print(word)
                    if (url_regex.match(word) is None):
                        subbed_word = word_sub(word, char_to_creative)
                        generated_msg += (subbed_word + ' ')
                    else:
                        #print(f'URL detected..skipping url...{word}')
                        generated_msg += (word + ' ')
                result_list.append([generated_msg.strip(' '),'creative'])

        print(f'Writing to csv file:{output_csv}..')
        creative_msgdatas = pd.DataFrame(result_list, columns= ['msgdata', 'nature'])
        creative_msgdatas.to_csv(output_csv, na_rep="", index=False, sep=',',encoding='utf-8')
        print(f'Successfully written to file {output_csv}')

if __name__ == "__main__":
    main(5000, 5000, 5)
