import re 
import matplotlib.pyplot as plt 
import numpy as np 

class model_result:

    def __init__(self, model_name) -> None:
        self.name = model_name
        self.normal_count = 0
        self.time_taken = 0 # total time in (s)
        self.total_msg_analysed = 0

    def add_normal_count(self, count):
        self.normal_count += int(count) 
        return True 

    def add_time_taken(self, time):
        self.time_taken += float(time)
        return True 

    def add_total_msg_analysed(self, msg_count):
        self.total_msg_analysed += int(msg_count)
        return True 

    def get_normal_count(self):
        return self.normal_count
    
    def get_total_time(self):
        return self.time_taken
    
    def get_process_time_for_a_msg(self):
        return self.time_taken/self.total_msg_analysed
    
    def get_total_msg_analysed(self):
        return self.total_msg_analysed

def main():
    global_memory = {}
    analysis_file = 'test_model_prediction_nb.txt'
    current_model_string = "Current Model: "
    total_msg_count_string = "Total normal message in msgdatas: "
    predicted_normal_count_string = "Predicted normal count: "
    total_time_taken_string = "Total time taken for prediction: "

    with open(analysis_file, mode = 'r', encoding='utf-8') as f:
        for data in f.readlines():
            if data.find(current_model_string) != -1:
                current_model = data[(data.index(current_model_string)+len(current_model_string)):].strip()
                print('current model',current_model)
            
            elif data.find(predicted_normal_count_string) != -1:
                cur_model_predict_normal = data[(data.index(predicted_normal_count_string)+len(predicted_normal_count_string)):data.index(",")].strip()
                print('predicted normal count',cur_model_predict_normal)

            elif data.find(total_msg_count_string) != -1:
                cur_model_total_msg = data[(data.index(total_msg_count_string)+len(total_msg_count_string)):].strip()
                print('total msg count',cur_model_total_msg)

            elif data.find(total_time_taken_string) != -1:
                cur_model_total_time = data[(data.index(total_time_taken_string)+len(total_time_taken_string)):data.index('(')].strip()
                print('total time taken for model',cur_model_total_time)
                print('Inserting to dict..')
                if current_model not in global_memory.keys():
                    model_to_insert = model_result(current_model)
                    model_to_insert.add_normal_count(cur_model_predict_normal)
                    model_to_insert.add_time_taken(cur_model_total_time)
                    model_to_insert.add_total_msg_analysed(cur_model_total_msg)
                    global_memory[current_model] = model_to_insert

                else: 
                    model_to_insert = global_memory[current_model]
                    model_to_insert.add_normal_count(cur_model_predict_normal)
                    model_to_insert.add_time_taken(cur_model_total_time)
                    model_to_insert.add_total_msg_analysed(cur_model_total_msg)

                print(model_to_insert.name, model_to_insert.get_normal_count(), model_to_insert.get_total_time(), model_to_insert.get_total_msg_analysed(), model_to_insert.get_process_time_for_a_msg())

            else:
                pass 
    
    model_result_point2 = {}
    model_result_point3 = {}
    model_size = []

    for keys in global_memory.keys():
        current_model_info = global_memory[keys]
        underscore_pos = [m.start() for m in re.finditer('_', keys)]
        current_model_size = keys[underscore_pos[1]+1:underscore_pos[2]]
        current_model_ratio = keys[underscore_pos[2]+1:-4]
        current_model_time_taken = current_model_info.get_total_time() 
        current_model_normal_count = current_model_info.get_normal_count()
        current_model_total_msg_analysed = current_model_info.get_total_msg_analysed()
        to_insert_to_list = [current_model_time_taken, int(current_model_normal_count), int(current_model_total_msg_analysed)]

        if current_model_ratio == '0.2':
            model_result_point2[current_model_size] = to_insert_to_list

        else:
            model_result_point3[current_model_size] = to_insert_to_list

        if int(current_model_size) not in model_size:
            model_size.append(int(current_model_size))

        print(current_model_size, current_model_ratio)

    model_size.sort()
    print(model_size)

    false_positive_rate_point_2 = []
    false_positive_rate_point_3 = []

    for size in model_size:
        model_info_point_2 = model_result_point2[str(size)]
        model_info_point_3 = model_result_point3[str(size)]
        fp_point2 = ((model_info_point_2[2] - model_info_point_2[1]) / model_info_point_2[2])
        fp_point3 = ((model_info_point_3[2] - model_info_point_3[1]) / model_info_point_3[2])
        false_positive_rate_point_2.append(fp_point2)
        false_positive_rate_point_3.append(fp_point3)

    
    print(false_positive_rate_point_2, false_positive_rate_point_3)
    print(len(model_size), len(false_positive_rate_point_2), len(false_positive_rate_point_3))
    model_size = np.array(model_size)
    false_positive_rate_point_2 = np.array(false_positive_rate_point_2)
    false_positive_rate_point_3 = np.array(false_positive_rate_point_3)


    plt.xlabel('Dataset Size')
    plt.ylabel('false positive rate(%)')
    plt.title('false positive rate vs dataset size (0.2)')
    interval = np.linspace(model_size.min(), model_size.max(), 100)
    plt.xticks(interval, rotation = 90)
    plt.grid(True)
    plt.plot(model_size, false_positive_rate_point_2)
    plt.savefig('false_positive_analysis_0.2.png')
    plt.show() 

    plt.xlabel('Dataset Size')
    plt.ylabel('false positive rate(%)')
    plt.title('false positive rate vs dataset size (0.3)')
    plt.xticks(interval, rotation = 90)
    plt.grid(True)
    plt.plot(model_size, false_positive_rate_point_3)
    plt.savefig('false_positive_analysis_0.3.png')
    plt.show()

if __name__ == "__main__":
    main()