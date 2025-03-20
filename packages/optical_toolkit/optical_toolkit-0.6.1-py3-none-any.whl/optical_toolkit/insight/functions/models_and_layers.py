import tensorflow as tf
import random
from tensorflow.keras.applications import (
    VGG16,
    DenseNet121,
    EfficientNetB0,
    InceptionV3,
    MobileNet,
    ResNet50,
    Xception,
)


def instantiate_model(model_path):
    # Check if model_path corresponds to a pretrained model name
    pretrained_models = {
        "xception": Xception,
        "resnet50": ResNet50,
        "inceptionv3": InceptionV3,
        "vgg16": VGG16,
        "densenet121": DenseNet121,
        "mobilenet": MobileNet,
        "efficientnetb0": EfficientNetB0,
    }

    if model_path.lower() in pretrained_models:
        # Load the corresponding pretrained model
        model = pretrained_models[model_path.lower()](
            weights="imagenet", include_top=False
        )
    else:
        # Load the model from the specified path
        try:
            model = tf.keras.models.load_model(model_path)
        except ValueError as e:
            raise ValueError(f"{e}: Model not found")

    return model


def get_layer(model, layer_name):
    if layer_name is None:
        # Find all convolutional layers in the model
        conv_layers = [
            layer for layer in model.layers if isinstance(layer, tf.keras.layers.Conv2D)
        ]

        if not conv_layers:
            raise ValueError("No convolutional layers found in the model.")

        layer = random.choice(conv_layers)
    else:
        layer = model.get_layer(name=layer_name)

    return layer


def get_conv_layers(model):
    return [
        layer for layer in model.layers if isinstance(layer, tf.keras.layers.Conv2D)
    ]
