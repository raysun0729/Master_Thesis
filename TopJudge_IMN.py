import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import json
from model.layer.Attention import Attention
from model.encoder.CNNEncoder import CNNEncoder
from model.encoder.BertEncoder import BertEncoder
from model.encoder.LoRAEncoder import LoRAEncoder
from model.loss import MultiLabelSoftmaxLoss, log_square_loss, RMSE_loss
from model.ljp.Predictor import LJPPredictor
from tools.accuracy_tool import multi_label_accuracy, log_distance_accuracy_function, RMSE_function


class LSTMDecoder(nn.Module):
    def __init__(self, config):
        super(LSTMDecoder, self).__init__()
        self.feature_len = config.getint("model", "hidden_size")

        features = self.feature_len
        self.hidden_dim = features

        self.task_name = ["article_source", "article", "accuse", "term"]

        self.midfc = []
        for x in self.task_name:
            self.midfc.append(nn.Linear(features, features))

        self.cell_list = [None]
        for x in self.task_name:
            self.cell_list.append(nn.LSTMCell(self.feature_len, self.feature_len))

        self.hidden_state_fc_list = []
        for a in range(0, len(self.task_name) + 1):
            arr = []
            for b in range(0, len(self.task_name) + 1):
                arr.append(nn.Linear(features, features))
            arr = nn.ModuleList(arr)
            self.hidden_state_fc_list.append(arr)

        self.cell_state_fc_list = []

        for a in range(0, len(self.task_name) + 1):
            arr = []
            for b in range(0, len(self.task_name) + 1):
                arr.append(nn.Linear(features, features))
            arr = nn.ModuleList(arr)
            self.cell_state_fc_list.append(arr)

        self.midfc = nn.ModuleList(self.midfc)
        self.cell_list = nn.ModuleList(self.cell_list)
        self.hidden_state_fc_list = nn.ModuleList(self.hidden_state_fc_list)
        self.cell_state_fc_list = nn.ModuleList(self.cell_state_fc_list)

    def init_hidden(self, bs):
        self.hidden_list = []
        for a in range(0, len(self.task_name) + 1):
            self.hidden_list.append((torch.autograd.Variable(torch.zeros(bs, self.hidden_dim).cuda()),
                                     torch.autograd.Variable(torch.zeros(bs, self.hidden_dim).cuda())))

    def forward(self, x):
        fc_input = x
        outputs = {}
        batch_size = x.size()[0]
        self.init_hidden(batch_size)

        first = []
        for a in range(0, len(self.task_name) + 1):
            first.append(True)
        for a in range(1, len(self.task_name) + 1):
            h, c = self.cell_list[a](fc_input, self.hidden_list[a])
            for b in range(1, len(self.task_name) + 1):
                hp, cp = self.hidden_list[b]
                if first[b]:
                    first[b] = False
                    hp, cp = h, c
                else:
                    hp = hp + self.hidden_state_fc_list[a][b](h)
                    cp = cp + self.cell_state_fc_list[a][b](c)
                self.hidden_list[b] = (hp, cp)
            outputs[self.task_name[a - 1]] = self.midfc[a - 1](h).view(batch_size, -1)

        return outputs


class TopJudge(nn.Module):
    def __init__(self, config, gpu_list, *args, **params):
        super(TopJudge, self).__init__()

        self.encoder = CNNEncoder(config, gpu_list, *args, **params)
        # self.encoder = BertEncoder(config, gpu_list, *args, **params)
        self.decoder = LSTMDecoder(config)
        self.Attention = Attention(config, gpu_list, *args, **params)
        self.fc = LJPPredictor(config, gpu_list, *args, **params)
        self.dropout = nn.Dropout(config.getfloat("model", "dropout"))

        self.criterion = {
            "accuse": MultiLabelSoftmaxLoss(config, 94),
            "article_source": MultiLabelSoftmaxLoss(config, 33),
            "article": MultiLabelSoftmaxLoss(config, 165),
            "term": RMSE_loss
        }
        self.accuracy_function = {
            "accuse": multi_label_accuracy,
            "article_source":multi_label_accuracy,
            "article": multi_label_accuracy,
            "term": RMSE_function
        }
        num_params = sum(p.numel() for p in super(TopJudge, self).parameters() if p.requires_grad)
        print("Number of parameters: ", num_params)
        self.hidden_size = config.getint("model", "hidden_size")
        self.embedding = nn.Embedding(len(json.load(open(config.get("data", "word2id")))),
                                      config.getint("model", "hidden_size"))
        self.CNN = nn.Conv1d(1, 1, kernel_size = 5, padding = 2)
        self.charge_fc = nn.Linear(self.hidden_size, 94 * 2)
        self.article_fc = nn.Linear(self.hidden_size, 165 * 2)
        self.article_source_fc = nn.Linear(self.hidden_size, 33 * 2)
        self.term_fc = nn.Linear(self.hidden_size, 1)
        self.sentence_enc = nn.Linear(self.hidden_size + 94*2 + 165*2 + 33*2 + 1, self.hidden_size)
    def init_multi_gpu(self, device, config, *args, **params):
        return
        self.encoder = nn.DataParallel(self.encoder, device_ids=device)
        self.decoder = nn.DataParallel(self.decoder, device_ids=device)
        self.dropout = nn.DataParallel(self.dropout, device_ids=device)
        self.fc = nn.DataParallel(self.fc, device_ids=device)

    def forward(self, data, config, gpu_list, acc_result, mode):
        x = data['text']
        x = self.embedding(x)
        sentence_output = self.encoder(x)
        for i in range(3):
        # result = self.fc(y)
            # print('Interaction number ', i)
            charge_output = sentence_output
            article_output = sentence_output
            article_source_output = sentence_output
            term_output = sentence_output
            ##############
            ### charge ###
            ##############
            # print(charge_output)
            charge_output = charge_output.unsqueeze(1)
            # print("charge_output:(unsqueeze) ", charge_output.size())
            charge_output = self.CNN(charge_output)
            # print("charge_output:(CNN) ", charge_output.size())
            
            
            ###############
            ### article ###
            ###############
            article_output = article_output.unsqueeze(1)
            article_output = self.CNN(article_output)

            article_source_output = article_source_output.unsqueeze(1)
            article_source_output = self.CNN(article_source_output)

            term_output = term_output.unsqueeze(1)
            term_output = self.CNN(term_output)
            ###############
            ###Attention###
            ###############
            charge_att, article_att, _att = self.Attention(charge_output, article_output)
            # article_att, article_source_att, _att = self.Attention(article_output, article_source_output)
            # article_att, term_att, _att = self.Attention(article_output, term_output)
            # term_att, article_source_att, _att = self.Attention(term_output, article_source_output)
            
            # charge_att, article_att, _att = self.Attention(charge_output, article_output)
            # article_att, term_att, _att = self.Attention(article_output, term_output)
            # term_att, article_source_att, _att = self.Attention(term_output, article_source_output)
            
            # charge_att, article_att, term_att, _att = self.Attention(charge_output, article_output, term_output)
            # print("charge_att: ", charge_att.size())
            
            ###############
            ### fc ###
            ###############
            charge_output = charge_att.squeeze(1)
            # charge_output = charge_output.squeeze(1)
            # print("charge_output:(squeeze) ", charge_output.size())
            charge_probs = self.charge_fc(charge_output)
            # print(charge_probs)
            # print("charge_probs:(fc) ",charge_probs.size())
            article_output = article_att.squeeze(1)
            article_probs = self.article_fc(article_output)

            article_source_output = article_source_output.squeeze(1)
            # article_source_output = article_source_output.squeeze(1)
            article_source_probs = self.article_source_fc(article_source_output)

            # term_output = term_att.squeeze(1)
            term_output = term_output.squeeze(1)
            term_probs = self.term_fc(term_output)
            
            sentence_output = torch.cat((sentence_output, charge_probs, article_probs, term_probs, article_source_probs), 1)
            # sentence_output = torch.cat(sentence_output, article_probs)
            # print(sentence_output.size())
            sentence_output = self.sentence_enc(sentence_output)
        # hidden = self.encoder(x)
        sentence_output = self.dropout(sentence_output)
        # hidden = self.dropout(hidden)
        result = self.decoder(sentence_output)
        # result = self.decoder(hidden)
        for name in result:
            result[name] = self.fc(self.dropout(result[name]))[name]

        loss = 0
        for name in ["accuse", "article_source", "article", "term"]:
            loss += self.criterion[name](result[name], data[name])

        if acc_result is None:
            acc_result = {"accuse": None, "article_source": None, "article": None, "term": None}

        for name in ["accuse", "article_source", "article", "term"]:
            acc_result[name] = self.accuracy_function[name](result[name], data[name], config, acc_result[name])

        return {"loss": loss, "acc_result": acc_result}
