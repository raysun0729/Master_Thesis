# AILA
artificial intelligence law
## TWLJP Dataset
自司法院裁判書系統，整理自民國107年至110年之刑事起訴書及裁判書之資料。
在刑責部分以月為單位，並移除僅有易科罰金、無罪、不受理之部分。若處拘役則輸出為1(1月)。

> Here the dataset link: https://drive.google.com/drive/folders/13qBKAIz7DOMIkOZezWpwX1v0DQnXZP0d?usp=share_link

Before filtering out freq<30 charge, we have 280k cases in total.
data: train_law, valid_law, test_law

## Model
### Bert
python train.py --config bert_law.config --do_test
for baseline
