import keras
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import ImageDataGenerator, center_crop
from keras.layers import Flatten, Dense, Input, Dropout, Activation
from keras.layers.normalization import BatchNormalization
from keras.models import Model
import numpy as np
import pdb
train_datagen = ImageDataGenerator(
        rotation_range=90,
        rescale=1./255,
        zoom_range=0.2,
        horizontal_flip=True)

test_datagen = ImageDataGenerator(rescale=1./255)

train_datagen.config['center_crop_size'] = (224,224)
train_datagen.set_pipeline([center_crop])

test_datagen.config['center_crop_size'] = (224,224)
test_datagen.set_pipeline([center_crop])



dgdx = train_datagen.flow_from_directory(
        '/home/nancy/mvmt_vid_dataset/train/',
        read_formats={'png'},
        target_size=(int(256*(224/192.0)), int(192*(224/192.0))),
        batch_size=32,
        class_mode='binary')

dgdx_val = test_datagen.flow_from_directory(
        '/home/nancy/mvmt_vid_dataset/test/',
        read_formats={'png'},
        target_size=(int(256*(224/192.0)), int(192*(224/192.0))),
        batch_size=32,
        class_mode='binary')

train_datagen.fit_generator(dgdx, nb_iter=100)
test_datagen.fit_generator(dgdx_val, nb_iter=100)

train_generator=dgdx
validation_generator=dgdx_val

base_model = VGG16(input_tensor=(Input(shape=(224, 224, 3))), weights='imagenet', include_top=False)
#base_model = VGG16(input_tensor=(Input(shape=(224, 224, 3))), include_top=False)

x = base_model.output
x = Flatten(name='flatten')(x)
x = Dense(1024,  name='fc1')(x)
x = BatchNormalization()(x)
x = Activation('relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, name='fc2')(x)
x = BatchNormalization()(x)
x = Activation('relu')(x)
#x = Dropout(0.5)(x)
x = Dense(1, name='predictions')(x)
x = BatchNormalization()(x)
predictions = Activation('sigmoid')(x)

#for layer in base_model.layers[:10]:
#    layer.trainable = False

model = Model(input=base_model.input, output=predictions)

sgd = keras.optimizers.SGD(lr=0.001, clipnorm=0.5)

model.compile(optimizer=sgd,
              loss='binary_crossentropy',
              metrics=['accuracy'])

history_callback = model.fit_generator(
        train_generator,
        samples_per_epoch=20000,
        nb_epoch=50,
        validation_data=validation_generator,
        nb_val_samples=800)
#pdb.set_trace()
#loss_history = history_callback.history["loss"]
#numpy_loss_history = np.array(loss_history)
#writefile = open("loss_history.txt", "wb")
with open("loss_history.txt", 'w') as f:
	for key, value in history_callback.history.items():
		f.write('%s:%s\n' % (key, value))

model.save("my_model.h5")

