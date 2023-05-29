from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui


# Create Free Pivot Control Group on selected control
# >>>>>>>>>>>>>>>>>>>>>
#
# copy paste this script to maya script directory
# eg : C:\Users\henry\OneDrive\Documents\maya\2023\scripts
#
# then run the following two lines, and should work when save to shelf button
#
# >>>>>>>>>>>>>>>>>>>>>
# from FreePivot_Anim_prod_ready import FreePivotCreator
# FreePivotCreator.show_dialog()
# >>>>>>>>>>>>>>>>>>>>>




def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class FreePivotCreator(QtWidgets.QDialog):
    free_pivot_creator = None

    @classmethod
    def show_dialog(cls):
        if not cls.free_pivot_creator:
            cls.free_pivot_creator = FreePivotCreator()

        if cls.free_pivot_creator.isHidden():
            cls.free_pivot_creator.show()
        else:
            cls.free_pivot_creator.raise_()
            cls.free_pivot_creator.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(FreePivotCreator, self).__init__(parent)

        self.setWindowTitle('Simple Free Pivot')
        self.setMinimumSize(300, 80)

        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMinimizeButtonHint)
        # self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):

        self.obj_combobox_frame = QtWidgets.QFrame()
        self.obj_combobox_frame.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        self.obj_combobox_frame.setLayout(QtWidgets.QVBoxLayout())

        self.obj_combobox_label = QtWidgets.QLabel("Free Pivot List")
        self.obj_combobox_label.setAlignment(QtCore.Qt.AlignCenter)
        self.obj_combobox = QtWidgets.QComboBox()
        self.obj_combobox.setMinimumWidth(200)

        self.selected_obj_lineedit = QtWidgets.QLineEdit()
        self.selected_obj_lineedit.setReadOnly(True)
        self.selected_obj_lineedit_btn = QtWidgets.QPushButton("Select")
        self.selected_obj_lineedit_label = QtWidgets.QLabel("Target Controller: ")

        self.create_btn = QtWidgets.QPushButton('Create Free Pivot')
        self.create_btn.setEnabled(False)

        self.attach_btn = QtWidgets.QPushButton("Attach")
        self.attach_btn.setEnabled(False)
        self.detach_btn = QtWidgets.QPushButton("Detach")
        self.detach_btn.setEnabled(False)

        self.close_btn = QtWidgets.QPushButton('Close')

        self.delete_btn = QtWidgets.QPushButton("Delete")

    def create_layout(self):

        self.combobox_layout = QtWidgets.QVBoxLayout()
        self.combobox_layout.addWidget(self.obj_combobox_label)
        self.combobox_layout.addWidget(self.obj_combobox)
        self.obj_combobox_frame.layout().addLayout(self.combobox_layout)
        self.obj_combobox_frame.layout().addWidget(self.delete_btn)

        self.selected_obj_lineedit_layout = QtWidgets.QHBoxLayout()
        self.selected_obj_lineedit_layout.addWidget(self.selected_obj_lineedit_label)
        self.selected_obj_lineedit_layout.addWidget(self.selected_obj_lineedit)
        self.selected_obj_lineedit_layout.addWidget(self.selected_obj_lineedit_btn)

        self.attach_detach_layout = QtWidgets.QHBoxLayout()
        self.attach_detach_layout.addWidget(self.attach_btn)
        self.attach_detach_layout.addWidget(self.detach_btn)

        self.button_layout = QtWidgets.QVBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.create_btn)
        self.button_layout.addLayout(self.selected_obj_lineedit_layout)
        self.button_layout.addWidget(self.obj_combobox_frame)
        self.button_layout.addLayout(self.attach_detach_layout)
        self.button_layout.addWidget(self.close_btn)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.button_layout)

    def create_connections(self):
        self.create_btn.clicked.connect(self.create_free_pivot_grp)
        self.close_btn.clicked.connect(self.close)

        self.selected_obj_lineedit_btn.clicked.connect(self.select_obj)

        self.attach_btn.clicked.connect(self.attach)
        self.detach_btn.clicked.connect(self.detach)
        self.delete_btn.clicked.connect(self.delete_grp)

    def select_obj(self):

        if cmds.ls(sl=True):

            if cmds.objExists("FreePivot_Ctrl_Grp"):
                self.sel_obj = cmds.ls(sl=True)

                self.selected_obj_lineedit.setText(self.sel_obj[0])
                self.main_parent = cmds.listRelatives(self.sel_obj, p=True)
            else:
                # self.attach_btn.setEnabled(True)
                self.create_btn.setEnabled(True)
                self.sel_obj = cmds.ls(sl=True)

                self.selected_obj_lineedit.setText(self.sel_obj[0])
                self.main_parent = cmds.listRelatives(self.sel_obj, p=True)
                print(self.main_parent)
        else:
            print("Please Select 1 Controller")

    def attach(self):
        sel_obj = self.selected_obj_lineedit.text()

        self.rename_combobox_item()

        self.detach_btn.setEnabled(True)
        self.obj_combobox.itemData(self.obj_combobox.currentIndex()).attach_grp(sel_obj)

    def detach(self):
        self.attach_btn.setEnabled(True)
        self.obj_combobox.itemData(self.obj_combobox.currentIndex()).detach_grp()

    def create_free_pivot_grp(self):
        name = cmds.ls(sl=True)[0]

        self.attach_btn.setEnabled(True)
        self.create_grp = CreateFreePivotGrp()

        self.obj_combobox.addItem(name + "_FreePivot_Ctrl_Grp", userData=self.create_grp)

    def rename_combobox_item(self):
        new_name = self.selected_obj_lineedit.text()
        new_name = new_name.replace("_Ctrl", "_FreePivot_Ctrl_Grp")

        rename = self.obj_combobox.itemData(self.obj_combobox.currentIndex()).rename(new_name)
        sel_obj_index = self.obj_combobox.currentIndex()
        self.obj_combobox.setItemText(sel_obj_index, new_name)

    def delete_grp(self):
        sel_obj = self.obj_combobox.currentText()
        sel_obj_index = self.obj_combobox.currentIndex()
        cmds.delete(sel_obj)
        self.obj_combobox.removeItem(sel_obj_index)

    ###################################################################


class CreateFreePivotGrp(object):
    def __init__(self):
        if cmds.ls(sl=True):
            pass
        else:
            print("Please Select 1 Controller")

        sel_obj = cmds.ls(sl=True, dag=False)

        for j in sel_obj:
            free_p_main_controller_name = j + "_FreePivot_Ctrl"
            name_parts = free_p_main_controller_name.split('_')
            name_parts[0] = j + '_Suba'
            free_p_sub_controller_name = '_'.join(name_parts)

            parent_control_name = j + '_FreePivot_Ctrl'

            j_position = cmds.xform(j, q=True, ws=True, t=True)
            j_rotation = cmds.xform(j, q=True, ws=True, ro=True)
            self.main_ctrl = cmds.circle(
                n=free_p_main_controller_name,
                c=(0, 0, 0),
                nr=(0, 1, 0),
                sw=360, r=24,
                d=1, ch=False
            )
            cmds.setAttr(self.main_ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(self.main_ctrl[0] + ".overrideColor", 13)
            cmds.xform(self.main_ctrl, t=j_position, ro=j_rotation)

            self.sub_ctrl = cmds.circle(
                n=free_p_sub_controller_name,
                c=(0, 0, 0),
                nr=(0, 1, 0),
                sw=360, r=20,
                d=1, ch=False
            )
            cmds.setAttr(self.sub_ctrl[0] + ".overrideEnabled", 1)
            cmds.setAttr(self.sub_ctrl[0] + ".overrideColor", 17)
            cmds.xform(self.sub_ctrl, t=j_position, ro=j_rotation)
            cmds.select(cl=True)

            self.parent_grp = cmds.group(em=True, n=parent_control_name + "_Grp")
            cmds.select(cl=True)

            cmds.xform(self.parent_grp, ws=True, t=j_position, ro=j_rotation)

            self.null_grp = cmds.group(n=free_p_main_controller_name.split("Ctrl")[0] + 'null', em=True)
            cmds.parent(self.sub_ctrl, self.main_ctrl)
            self.parent_cons = cmds.parentConstraint(self.sub_ctrl[0], self.null_grp, mo=True)
            cmds.select(cl=True)
            cmds.parent(self.null_grp, self.parent_grp)
            cmds.parent(self.main_ctrl, self.parent_grp)

            trans_multi_node = cmds.createNode('multiplyDivide')

            cmds.setAttr(self.main_ctrl[0] + '.rx', lock=True, keyable=False)
            cmds.setAttr(self.main_ctrl[0] + '.ry', lock=True, keyable=False)
            cmds.setAttr(self.main_ctrl[0] + '.rz', lock=True, keyable=False)

            cmds.setAttr(trans_multi_node + '.i2x', -1)
            cmds.setAttr(trans_multi_node + '.i2y', -1)
            cmds.setAttr(trans_multi_node + '.i2z', -1)

            rot_multi_node = cmds.createNode('multiplyDivide')
            cmds.setAttr(rot_multi_node + '.i2x', -1)
            cmds.setAttr(rot_multi_node + '.i2y', -1)
            cmds.setAttr(rot_multi_node + '.i2z', -1)

            cmds.connectAttr(self.main_ctrl[0] + '.translate', '{}.input1'.format(trans_multi_node))
            cmds.connectAttr(self.main_ctrl[0] + '.rotate', '{}.input1'.format(rot_multi_node))

            cmds.connectAttr('{}.output'.format(trans_multi_node),
                             '{}.target[0].targetOffsetTranslate'.format(self.parent_cons[0]))
            cmds.connectAttr('{}.output'.format(rot_multi_node),
                             '{}.target[0].targetOffsetRotate'.format(self.parent_cons[0]))
            cmds.select(cl=True)

    def attach_grp(self, sel_obj):
        self.sel_obj = sel_obj
        self.main_parent = cmds.listRelatives(sel_obj, p=True)

        controller_origin_pos = cmds.xform(self.sel_obj, q=True, ws=True, t=True)
        controller_origin_ro = cmds.xform(self.sel_obj, q=True, ws=True, ro=True)
        controller_origin_scale = cmds.xform(self.sel_obj, q=True, ws=True, s=True)
        cmds.xform(self.parent_grp, ws=True, t=controller_origin_pos, ro=controller_origin_ro,
                   s=controller_origin_scale)
        cmds.parent(self.parent_grp, self.main_parent)
        cmds.parent(self.sel_obj, self.null_grp)

    def detach_grp(self):

        before_detach_pos = cmds.xform(self.sel_obj, q=True, ws=True, t=True)
        before_detach_ro = cmds.xform(self.sel_obj, q=True, ws=True, ro=True)
        before_detach_scale = cmds.xform(self.sel_obj, q=True, ws=True, s=True)

        cmds.parent(self.parent_grp, w=True)
        cmds.parent(self.sel_obj, self.main_parent)

        cmds.xform(self.sel_obj, ws=True, t=before_detach_pos, ro=before_detach_ro, s=before_detach_scale)

    def rename(self, new_name):
        cmds.rename(self.parent_grp, new_name)
        self.parent_grp = new_name

        new_null_name = new_name.replace("_FreePivot_Ctrl_Grp", "_null")
        cmds.rename(self.null_grp, new_null_name)
        self.null_grp = new_null_name

        new_main_ctrl_name = new_name.replace("_FreePivot_Ctrl_Grp", "_FreePivot_Ctrl")
        cmds.rename(self.main_ctrl, new_main_ctrl_name)
        self.main_ctrl = new_main_ctrl_name

        new_sub_ctrl_name = new_name.replace("_FreePivot_Ctrl_Grp", "_Suba_FreePivot_Ctrl")
        cmds.rename(self.sub_ctrl, new_sub_ctrl_name)
        self.sub_ctrl = new_sub_ctrl_name

        new_parent_cons_name = new_name.replace("_FreePivot_Ctrl_Grp", "_null_parentConstraint1")
        cmds.rename(self.parent_cons, new_parent_cons_name)
        self.parent_cons = new_parent_cons_name


###################################################################

if __name__ == '__main__':
    try:
        free_pivot_creator.close()
        free_pivot_creator.deleteLater()
    except:
        pass

    free_pivot_creator = FreePivotCreator()
    free_pivot_creator.show()



