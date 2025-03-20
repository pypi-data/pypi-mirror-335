from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import RandomTreesEmbedding
from sklearn.manifold import (
    MDS,
    TSNE,
    Isomap,
    LocallyLinearEmbedding,
    SpectralEmbedding,
)
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sklearn.pipeline import make_pipeline
from sklearn.random_projection import SparseRandomProjection

from .manifold_aliases import MANIFOLD_ALIASES
from .manifold_type import ManifoldType


def get_manifold(manifold_type: str | ManifoldType, dims, kappa, seed):
    """
    Returns a dimensionality reduction model based on the given manifold type.
    Allows passing either a string or a ManifoldType enum.
    """

    if isinstance(manifold_type, str):
        manifold_type = MANIFOLD_ALIASES.get(manifold_type, manifold_type)
        try:
            manifold_type = ManifoldType(manifold_type)
        except ValueError:
            raise ValueError(
                f"Invalid embedding type: '{manifold_type}'. Valid options: "
                f"{[e.value for e in ManifoldType]}"
            )

    manifold_methods = {
        ManifoldType.RANDOM_PROJECTION: SparseRandomProjection(
            n_components=dims, random_state=seed
        ),
        ManifoldType.TRUNCATED_SVD: TruncatedSVD(n_components=dims),
        ManifoldType.ISOMAP: Isomap(n_neighbors=kappa, n_components=dims),
        ManifoldType.STANDARD_LLE: LocallyLinearEmbedding(
            n_neighbors=kappa, n_components=dims, method="standard"
        ),
        ManifoldType.MODIFIED_LLE: LocallyLinearEmbedding(
            n_neighbors=kappa, n_components=dims, method="modified"
        ),
        ManifoldType.HESSIAN_LLE: LocallyLinearEmbedding(
            n_neighbors=kappa, n_components=dims, method="hessian"
        ),
        ManifoldType.LTSA_LLE: LocallyLinearEmbedding(
            n_neighbors=kappa, n_components=dims, method="ltsa"
        ),
        ManifoldType.MDS: MDS(n_components=dims, n_init=1, max_iter=120, n_jobs=-1),
        ManifoldType.RANDOM_TREES: make_pipeline(
            RandomTreesEmbedding(n_estimators=200, max_depth=5, random_state=seed),
            TruncatedSVD(n_components=dims),
        ),
        ManifoldType.SPECTRAL: SpectralEmbedding(
            n_components=dims, random_state=seed, eigen_solver="arpack"
        ),
        ManifoldType.TSNE: TSNE(
            n_components=dims,
            max_iter=500,
            n_iter_without_progress=150,
            n_jobs=-1,
            random_state=seed,
        ),
        ManifoldType.NCA: NeighborhoodComponentsAnalysis(
            n_components=dims, init="pca", random_state=seed
        ),
    }

    return manifold_methods.get(manifold_type, None)
