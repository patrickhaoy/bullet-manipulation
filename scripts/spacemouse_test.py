import roboverse as rv
import numpy as np
import pickle as pkl
from tqdm import tqdm
from roboverse.utils.renderer import EnvRenderer, InsertImageEnv
from roboverse.bullet.misc import quat_to_deg 
import os
from PIL import Image
import argparse

from rlkit.misc.asset_loader import load_local_or_remote_file
def load_vae(vae_file):
    vae = load_local_or_remote_file(vae_file)
    vae.to("cpu")
    print(vae.representation_size)
    return vae

vae_path = "/home/ashvin/data/temp_vqvae/best_vqvae.pt"
model = load_vae(vae_path)

#spacemouse = rv.devices.SpaceMouse(DoF=3)

#env.reset()
images = []
for env_type in ['tray', 'obj',1, 1]:
    env = rv.make('SawyerRigAffordances-v0', test_env=True, env_type='bottom_drawer')
    #print('Iteration: ', j)
    env.demo_reset()

    for i in range(50):
        #img = Image.fromarray(np.uint8(env.render_obs()))

        img = np.uint8(env.render_obs()).transpose() / 255.0
        z = model.encode_one_np(img)
        img_recon = model.decode_one_np(z).transpose() * 255.0

        images.append(Image.fromarray(np.uint8(img_recon)))

        action = env.get_demo_action()
        #env.get_reward(print_stats=True)
        next_observation, reward, done, info = env.step(action)

# env.demo_reset()
# i = 0
# while True:
#     i += 1
#     if i % 50 == 0:
#         env.reset()
#     img = np.uint8(env.render_obs())
#     action = spacemouse.get_action()
#     env.get_reward(print_stats=True)
#     next_obs, rew, term, info = env.step(action)
#     #print(rew)
#     if term: break

images[0].save('/home/ashvin/data/sasha/drawer_test/rollout.gif',
                       format='GIF', append_images=images[1:],
                       save_all=True, duration=100, loop=0)
# images[0].save('/Users/sasha/Desktop/rollout.gif',
#                        format='GIF', append_images=images[1:],
#                        save_all=True, duration=100, loop=0)