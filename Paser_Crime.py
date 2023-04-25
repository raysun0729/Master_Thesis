import os
import json
import time
import pandas as pd
import openpyxl

print("Initializing：", time.ctime())
# "C:\Users\user\Desktop\Master_Thesis\Dataset\data_org"
DATA_DIR = 'C:/Users/user/Desktop/Master_Thesis/Dataset/data_org'
# DATA_DIR = 'D:/law_data/data_org/'
STORE_DIR = 'C:/Users/user/Desktop/Master_Thesis/Dataset/data_org'
# STORE_DIR = 'D:/law_data/data_task1_20201225/'

Procuratorate_dirs = os.listdir(DATA_DIR)

no_crimimals_count = 0
used_count = 0
for dir in Procuratorate_dirs:
    dir_path = DATA_DIR + '/' + dir + '/'
    print(dir+', ', len([name for name in os.listdir(dir_path) if os.path.join(dir_path, name)]))

LAW_article = ['刑法', '毒品危害防制條例', '槍砲彈藥刀械管制條例', '藥事法', '著作權法', \
               '廢棄物清理法', '性騷擾防治法', '公職人員選舉罷免法', '建築法', '家庭暴力防治法', \
               '就業服務法', '入出國及移民法', '性侵害犯罪防治法', '公司法', '商業會計法', '稅捐稽徵法',\
               '洗錢防制法', '兒童及少年性剝削防制條例', '區域計畫法', '醫療法', '水土保持法',
               '組織犯罪防制條例', '妨害兵役治罪條例', '銀行法', '電子遊戲場業管理條例', '醫師法', \
               '政府採購法', '個人資料保護法', '森林法', '野生動物保育法', '水污染防治法', '臺灣地區與大陸地區人民關係條例', \
               '動物保護法', '貪污治罪條例', '商標法', '漁業法', '菸酒管理法', '替代役實施條例', '空氣污染防制法', \
               '動物傳染病防治條例', '期貨交易法']

import re

def chk_dir(dir_path):
    dir_path =  STORE_DIR + '/' + dir + '/'
    if os.path.exists(dir_path):
        pass
    else:
        os.mkdir(dir_path)
    
    return dir_path

def strQ2B(ustring):
    """把字串全形轉半形"""
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # 全形空格直接轉換
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字元（除空格）根據關係轉化
                inside_code -= 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)

def parse_law_article(content):
    law_article = []
#     print(content)
    for line in content:
        line = line.strip()
        for keyword in LAW_article:
            # print(keyword, line)
            if (keyword in line) and ('科刑法條' not in line) and len(line) < 25:
                line = strQ2B(line)
                law_article.append(line)
                break
    # print(law_article)
    return law_article

law_article_begin = ['所犯法條', '所犯法條:', '所犯法條：', '附錄法條', '附錄本案論罪科刑法條全文：', \
                     '附錄本案論罪科刑法條：', '附錄本案論罪科刑法條', '參考法條', '參考法條：', \
                     '附錄所犯法條：', '附錄本件論罪科刑法條：', '附錄本案論罪科刑法條:', '附錄本案所犯法條全文', \
                     '附錄本判決論罪法條全文：', '附錄論罪科刑法條：', '附錄本案論罪法條全文：', '附錄本判決論罪科刑法條：', \
                     '附錄論罪科刑法條全文：', '附錄本案論罪科刑所適用之法條：', '附錄本案論罪科刑法條：']

def find_law_article_line(content):
    for line_number, line in enumerate(content):
        for begin_word in law_article_begin:
            if begin_word in line.strip() and '證據並所犯法條' not in line.strip():
                law_begin_line_number = line_number
                return law_begin_line_number
                break
    
def find_clerk_line(content):
    for line_number, line in enumerate(content):
#         print(line.strip())
        if '書記官' in line.strip() or '書  記  官' in line.strip() or '書 記 官' in line.strip() or '書  記  官' in line.strip():
            law_begin_line_number = line_number
            return law_begin_line_number
            break

USE_LAW = ['刑法第185條', '毒品危害防制條例第10條', '刑法第320條', '刑法第284條', '刑法第277條', '刑法第339條', '刑法第321條', \
           '毒品危害防制條例第4條', '毒品危害防制條例第11條', '刑法第309條', '刑法第354條', '刑法第305條', '刑法第276條', '刑法第337條',\
           '刑法第266條', '商標法第97條', '刑法第268條', '刑法第140條', '刑法第336條', '刑法第335條', '刑法第231條', '藥事法第83條', \
           '刑法第310條', '家庭暴力防治法第61條', '刑法第135條', '刑法第304條', '性騷擾防治法第25條']

law_number_dict = {}

# def get_punishment(jud_main_line):
#     sentence1 = re.search(r'.+拘役(.+?)日', jud_main_line)
#     sentence2 = re.search(r'.+有期徒刑(.+?)月', jud_main_line)
#     if sentence1:
#         punishment = sentence1.group(1).strip()
#         if punishment.isdigit():
#             days = int(punishment)
#             if days < 30:
#                 return "一月"
#             else:
#                 return str(days) + "日"
#         else:
#             return punishment+"日"
#     elif sentence2:
#         punishment = sentence2.group(1).strip()
#         if punishment.isdigit():
#             months = int(punishment)
#             days = months * 30
#             return str(days) + "日"
#         else:
#             return punishment + "月"
#     else:
#         return "不受理"

def law2reg(law_articles):
    reg_law_article = []
    all_law_text = []
    continue_flag = False
    for law_article in law_articles:
        law_article = law_article.replace(" ", "")
        law_article_part = law_article.split("第", 1)
        # print(sentence_part)
    #     law = sentence_part[0]

        if len(law_article_part) == 2:
            law_number = ''
            for letter in law_article_part[1]:
        #         print(letter)
                if letter.isdigit():
                    law_number += letter
                else:
                    break
            if law_number == '':
                pass
                # print(law_article)
        #     print(number)
            dash_in_law = False
            
            if '之' in law_article:
                
                dash_article_part = law_article.split("之", 1)
                dash_number = ''
                for letter in dash_article_part[1]:
            #         print(letter)
                    if letter.isdigit():
                        dash_number += letter
                        dash_in_law = True
                    else:
                        break
                if dash_number == '' and dash_in_law == True:
                    pass
                    # print(law_article)
            
            for law in LAW_article:
                if law in law_article_part[0]:
                    if dash_in_law:
                        law_last_part = '第' + law_number + '條之' + dash_number
                    else:
                        law_last_part = '第' + law_number + '條'
                    law_text = law + law_last_part
                    all_law_text.append(law_text)
                    append_text = (law, law_last_part)
    #                     print(append_text)
                    reg_law_article.append(append_text)
    
                    if law_number_dict.get(law_text):
                        law_number_dict[law_text] = law_number_dict[law_text] + 1
                    else:
                        law_number_dict[law_text] = 1
    for text in all_law_text:
        if text not in USE_LAW:
            continue_flag = True
    
    return reg_law_article, continue_flag

def list2txt(lists):
    txt = ''
    for i, item in enumerate(lists):
        if i < len(lists) - 1:
            txt += item + '、'
        else:
            txt += item
#     print(txt)
    return txt

# function to get unique values
def unique(list1):
 
    # initialize a null list
    unique_list = []
     
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    
    return unique_list

def parse_criminals(fact, criminal_lines):
    criminals = []
    # print(criminal_lines)
    for line in criminal_lines:
        if ('被' in line) and ('告' in line) and ('偵查終結' not in line) and ('緩起訴' not in line):
            criminal = line.replace("被", "", 1).replace("告", "", 1).strip()
            try:
                criminal = criminal.split()[0]
            except:
                print("split error: ", criminal_lines, line)
            criminals.append(criminal)
    return criminals
def get_punishment(jud_txt):
    sentence1 = re.search(r'.+拘役(.+?)日', jud_txt)
    sentence2 = re.search(r'.+有期徒刑(.+?)月', jud_txt)
    if sentence1:
        punishment = sentence1.group(1).strip()
        if punishment.isdigit():
            days = int(punishment)
            if days < 30:
                return "一月"
            else:
                return str(days) + "日"
        else:
            return punishment+"日"
    elif sentence2:
                    punishment = sentence2.group(1).strip()
                    if punishment.isdigit():
                        months = int(punishment)
                        days = months * 30
                        return str(days) + "日"
                    else:
                        return punishment + "月"
    else:
        return "不受理"
print("Start processing：", time.ctime())
case_dict = {}
article_source_dict = {}
article_dict = {}
innocent_count = 0
same_count = 0
for dir in Procuratorate_dirs:
    dir_path = chk_dir(DATA_DIR + '/' + dir + '/')
    print("dir_path:", dir_path)
    store_dir_path = chk_dir(STORE_DIR + '/' + dir + '/')
    print("store_dir_path:",store_dir_path)
    problem_dir = chk_dir(STORE_DIR + '/' + dir + '/problem/')
    if dir == 'problem_file':
        continue
    print('processing:  ' + dir)
    print("time：", time.ctime())
    json_file = open(os.path.join(STORE_DIR, dir + '.json'), 'w', encoding = 'utf-8')
    
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        new_file_path = os.path.join(store_dir_path, file)
        if file == 'problem':
            continue
        print('file:',file)
        with open(file_path, encoding = 'utf-8') as f:
            file_content = f.readlines()
            
            # split psue and judgement
            for line_number, content in enumerate(file_content):
                print([content])
                if content == '------------------------------\n':
                    split_line_number = line_number
                    break
            
            psue_content = file_content[:split_line_number]
            jud_content = file_content[split_line_number + 2 :len(file_content)]

            print('jud_content:',jud_content)

            ###################
            # processing psue #
            ###################
            
            psue_fact_line = 0
            psue_evidence_line = 0
            psue_content_temp = []
            for psue_line_number, content in enumerate(psue_content):
                content = content.replace(u'\u3000', u' ').replace(u'\xa0', u' ').strip()
                print([content])
                if content == '犯罪事實':
                    psue_fact_line = psue_line_number
                elif content == '證據並所犯法條' or content == '證據名稱並所犯法條':
                    psue_evidence_line = psue_line_number
                psue_content_temp.append(content)
            psue_content = psue_content_temp
            print('psue_content:',psue_content)
            
            print('psue_fact_line:',psue_fact_line)
#             print(psue_evidence_line)
            
            ########################
            # if can not parse fact, copy the file to problem dir and continue to next file
            ########################
            
            if psue_fact_line == 0 or psue_evidence_line == 0:
                new_file = open(os.path.join(problem_dir, file), 'w', encoding = 'utf-8')
                # print(file, str(psue_fact_line), str(psue_evidence_line))
                continue
                
            psue_law_begin_line_number = find_law_article_line(psue_content)
            
            if psue_law_begin_line_number == None:
                psue_law_begin_line_number = find_clerk_line(psue_content)
            
            if psue_law_begin_line_number == None:
                psue_law_begin_line_number = split_line_number -2
            
            psue_law_articles = parse_law_article(psue_content[psue_law_begin_line_number +1:])
            psue_law_articles.sort()
            if len(psue_law_articles) == 0:
                continue
            # print(psue_law_articles)
            
            reg_psue_law_articles, continue_flag = law2reg(psue_law_articles)
            if continue_flag:
                continue

            # print(reg_law_articles)
            
# #             print(jud_content)
            ########################
            # processing judgement #
            ########################
            
            jud_main_line = 0
            jud_reason_line = 0
            for jud_line_number, content in enumerate(jud_content):
                content = content.replace(u'\u3000', u'').replace(u'\xa0', u'').replace(' ', '').strip()
#                 print([content])
                if content == '主文':
                    jud_main_line = jud_line_number
                elif content == '事實及理由' or content == '犯罪事實' or content == '理由' or content == '犯罪事實及理由' or content == '事實':
                    jud_reason_line = jud_line_number
                    break
            print('jud_main_line:',jud_main_line)
            print('jud_reason_line: ',jud_reason_line)
            ########################
            # processing judgement main content#
            ########################
            
            jud_main_content = jud_content[jud_main_line + 2 :jud_reason_line - 1]
            jud_txt = ''
            for line in jud_main_content:
                line = line.strip()
                jud_txt += line
            print('jud_text:',jud_txt)
            # print(abc)
            print('jud_main_content:',jud_main_content)
            if '無罪' in jud_txt:
                innocent_count += 1
                # print(jud_txt)
            
            
            ########################
            # '''
#             print(jud_txt)
            

            
            
            if jud_main_line == 0 or jud_reason_line == 0:
                # f.close()
                # print(file, str(jud_main_line), str(jud_reason_line))
                # problem_dir_path = DATA_DIR + '/' + dir + '/problem/' 
                # des_path = os.path.join(problem_dir_path, file)
                # print("file_path:",file_path)
                # print("des_path:",des_path)
                # os.rename(file_path, des_path)
                continue
            
            jud_law_begin_line_number = find_law_article_line(jud_content)
#             jud_law_begin_line_number = find_clerk_line(file_content[split_line_number:])
            # print(jud_law_begin_line_number)
            if jud_law_begin_line_number == None:
                jud_law_begin_line_number = find_clerk_line(jud_content)
                
            if jud_law_begin_line_number == None:
                jud_law_begin_line_number = len(jud_content) -2
             
            jud_law_article = parse_law_article(jud_content[jud_law_begin_line_number:])
            if len(jud_law_article) == 0:
                continue
            jud_law_article.sort()
            reg_jud_law_articles, flag = law2reg(jud_law_article)
            
            if set(unique(reg_psue_law_articles)) != set(unique(reg_jud_law_articles)):
                # print(set(unique(reg_psue_law_articles)), set(unique(reg_jud_law_articles)))
                same_count += 1
            # print(unique(reg_psue_law_articles), unique(reg_jud_law_articles))
            # print(set(unique(reg_psue_law_articles)) == set(unique(reg_jud_law_articles)))
            # print(abc)
            fact = psue_content[psue_fact_line + 1 : psue_evidence_line]
            fact_txt = ''
            for line in fact:
                fact_txt += line.strip()
            criminals = []
            print('fact_txt:',fact_txt)

            criminals = parse_criminals(fact, psue_content[3:psue_fact_line-1])
            # print(criminals)
            if len(criminals) == 0:
                no_crimimals_count += 1
            case = psue_content[2].split('：')[1]  # replace'\n'
            unique_reg_psue_law_articles = unique(reg_psue_law_articles)
            # jud_arr = []
            # jud_arr.append(jud_txt)
            # time_arr = []
            # time_arr.append(get_punishment(jud_txt))
            fileDict = {   
                    "fact": fact_txt,   
                    "file": file,
                    "meta": 
                            {  
                                "relevant_articles": unique_reg_psue_law_articles,
                                "#_relevant_articles" : len(unique_reg_psue_law_articles),
                                "relevant_articles_org": psue_law_articles,
                                "criminals": criminals,
                                "#_criminals": len(criminals),
                                "jud_text": jud_txt,
                                "accusation": case,
                                "term_of_imprisonment": 
                                {  
                                    "death_penalty": None,  
                                    "imprisonment": get_punishment(jud_txt),  
                                    "life_imprisonment": None
                                }
                            }
                        }
            json_text = json.dumps(fileDict, ensure_ascii=False)
            
            # statistic
            
            
            if len(unique_reg_psue_law_articles) >= 1:
                # case
                if case_dict.get(case):
                    case_dict[case] = case_dict[case] + 1
                else:
                    case_dict[case] = 1
                # article_source
                for arti in unique_reg_psue_law_articles:
                    article_source = arti[0]
                    print(article_source)
                    if article_source_dict.get(article_source):
                        article_source_dict[article_source] = article_source_dict[article_source] + 1
                    else:
                        article_source_dict[article_source] = 1
                    article = arti[0] + arti[1]
                    print(article)
                    if article_dict.get(article):
                        article_dict[article] = article_dict[article] + 1
                    else:
                        article_dict[article] = 1

            
                json_file.write(json_text + '\n')
                json_file.flush()
                used_count += 1

    # df = pd.DataFrame({"jud_text": jud_arr, "sentence": time_arr})
    # df.to_excel("output.xlsx", index=False)                
    # break

print(same_count)
print('done')
#     break

print(no_crimimals_count)
print(used_count)


for case in case_dict:
    print(case + ', ' + str(case_dict[case]))
for article_source in article_source_dict:
    print(article_source + ', ' + str(article_source_dict[article_source]))
for article in article_dict:
    print(article + ', ' + str(article_dict[article]))