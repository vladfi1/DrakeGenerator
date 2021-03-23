import tensorflow as tf
from tensorflow import keras

class DrakeGRUSequential(keras.Model):
    def __init__(self, vocab_size, embedding_dim, rnn_units=150):
        super().__init__()
        self.embed_layer = keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(rnn_units, return_sequences=True, return_state=True)
        #self.lstm = keras.layers.LSTM(lstm_units, return_state=True)
        self.reshape_layer = keras.layers.Dense(vocab_size)

    def call(self, inputs, states=None, return_state=False, training=False):
        x = inputs
        x = self.embed_layer(x, training=training)
        if states is None:
            states = self.gru.get_initial_state(x)
        x, states = self.gru(x, initial_state=states, training=training)
        x = self.reshape_layer(x, training=training)

        if return_state:
            return x, states
        else:
            return x

class MyCellModelWrapper(keras.Model):
    def __init__(self, cell):
        super().__init__()
        self.rnn = keras.layers.RNN(cell, return_state=True)

    def call(self, inputs, states=None, return_state=False, training=False):
        x = inputs
        x, states = self.rnn(inputs=x)
        if return_state:
            return x, states
        else:
            return x

class MyRNNCell(keras.layers.Layer):
    def __init__(self, output_size, hidden_units=10, **kwargs):
      super(MyRNNCell, self).__init__(**kwargs)
      self.hidden_units = hidden_units
      self.output_size = output_size
      self.state_size = hidden_units

    def build(self, input_shape):
      self.w_xh = self.add_weight(shape=(input_shape[-1], self.hidden_units), initializer='random_normal', trainable=True, name="W_xh")
      self.w_hh = self.add_weight(shape=(self.hidden_units, self.hidden_units), initializer='random_normal', trainable=True, name="W_hh")
      self.w_hy = self.add_weight(shape=(self.hidden_units, self.output_size), initializer='random_normal', trainable=True, name="W_hy")
    
    def get_initial_state(self, inputs=None, batch_size=None, dtype=None):
      batch = batch_size if batch_size is not None else inputs.shape[0]
      return tf.zeros((batch, self.hidden_units))

    def call(self, inputs, states):
      if len(inputs.shape) is 1:
        inputs = tf.expand_dims(inputs, 0)
      if states is None:
        initial_states = self.get_initial_state(inputs)
      else:
        initial_states = states[0]
      #h_t = w_hh.prev_h + w_xh.inputs
      input_to_h =  tf.matmul(inputs, self.w_xh)
      weighted_prev_state =  tf.matmul(initial_states, self.w_hh) 
      next_state = input_to_h + weighted_prev_state
      #h_t = activation(h_t)
      next_state = tf.keras.activations.tanh(next_state)
      #y_t = w_hy.h_t
      output = tf.matmul(next_state, self.w_hy)
      # return y_t, h_t
      return output, next_state

class MyGRUCell(keras.layers.Layer):
    def __init__(self, output_size, hidden_units=10, **kwargs):
      super(MyGRUCell, self).__init__(**kwargs)
      self.hidden_units = hidden_units
      self.output_size = output_size
      self.state_size = hidden_units

    def build(self, input_shape):
      self.w_z = self.add_weight(shape=(input_shape[-1], self.hidden_units), initializer='random_normal', trainable=True, name="W_xh")
      self.w_hh = self.add_weight(shape=(self.hidden_units, self.hidden_units), initializer='random_normal', trainable=True, name="W_hh")
      self.w_hy = self.add_weight(shape=(self.hidden_units, self.output_size), initializer='random_normal', trainable=True, name="W_hy")
    
    def get_initial_state(self, inputs=None, batch_size=None, dtype=None):
      batch = batch_size if batch_size is not None else inputs.shape[0]
      return tf.zeros((batch, self.hidden_units))
    
    def call(self, inputs, states):
      # TODO write me!
      # Update gate, info to pass on (same as simple RNN up until sigmoid)
      #z_t = \sigma(W^zx_t + U^(z)h_{t-1})

      # Reset Gate, how much to forget
      #r_t = \sigma(W^rx_t + U^rh_{t-1})

      # Current memory context
      # h'_t=tanh(Wx_t + r_t . Uh_{t-1})

      # Final memory, Combination of current context and previous memories
      # h_t=z_t.h_{t-1} + (1-z_t).h'_t

      # Output and state are the same interestingly enough
      return None
