import os
import sys
import json
import base64
import typing
import shlex
import typer
from typing import List
from typing_extensions import Annotated
from dektools.file import read_lines, remove_path
from dektools.typer import command_mixin, multi_options_to_dict, annotation
from ..artifacts.docker import DockerArtifact
from ..allinone.docker import DockerAllInOne

app = typer.Typer(add_completion=False)


@app.command()
def login(registry, username, password):
    DockerArtifact.login(registry, username, password)


@app.command()
def auths(items: List[str], b64: Annotated[bool, typer.Option("--base64/--no-base64")] = False):
    data_list = []
    for item in items:
        registry, username, password = item.split(':')
        data_list.append(dict(
            registry=registry, username=username, password=password
        ))
    data = DockerArtifact.auths(*data_list)
    if b64:
        result = base64.b64encode(json.dumps(data, indent=4).encode('utf-8')).decode('ascii')
    else:
        result = json.dumps(data)
    sys.stdout.write(result)


@app.command()
def exports(path, items=''):
    if items:
        images = read_lines(items, skip_empty=True)
    else:
        images = DockerArtifact.images()
    DockerArtifact.exports(images, path)


@app.command()
def imports(path, skip=True):
    DockerArtifact.imports(path, skip)


@app.command()
def sync(path, force: Annotated[bool, typer.Option("--force/--no-force")] = True):
    if os.path.exists(path) or force:
        DockerArtifact.exports(DockerArtifact.images(), path)
        DockerArtifact.imports(path)


@app.command()
def sync_keep(
        path, images: List[str],
        running: Annotated[bool, typer.Option("--running/--no-running")] = True,
        tag: Annotated[bool, typer.Option("--tag/--no-tag")] = True
):
    def goon():  # if `docker ps` is empty
        return running or not list(DockerArtifact.container_active(True))

    if not goon():
        return
    image_no_tag = {x.split(':')[0] for x in images}
    for image in DockerArtifact.images():
        if tag:
            ok = image not in images
        else:
            ok = image.split(':')[0] not in image_no_tag
        if ok:
            if goon():
                DockerArtifact.remove(image)
                remove_path(os.path.join(path, DockerArtifact.url_to_filename(image)))
    if goon():
        DockerArtifact.remove_none()


@command_mixin(app)
def cp(args, image, ignore: Annotated[bool, annotation.Option("--ignore/--no-ignore")] = False):
    DockerArtifact.cp(image, *shlex.split(args), ignore=ignore)


@app.command()
def migrate(path, items, registry, ga='', la=''):
    DockerArtifact.imports(path, False)
    for image in read_lines(items, skip_empty=True):
        image_new = f"{registry}/{image.split('/', 1)[-1]}"
        DockerArtifact.tag(image, image_new)
        DockerArtifact.push(image_new, ga=ga, la=la)
        DockerArtifact.remove(image)
        DockerArtifact.remove(image_new)


@app.command()
def clean_none(args=''):
    DockerArtifact.clean_none_images(args)


@app.command()
def build(
        path,
        image: typing.Optional[typing.List[str]] = typer.Option(None),
        basic=None, step=None, base=None,
        arg: typing.Optional[typing.List[str]] = typer.Option(None),
        options=None,
        push: Annotated[bool, typer.Option("--push/--no-push")] = True,
        push_only_last: Annotated[bool, typer.Option("--last/--no-last")] = False
):
    images = multi_options_to_dict(image)
    args = multi_options_to_dict(arg)
    DockerArtifact.build_fast(path, images, basic, step, base, args, options, push, push_only_last)


@app.command(name='push')
def all_in_one_push(registry: str, images: List[str]):
    DockerAllInOne(registry).push(images)


@app.command(name='pull')
def all_in_one_pull(registry: str, images: List[str]):
    DockerAllInOne(registry).pull(images)
