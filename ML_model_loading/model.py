import keras
from keras.layers import Input, Dense, GlobalMaxPooling1D, concatenate
from keras.models import Model
from keras.models import Sequential
from tensorflow.python.keras.layers import Conv1D, Dropout, MaxPooling1D, Flatten
from tensorflow.python.keras.utils.vis_utils import plot_model

import settings

VAL_SPLIT = 0.2
EPOCHS = 20 # může se zvyšit, ale výsledek by to němělo příliš ovlivnit


# větev zpracovávající lokalitu (= rozsah pohybu v okně, tj. cca poloměr kruhu, v němž jsou všechny pozice
def locality_branch():
    input = Input(shape=(1,))
    x = Dense(50, activation='relu')(input) # hodnotu lze měnit 10-100)
    x = Dense(5, activation='relu')(x)
    return Model(inputs=input, outputs=x)

# větev zpravovávající data z polohových a pozičních senzorů
def conv_branch():
    KERNEL_SIZE_1 = 10  # zde lze měnit (3-20)
    POOL_SIZE_1 = 10  # také lze měnit (2-20)
    KERNEL_SIZE_2 = 5  # změny ta 3-10
    POOL_SIZE_2 = 2  # lze mírně zvýšit
    FILTERS_1 = 16 # možná pomůže zvýšení či snížení
    FILTERS_2 = 16 # dtto

    input = Input(shape=(settings.WINDOW_SIZE, len(settings.ATTRIB)))
    x = Conv1D(filters=FILTERS_1, kernel_size=KERNEL_SIZE_1, activation='relu')(input)
    x = Dropout(0.1)(x)
    x = MaxPooling1D(pool_size=POOL_SIZE_1)(x)
    x = Conv1D(filters=FILTERS_2, kernel_size=KERNEL_SIZE_2, activation='relu')(x)
    x = Dropout(0.1)(x)
    x = MaxPooling1D(pool_size=POOL_SIZE_2)(x)
    x = Flatten()(x)
    x = Dense(100, activation='relu')(x) # hodnotu 100 lze měnit (možná bude 10 - 200)
    x = Dense(5, activation='relu')(x) # hodnota by měla zůstat fixní
    return Model(inputs=input, outputs=x)


def mixed_model():
    mx = conv_branch()
    my = locality_branch()
    combined = concatenate([mx.output, my.output])
    x = Dense(2, activation="relu")(combined)
    x = Dense(1, activation='sigmoid')(x)
    model = Model(inputs=[mx.input, my.input], outputs=x)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


if __name__ == "__main__":
    model = mixed_model()
    plot_model(model, to_file='model_plot.png', show_shapes=True)
