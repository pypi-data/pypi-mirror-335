"""
protein_designer_gui.py

3D Coarse-Grained Protein Designer with full 3D picking,
using PyQt6 + PyOpenGL + color-picking for sphere selection.

This script demonstrates a coarse-grained protein design tool that allows
users to:
  - Create proteins and place centers of mass (COM) in a 3D scene.
  - Create interfaces on those proteins.
  - Define binding rules between interfaces.
  - Visualize and interact with the 3D objects (COMs and interfaces) via
    mouse picking (color-based selection).

Usage:
    python protein_designer.py
"""

import sys
import math
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QLineEdit, QDialogButtonBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

# PyOpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *


###############################################################################
# Data Model Classes
###############################################################################

class Interface:
    """
    Represents an binding interface on a protein, storing a name, 3D position.

    :param name: Short identifier for this interface (e.g. "Interface_A").
    :type name: str
    :param position: The 3D position (x, y, z) of this interface.
    :type position: tuple[float, float, float]
    """
    def __init__(self, name, position):
        self.name = name
        self.position = position

class Protein:
    """
    Represents a protein, storing a list of centers-of-mass (COM) points
    and a list of interfaces.

    :param name: The protein name (e.g. "Protein_0").
    :type name: str
    """
    def __init__(self, name):
        self.name = name
        self.centers_of_mass = []  # [float, float, float]
        self.interfaces = []       # list[Interface]


class BindingRule:
    """
    Defines a binding rule between two interface types.

    :param interface_type_a: First interface type (e.g. "hydrophobic").
    :type interface_type_a: str
    :param interface_type_b: Second interface type (e.g. "electrostatic+").
    :type interface_type_b: str
    :param binding_distance: Maximum allowed distance for binding.
    :type binding_distance: float
    :param orientation: Placeholder for orientation constraint (not used here).
    :type orientation: Optional[Any]
    """
    def __init__(self, interface_type_a, interface_type_b, binding_distance, orientation=None):
        self.interface_type_a = interface_type_a
        self.interface_type_b = interface_type_b
        self.binding_distance = binding_distance
        self.orientation = orientation


class CGModel:
    """
    Holds all proteins and binding rules for the coarse-grained system.
    """
    def __init__(self):
        self.proteins = []      # list[Protein]
        self.binding_rules = [] # list[BindingRule]

    def add_protein(self, protein):
        """
        Add a new Protein to the model.

        :param protein: The Protein object to add.
        :type protein: Protein
        """
        self.proteins.append(protein)

    def add_binding_rule(self, rule):
        """
        Add a binding rule to the model.

        :param rule: The BindingRule to add.
        :type rule: BindingRule
        """
        self.binding_rules.append(rule)

    @staticmethod
    def distance(p1, p2):
        """
        Compute Euclidean distance between two 3D points.

        :param p1: Point (x1, y1, z1).
        :type p1: tuple[float, float, float]
        :param p2: Point (x2, y2, z2).
        :type p2: tuple[float, float, float]
        :return: The distance between p1 and p2.
        :rtype: float
        """
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)
    
###############################################################################
# 3D Viewer with Color Picking
###############################################################################

class GLViewer(QOpenGLWidget):
    """
    A 3D viewer that uses:
      - a perspective camera (orbiting, zoom)
      - color-picking to select existing objects
      - simple ray-plane intersection to place new COMs in 3D if the user clicks empty space.

    :param cg_model: The shared CGModel instance containing proteins and rules.
    :type cg_model: CGModel
    :param main_window: Reference to the main application window.
    :type main_window: MainWindow
    """
    def __init__(self, parent=None, cg_model=None, main_window=None):
        super().__init__(parent)
        self.cg_model = cg_model
        self.main_window = main_window

        # Camera parameters
        self.cam_distance = 40.0
        self.cam_azimuth = 45.0   # horizontal angle
        self.cam_elevation = 25.0 # vertical angle

        # For trackball rotation
        self.last_mouse_x = None
        self.last_mouse_y = None

        # Sizing of the spheres
        self.com_sphere_radius = 0.6
        self.if_sphere_radius = 0.4

        # For highlighting selected object
        self.selected_object_id = None  # stores the ID of whichever sphere was clicked

        # We'll keep a list of "render info" about each sphere for color-picking
        # Each entry in self.sphere_records: dict:
        #   {
        #       "id": unique int,
        #       "type": "com" or "interface",
        #       "protein_index": int,
        #       "com_index" or "interface_index": int,
        #       "position": (x, y, z)
        #   }
        self.sphere_records = []

    def initializeGL(self):
        """
        Initialize OpenGL state, including clearing color and enabling depth test.
        """
        glClearColor(0.95, 0.95, 0.95, 1.0)
        glEnable(GL_DEPTH_TEST)

        # For convenience, initialize GLUT for sphere rendering
        import OpenGL.GLUT
        OpenGL.GLUT.glutInit()

    def resizeGL(self, w, h):
        """
        Handle resizing of the OpenGL viewport.

        :param w: New width.
        :type w: int
        :param h: New height.
        :type h: int
        """
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / float(h) if h else 1.0
        gluPerspective(45.0, aspect, 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """
        Render the scene using the main render pass
        (axes, grid, and spheres for COM and interfaces).
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Set up camera
        cx, cy, cz = self._camera_position()
        gluLookAt(cx, cy, cz, 0, 0, 0, 0, 1, 0)

        # Draw reference objects
        self._draw_axes()
        self._draw_grid()

        # Draw all protein objects (COMs and interfaces)
        self._draw_spheres()

    # -------------------------------------------------------------------------
    # Event Handling
    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """
        Handle mouse press events. Left-click performs color-picking to see if
        a sphere was clicked; if not, we place a new COM in 3D at z=0 plane.

        :param event: The QMouseEvent containing position and button state.
        :type event: QMouseEvent
        """
        if event.button() == Qt.MouseButton.LeftButton:
            x = int(event.position().x())
            y = int(event.position().y())

            # 1) Perform color-picking
            clicked_id = self._pick_at_pixel(x, y)

            if clicked_id is not None:
                # We clicked on an existing sphere -> select it
                self.selected_object_id = clicked_id
                if self.main_window:
                    self.main_window.on_sphere_selected(clicked_id)
                self.update()
            else:
                # Clicked on empty space -> place a new COM in 3D
                plane_z = 0.0
                world_pos = self._ray_plane_intersect(x, y, plane_z)
                if self.main_window:
                    self.main_window.place_com_at(world_pos)
                self.update()

        # Track last mouse position for potential dragging
        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()

    def mouseMoveEvent(self, event):
        """
        Handle mouse move events. If the right mouse button is held,
        orbit (rotate) the camera.

        :param event: The QMouseEvent containing new mouse position.
        :type event: QMouseEvent
        """
        if event.buttons() & Qt.MouseButton.RightButton:
            dx = (event.position().x() - self.last_mouse_x) * 0.5
            dy = (event.position().y() - self.last_mouse_y) * 0.5
            self.cam_azimuth += dx
            self.cam_elevation -= dy
            self.update()

        self.last_mouse_x = event.position().x()
        self.last_mouse_y = event.position().y()

    def wheelEvent(self, event):
        """
        Handle mouse wheel events to zoom the camera in/out.

        :param event: The QWheelEvent.
        :type event: QWheelEvent
        """
        delta = event.angleDelta().y()
        self.cam_distance -= delta * 0.05
        if self.cam_distance < 1.0:
            self.cam_distance = 1.0
        self.update()

    # -------------------------------------------------------------------------
    # Camera & Scene Drawing
    # -------------------------------------------------------------------------
    def _camera_position(self):
        """
        Convert spherical (distance, azimuth, elevation) to a 3D camera position.

        :return: (cam_x, cam_y, cam_z)
        :rtype: tuple[float, float, float]
        """
        rad_az = math.radians(self.cam_azimuth)
        rad_el = math.radians(self.cam_elevation)
        cx = self.cam_distance * math.cos(rad_el) * math.sin(rad_az)
        cy = self.cam_distance * math.sin(rad_el)
        cz = self.cam_distance * math.cos(rad_el) * math.cos(rad_az)
        return (cx, cy, cz)

    def _draw_axes(self):
        """
        Draw simple RGB axes at the origin for reference.
        """
        from OpenGL.GL import glBegin, glEnd, glVertex3f, glColor3f, GL_LINES
        glBegin(GL_LINES)
        # x-axis = red
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(5, 0, 0)
        # y-axis = green
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 5, 0)
        # z-axis = blue
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 5)
        glEnd()

    def _draw_grid(self):
        """
        Draw a simple grid on the XZ plane (y=0) for reference.
        """
        glColor3f(0.75, 0.75, 0.75)
        size = 20
        step = 2
        from OpenGL.GL import glBegin, glEnd, glVertex3f, GL_LINES
        for i in range(-size, size + 1, step):
            glBegin(GL_LINES)
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            glEnd()
            glBegin(GL_LINES)
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
            glEnd()

    def _draw_spheres(self):
        """
        Draw all COM and interface spheres from the CGModel.
        Also track them in self.sphere_records for picking.
        Highlight the selected sphere if self.selected_object_id is set.
        """
        self.sphere_records.clear()
        current_id = 1  # ID 0 is reserved for background

        # Access GLUT's sphere function
        from OpenGL.GLUT import glutSolidSphere

        # Iterate over proteins
        for p_idx, protein in enumerate(self.cg_model.proteins):
            # 1) Draw each COM
            for c_idx, com_pos in enumerate(protein.centers_of_mass):
                record = {
                    "id": current_id,
                    "type": "com",
                    "protein_index": p_idx,
                    "com_index": c_idx,
                    "position": com_pos
                }
                self.sphere_records.append(record)

                is_selected = (self.selected_object_id == current_id)

                glPushMatrix()
                glTranslatef(*com_pos)
                if is_selected:
                    # highlight = bright yellow
                    glColor3f(1.0, 1.0, 0.0)
                else:
                    # normal = bluish
                    glColor3f(0.2, 0.2, 0.8)
                glutSolidSphere(self.com_sphere_radius, 20, 20)
                glPopMatrix()

                current_id += 1

            # 2) Draw each interface
            for i_idx, interface in enumerate(protein.interfaces):
                record = {
                    "id": current_id,
                    "type": "interface",
                    "protein_index": p_idx,
                    "interface_index": i_idx,
                    "position": interface.position
                }
                self.sphere_records.append(record)

                is_selected = (self.selected_object_id == current_id)

                glPushMatrix()
                glTranslatef(*interface.position)
                if is_selected:
                    glColor3f(1.0, 1.0, 0.0)  # highlight
                else:
                    # color by interface type
                    itype = interface.interface_type.lower()
                    if itype.startswith("hydro"):
                        glColor3f(0.0, 1.0, 0.0)  # green
                    elif itype.startswith("electro"):
                        glColor3f(1.0, 0.0, 0.0)  # red
                    else:
                        glColor3f(0.8, 0.6, 0.1)  # e.g. yellowish
                glutSolidSphere(self.if_sphere_radius, 20, 20)
                glPopMatrix()

                current_id += 1

    # -------------------------------------------------------------------------
    # Color-Picking Pass
    # -------------------------------------------------------------------------
    def _pick_at_pixel(self, x, y):
        """
        Renders the scene in a hidden "picking pass" where each sphere is drawn
        with a unique color encoding its ID. We then read back the color at
        (x,y). If it matches a sphere, return that sphere's ID; else None.

        :param x: X-coordinate in window space.
        :type x: int
        :param y: Y-coordinate in window space.
        :type y: int
        :return: The ID of the clicked sphere, or None if background.
        :rtype: Optional[int]
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Set the camera
        cx, cy, cz = self._camera_position()
        gluLookAt(cx, cy, cz, 0, 0, 0, 0, 1, 0)

        # Render spheres in a unique flat color
        self._draw_spheres_in_pick_mode()

        # Finish
        glFlush()

        # Read back the pixel.
        # OpenGL uses bottom-left origin, while Qt uses top-left.
        # Invert y to match OpenGL's coordinate system.
        h = self.height()
        real_y = h - y - 1

        pixel = glReadPixels(x, real_y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)
        (r, g, b, a) = pixel[0][0]
        picked_id = self._color_to_id(r, g, b)

        if picked_id == 0:
            return None
        return picked_id

    def _draw_spheres_in_pick_mode(self):
        """
        Draw each sphere in a unique color (derived from "id") for picking.
        No lighting or shading is applied here.
        """
        self.sphere_records.clear()
        current_id = 1
        from OpenGL.GLUT import glutSolidSphere

        for p_idx, protein in enumerate(self.cg_model.proteins):
            # COMs
            for c_idx, com_pos in enumerate(protein.centers_of_mass):
                record = {
                    "id": current_id,
                    "type": "com",
                    "protein_index": p_idx,
                    "com_index": c_idx,
                    "position": com_pos
                }
                self.sphere_records.append(record)

                color = self._id_to_color(current_id)
                glColor3f(*color)
                glPushMatrix()
                glTranslatef(*com_pos)
                glutSolidSphere(self.com_sphere_radius, 10, 10)
                glPopMatrix()

                current_id += 1

            # Interfaces
            for i_idx, interface in enumerate(protein.interfaces):
                record = {
                    "id": current_id,
                    "type": "interface",
                    "protein_index": p_idx,
                    "interface_index": i_idx,
                    "position": interface.position
                }
                self.sphere_records.append(record)

                color = self._id_to_color(current_id)
                glColor3f(*color)
                glPushMatrix()
                glTranslatef(*interface.position)
                glutSolidSphere(self.if_sphere_radius, 10, 10)
                glPopMatrix()

                current_id += 1

    @staticmethod
    def _id_to_color(obj_id):
        """
        Encode an integer ID into an RGB color in [0..1].
        We only handle IDs up to about 16 million.

        :param obj_id: The integer ID of the object.
        :type obj_id: int
        :return: (r, g, b) each in [0..1]
        :rtype: tuple[float, float, float]
        """
        r = (obj_id & 0x000000FF) / 255.0
        g = ((obj_id & 0x0000FF00) >> 8) / 255.0
        b = ((obj_id & 0x00FF0000) >> 16) / 255.0
        return (r, g, b)

    @staticmethod
    def _color_to_id(r, g, b):
        """
        Decode an (R,G,B) in [0..255] back into an integer ID.

        :param r: Red channel in [0..255].
        :type r: int
        :param g: Green channel in [0..255].
        :type g: int
        :param b: Blue channel in [0..255].
        :type b: int
        :return: The object ID encoded in these color channels.
        :rtype: int
        """
        return (r + (g << 8) + (b << 16))

    # -------------------------------------------------------------------------
    # Simple Ray–Plane Intersection
    # -------------------------------------------------------------------------
    def _ray_plane_intersect(self, x, y, plane_z=0.0):
        """
        Cast a ray from the camera through (x,y) in window coordinates,
        find intersection with a plane z=plane_z, and return (ix, iy, iz).

        :param x: X-coordinate in window space.
        :type x: float
        :param y: Y-coordinate in window space.
        :type y: float
        :param plane_z: The Z-value of the plane to intersect.
        :type plane_z: float
        :return: The intersection point (x, y, plane_z). If the ray is parallel
                 or behind, returns (0.0, 0.0, plane_z).
        :rtype: tuple[float, float, float]
        """
        w = self.width()
        h = self.height()
        # Convert (x, y) to normalized device coords
        ndc_x = 2.0 * (x / w) - 1.0
        ndc_y = 1.0 - 2.0 * (y / h)

        # Camera position
        cx, cy, cz = self._camera_position()
        cam_pos = np.array([cx, cy, cz], dtype=np.float64)
        center = np.array([0.0, 0.0, 0.0], dtype=np.float64)
        up_vec = np.array([0.0, 1.0, 0.0], dtype=np.float64)

        # Build forward/right/up from camera
        forward = center - cam_pos
        forward /= np.linalg.norm(forward)
        right = np.cross(forward, up_vec)
        right /= np.linalg.norm(right)
        up = np.cross(right, forward)
        up /= np.linalg.norm(up)

        # For 45 deg FOV, near=0.1, half-height ~ 0.1 * tan(22.5°)
        near_dist = 0.1
        half_height = near_dist * math.tan(math.radians(45.0 / 2.0))
        aspect = w / float(h)
        half_width = half_height * aspect

        # Transform NDC to point on near plane
        local_x = ndc_x * half_width
        local_y = ndc_y * half_height

        near_pt = cam_pos + forward * near_dist + right * local_x + up * local_y
        ray_dir = near_pt - cam_pos
        ray_dir /= np.linalg.norm(ray_dir)

        # Solve intersection with plane z=plane_z
        denom = ray_dir[2]
        if abs(denom) < 1e-9:
            return (0.0, 0.0, plane_z)
        t = (plane_z - cam_pos[2]) / denom
        if t < 0:
            return (0.0, 0.0, plane_z)

        intersect = cam_pos + t * ray_dir
        return (float(intersect[0]), float(intersect[1]), float(intersect[2]))


###############################################################################
# Dialogs
###############################################################################

class NewInterfaceDialog(QDialog):
    """
    Dialog to collect a new interface's name and type.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Interface")

        layout = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Interface name (e.g. Interface_A)")

        layout.addWidget(QLabel("Interface Name:"))
        layout.addWidget(self.name_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def get_data(self):
        """
        Retrieve the user-input name and interface type from the dialog.

        :return: (name, interface_type)
        :rtype: tuple[str, str]
        """
        return self.name_edit.text().strip(), self.type_edit.text().strip()


class NewBindingRuleDialog(QDialog):
    """
    Dialog to collect a binding rule with two interface types and a distance.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Binding Rule")

        layout = QVBoxLayout()
        self.type_a_edit = QLineEdit()
        self.type_a_edit.setPlaceholderText("Interface Type A")
        self.type_b_edit = QLineEdit()
        self.type_b_edit.setPlaceholderText("Interface Type B")
        self.dist_edit = QLineEdit()
        self.dist_edit.setPlaceholderText("Binding Distance")

        layout.addWidget(QLabel("Interface Type A:"))
        layout.addWidget(self.type_a_edit)
        layout.addWidget(QLabel("Interface Type B:"))
        layout.addWidget(self.type_b_edit)
        layout.addWidget(QLabel("Binding Distance:"))
        layout.addWidget(self.dist_edit)

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def get_data(self):
        """
        Return the binding rule parameters from user input.

        :return: (interface_type_a, interface_type_b, binding_distance)
        :rtype: tuple[str, str, float]
        """
        a_type = self.type_a_edit.text().strip()
        b_type = self.type_b_edit.text().strip()
        dist_str = self.dist_edit.text().strip()
        try:
            dist = float(dist_str)
        except ValueError:
            dist = 0.0
        return a_type, b_type, dist


###############################################################################
# Main Window
###############################################################################

class MainWindow(QMainWindow):
    """
    The main window of the CG Protein Designer. Provides controls to:
      - Add proteins
      - Add interfaces
      - Define binding rules
      - Check bindings
      - Interact with the 3D viewer for placing COMs and selecting objects
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D CG Protein Designer with PyQt6")

        self.cg_model = CGModel()
        self.current_protein = None  # The active protein for adding COMs/interfaces

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # Left control panel
        panel_layout = QVBoxLayout()
        main_layout.addLayout(panel_layout, 0)

        self.info_label = QLabel("No protein selected.")
        panel_layout.addWidget(self.info_label)

        btn_add_protein = QPushButton("Add Protein")
        btn_add_protein.clicked.connect(self.on_add_protein)
        panel_layout.addWidget(btn_add_protein)

        btn_add_interface = QPushButton("Add Interface (to Active Protein)")
        btn_add_interface.clicked.connect(self.on_add_interface)
        panel_layout.addWidget(btn_add_interface)

        btn_add_rule = QPushButton("Add Binding Rule")
        btn_add_rule.clicked.connect(self.on_add_rule)
        panel_layout.addWidget(btn_add_rule)

        self.protein_selector = QComboBox()
        self.protein_selector.currentIndexChanged.connect(self.on_protein_selected)
        panel_layout.addWidget(self.protein_selector)

        btn_check_bindings = QPushButton("Check Bindings")
        btn_check_bindings.clicked.connect(self.on_check_bindings)
        panel_layout.addWidget(btn_check_bindings)

        panel_layout.addStretch()

        # The 3D viewer on the right
        self.gl_viewer = GLViewer(cg_model=self.cg_model, main_window=self)
        main_layout.addWidget(self.gl_viewer, 1)

        self.resize(1200, 800)
        self.show()

    def on_add_protein(self):
        """
        Create a new Protein, add it to the model,
        and make it the active protein.
        """
        name = f"Protein_{len(self.cg_model.proteins)}"
        p = Protein(name)
        self.cg_model.add_protein(p)
        self.protein_selector.addItem(name)
        self.protein_selector.setCurrentIndex(self.protein_selector.count() - 1)
        self.log(f"Created {name}")

    def on_add_interface(self):
        """
        Create a new interface on the current protein, near its last COM or at (0,0,0).
        """
        if not self.current_protein:
            QMessageBox.warning(self, "No Protein", "Select/create a protein first.")
            return

        dlg = NewInterfaceDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, itype = dlg.get_data()
            if not name or not itype:
                QMessageBox.warning(self, "Invalid", "Interface name/type cannot be empty.")
                return
            # Place the interface near the last COM or at (0,0,0).
            if self.current_protein.centers_of_mass:
                x, y, z = self.current_protein.centers_of_mass[-1]
                int_pos = (x + 1.0, y, z)
            else:
                int_pos = (0, 0, 0)

            new_if = Interface(name, int_pos, itype)
            self.current_protein.interfaces.append(new_if)
            self.log(f"Added interface '{name}' ({itype}) to {self.current_protein.name}")
            self.gl_viewer.update()

    def on_add_rule(self):
        """
        Create and add a binding rule to the CG model.
        """
        dlg = NewBindingRuleDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            a_type, b_type, dist = dlg.get_data()
            if not a_type or not b_type or dist <= 0:
                QMessageBox.warning(self, "Invalid Rule", "Interface types can't be empty and distance > 0.")
                return
            rule = BindingRule(a_type, b_type, dist)
            self.cg_model.add_binding_rule(rule)
            self.log(f"Added rule: {a_type} <-> {b_type}, max dist={dist}")

    def on_protein_selected(self, index):
        """
        Update the active protein when the user selects a different protein.

        :param index: Index in the protein_selector combo box.
        :type index: int
        """
        if 0 <= index < len(self.cg_model.proteins):
            self.current_protein = self.cg_model.proteins[index]
            self.info_label.setText(f"Active Protein: {self.current_protein.name}")
        else:
            self.current_protein = None
            self.info_label.setText("No protein selected.")

    def on_check_bindings(self):
        """
        Check all pairs of interfaces in all proteins to see if they can bind.
        Displays a dialog with the results.
        """
        results = []
        for p1 in self.cg_model.proteins:
            for i1 in p1.interfaces:
                for p2 in self.cg_model.proteins:
                    if p1 == p2:
                        continue
                    for i2 in p2.interfaces:
                        if self.cg_model.check_binding(i1, i2):
                            results.append(f"{p1.name}:{i1.name} <-> {p2.name}:{i2.name}")
        if results:
            msg = "Possible bindings:\n" + "\n".join(results)
        else:
            msg = "No possible bindings found."
        QMessageBox.information(self, "Bindings", msg)

    def place_com_at(self, pos):
        """
        Called by the GLViewer when user clicks empty space.
        We place a new COM for the active protein at that location.

        :param pos: The (x, y, z) in world coordinates.
        :type pos: tuple[float, float, float]
        """
        if not self.current_protein:
            self.log("No protein selected, ignoring click.")
            return
        self.current_protein.centers_of_mass.append(pos)
        self.log(f"Placed new COM at {pos} in {self.current_protein.name}")
        self.gl_viewer.update()

    def on_sphere_selected(self, sphere_id):
        """
        Called by GLViewer when user clicks an existing sphere (COM or interface).
        Highlights that sphere in the 3D view and logs the selection.

        :param sphere_id: The internal color-picking ID for the selected sphere.
        :type sphere_id: int
        """
        record = None
        for rec in self.gl_viewer.sphere_records:
            if rec["id"] == sphere_id:
                record = rec
                break
        if not record:
            return

        # Identify whether it's a COM or interface, and log it
        if record["type"] == "com":
            self.log(f"Selected COM #{record['com_index']} in {self.cg_model.proteins[record['protein_index']].name}")
        else:
            self.log(f"Selected interface #{record['interface_index']} in {self.cg_model.proteins[record['protein_index']].name}")

    def log(self, msg):
        """
        Display a message on the info_label and print to stdout.

        :param msg: The message text to display.
        :type msg: str
        """
        print(msg)
        self.info_label.setText(msg)


###############################################################################
# Main
###############################################################################

def main():
    """
    Main entry point: sets up the OpenGL format, creates the application and main window,
    then starts the event loop.
    """
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
