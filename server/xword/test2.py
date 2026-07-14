#https://debuggercafe.com/word-level-text-generation-using-lstm/

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from collections import Counter

# Dataset Preparation
with open('./data/alice.txt', 'r', encoding='utf-8') as file:
    text = file.read()
# Tokenize the text into words
words = text.split()
word_counts = Counter(words)
vocab = list(word_counts.keys())
vocab_size = len(vocab)
word_to_int = {word: i for i, word in enumerate(vocab)}
int_to_word = {i: word for word, i in word_to_int.items()}
SEQUENCE_LENGTH = 64
samples = [words[i:i+SEQUENCE_LENGTH+1] for i in range(len(words)-SEQUENCE_LENGTH)]
print(vocab)
print(word_to_int)
print(int_to_word)


class TextDataset(Dataset):
    def __init__(self, samples, word_to_int):
        self.samples = samples
        self.word_to_int = word_to_int
    def __len__(self):
        return len(self.samples)
    def __getitem__(self, idx):
        sample = self.samples[idx]
        input_seq = torch.LongTensor([self.word_to_int[word] for word in sample[:-1]])
        target_seq = torch.LongTensor([self.word_to_int[word] for word in sample[1:]])
        return input_seq, target_seq


class TextGenerationLSTM(nn.Module):
    def __init__(
        self,
        vocab_size,
        embedding_dim,
        hidden_size,
        num_layers
    ):
        super(TextGenerationLSTM, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(
            input_size=embedding_dim, 
            hidden_size=hidden_size, 
            num_layers=num_layers, 
            batch_first=True
        )
        self.fc = nn.Linear(hidden_size, vocab_size)
        self.hidden_size = hidden_size
        self.num_layers = num_layers
    def forward(self, x, hidden=None):
        if hidden == None:
            hidden = self.init_hidden(x.shape[0])
        x = self.embedding(x)
        out, (h_n, c_n) = self.lstm(x, hidden)
        out = out.contiguous().view(-1, self.hidden_size)
        out = self.fc(out)
        return out, (h_n, c_n)
    def init_hidden(self, batch_size):
        h0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        c0 = torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device)
        return h0, c0
    

BATCH_SIZE = 32
dataset = TextDataset(samples, word_to_int)
dataloader = DataLoader(
    dataset, 
    batch_size=BATCH_SIZE, 
    shuffle=True, 
)
print(dataset[1])


# Training Setup
embedding_dim = 16
hidden_size = 32
num_layers = 1
learning_rate = 0.01
epochs = 50


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = TextGenerationLSTM(
    vocab_size, 
    embedding_dim, 
    hidden_size, 
    num_layers
).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)


# Training
def train(model, epochs, dataloader, criterion):
    model.train()
    for epoch in range(epochs):
        running_loss = 0
        for input_seq, target_seq in dataloader:
            input_seq, target_seq = input_seq.to(device), target_seq.to(device)
            outputs, _ = model(input_seq)
            loss = criterion(outputs, target_seq.view(-1))
    
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.detach().cpu().numpy()
        epoch_loss = running_loss / len(dataloader)
        print(f"Epoch {epoch} loss: {epoch_loss:.3f}")
train(model, epochs, dataloader, criterion)


# Inference
def generate_text(model, start_string, num_words):
    model.eval()
    words = start_string.split()
    for _ in range(num_words):
        input_seq = torch.LongTensor([word_to_int[word] for word in words[-SEQUENCE_LENGTH:]]).unsqueeze(0).to(device)
        h, c = model.init_hidden(1)
        output, (h, c) = model(input_seq, (h, c))
        next_token = output.argmax(1)[-1].item()
        words.append(int_to_word[next_token])
    return " ".join(words)
# Example usage:
print("Generated Text:", generate_text(model, start_string="Alice was a", num_words=100))
