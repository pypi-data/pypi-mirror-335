from tensorflow import keras

from .functions.filter_patterns import generate_filter_patterns
from .functions.models_and_layers import instantiate_model, get_layer, get_conv_layers
from .functions.stitched_image import stitched_image, concat_images


def display_filters(model_path, layer_name=None, num_filters=16, output_path=None):
    """
        Displays the learned filters of a layer of a pretrained model.

        Parameters:
            model_path (str): The path to the model
            layer_name (str): The layer name respective to the given model
            num_filters (int): Number of filters to display in the layer
            output_path (str): Where to save the visualization

        Returns:
            None
    """
    model = instantiate_model(model_path)
    layer = get_layer(model, layer_name)

    if layer.filters < num_filters:
        num_filters = layer.filters

    feature_extractor = keras.Model(inputs=model.input, outputs=layer.output)

    IMG_SZ = 100

    filters = generate_filter_patterns(
        layer, num_filters, IMG_SZ, feature_extractor)

    stitched_filters = stitched_image(filters, num_filters, IMG_SZ)

    if output_path is None:
        output_path = f"{layer.name}_layer_filters.png"

    keras.utils.save_img(output_path, stitched_filters)


def display_model_filters(model_path, num_filters=16, output_path=None):
    """
        Displays the learned filters of a pretrained model.
        The layers are automatically selected from bottom-mid-top level layers.

        Parameters:
            model_path (str): The path to the model
            num_filters (int): Number of filters to display in the layer
            output_path (str): Where to save the visualization

        Returns:
            None
    """
    model = instantiate_model(model_path)
    conv_layers = get_conv_layers(model)
    conv_layer_names = [conv_layer.name for conv_layer in conv_layers]

    # Percentiles that represent bot-mid-top level layers
    BOT_PERC = [0.15, 0.35]
    MID_PERC = [0.55, 0.65]
    TOP_PERC = [0.75, 0.95]

    percentiles = BOT_PERC + MID_PERC + TOP_PERC

    num_layers = len(conv_layers)

    if num_layers < len(percentiles):
        percentiles = percentiles[:num_layers]

    layer_indices = [int(p * (num_layers - 1)) for p in percentiles]

    # Select layers based on computed indices
    selected_layer_names = [conv_layer_names[i] for i in layer_indices]

    layer_filters = []
    IMG_SZ = 100

    for layer_name in selected_layer_names:
        layer = model.get_layer(layer_name)

        if layer.filters < num_filters:
            num_filters = layer.filters

        feature_extractor = keras.Model(
            inputs=model.input, outputs=layer.output)

        filters = generate_filter_patterns(
            layer, num_filters, IMG_SZ, feature_extractor)

        stitched_filters = stitched_image(filters, num_filters, IMG_SZ)
        layer_filters.append(stitched_filters)

    layer_filters = concat_images(layer_filters, axis=0)

    if output_path is None:
        output_path = f"{model.name}_filters.png"

    keras.utils.save_img(output_path, layer_filters)
