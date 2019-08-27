from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout, Conv2D
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard
from tensorflow.keras.applications import VGG19


def create_model(target_size, learning_rate, nb_classes):
    '''
    VGG layers are added manually instead of using 'model.add(conv_base)'
    to make them directly accessible by name
    (eg. model.get_layer('block3_conv2') instead of
         model.get_layer("vgg19').get_layer('block3_conv2')),
    needed for the grad-cam heatmap visualization using tf-explain.
    The first layer is added independently to avoid a ValueError when loading
    the model due to having an implicit InputLayer, uses input_shape instead.
    '''
    model = Sequential()
    conv_base = VGG19(weights='imagenet', include_top=False,
                      input_shape=(*target_size, 3))
    conv_base.trainable = False
    vgg19_first = Conv2D(64, (3, 3), activation='relu', padding='same',
                         name='block1_conv1', input_shape=(*target_size, 3))
    vgg19_first.trainable = True
    model.add(vgg19_first)
    for layer in conv_base.layers[2:]:
        model.add(layer)
    model.add(Flatten())
    model.add(Dense(4096, activation='relu'))
    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(512, activation='relu'))
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dense(nb_classes, activation='softmax'))

    model.summary()
    model.compile(loss='categorical_crossentropy',
                  optimizer=optimizers.RMSprop(lr=learning_rate),
                  metrics=['accuracy'])
    return model
