import keras
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import ImageDataGenerator, center_crop
from keras.layers import Flatten, Dense, Input, Dropout, Activation, merge
from keras.layers.normalization import BatchNormalization
from keras.models import Model
from keras.regularizers import l2
from convnetskeras.convnets import convnet
import pickle

import numpy as np
import pdb
train_datagen = ImageDataGenerator(
        rotation_range=40,
        rescale=1./255,
        zoom_range=0.2,
        horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

train_datagen.config['center_crop_size'] = (227,227)
train_datagen.set_pipeline([center_crop])

test_datagen.config['center_crop_size'] = (227,227)
test_datagen.set_pipeline([center_crop])



dgdx = train_datagen.flow_from_directory(
        '/home/wangnxr/dataset/vid_offset_0/train/',
        read_formats={'png'},
        num_frames=4,
        target_size=(int(340), int(256)),
        batch_size=32,
        class_mode='binary')

dgdx_val = test_datagen.flow_from_directory(
        '/home/wangnxr/dataset/vid_offset_0/test/',
        read_formats={'png'},
        num_frames=4,
        target_size=(int(340), int(256)),
        batch_size=32,
        class_mode='binary')
#pdb.set_trace()
train_datagen.fit_generator(dgdx, nb_iter=96)
test_datagen.fit_generator(dgdx_val, nb_iter=96)

train_generator=dgdx
validation_generator=dgdx_val
#pdb.set_trace()
alexnet_model = convnet('alexnet', weights_path="/home/wangnxr/Documents/ecogdeep/convnets-keras/examples/alexnet_weights.h5")
#base_model = VGG16(input_tensor=(Input(shape=(3,224, 224))), include_top=False, weights='imagenet')
base_model = Model(alexnet_model.input, alexnet_model.get_layer("dense_2").output)

frame_a = Input(shape=(3,227,227))
frame_b = Input(shape=(3,227,227))
frame_c = Input(shape=(3,227,227))
frame_d = Input(shape=(3,227,227))


tower1 = base_model(frame_a)
tower2 = base_model(frame_b)
tower3 = base_model(frame_c)
tower4 = base_model(frame_d)
x = merge([tower1, tower2, tower3, tower4], mode='concat')

#x = base_model.output
#x = Flatten(name='flatten')(x)
x = Dropout(0.5)(x)
x = Dense(512, W_regularizer=l2(0.01), name='fc1')(x)
x = BatchNormalization()(x)
x = Activation('relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, W_regularizer=l2(0.01), name='fc2')(x)
x = BatchNormalization()(x)
x = Activation('relu')(x)
x = Dropout(0.5)(x)
x = Dense(1, name='predictions')(x)
#x = BatchNormalization()(x)
predictions = Activation('sigmoid')(x)

#for layer in base_model.layers[:10]:
#    layer.trainable = False

model = Model(input=[frame_a, frame_b, frame_c, frame_d], output=predictions)

sgd = keras.optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9)

model.compile(optimizer=sgd,
              loss='binary_crossentropy',
              metrics=['accuracy'])

history_callback = model.fit_generator(
        train_generator,
        samples_per_epoch=43904,
        nb_epoch=200,
        validation_data=validation_generator,
        nb_val_samples=11232)

model.save("vid_model_alexnet_4towers.h5")
pickle.dump(history_callback.history, open("vid_history_alexnet_4towers.p", "wb"))


