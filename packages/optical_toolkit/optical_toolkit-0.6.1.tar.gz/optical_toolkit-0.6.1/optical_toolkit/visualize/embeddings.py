import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from optical_toolkit.utils import preprocess

from .functions.manifolds import ManifoldType, get_manifold


def get_embeddings(
    X,
    y=None,
    dims: int = 2,
    embedding_type: str | ManifoldType = "TSNE",
    fname="embedding",
    kappa: int = 30,
    return_plot: bool = False,
    seed: int | None = 42,
):
    """
        Given a numpy array of images X, flatten the images
        and plot a 2D or 3D embedding using t-SNE.

        Parameters:
            X (numpy array): Array of images of shape --
                            (num_images, height, width, channels)
                            or (num_images, height, width) for grayscale images.
            dims (int): Number of dims for t-SNE embedding (2 or 3).

        Returns:
            embedding (numpy array): The 2D or 3D embedding.
    """

    if dims not in [2, 3]:
        raise ValueError("dims parameter must be 2 or 3.")

    X = preprocess(X)

    # Get number of images and flatten each image
    num_images = X.shape[0]
    image_size = np.prod(
        X.shape[1:]
    )  # height * width * channels (or height * width for grayscale)
    flat_images = X.reshape(num_images, image_size)

    # Apply t-SNE to reduce dimensionality to 2D or 3D
    manifold_model = get_manifold(embedding_type, dims=dims, kappa=kappa, seed=seed)
    embedding = manifold_model.fit_transform(flat_images)
    embedding = MinMaxScaler().fit_transform(embedding)

    # Assign colors if needed
    colors = "black"
    if y is not None:
        unique_classes = np.unique(y)
        colormap = matplotlib.colormaps.get_cmap("tab10")
        class_to_color = {
            cls: colormap(i / max(1, len(unique_classes) - 1))
            for i, cls in enumerate(unique_classes)
        }
        colors = np.array([class_to_color[label] for label in y])

    # Plot the embedding
    plt.figure(figsize=(8, 6))
    if dims == 2:
        plt.scatter(embedding[:, 0], embedding[:, 1], s=5, c=colors)
        plt.title(f"2D Embedding of Images using {embedding_type}")
        plt.xlabel("Dimension 1")
        plt.ylabel("Dimension 2")
        plt.xticks([])
        plt.yticks([])

        if y is not None:
            legend_labels = [
                plt.Line2D(
                    [0],
                    [0],
                    marker="o",
                    color="w",
                    markerfacecolor=class_to_color[cls],
                    markersize=8,
                )
                for cls in unique_classes
            ]
            plt.legend(legend_labels, unique_classes, title="Classes", loc="best")

    elif dims == 3:
        ax = plt.axes(projection="3d")
        ax.scatter(embedding[:, 0], embedding[:, 1], embedding[:, 2], s=5, c=colors)
        ax.set_title(f"3D Embedding of Images using {embedding_type}")
        ax.set_xlabel("Dimension 1")
        ax.set_ylabel("Dimension 2")
        ax.set_zlabel("Dimension 3")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        if y is not None:
            for cls in unique_classes:
                ax.scatter([], [], [], color=class_to_color[cls], label=str(cls))
            ax.legend(title="Classes", loc="best")

    plt.show()

    return embedding, plt.gcf() if return_plot else embedding
