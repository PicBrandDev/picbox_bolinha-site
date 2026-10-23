"""Conversoes B-rep -> malha (so para checagem, render e exportacao)."""
import numpy as np
import cadquery as cq
import trimesh

from . import fab


def _shape(obj):
    if isinstance(obj, cq.Workplane):
        vals = [v for v in obj.vals() if isinstance(v, cq.Shape)]
        return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)
    return obj


def para_trimesh(obj, tol=fab.TOL_LINEAR, ang=fab.TOL_ANGULAR):
    sh = _shape(obj)
    v, t = sh.tessellate(tol, ang)
    m = trimesh.Trimesh(np.array([p.toTuple() for p in v]), np.array(t), process=True)
    m.merge_vertices()
    # o mesher do OCC deixa triangulos de area zero na costura de filetes; remove-los nao muda a geometria
    m.update_faces(m.nondegenerate_faces(height=1e-6))
    m.remove_unreferenced_vertices()
    m.merge_vertices()
    return m


def para_manifold(m):
    import manifold3d as mf
    if not isinstance(m, trimesh.Trimesh):
        m = para_trimesh(m, 0.05, 0.2)
    if not m.is_watertight:
        # GLB/STL antigos vem com vertices duplicados por face (normais)
        m = m.copy()
        m.merge_vertices(merge_tex=True, merge_norm=True, digits_vertex=4)
    r = mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                            tri_verts=np.asarray(m.faces, np.uint32)))
    if r.is_empty():
        # ultimo recurso: casco convexo por corpo (conservador: so aumenta a peca)
        partes = [mf.Manifold.hull_points(np.asarray(c.vertices, np.float32)) for c in m.split(only_watertight=False)]
        r = mf.Manifold.batch_boolean(partes, mf.OpType.Add) if len(partes) > 1 else partes[0]
    return r


def transladar(m, v):
    m = m.copy()
    m.apply_translation(v)
    return m
