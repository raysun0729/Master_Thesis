import json
import random
import os

# set input and output dir and create output file
root = 'data'
output_dir = 'output'

os.makedirs(output_dir, exist_ok = True)
f = open('{}/train.json'.format(output_dir), 'w'); f.close()
f = open('{}/valid.json'.format(output_dir), 'w'); f.close()
f = open('{}/test.json'.format(output_dir), 'w'); f.close()

# create dictionary to classify accusation
accusation_dict = {}

# search every filename in data and parse
for filename in os.listdir(root):
    print('{}/{} processing...'.format(root, filename))
    with open('{}/{}'.format(root, filename), 'r', encoding = 'utf-8') as f:
        for line in f:
            data = json.loads(line)
            accusation = data['meta']['accusation']

            if accusation not in accusation_dict:
                accusation_dict[accusation] = []
            accusation_dict[accusation].append(data)

# create file writer
train_f = open('{}/train.json'.format(output_dir), 'a', encoding = 'utf-8')
valid_f = open('{}/valid.json'.format(output_dir), 'a', encoding = 'utf-8')
test_f = open('{}/test.json'.format(output_dir), 'a', encoding = 'utf-8')

# write down json information to file
for accusation, content in accusation_dict.items():
    # if amount of accusation less than 10 => all content will become training data
    if len(content) < 10:
        print('{} train: {}'.format(accusation, len(content)))  # output train data amount
        for line in content:
            train_f.write('{}\n'.format(json.dumps(line, ensure_ascii = False)))
    else:
        train_count = int(len(content) * 0.8)
        valid_count = int(len(content) * 0.9)
        print('{} train: {}, valid: {}, test: {}'.format(accusation, train_count, valid_count - train_count, len(content) - valid_count))   # output train, valid, test data amount

        # random pick content index
        random_index_list = list(range(len(content)))
        random.shuffle(random_index_list)

        for index in random_index_list[:train_count]:  # write to train file
            train_f.write('{}\n'.format(json.dumps(content[index], ensure_ascii = False)))
            
        for index in random_index_list[train_count:valid_count]:  # write to valid file
            valid_f.write('{}\n'.format(json.dumps(content[index], ensure_ascii = False)))
            
        for index in random_index_list[valid_count:]:  # write to test file
            test_f.write('{}\n'.format(json.dumps(content[index], ensure_ascii = False)))

# close all file
train_f.close()
valid_f.close()
test_f.close()