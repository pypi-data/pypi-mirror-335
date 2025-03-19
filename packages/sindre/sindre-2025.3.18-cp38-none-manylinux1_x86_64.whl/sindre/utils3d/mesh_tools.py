from functools import cached_property
import numpy as np
import json
from sindre.utils3d.tools import NpEncoder

class SindreMesh:
    """三维网格中转类，假设都是三角面片 """
    def __init__(self, any_mesh=None, vertices=None, faces=None) -> None:
        # 检查传入的参数
        
        if any_mesh is None:
            if any_mesh is None and (vertices is None or faces is None):
                raise ValueError("必须传入 any_mesh 或者同时传入 vertices 和 faces")
            else:
                vertices,faces=np.array(vertices),np.array(faces)
                import vedo
                self.any_mesh=vedo.Mesh([vertices,faces])
        else:
            self.any_mesh = any_mesh

        self.vertices = None
        self.vertex_colors = None
        self.vertex_normals = None
        self.face_normals = None
        self.faces = None
        try:
            self._convert()
        except Exception as e:
            raise RuntimeError(f"转换错误:{e}")
        
    def _convert(self):
        """将模型转换到类中"""
        inputobj_type = str(type(self.any_mesh))
        
        # Trimesh 转换
        if "Trimesh" in inputobj_type or "primitives" in inputobj_type:
            self.vertices = np.asarray(self.any_mesh.vertices, dtype=np.float64)
            self.faces = np.asarray(self.any_mesh.faces, dtype=np.int32)
            self.vertex_normals = np.asarray(self.any_mesh.vertex_normals, dtype=np.float64)
            self.face_normals = np.asarray(self.any_mesh.face_normals, dtype=np.float64)
            
            if self.any_mesh.visual.kind == "face":
                self.vertex_colors = np.asarray(self.any_mesh.visual.face_colors, dtype=np.uint8)
            else:
                self.vertex_colors = np.asarray(self.any_mesh.visual.to_color().vertex_colors, dtype=np.uint8)
        
        # MeshLab 转换
        elif "MeshSet" in inputobj_type:
            import pymeshlab
            mmesh = self.any_mesh.current_mesh()
            self.vertices = np.asarray(mmesh.vertex_matrix(), dtype=np.float64)
            self.faces = np.asarray(mmesh.face_matrix(), dtype=np.int32)
            self.vertex_normals =np.asarray(mmesh.vertex_normal_matrix(), dtype=np.float64)
            self.vertex_colors = (np.asarray(mmesh.vertex_color_matrix()) * 255).astype(np.uint8)
            if mmesh.has_vertex_color():
                self.face_normals = np.asarray(mmesh.face_normal_matrix(), dtype=np.float64) 
            
        
        # Open3D 转换
        elif "open3d" in inputobj_type:
            import open3d as o3d
            self.any_mesh.compute_vertex_normals()
            self.vertices = np.asarray(self.any_mesh.vertices, dtype=np.float64)
            self.faces = np.asarray(self.any_mesh.triangles, dtype=np.int32)
            self.vertex_normals = np.asarray(self.any_mesh.vertex_normals, dtype=np.float64)
            self.face_normals = np.asarray(self.any_mesh.triangle_normals, dtype=np.float64)
            
            if self.any_mesh.has_vertex_colors():
                self.vertex_colors = (np.asarray(self.any_mesh.vertex_colors) * 255).astype(np.uint8)
        
        # Vedo/VTK 转换
        elif "vedo" in inputobj_type or "vtk" in inputobj_type:
            self.any_mesh.compute_normals()
            self.vertices = np.asarray(self.any_mesh.vertices, dtype=np.float64)
            self.faces = np.asarray(self.any_mesh.cells, dtype=np.int32)
            self.vertex_normals =self.any_mesh.vertex_normals
            self.face_normals =self.any_mesh.cell_normals
            self.vertex_colors = self.any_mesh.pointdata["RGBA"]


    def to_trimesh(self):
        """转换成trimesh"""
        import trimesh
        mesh = trimesh.Trimesh(
            vertices=self.vertices,
            faces=self.faces,
            vertex_normals=self.vertex_normals,
            face_normals=self.face_normals
        )
        if self.vertex_colors is not None:
            mesh.visual.vertex_colors = self.vertex_colors
        return mesh

    def to_meshlab(self):
        """转换成meshlab"""
        import pymeshlab
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(
            vertex_matrix=self.vertices,
            face_matrix=self.faces,
        ))
        return ms

    def to_vedo(self):
        """转换成vedo"""
        from vedo import Mesh
        vedo_mesh = Mesh([self.vertices, self.faces])
        if self.vertex_colors is not None:
            vedo_mesh.pointcolors = self.vertex_colors
        return vedo_mesh

    def to_open3d(self):
        """转换成open3d"""
        import open3d as o3d
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(self.vertices)
        mesh.triangles = o3d.utility.Vector3iVector(self.faces)
        if self.vertex_normals is not None:
            mesh.vertex_normals = o3d.utility.Vector3dVector(self.vertex_normals)
        if self.vertex_colors is not None:
            mesh.vertex_colors = o3d.utility.Vector3dVector(self.vertex_colors[...,:3]/255.0)
        return mesh

    def to_dict(self):
        """将属性转换成python字典"""
        return {
            'vertices': self.vertices if self.vertices is not None else [],
            'faces': self.faces if self.faces is not None else [],
            'vertex_colors': self.vertex_colors if self.vertex_colors is not None else [],
            'vertex_normals': self.vertex_normals if self.vertex_normals is not None else []
        }

    def to_json(self):
        """转换成json"""
        return json.dumps(self.to_dict(),cls=NpEncoder)

    
    def to_torch(self):
        """将顶点&面片转换成torch形式

        Returns:
            v,f : 顶点，面片
        """
        import torch
        v= torch.from_numpy(self.vertices)
        f= torch.from_numpy(self.faces)
        return v,f 
        
    def to_pytorch3d(self):
        """转换成pytorch3d形式

        Returns:
            mesh : pytorch3d类型mesh
        """
        from pytorch3d.structures import Meshes
        v,f= self.to_torch()
        mesh = Meshes(verts=v[None], faces=f[None])
        return mesh
    
    def show(self,labels=None,exclude_list=[0]):
        """
        渲染展示网格数据，并根据标签添加标记和坐标轴。

        Args:
            labels (numpy.ndarray, optional): 网格顶点的标签数组，默认为None。如果提供，将根据标签为顶点着色，并为每个非排除标签添加标记。
            exclude_list (list, optional): 要排除的标签列表，默认为[0]。列表中的标签对应的标记不会被显示。

        Returns:
            None: 该方法没有返回值，直接进行渲染展示。
        """
        import vedo
        from sindre.utils3d.tools import labels2colors
        mesh_vd=self.to_vedo()
        show_list=[]
        if labels is not None:
            labels = labels.reshape(-1)
            fss =self._labels_flag(mesh_vd,labels,exclude_list=exclude_list)
            show_list=show_list+fss
            colors = labels2colors(labels)
            mesh_vd.pointcolors=colors
            self.vertex_colors=colors
            
        show_list.append(mesh_vd)
        show_list.append(self._create_vedo_axes(mesh_vd))
            
        # 渲染
        vp = vedo.Plotter(N=1, title="SindreMesh", bg2="black", axes=3)
        vp.at(0).show(show_list)
        vp.close()
        


    def _create_vedo_axes(self,mesh_vd):
        """
        创建vedo的坐标轴对象。

        Args:
            mesh_vd (vedo.Mesh): vedo的网格对象，用于确定坐标轴的长度。

        Returns:
            vedo.Arrows: 表示坐标轴的vedo箭头对象。
        """
        import vedo
        bounds = mesh_vd.bounds()
        max_length = max([bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]])
        start_points = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
        end_points = [(max_length, 0, 0),(0, max_length, 0),(0, 0, max_length)]
        colors = ['red', 'green', 'blue']
        arrows = vedo.Arrows(start_points, end_points, c=colors, shaft_radius=0.005,head_radius=0.01,head_length=0.02)
        return arrows



    def _labels_flag(self,mesh_vd,labels,exclude_list=[0]):
        """
        根据标签为网格的每个非排除类别创建标记。

        Args:
            mesh_vd (vedo.Mesh): vedo的网格对象。
            labels (numpy.ndarray): 网格顶点的标签数组。
            exclude_list (list, optional): 要排除的标签列表，默认为[0]。列表中的标签对应的标记不会被创建。

        Returns:
            list: 包含所有标记对象的列表。
        """
        fss = []
        for i in np.unique(labels):
            if int(i) not in exclude_list:
                v_i = mesh_vd.vertices[labels == i]
                cent = np.mean(v_i, axis=0)
                fs = mesh_vd.flagpost(f"{i}", cent)
                fss.append(fs)
        return fss
        


    def _count_duplicate_vertices(self):
        """统计重复顶点"""
        return len(self.vertices) - len(np.unique(self.vertices, axis=0)) if self.vertices is not None else 0

    def _count_degenerate_faces(self):
        """统计退化面片"""
        if self.faces is None:
            return 0
        areas = np.linalg.norm(self.face_normals, axis=1)/2
        return np.sum(areas < 1e-8)

    def _count_connected_components(self):
        """计算连通体数量"""
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components
        if self.faces is None:
            return 0
        n = len(self.vertices)
        data = np.ones(len(self.faces)*3)
        rows = self.faces.flatten()
        cols = np.roll(self.faces, shift=1, axis=1).flatten()
        adj = csr_matrix((data, (rows, cols)), shape=(n, n))
        return connected_components(adj, directed=False)

    def _count_unused_vertices(self):
        """统计未使用顶点"""
        if self.vertices is None or self.faces is None:
            return 0
        used = np.unique(self.faces)
        return len(self.vertices) - len(used)

    def _is_watertight(self):
        """判断是否闭合"""
        if self.faces is None:
            return False
        edges = np.concatenate([self.faces[:, :2], self.faces[:, 1:], self.faces[:, [2,0]]])
        unique_edges = np.unique(np.sort(edges, axis=1), axis=0)
        return len(edges) == 2*len(unique_edges)

    def to_texture(self):
        """将颜色转换为纹理贴图"""
        if self.vertex_colors is not None:
            return self.vertex_colors.reshape(-1, 3)
        return None
    
    def check(self):
        """检测数据完整性,正常返回True"""
        checks = [
            self.vertices is not None,
            self.faces is not None,
            not np.isnan(self.vertices).any() if self.vertices is not None else False,
            not np.isinf(self.vertices).any() if self.vertices is not None else False,
            not np.isnan(self.vertex_normals).any() if self.vertex_normals is not None else False
        ]
        return all(checks)
    
    
    
    
    def __repr__(self):
        return self.get_quality
        
    @cached_property
    def get_quality(self):
        """网格质量检测"""
        mesh = self.to_open3d()
        edge_manifold = mesh.is_edge_manifold(allow_boundary_edges=True)
        edge_manifold_boundary = mesh.is_edge_manifold(allow_boundary_edges=False)
        vertex_manifold = mesh.is_vertex_manifold()
        orientable = mesh.is_orientable()
        


        stats = [
            "\033[91m\t网格质量检测: \033[0m",
            f"\033[94m顶点数:             {len(self.vertices) if self.vertices is not None else 0}\033[0m",
            f"\033[94m面片数:             {len(self.faces) if self.faces is not None else 0}\033[0m",
            f"\033[94m网格水密(闭合):     {self._is_watertight()}\033[0m",
            f"\033[94m连通体数量：        {self._count_connected_components()[0]}\033[0m",
            f"\033[94m未使用顶点:         {self._count_unused_vertices()}\033[0m",
            f"\033[94m重复顶点:           {self._count_duplicate_vertices()}\033[0m",
            f"\033[94m网格退化:           {self._count_degenerate_faces()}\033[0m",
            f"\033[94m法线异常:           {np.isnan(self.vertex_normals).any() if self.vertex_normals is not None else True}\033[0m",
            f"\033[94m边为流形:           {edge_manifold}\033[0m",
            f"\033[94m边的边界为流形:     {edge_manifold_boundary}\033[0m",
            f"\033[94m顶点为流形:         {vertex_manifold}\033[0m",
            f"\033[94m可定向:             {orientable}\033[0m",
        ]

        return "\n".join(stats)

    