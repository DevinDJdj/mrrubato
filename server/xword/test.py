#https://www.kaggle.com/code/dota2player/next-word-prediction-with-lstm-pytorch

#> pip install demoji
#> pip install bs4
#> pip install torchtext

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import re
import demoji
import random
import matplotlib.pyplot as plt

import torch
import torchtext
import torch.nn.functional as F
from torchtext.data.utils import get_tokenizer
from torchtext import vocab
from torch.utils.data import TensorDataset, DataLoader, random_split
from torch.nn.functional import one_hot
import torch.nn as nn
import torch.optim as optim

import warnings
warnings.filterwarnings("ignore")


seed = 42
torch.manual_seed(seed)
np.random.seed(seed)

df = pd.read_csv('./data/kaggle/medium_data.csv')
df.head()

def remove_html_tags(title):
    soup = BeautifulSoup(title, 'html.parser')
    return soup.get_text()

def remove_non_alphabetic(title):
    return re.sub('[^a-zA-Z]', ' ', title)

def remove_imojis(title):
    return demoji.replace(title, '')

def preprocessing_title(title):
    title = remove_html_tags(title)
    title = remove_imojis(title)
    title = remove_non_alphabetic(title)
    title.replace(u'\xa0', u' ')
    title.replace('\x200a', ' ')
    return title

df_titles = df['title']
df_titles.shape

df_titles = df_titles.apply(preprocessing_title)



tokenizer = get_tokenizer('basic_english')

tokenized_titles = [tokenizer(title) for title in df_titles]

len(tokenized_titles)


features_vocab = vocab.build_vocab_from_iterator(
    tokenized_titles,
    min_freq=2,
    specials=['<pad>', '<oov>'],
    special_first=True
)
target_vocab = vocab.build_vocab_from_iterator(
    tokenized_titles,
    min_freq=2
)

features_vocab_total_words = len(features_vocab)
target_vocab_total_words = len(target_vocab)

print(f'Total number of words in features vocabulary: {features_vocab_total_words}')
print(f'Total number of words in target vocabulary: {target_vocab_total_words}')
print('-'*30)
print('Word -> ID')
print('<pad> -> '+ str(features_vocab['<pad>']))
print('<oov> -> '+ str(features_vocab['<oov>']))
print('embedding in feature vocab-> '+ str(features_vocab['embedding']))
print('embedding in target vocab-> '+ str(target_vocab['embedding']))

def text_to_numerical_sequence(tokenized_text):
    tokens_list = []
    if tokenized_text[-1] in target_vocab.get_itos():
        for token in tokenized_text[:-1]:
            num_token = features_vocab[token] if token in features_vocab.get_itos() else features_vocab['<oov>']
            tokens_list.append(num_token)
        num_token = target_vocab[tokenized_text[-1]]
        tokens_list.append(num_token)
        return tokens_list
    return None


def add_random_oov_tokens(ngram):
    for idx, word in enumerate(ngram[:-1]):
        if random.uniform(0, 1) < 0.1:
            ngram[idx] = '<oov>'
    return ngram

def make_ngrams(tokenized_title):
    list_ngrams = []
    for i in range(1, len(tokenized_title)):
        ngram_sequence = tokenized_title[:i+1]
        list_ngrams.append(ngram_sequence)
    return list_ngrams


ngrams_list = []
for tokenized_title in tokenized_titles:
    ngrams_list.extend(make_ngrams(tokenized_title))
len(ngrams_list)

ngrams_list_oov = []
for ngram in ngrams_list:
    ngrams_list_oov.append(add_random_oov_tokens(ngram))
print(any('<oov>' in ngram for ngram in ngrams_list_oov))


input_sequences = [text_to_numerical_sequence(sequence) for sequence in ngrams_list_oov if text_to_numerical_sequence(sequence)]


print(f'Total input sequences: {len(input_sequences)}')
print(input_sequences[7:9])

X = [sequence[:-1] for sequence in input_sequences]
y = [sequence[-1] for sequence in input_sequences]
len(X[0]), y[0]


longest_sequence_feature = max(len(sequence) for sequence in X)
longest_sequence_feature

padded_X = [F.pad(torch.tensor(sequence), (longest_sequence_feature - len(sequence),
                                           0), value=0) for sequence in X]
padded_X[0], X[0], len(padded_X[0])

padded_X = torch.stack(padded_X)
y = torch.tensor(y)
type(y), type(padded_X)


y_one_hot = one_hot(y, num_classes=target_vocab_total_words)


data = TensorDataset(padded_X, y_one_hot)

train_size = int(0.8 * len(data))
test_size = len(data) - train_size
batch_size = 32

train_data, test_data = random_split(data, [train_size, test_size])

train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)



class My_LSTM(nn.Module):
    def __init__(self, features_vocab_total_words, target_vocab_total_words, embedding_dim, hidden_dim):
        super(My_LSTM, self).__init__()
        self.embedding = nn.Embedding(features_vocab_total_words, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True) 
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_dim, target_vocab_total_words)

    def forward(self, x):
        x = x.to(self.embedding.weight.device)
        embedded = self.embedding(x)
        lstm_out, _ = self.lstm(embedded)
        lstm_out = self.dropout(lstm_out)
        output = self.fc(lstm_out[:, -1, :])
        return output


embedding_dim = longest_sequence_feature
hidden_dim = 200
epochs = 50

model = My_LSTM(features_vocab_total_words, target_vocab_total_words, embedding_dim=embedding_dim, hidden_dim=hidden_dim)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0009)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device


def calculate_topk_accuracy(model, data_loader, k=3):
    model.eval()
    correct_predictions = 0
    total_predictions = 0

    with torch.no_grad():
        for batch_x, batch_y in data_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            # Forward pass
            output = model(batch_x)

            # Get top-k predictions
            _, predicted_indices = output.topk(k, dim=1)

            # Check if the correct label is in the top-k predictions
            correct_predictions += torch.any(predicted_indices == torch.argmax(batch_y, dim=1, keepdim=True), dim=1).sum().item()
            total_predictions += batch_y.size(0)

    accuracy = correct_predictions / total_predictions
    return accuracy

model.to(device)


all_accuracies = []
all_losses = []
for epoch in range(epochs):   
    model.train()
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y.argmax(dim=1))
        loss.backward()
        optimizer.step()
            
    if epoch % 5 == 0:
        accuracy = calculate_topk_accuracy(model, train_loader)
        print(f'Epoch {epoch}/{epochs}, Loss: {loss.item():.4f}, Train K-Accuracy: {accuracy * 100:.2f}%')
        all_accuracies.append(accuracy)
        all_losses.append(loss.item())

epoch_list = [i for i in range(1,epochs,5)]

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4)) 

axes[0].plot(epoch_list, all_accuracies, color='#5a7da9', label='Accuracy', linewidth=3)
axes[0].set_xlabel('Epochs')
axes[0].set_ylabel('Accuracy')
axes[0].set_title('Accuracy Graph')
axes[0].grid(True)
 
axes[1].plot(epoch_list, all_losses, color='#adad3b', label='Accuracy', linewidth=3)
axes[1].set_xlabel('Epochs')
axes[1].set_ylabel('Loss')
axes[1].set_title('Loss Graph')
axes[1].grid(True)

plt.tight_layout()
plt.show()


accuracy = calculate_topk_accuracy(model, test_loader)
print(f'Test K-Accuracy: {accuracy * 100:.2f}%')

def text_to_numerical_sequence_test(tokenized_text):
    tokens_list = []
    for token in tokenized_text:
        num_token = features_vocab[token] if token in features_vocab.get_itos() else features_vocab['<oov>']
        tokens_list.append(num_token)
    return tokens_list


def use_model(input_list):
    model.eval()
    output_list = []
    for data in input_test:
        sentence = data[0]
        num_words = data[1]
        for i in range(num_words):
            output_of_model = []
            tokenized_input_test = tokenizer(sentence)
            tokenized_sequence_input_test = text_to_numerical_sequence_test(tokenized_input_test)
            padded_tokenized_sequence_input_test = F.pad(torch.tensor(tokenized_sequence_input_test),
                                                         (longest_sequence_feature - len(tokenized_sequence_input_test)-1, 0),
                                                         value=0)
            output_test_walking = torch.argmax(model(padded_tokenized_sequence_input_test.unsqueeze(0)))
            sentence = sentence + ' ' + target_vocab.lookup_token(output_test_walking.item())
        output_list.append(sentence)
    return output_list

input_test = [['stand', 5], ['deep learning is', 5], ['data cleaning', 4], ['6 ways', 4], ['you did a', 2]]

outputs_model = use_model(input_test)
outputs_model
