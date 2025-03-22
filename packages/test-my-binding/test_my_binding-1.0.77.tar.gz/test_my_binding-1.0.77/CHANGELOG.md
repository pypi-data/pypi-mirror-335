# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

* Changed `scip` version to `9.1` for linux and osx.

### Removed

## [1.0.51] 2025-03-14

### Added

### Changed

* Upload to pip.

### Removed

## [1.0.1] 2025-03-06

### Added

### Changed

* Nanobind integration.

### Removed

* Files related to pybind11.

## [0.7.2] 2024-10-29

### Added

* Added recipe hasher.
* Added `scip` to dev install instructions in README.md
* Added `test_my_binding.straight_skeleton_2.offset_polygon_with_holes`.

### Changed

* Changed name of `test_my_binding.straight_skeleton_2.create_interior_straight_skeleton` to `interior_straight_skeleton`
* Changed name of `test_my_binding.straight_skeleton_2.create_interior_straight_skeleton_with_holes` to `interior_straight_skeleton_with_holes`
* Changed name of `test_my_binding.straight_skeleton_2.create_offset_polygons_2` to `offset_polygon`
* Changed name of `test_my_binding.straight_skeleton_2.create_weighted_offset_polygons_2` to `weighted_offset_polygon`
* Changed version to `scip=9.0.0` for windows.

### Removed

* Removed optional support for GLPK for polygonal surface reconstruction.

## [0.7.1] 2024-09-26

### Added

### Changed

* Changed the return values of `test_my_binding.straight_skeleton_2.create_interior_straight_skeleton` and `test_my_binding.straight_skeleton_2.create_interior_straight_skeleton_with_holes`.
* Changed the return values of `test_my_binding.create_interior_straight_skeleton`.

### Removed

## [0.7.0] 2024-05-14

### Added

* Added `test_my_binding.straight_skeleton_2.create_interior_straight_skeleton`.
* Added `test_my_binding.straight_skeleton_2.create_interior_straight_skeleton_with_holes`.
* Added `test_my_binding.straight_skeleton_2.create_offset_polygons_2_inner`.
* Added `test_my_binding.straight_skeleton_2.create_offset_polygons_2_outer`.
* Added `test_my_binding.straight_skeleton_2.create_weighted_offset_polygons_2_inner`.
* Added `test_my_binding.straight_skeleton_2.create_weighted_offset_polygons_2_outer`.

### Changed

### Removed

## [0.6.0] 2024-02-01

### Added

* Added `test_my_binding.reconstruction.poission_surface_reconstruction`.
* Added `test_my_binding.reconstruction.pointset_outlier_removal`.
* Added `test_my_binding.reconstruction.pointset_reduction`.
* Added `test_my_binding.reconstruction.pointset_smoothing`.
* Added `test_my_binding.reconstruction.pointset_normal_estimation`.
* Added `test_my_binding.skeletonization.mesh_skeleton`.
* Added `test_my_binding.subdivision.mesh_subdivision_catmull_clark`.
* Added `test_my_binding.subdivision.mesh_subdivision_loop`.
* Added `test_my_binding.subdivision.mesh_subdivision_sqrt3`.
* Added `test_my_binding.triangulation.refined_delaunay_mesh`.

### Changed

* Moved main include types like `Point`, `Vector`, `Polyline` and etc. to the `compas` namespace.

### Removed

## [0.5.0] 2022-10-07

### Added

* Support to python 3.10.
* Added Changelog check in PRs.
* Exposing mesh `test_my_binding.booleans.split` function.

### Changed

* Updated github workflow.

### Removed

## [0.4.0] 2022-01-20

### Added

* Added type annotations.
* Added dimension checks to trimesh setters.
* Added `test_my_binding.measure.volume`.
* Added `test_my_binding.subdivision.catmull_clark`.

### Changed

### Removed

## [0.3.0] 2021-12-14

### Added

* Added `test_my_binding.booleans.boolean_union`.
* Added `test_my_binding.booleans.boolean_difference`.
* Added `test_my_binding.booleans.boolean_intersection`.
* Added `test_my_binding.intersections.intersection_mesh_mesh`.
* Added `test_my_binding.meshing.remesh`.
* Added `test_my_binding.slicer.slice_mesh`.
* Added `test_my_binding.triangulation.delaunay_triangulation`.
* Added `test_my_binding.triangulation.constrained_delaunay_triangulation`.
* Added `test_my_binding.triangulation.conforming_delaunay_triangulation`.

### Changed

### Removed
