from setuptools import setup

name = "types-networkx"
description = "Typing stubs for networkx"
long_description = '''
## Typing stubs for networkx

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`networkx`](https://github.com/networkx/networkx) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `networkx`. This version of
`types-networkx` aims to provide accurate annotations for
`networkx==3.4.2`.

This stub package is marked as [partial](https://peps.python.org/pep-0561/#partial-stub-packages).
If you find that annotations are missing, feel free to contribute and help complete them.


This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/networkx`](https://github.com/python/typeshed/tree/main/stubs/networkx)
directory.

This package was tested with
mypy 1.15.0,
pyright 1.1.396,
and pytype 2024.10.11.
It was generated from typeshed commit
[`45e9a79e2644e5c561dc904f40f15c6659fe3234`](https://github.com/python/typeshed/commit/45e9a79e2644e5c561dc904f40f15c6659fe3234).
'''.lstrip()

setup(name=name,
      version="3.4.2.20250319",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/networkx.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['numpy>=1.20'],
      packages=['networkx-stubs'],
      package_data={'networkx-stubs': ['__init__.pyi', 'algorithms/__init__.pyi', 'algorithms/approximation/__init__.pyi', 'algorithms/approximation/clique.pyi', 'algorithms/approximation/clustering_coefficient.pyi', 'algorithms/approximation/connectivity.pyi', 'algorithms/approximation/distance_measures.pyi', 'algorithms/approximation/dominating_set.pyi', 'algorithms/approximation/kcomponents.pyi', 'algorithms/approximation/matching.pyi', 'algorithms/approximation/maxcut.pyi', 'algorithms/approximation/ramsey.pyi', 'algorithms/approximation/steinertree.pyi', 'algorithms/approximation/traveling_salesman.pyi', 'algorithms/approximation/treewidth.pyi', 'algorithms/approximation/vertex_cover.pyi', 'algorithms/assortativity/__init__.pyi', 'algorithms/assortativity/connectivity.pyi', 'algorithms/assortativity/correlation.pyi', 'algorithms/assortativity/mixing.pyi', 'algorithms/assortativity/neighbor_degree.pyi', 'algorithms/assortativity/pairs.pyi', 'algorithms/asteroidal.pyi', 'algorithms/bipartite/__init__.pyi', 'algorithms/bipartite/basic.pyi', 'algorithms/bipartite/centrality.pyi', 'algorithms/bipartite/cluster.pyi', 'algorithms/bipartite/covering.pyi', 'algorithms/bipartite/edgelist.pyi', 'algorithms/bipartite/extendability.pyi', 'algorithms/bipartite/generators.pyi', 'algorithms/bipartite/matching.pyi', 'algorithms/bipartite/matrix.pyi', 'algorithms/bipartite/projection.pyi', 'algorithms/bipartite/redundancy.pyi', 'algorithms/bipartite/spectral.pyi', 'algorithms/boundary.pyi', 'algorithms/bridges.pyi', 'algorithms/broadcasting.pyi', 'algorithms/centrality/__init__.pyi', 'algorithms/centrality/betweenness.pyi', 'algorithms/centrality/betweenness_subset.pyi', 'algorithms/centrality/closeness.pyi', 'algorithms/centrality/current_flow_betweenness.pyi', 'algorithms/centrality/current_flow_betweenness_subset.pyi', 'algorithms/centrality/current_flow_closeness.pyi', 'algorithms/centrality/degree_alg.pyi', 'algorithms/centrality/dispersion.pyi', 'algorithms/centrality/eigenvector.pyi', 'algorithms/centrality/flow_matrix.pyi', 'algorithms/centrality/group.pyi', 'algorithms/centrality/harmonic.pyi', 'algorithms/centrality/katz.pyi', 'algorithms/centrality/laplacian.pyi', 'algorithms/centrality/load.pyi', 'algorithms/centrality/percolation.pyi', 'algorithms/centrality/reaching.pyi', 'algorithms/centrality/second_order.pyi', 'algorithms/centrality/subgraph_alg.pyi', 'algorithms/centrality/trophic.pyi', 'algorithms/centrality/voterank_alg.pyi', 'algorithms/chains.pyi', 'algorithms/chordal.pyi', 'algorithms/clique.pyi', 'algorithms/cluster.pyi', 'algorithms/coloring/__init__.pyi', 'algorithms/coloring/equitable_coloring.pyi', 'algorithms/coloring/greedy_coloring.pyi', 'algorithms/communicability_alg.pyi', 'algorithms/community/__init__.pyi', 'algorithms/community/asyn_fluid.pyi', 'algorithms/community/centrality.pyi', 'algorithms/community/community_utils.pyi', 'algorithms/community/divisive.pyi', 'algorithms/community/kclique.pyi', 'algorithms/community/kernighan_lin.pyi', 'algorithms/community/label_propagation.pyi', 'algorithms/community/louvain.pyi', 'algorithms/community/lukes.pyi', 'algorithms/community/modularity_max.pyi', 'algorithms/community/quality.pyi', 'algorithms/components/__init__.pyi', 'algorithms/components/attracting.pyi', 'algorithms/components/biconnected.pyi', 'algorithms/components/connected.pyi', 'algorithms/components/semiconnected.pyi', 'algorithms/components/strongly_connected.pyi', 'algorithms/components/weakly_connected.pyi', 'algorithms/connectivity/__init__.pyi', 'algorithms/connectivity/connectivity.pyi', 'algorithms/connectivity/cuts.pyi', 'algorithms/connectivity/disjoint_paths.pyi', 'algorithms/connectivity/edge_augmentation.pyi', 'algorithms/connectivity/edge_kcomponents.pyi', 'algorithms/connectivity/kcomponents.pyi', 'algorithms/connectivity/kcutsets.pyi', 'algorithms/connectivity/stoerwagner.pyi', 'algorithms/connectivity/utils.pyi', 'algorithms/core.pyi', 'algorithms/covering.pyi', 'algorithms/cuts.pyi', 'algorithms/cycles.pyi', 'algorithms/d_separation.pyi', 'algorithms/dag.pyi', 'algorithms/distance_measures.pyi', 'algorithms/distance_regular.pyi', 'algorithms/dominance.pyi', 'algorithms/dominating.pyi', 'algorithms/efficiency_measures.pyi', 'algorithms/euler.pyi', 'algorithms/flow/__init__.pyi', 'algorithms/flow/boykovkolmogorov.pyi', 'algorithms/flow/capacityscaling.pyi', 'algorithms/flow/dinitz_alg.pyi', 'algorithms/flow/edmondskarp.pyi', 'algorithms/flow/gomory_hu.pyi', 'algorithms/flow/maxflow.pyi', 'algorithms/flow/mincost.pyi', 'algorithms/flow/networksimplex.pyi', 'algorithms/flow/preflowpush.pyi', 'algorithms/flow/shortestaugmentingpath.pyi', 'algorithms/flow/utils.pyi', 'algorithms/graph_hashing.pyi', 'algorithms/graphical.pyi', 'algorithms/hierarchy.pyi', 'algorithms/hybrid.pyi', 'algorithms/isolate.pyi', 'algorithms/isomorphism/__init__.pyi', 'algorithms/isomorphism/ismags.pyi', 'algorithms/isomorphism/isomorph.pyi', 'algorithms/isomorphism/isomorphvf2.pyi', 'algorithms/isomorphism/matchhelpers.pyi', 'algorithms/isomorphism/temporalisomorphvf2.pyi', 'algorithms/isomorphism/tree_isomorphism.pyi', 'algorithms/isomorphism/vf2pp.pyi', 'algorithms/isomorphism/vf2userfunc.pyi', 'algorithms/link_analysis/__init__.pyi', 'algorithms/link_analysis/hits_alg.pyi', 'algorithms/link_analysis/pagerank_alg.pyi', 'algorithms/link_prediction.pyi', 'algorithms/lowest_common_ancestors.pyi', 'algorithms/matching.pyi', 'algorithms/minors/__init__.pyi', 'algorithms/minors/contraction.pyi', 'algorithms/mis.pyi', 'algorithms/moral.pyi', 'algorithms/node_classification.pyi', 'algorithms/non_randomness.pyi', 'algorithms/operators/__init__.pyi', 'algorithms/operators/all.pyi', 'algorithms/operators/binary.pyi', 'algorithms/operators/product.pyi', 'algorithms/operators/unary.pyi', 'algorithms/planar_drawing.pyi', 'algorithms/planarity.pyi', 'algorithms/polynomials.pyi', 'algorithms/reciprocity.pyi', 'algorithms/regular.pyi', 'algorithms/richclub.pyi', 'algorithms/shortest_paths/__init__.pyi', 'algorithms/shortest_paths/astar.pyi', 'algorithms/shortest_paths/dense.pyi', 'algorithms/shortest_paths/generic.pyi', 'algorithms/shortest_paths/unweighted.pyi', 'algorithms/shortest_paths/weighted.pyi', 'algorithms/similarity.pyi', 'algorithms/simple_paths.pyi', 'algorithms/smallworld.pyi', 'algorithms/smetric.pyi', 'algorithms/sparsifiers.pyi', 'algorithms/structuralholes.pyi', 'algorithms/summarization.pyi', 'algorithms/swap.pyi', 'algorithms/threshold.pyi', 'algorithms/time_dependent.pyi', 'algorithms/tournament.pyi', 'algorithms/traversal/__init__.pyi', 'algorithms/traversal/beamsearch.pyi', 'algorithms/traversal/breadth_first_search.pyi', 'algorithms/traversal/depth_first_search.pyi', 'algorithms/traversal/edgebfs.pyi', 'algorithms/traversal/edgedfs.pyi', 'algorithms/tree/__init__.pyi', 'algorithms/tree/branchings.pyi', 'algorithms/tree/coding.pyi', 'algorithms/tree/decomposition.pyi', 'algorithms/tree/mst.pyi', 'algorithms/tree/operations.pyi', 'algorithms/tree/recognition.pyi', 'algorithms/triads.pyi', 'algorithms/vitality.pyi', 'algorithms/voronoi.pyi', 'algorithms/walks.pyi', 'algorithms/wiener.pyi', 'classes/__init__.pyi', 'classes/coreviews.pyi', 'classes/digraph.pyi', 'classes/filters.pyi', 'classes/function.pyi', 'classes/graph.pyi', 'classes/graphviews.pyi', 'classes/multidigraph.pyi', 'classes/multigraph.pyi', 'classes/reportviews.pyi', 'convert.pyi', 'convert_matrix.pyi', 'drawing/__init__.pyi', 'drawing/layout.pyi', 'drawing/nx_agraph.pyi', 'drawing/nx_latex.pyi', 'drawing/nx_pydot.pyi', 'drawing/nx_pylab.pyi', 'exception.pyi', 'generators/__init__.pyi', 'generators/atlas.pyi', 'generators/classic.pyi', 'generators/cographs.pyi', 'generators/community.pyi', 'generators/degree_seq.pyi', 'generators/directed.pyi', 'generators/duplication.pyi', 'generators/ego.pyi', 'generators/expanders.pyi', 'generators/geometric.pyi', 'generators/harary_graph.pyi', 'generators/internet_as_graphs.pyi', 'generators/intersection.pyi', 'generators/interval_graph.pyi', 'generators/joint_degree_seq.pyi', 'generators/lattice.pyi', 'generators/line.pyi', 'generators/mycielski.pyi', 'generators/nonisomorphic_trees.pyi', 'generators/random_clustered.pyi', 'generators/random_graphs.pyi', 'generators/small.pyi', 'generators/social.pyi', 'generators/spectral_graph_forge.pyi', 'generators/stochastic.pyi', 'generators/sudoku.pyi', 'generators/time_series.pyi', 'generators/trees.pyi', 'generators/triads.pyi', 'lazy_imports.pyi', 'linalg/__init__.pyi', 'linalg/algebraicconnectivity.pyi', 'linalg/attrmatrix.pyi', 'linalg/bethehessianmatrix.pyi', 'linalg/graphmatrix.pyi', 'linalg/laplacianmatrix.pyi', 'linalg/modularitymatrix.pyi', 'linalg/spectrum.pyi', 'readwrite/__init__.pyi', 'readwrite/adjlist.pyi', 'readwrite/edgelist.pyi', 'readwrite/gexf.pyi', 'readwrite/gml.pyi', 'readwrite/graph6.pyi', 'readwrite/graphml.pyi', 'readwrite/json_graph/__init__.pyi', 'readwrite/json_graph/adjacency.pyi', 'readwrite/json_graph/cytoscape.pyi', 'readwrite/json_graph/node_link.pyi', 'readwrite/json_graph/tree.pyi', 'readwrite/leda.pyi', 'readwrite/multiline_adjlist.pyi', 'readwrite/p2g.pyi', 'readwrite/pajek.pyi', 'readwrite/sparse6.pyi', 'readwrite/text.pyi', 'relabel.pyi', 'utils/__init__.pyi', 'utils/backends.pyi', 'utils/configs.pyi', 'utils/decorators.pyi', 'utils/heaps.pyi', 'utils/mapped_queue.pyi', 'utils/misc.pyi', 'utils/random_sequence.pyi', 'utils/rcm.pyi', 'utils/union_find.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0",
      python_requires=">=3.9",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
