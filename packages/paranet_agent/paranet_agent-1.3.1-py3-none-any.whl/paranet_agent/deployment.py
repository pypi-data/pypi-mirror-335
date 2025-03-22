import os
import asyncio
from python_on_whales import docker
from python_on_whales import DockerClient

from .composer import generate_compose

if 'LOCALAPPDATA' in os.environ:
    appdir = os.path.join(os.environ['LOCALAPPDATA'], 'paranet-python')
else:
    appdir = os.path.join(os.environ['HOME'], '.paranet-python')

if not os.path.isdir(appdir):
    os.mkdir(appdir)

def compose_filename(prj):
    folder = os.path.join(appdir, prj)
    if not os.path.isdir(folder):
        os.mkdir(folder)

    return os.path.join(folder, 'docker-compose.yml')

def start_project(filename):
    client = DockerClient(compose_files=[filename])
    client.compose.up(detach=True,wait=True)

def stop_project(filename):
    client = DockerClient(compose_files=[filename])
    client.compose.stop()

def get_testdrive_config():
    for x in docker.ps():
        labels = x.config.labels
        if 'com.docker.compose.project' not in labels:
            continue
        project = labels['com.docker.compose.project']
        nets = list(x.network_settings.networks.keys())
        if len(nets) != 1:
            continue
        network = x.network_settings.networks[nets[0]]
        ports = list(x.network_settings.ports)
        if 'grokit' in x.config.image or 'otonoma' in x.config.image:
            if '3131/tcp' in ports:
                # found broker
                return {'project': project,
                        'broker-ip': network.ip_address,
                        'net': nets[0]}
    return None

async def launch_actors(prj, actors, port, restart):
    loop = asyncio.get_running_loop()

    testdrive = await loop.run_in_executor(None, get_testdrive_config)
    if not testdrive:
        raise Exception('Failed to find Paranet docker-compose environment')

    filename = compose_filename(prj)
    if os.path.isfile(filename):
        if restart:
            print('Stopping actors')
            await loop.run_in_executor(None, lambda: stop_project(filename))
            print('Restarting actors:', ','.join(actors))
        else:
            print('Skipping actors restart')
    else:
        print('Starting actors:', ','.join(actors))

    generate_compose(prj, actors, port, testdrive['project'], testdrive['net'], testdrive['broker-ip'], filename)
    await loop.run_in_executor(None, lambda: start_project(filename))

    print('Actors running')
