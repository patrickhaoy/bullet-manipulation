import pybullet as p
import roboverse.bullet as bullet
import roboverse.bullet.control as control
import numpy as np


def open_drawer(drawer, num_ts=None, render_obs=None):
    return slide_drawer(drawer, -1, num_ts=num_ts, render_obs=render_obs)


def close_drawer(drawer):
    return slide_drawer(drawer, 1)


def get_drawer_base_joint(drawer):
    joint_names = [control.get_joint_info(drawer, j, 'jointName')
                   for j in range(p.getNumJoints(drawer))]
    drawer_frame_joint_idx = joint_names.index('base_frame_joint')
    return drawer_frame_joint_idx

#['frame', 'base', 'handle_plate_far', 'handle_plate_near', 'handle_r']
def get_drawer_handle_link(drawer):
    link_names = [bullet.get_joint_info(drawer, j, 'link_name')
                  for j in range(bullet.p.getNumJoints(drawer))]
    handle_link_idx = link_names.index('handle_r')
    return handle_link_idx

def get_drawer_bottom_pos(drawer):
    drawer_bottom_pos = bullet.get_link_state(
        drawer, get_drawer_base_joint(drawer))
    return drawer_bottom_pos['pos']

def get_drawer_handle_pos(drawer):
    handle_pos = bullet.get_link_state(
        drawer, get_drawer_handle_link(drawer))
    return handle_pos['pos']

def get_drawer_frame_pos(drawer):
    link_names = [bullet.get_joint_info(drawer, j, 'link_name')
                  for j in range(bullet.p.getNumJoints(drawer))]
    frame_link_idx = link_names.index('frame')
    frame_pos = bullet.get_link_state(
        drawer, frame_link_idx)
    return frame_pos['pos']

def get_drawer_opened_percentage(
        left_opening, min_x_pos, max_x_pos, drawer_x_pos):
    if left_opening:
        return (drawer_x_pos - min_x_pos) / (max_x_pos - min_x_pos)
    else:
        return (max_x_pos - drawer_x_pos) / (max_x_pos - min_x_pos)


def slide_drawer(drawer, direction, num_ts=None, render_obs=None):
    assert direction in [-1, 1]
    # -1 = open; 1 = close
    drawer_frame_joint_idx = get_drawer_base_joint(drawer)

    if not num_ts:
        num_ts = 200 if direction == -1 else 300

        command = np.clip(10 * direction,
                        -10 * np.abs(direction), np.abs(direction))
        # enable fast opening; slow closing
    else:
        command = direction

    # Wait a little before closing
    wait_ts = 30  # 0 if direction == -1 else 30
    control.step_simulation(wait_ts)

    p.setJointMotorControl2(
        drawer,
        drawer_frame_joint_idx,
        controlMode=p.VELOCITY_CONTROL,
        targetVelocity=command,
        force=1
    )

    drawer_pos = get_drawer_bottom_pos(drawer)
    
    control.step_simulation(num_ts)

    p.setJointMotorControl2(
        drawer,
        drawer_frame_joint_idx,
        controlMode=p.VELOCITY_CONTROL,
        targetVelocity=0,
        force=1
    )
    
    control.step_simulation(num_ts)

    return drawer_pos