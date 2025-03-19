# simple wrapper for Open3D that has look and feel like MVTB

import numpy as np
import spatialmath.base as smb
from spatialmath import SE3
from warnings import warn

import open3d as o3d

try:
    import open3d as o3d

    _open3d = True
except ModuleNotFoundError:
    _open3d = False


class PointCloud:
    def __init__(self, arg, depth_scale=1.0, **kwargs):
        """
        Create new point cloud object

        :param arg: point cloud data as an Open3D or MVTB PointCloud object, 3xN array of points.
        :type arg: :obj:`o3d.geometry.PointCloud`, :obj:`~machinevisiontoolbox.PointCloud`, ndarray(3,N)
        :param depth_scale: depth scale factor, defaults to 1.0
        :type depth_scale: float, optional
        :raises RuntimeError: PointCloud class requires Open3D to be installed: pip install open3d
        :raises ValueError: bad arguments

        This object wraps an Open3D :obj:`open3d.geometry.PointCloud` object.  It can be
        created from:

        - an Open3D point cloud object
        - a 3xN array of point coordinates
        - a depth image as a 1-plane :class:`~machinevisiontoolbox.Image` instance
        - an RGBD image as a 4-plane :class:`~machinevisiontoolbox.Image` instance
        - a tuple of two images (RGB, D) as 3-plane and 1-plane :class:`~machinevisiontoolbox.Image` instances

        .. warning:: Open3D must be installed.

        The wrapped Open3D :obj:`open3d.geometry.PointCloud` object has many methods and properties
        but rather than writing individual wrappers the :func:`__getattr__` picks up these
        references and invokes them on the underlying Open3D object.  Any returned Open3D
        point cloud objects are converted to a :class:`PointCloud` instance.

        :seealso: :func:`__getattr__` :obj:`open3d.geometry.PointCloud` :class:`~machinevisiontoolbox.ImageCore.Image` :class:`~machinevisiontoolbox.Camera.CentralCamera`
        """
        from machinevisiontoolbox import Image

        if not _open3d:
            raise RuntimeError(
                "PointCloud class requires Open3D to be installed: pip install open3d"
            )

        if isinstance(arg, o3d.geometry.PointCloud):
            # Open3D point cloud
            pcd = arg

        elif isinstance(arg, np.ndarray):
            arg = smb.getmatrix(arg, (3, None)).astype("float32")

            # simple point cloud:
            # passed a 3xN array of point coordinates
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(arg.T)

        else:
            raise ValueError(
                "arg must be PointCloud or ndarray, for a depth image use DepthImage() constructor"
            )

        self._pcd = pcd

    @staticmethod
    def _intrinsics(camera):
        """Return an Open3D style camera intrinsic object

        :param camera: camera model
        :type: :class:`~machinevisiontoolbox.Camera.CentralCamera`
        :return: Open3D camera intrinsic object
        :rtype: :class:`open3d.camera.PinholeCameraIntrinsic`
        """
        return o3d.camera.PinholeCameraIntrinsic(
            camera.width, camera.height, *camera.fpix, *camera.pp
        )

    @staticmethod
    def _image(image):
        """Return an Open3D style image object

        :param image: MVTB image
        :type image: :class:`~machinevisiontoolbox.Image` instance
        :return: Open3D image
        :rtype: :class:`open3d.geometry.Image` instance
        """
        img = image.image
        if not img.data.c_contiguous:
            img = img.copy()  # make contiguous
        return o3d.geometry.Image(img)

    def copy(self):
        """
        Copy point cloud

        :return: copy of point cloud
        :rtype: :class:`PointCloud`

        Return a new point cloud instance that contains a copy of
        the point data.
        """
        return self.__class__(o3d.geometry.PointCloud(self._pcd))

    def __len__(self):
        """
        Number of points

        :return: number of points
        :rtype: int
        """
        return np.asarray(self._pcd.points).shape[0]

    # allow methods of o3d.geometry.PointCloud to be invoked indirectly
    def __getattr__(self, name):
        """
        Access Open3D PointCloud methods and attributes

        :param name: method or attribute name
        :type name: str

        If ``P`` is a :class:`PointCloud` then ``P.name`` invokes
        method ``name`` of the underlying :obj:`open3d.geometry.PointCloud`
        object.  For example::

            >>> pcfiltered, ind = pc.remove_radius_outlier(radius=0.2, nb_points=100)
            >>> pc.is_empty()  # invoke is_empty predicate method
            >>> pc.colors   # get colors attribute

        .. note::
            - This is a convenience method to avoid having to explicitly all
              the properties and methods of the Open3D point cloud object.
            - If the method returns a new point cloud object, it is converted to a
              Toolbox :class:`PointCloud` instance.
        """

        def wrapper(*args, **kwargs):
            meth = getattr(self._pcd, name)
            retval = meth(*args, **kwargs)
            if isinstance(retval, tuple):
                return tuple(
                    PointCloud(r) if isinstance(r, o3d.geometry.PointCloud) else r
                    for r in retval
                )
            else:
                return retval

        if hasattr(self._pcd, name):
            if callable(getattr(self._pcd, name)):
                return wrapper
            else:
                return getattr(self._pcd, name)
        else:
            raise ValueError(f"object has no attribute '{name}'")

    def __str__(self):
        """
        Concise string representation of point cloud parameters

        :return: _description_
        :rtype: _type_
        """
        return str(self._pcd)

    def __repr__(self):
        return str(self)

    @property
    def pcd(self):
        return self._pcd

    @property
    def points(self):
        """
        Get points as array

        :return: points as array
        :rtype: ndarray(3,N)

        Points are returned as columns of the array. The columns correspond
        to the same columns in the :property:`colors` and :property:`normal` properties.

        :seealso: :property:`colors` :property:`normals`
        """
        return np.asarray(self._pcd.points).T

    @property
    def colors(self):
        """
        Get point color data as array

        :return: point color
        :rtype: ndarray(3,N)

        Point colors are returned as columns of the array. The columns correspond
        to the same columns in the :property:`points` and :property:`normal` properties.

        :seealso: :property:`points` :property:`normals`
        """
        return np.asarray(self._pcd.colors).T

    @property
    def iscolor(self):
        return self._pcd.has_colors()

    @classmethod
    def Read(cls, filename, *args, **kwargs):
        """
        Create point cloud from file

        :param filename: name of file
        :type filename: str
        :return: new point cloud
        :rtype: :class:`PointCloud` instance

        Read point cloud data from a file using :meth:`~open3d.io.read_point_cloud`.
        Supported filetypes include PLY.

        If the path is not absolute it is first searched for relative
        to the current directory, and if not found, it is searched for in
        the ``data`` folder of the
        ```mvtb_data`` package <https://github.com/petercorke/machinevision-toolbox-python/tree/master/mvtb-data>`_.

        """

        from machinevisiontoolbox import mvtb_path_to_datafile

        filename = mvtb_path_to_datafile("data", filename, string=True)
        pcd = o3d.io.read_point_cloud(filename, *args, **kwargs)
        return cls(pcd)

    @classmethod
    def DepthImage(cls, depth, camera, rgb=None, depth_scale=1.0, **kwargs):
        """Create point cloud from depth image

        Creates a colored or uncolored point cloud.

        :param depth: depth image or an RGBD image.
        :type depth: :class:`~machinevisiontoolbox.Image`
        :param camera: perspective camera model
        :type camera: :class:`~machinevisiontoolbox.Camera.CentralCamera`
        :param rgb: RGB image for colorizing point cloud, defaults to None
        :type rgb: :class:`~machinevisiontoolbox.Image`, optional
        :param depth_scale: depth scale factor, defaults to 1.0
        :type depth_scale: float, optional
        :raises RuntimeError: PointCloud class requires Open3D to be installed: pip install open3d
        :raises ValueError: input images has wrong number of planes

        The depth image is converted to a point cloud using the Open3D, and the pixel
        values are scaled by ``depth_scale``.  If the depth image is a multi-plane image
        then the ``D`` plane is used.

        There are two sources of color for point colorization:

            - RGB planes of the depth image, if present.
            - ``rgb`` is an optional RGB image.

        Camera intrinsics are required and provided by a :class:`~machinevisiontoolbox.CentralCamera` instance.

        """
        from machinevisiontoolbox import Image

        if camera is None:
            raise ValueError("camera model must be provided")
        if not isinstance(depth, Image):
            raise ValueError("depth image must be an Image instance")

        if depth.nplanes == 4:
            rgb = depth["RGB"]
            depth = depth["D"]

        if rgb is None:
            # no RGB, uncolored point cloud
            pcd = o3d.geometry.PointCloud.create_from_depth_image(
                PointCloud._image(depth),
                PointCloud._intrinsics(camera),
                depth_scale=depth_scale,
                **kwargs,
            )
        else:
            # colored point cloud
            rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
                color=PointCloud._image(rgb),
                depth=PointCloud._image(depth),
                depth_scale=depth_scale,
                **kwargs,
            )

            pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
                rgbd_image, PointCloud._intrinsics(camera)
            )

        return cls(pcd)

    def write(self, filename):
        """
        Write point cloud to file

        :param filename: name of file
        :type filename: str
        :return: return status
        :rtype: bool

        The file format is determined by the file extension.
        """
        return o3d.io.write_point_cloud(filename, self._pcd)

    def disp(self, block=False, file=None, **kwargs):
        """
        Display point cloud using Open3D

        :param block: block until window dismissed, defaults to False
        :type block: bool, optional
        :param file: save display as an image, defaults to None
        :type file: str, optional
        :param front: set front vector
        :type front: array_like(3)
        :param lookat: set lookat vector
        :type lookat: array_like(3)
        :param up: set up vector
        :type up: array_like(3)
        :param zoom: set zoom value
        :type zoom: float

        Various viewing options are passed to the Open3D :class:`open3d.visualization.ViewControl`.

        Typing "h" in the display window will print help information to the console.

        :seealso: :class:`open3d.visualization.ViewControl`
        """
        if block:
            o3d.visualization.draw_geometries([self._pcd], **kwargs)
        else:
            # nonblocking display
            vis = o3d.visualization.Visualizer()
            vis.create_window()
            vis.add_geometry(self._pcd)

            # get object to control viewpoint
            view_control = vis.get_view_control()

            # handle the possible options
            if "front" in kwargs:
                view_control.set_front(kwargs["front"])
            if "lookat" in kwargs:
                view_control.set_lookat(kwargs["lookat"])
            if "up" in kwargs:
                view_control.set_up(kwargs["up"])
            if "zoom" in kwargs:
                view_control.set_zoom(kwargs["zoom"])

            # update the display
            vis.poll_events()
            vis.update_renderer()

            # save to file if requested
            if file is not None:
                vis.capture_screen_image(str(file), do_render=False)

    def __rmul__(self, T):
        """
        Overload * opeator to transform points

        :param T: _description_
        :type T: :class:`~spatialmath.pose3d.SE3`
        :return: point cloud
        :rtype: :class:`PointCloud`

        Transform a :class:`PointCloud` by premultiplying by an
        :class:`~spatialmath..pose3d.SE3` instance.

        :seealso: :meth:`transform` :meth:`__imul__`
        """
        if isinstance(T, SE3):
            return self.copy().transform(T)
        else:
            return NotImplemented

    def __imul__(self, T):
        """
        Overload *= opeator to transform points

        :param T: _description_
        :type T: :class:`~spatialmath.pose3d.SE3`
        :return: point cloud
        :rtype: :class:`PointCloud`

        Transform a :class:`PointCloud` by inplace multiplication by an
        :class:`~spatialmath..pose3d.SE3` instance.

        :seealso: :meth:`__rmul__` :meth:`transform`
        """
        if isinstance(T, SE3):
            self.transform(T)
            return self
        else:
            return NotImplemented

    def transform(self, T, inplace=True):
        """
        Transform point cloud

        :param T: _description_
        :type T: :class:`~spatialmath..pose3d.SE3`
        :param inplace: transform points inpace, defaults to True
        :type inplace: bool, optional
        :return: point cloud
        :rtype: :class:`PointCloud`

        If ``inplace`` is False then the point cloud data is copied
        before transformation.

        :seealso: :meth:`__rmul__` :meth:`__imul__`
        """
        if inplace:
            self._pcd.transform(T.A)
            return self
        else:
            new = self.copy()
            new._pcd.transform(T.A)
            return new

    def __add__(self, other):
        """
        Overload the + operator to concatenate point clouds

        :param other: second point cloud
        :type other: :class:`PointCloud`
        :return: concatenated point clouds
        :rtype: :class:`PointCloud`
        """
        pcd = o3d.geometry.PointCloud()
        pcd.points.extend(self.points.T)
        pcd.points.extend(other.points.T)
        pcd.colors.extend(self.colors.T)
        pcd.colors.extend(other.colors.T)
        return self.__class__(pcd)

    def downsample_voxel(self, voxel_size):
        """
        Downsample point cloud by voxelization

        :param voxel_size: voxel dimension
        :type voxel_size: float
        :return: downsampled point cloud
        :rtype: :class:`PointCloud`

        Point cloud resolution is reduced by keeping only one
        point per voxel.

        :seealso: :meth:`downsample_random`
        """
        return self.__class__(self._pcd.voxel_down_sample(voxel_size))

    # random downsample
    def downsample_random(self, fraction, seed=None):
        """
        Downsample point cloud by random selection

        :param fraction: fraction of points to retain
        :type fraction: float
        :param seed: random number seed, defaults to None
        :type seed: int, optional
        :return: downsampled point cloud
        :rtype: :class:`PointCloud`

        Point cloud resolution is reduced by randomly selecting
        a subset of points.

        :seealso: :meth:`downsample_random`
        """
        if seed is None:
            return self.__class__(self._pcd.random_down_sample(fraction))

        if seed >= 0:
            np.random.seed(seed)
        n = len(self)
        ind = np.random.choice(n, int(fraction * n), replace=False)
        return self.__class__(self._pcd.select_by_index(ind))

    def estimate_normals(self, **kwargs):
        """
        Estimate point normals

        Normals are computed and stored within the Open3D point cloud
        object.  They can be:

        - accessed using the ``normals`` property
        - toggled on for display when the point cloud is displayed.

        :seealso: :meth:`disp` :meth:`open3d.geometry.PointCloud.estimate_normals`
        """
        # radius=0.1, max_nn=30
        self._pcd.estimate_normals(
            search_param=o3d.geometry.KDTreeSearchParamHybrid(**kwargs)
        )

    @property
    def normals(self):
        """
        Get point normal data as array

        :return: point normal
        :rtype: ndarray(3,N)

        Point normals are returned as columns of the array.  The columns correspond
        to the same columns in the :property:`points` and :property:`colors` properties.

        :seealso: :meth:`estimate_normals` :property:`points` :property:`colors`
        """
        return np.asarray(self._pcd.normals).T

    def remove_outlier(self, **kwargs):
        """
        Remove point cloud outliers

        :return: cleaned up point cloud
        :rtype: :class:`PointCloud`

        Remove outlying points. Any point with fewer than ``nb_points`` neighbors
        within a radius of ``radius`` is removed.

        :seealso: :meth:`open3d.geometry.PointCloud.remove_radius_outlier`
        """
        warn(
            "This method is deprecated. Use pc.remove_radius_outlier(radius=, nb_points=)[0] instead",
            DeprecationWarning,
            stacklevel=2,
        )
        # nb_points=16, radius=0.2
        pcd, ind = self._pcd.remove_radius_outlier(**kwargs)
        return self.__class__(pcd)

    def segment_plane(self, **kwargs):
        # distance_threshold=0.05,
        # ransac_n=3,
        # num_iterations=1000

        default_dict = dict(ransac_n=3, num_iterations=100)
        kwargs = {**default_dict, **kwargs}

        plane_model, inliers = self._pcd.segment_plane(**kwargs)
        inlier_cloud = self._pcd.select_by_index(inliers)
        outlier_cloud = self._pcd.select_by_index(inliers, invert=True)
        return plane_model, self.__class__(inlier_cloud), self.__class__(outlier_cloud)

    def select(self, ind, invert=False):
        """
        Select points by index

        :param ind: indices or lambda function
        :type ind: ndarray() or callable
        :param invert: exclude points, defaults to False
        :type invert: bool, optional
        :return: subset of point cloud
        :rtype: :class:`PointCloud`

        Create point cloud from points with indices given by integer
        array ``ind``.  If ``invert`` is True then select those points
        not given by ``ind``.

        If ``ind`` is a callable function then it is applied to each column of the
        3xN array of points and the point is included if the function returns True.
        For example::

            >>> pcd.select(lambda p: p[2] < 2)

        will select all points with a z-coordinate less than 2.

        """
        if callable(ind):
            ind = np.where(np.apply_along_axis(ind, axis=0, arr=self.points))[0]
        else:
            ind = np.array(ind)
        return self.__class__(self._pcd.select_by_index(ind, invert=invert))

    def paint(self, color):
        """
        Colorize point cloud

        :param color: color for points
        :type color: array_like(3), str
        :return: colorized point cloud
        :rtype: :class:`PointCloud`

        Paint all points in the point cloud this color.
        """
        self._pcd.paint_uniform_color(color)
        return self

    def ICP(self, data, T0=None, max_correspondence_distance=1, **kwargs):
        """
        Register point cloud using ICP

        :param data: point cloud to register
        :type data: :class:`PointCloud`
        :param T0: initial transform, defaults to None
        :type T0: :class:`~spatialmath..pose3d.SE3`, optional
        :param max_correspondence_distance: distance beyond which correspondence is broken, defaults to 1
        :type max_correspondence_distance: float, optional
        :return: pose of ``data`` with respect to instance poiints
        :rtype: :class:`~spatialmath..pose3d.SE3`

        :seealso: :obj:`open3d.pipelines.registration.TransformationEstimationPointToPoint`
        """
        estimation = o3d.pipelines.registration.TransformationEstimationPointToPoint()

        # Convergence-Criteria for Vanilla ICP
        criteria = o3d.pipelines.registration.ICPConvergenceCriteria(**kwargs)

        if T0 is None:
            T0 = np.eye(4)
        else:
            T0 = T0.A

        status = o3d.pipelines.registration.registration_icp(
            self._pcd, data._pcd, max_correspondence_distance, T0, estimation, criteria
        )
        # voxel_size, save_loss_log)

        T = SE3(smb.trnorm(status.transformation))

        return T, status

    def voxel_grid(self, voxel_size):
        """
        Voxelize point cloud

        :param voxel_size: voxel dimension
        :type voxel_size: float
        :return: voxel grid
        :rtype: :class:`VoxelGrid`
        """
        return VoxelGrid(self, voxel_size)


class VoxelGrid:
    def __init__(self, pcd, voxel_size):
        self._voxels = o3d.geometry.VoxelGrid.create_from_point_cloud(
            pcd._pcd, voxel_size=voxel_size
        )

    def write(self, filename):
        """
        Write voxel grid to file

        :param filename: filename
        :type filename: str

        :seealso: :obj:`open3d.io.write_voxel_grid`
        """
        o3d.io.write_voxel_grid(filename, self._voxels)

    def disp(self, block=True, file=None, **kwargs):
        """
        Display voxel grid

        :param block: block until window is dismissed, defaults to True
        :type block: bool, optional
        :param file: save display to this filename, defaults to None
        :type file: str, optional
        """
        if block:
            o3d.visualization.draw_geometries([self._voxels], **kwargs)
        else:
            # nonblocking display
            vis = o3d.visualization.Visualizer()
            vis.create_window()
            vis.add_geometry(self._voxels)

            # get object to control viewpoint
            view_control = vis.get_view_control()

            # handle the possible options
            if "front" in kwargs:
                view_control.set_front(kwargs["front"])
            if "lookat" in kwargs:
                view_control.set_lookat(kwargs["lookat"])
            if "up" in kwargs:
                view_control.set_up(kwargs["up"])
            if "zoom" in kwargs:
                view_control.set_zoom(kwargs["zoom"])

            render = vis.get_render_option()
            render.mesh_show_wireframe = True

            # update the display
            vis.poll_events()
            vis.update_renderer()

            # save to file if requested
            if file is not None:
                vis.capture_screen_image(str(file), do_render=False)


if __name__ == "__main__":
    from machinevisiontoolbox import mvtb_path_to_datafile

    pcd = PointCloud.Read(mvtb_path_to_datafile("data", "bunny.ply"))
    print(pcd)
    pcd.disp(block=False, file="bun.png")

    # import time
    # time.sleep(4)
