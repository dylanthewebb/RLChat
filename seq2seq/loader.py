from requirements import *
from seq2seq.models import EncoderRNN, LuongAttnDecoderRNN
from seq2seq.vocab import Voc
from seq2seq.rl_methods import RLGreedySearchDecoder
from seq2seq._config import *

def load_latest_state_dict(savepath='data\\save\\cb_model\\cornell movie-dialogs corpus\\2-2_500'):
    try:
        saves = os.listdir(savepath)
    except FileNotFoundError:
        savepath = os.path.join("C:\\Users\\Christopher\\PycharmProjects\\RLChat", savepath)
        saves = os.listdir(savepath)
    max_save = saves[0]
    for save in saves:
        if int(save.split('_')[0]) > int(max_save.split('_')[0]):
            max_save = save
    return torch.load(open(os.path.join(savepath, max_save), 'rb'))


def saveStateDict(episode, encoder, decoder, encoder_optimizer, decoder_optimizer, loss, voc, embedding, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(" ".join(["Saving model state as", "{} checkpoint".format(episode)]))
    torch.save({
        'iteration': episode,
        'en': encoder.state_dict(),
        'de': decoder.state_dict(),
        'en_opt': encoder_optimizer.state_dict(),
        'de_opt': decoder_optimizer.state_dict(),
        'loss': loss,
        'voc_dict': voc.__dict__,
        'embedding': embedding.state_dict()
    }, os.path.join(directory, '{}_{}.tar'.format(episode, 'checkpoint')))


def loadModel(gpu=False, hidden_size=hidden_size, encoder_n_layers=encoder_n_layers, decoder_n_layers=decoder_n_layers, dropout=dropout, attn_model=attn_model, learning_rate=learning_rate, decoder_learning_ratio=decoder_learning_ratio,
              directory='data\\save\\cb_model\\cornell movie-dialogs corpus\\2-2_500'):
    state_dict = load_latest_state_dict(directory)
    episode = state_dict['iteration']
    encoder_sd = state_dict['en']
    decoder_sd = state_dict['de']
    encoder_optimizer_sd = state_dict['en_opt']
    decoder_optimizer_sd = state_dict['de_opt']
    embedding_sd = state_dict['embedding']

    voc = Voc('placeholder_name')
    voc.__dict__ = state_dict['voc_dict']

    print('Building encoder and decoder ...')
    # Initialize word embeddings
    embedding = nn.Embedding(voc.num_words, hidden_size)
    embedding.load_state_dict(embedding_sd)
    # Initialize encoder & decoder models
    encoder = EncoderRNN(hidden_size, embedding, encoder_n_layers, dropout)
    decoder = LuongAttnDecoderRNN(attn_model, embedding, hidden_size, voc.num_words, decoder_n_layers, dropout)
    encoder.load_state_dict(encoder_sd)
    decoder.load_state_dict(decoder_sd)
    # Use appropriate device
    encoder = encoder.to(device)
    decoder = decoder.to(device)
    print('Models built and ready to go!')

    # Initialize optimizers
    print('Building optimizers ...')
    encoder_optimizer = optim.Adam(encoder.parameters(), lr=learning_rate)
    decoder_optimizer = optim.Adam(decoder.parameters(), lr=learning_rate * decoder_learning_ratio)
    encoder_optimizer.load_state_dict(encoder_optimizer_sd)
    decoder_optimizer.load_state_dict(decoder_optimizer_sd)

    if device == 'cuda':
        # If you have cuda, configure cuda to call
        for state in encoder_optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.cuda()

        for state in decoder_optimizer.state.values():
            for k, v in state.items():
                if isinstance(v, torch.Tensor):
                    state[k] = v.cuda()
    print('Optimizers built and ready to go!')

    searcher = RLGreedySearchDecoder(encoder, decoder, voc)

    return episode, encoder, decoder, encoder_optimizer, decoder_optimizer, searcher, voc

if __name__ == '__main__':
    encoder, decoder, encoder_optimizer, decoder_optimizer, searcher, voc = loadModel()