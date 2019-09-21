from requirements import *
from seq2seq.trainingMethods import GreedySearchDecoder, evaluateInput
from seq2seq.models import EncoderRNN, LuongAttnDecoderRNN
from seq2seq.vocab import Voc

def load_latest_state_dict():
    savepath = 'data\\save\\cb_model\\cornell movie-dialogs corpus\\2-2_500'
    saves = os.listdir(savepath)
    max_save = saves[0]
    for save in saves:
         if int(save.split('_')[0]) > int(max_save.split('_')[0]):
             max_save = save
    return torch.load(open(os.path.join(savepath, max_save), 'rb'))

def chat_with_latest():
    model = load_latest_state_dict()

    attn_model = 'dot'
    #attn_model = 'general'
    #attn_model = 'concat'
    hidden_size = 500
    encoder_n_layers = 2
    decoder_n_layers = 2
    dropout = 0.1
    batch_size = 64

    voc = Voc(model['voc_dict']['name'])
    voc.__dict__ = model['voc_dict']

    embedding = nn.Embedding(voc.num_words, hidden_size)

    encoder = EncoderRNN(hidden_size, embedding, encoder_n_layers, dropout)
    decoder = LuongAttnDecoderRNN(attn_model, embedding, hidden_size, voc.num_words, decoder_n_layers, dropout)

    encoder.load_state_dict(model['en'])
    decoder.load_state_dict(model['de'])

    searcher = GreedySearchDecoder(encoder, decoder)
    evaluateInput(encoder, decoder, searcher, voc)

if __name__ == '__main__':
    chat_with_latest()