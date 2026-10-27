# GRIDH Image processor

Work-in-progress

The image processor is a tool that runs image processing tasks for different other django projects as background tasks. The tasks can be either converting an image to a panorama image by using the pannellum generator or converting an image to IIIF via pyvips (planned).

The service uses PostgreSQL to manage a job queue and background workers that execute the tasks. It comes with a podman compose file to run postgres in a container.

The service expects the following folder structure in a shared volume of the involved django applications where `upload` is usually the media storage of the django instance:
```bash
<project1>/
├── upload/
│   └── digicure-viewer/
|       ├── original/
│       |   ├── panorama/
│       │   │   └── panorama-uuid.jpg
│       |   └── iiif/
│       │   │   └── image-uuid.jpg
|       ├── panorama/
|       |   └── panorama-uuid/
│       |       ├── config.json
│       |       ├── 1/
│       |       ├── 2/
│       |       └── fallback/
|       └── iiif/
|           └── image-uuid.tif
<project2>/
├── upload/
│   └── ...
```

## Installation & Configuration
- Create a virtual environment, we used uv here. And install the requirements from the pyproject.toml file.

- Create a .env in the project root folder image_processor, here an example for local development:

```yaml 
SECRET_KEY=<your-secret-key>
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://image_processor:<password>@localhost:5433/image_processor
PANORAMA_CONTAINER_IMAGE="localhost/pannellum-generator:latest"
```

- Create a config file in image_processor/image_processor/ for project specific configurations and allowed processing types. See projects_config.example.json for an example config file. (Currently panorama-only)

## Containers
For local development run podman compose to run a database container:
```bash
podman-compose up
```

For the pannellum generator, clone the official pannellum repository and build the image which is used by the worker:
```bash
git clone https://github.com/mpetroff/pannellum.git
cd pannellum/utils/multires

podman build -t pannellum-generator .
```
One important detail when working with a RHEL server is to `keep-groups` in the command of the panorama.py service, so the group access on a shared folder is possible for a rootless podman user and the django user of the application.

## Running the service
Start the django service as usual with
```bash
./manage.py runserver
```
which makes the API available at `localhost:8000/api` where you can submit a processing job.

__[tbc]__


