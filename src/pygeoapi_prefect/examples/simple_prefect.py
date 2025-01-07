"""Example pygeoapi process"""
from pathlib import Path

from prefect import (
    flow,
    get_run_logger,
)
from pygeoapi.process.base import JobError

# don't perform relative imports because otherwise prefect deployment won't
# work properly
from pygeoapi_prefect import schemas
from pygeoapi_prefect.process.base import BasePrefectProcessor
from pygeoapi_prefect.utils import get_storage


# When defining a prefect flow that will be deployed by prefect to some
# infrastructure, be sure to specify persist_result=True - otherwise the
# pygeoapi process manager will not be able to work properly
@flow(
    persist_result=True,
    log_prints=True,
)
def simple_flow(
    self,
    job_id: str,
    execution_request: schemas.ExecuteRequest,
) -> dict:
    """Echo back a greeting message.

    This is a simple prefect flow that does not use any tasks.
    """
    logger = get_run_logger()
    logger.debug(f"Inside the hi_prefect_world flow - locals: {locals()}")
    try:
        name = execution_request.inputs["name"].root
    except KeyError:
        raise JobError("Cannot process without a name")
    else:
        storage_type = self.outputs.get('type', 'LocalFileSystem')
        basepath = self.outputs.get('basepath', f'{Path.home()}/.prefect/storage')
        output_dir = get_storage(storage_type, basepath=basepath)
        msg = execution_request.inputs.get('message')
        message = msg.root if msg is not None else ''
        result_value = f"Hello {name}! {message}".strip()
        filename = f'simple-flow-result-{job_id}.txt'
        output_dir.write_path(filename, result_value.encode('utf-8'))
        return {
            'providers': {
                'my_provider': {
                    'type': storage_type,
                    'basepath': basepath
                }
            },
            'results': [
                {
                    'provider': 'my_provider',
                    'mime_type': 'text/plain',
                    'location': f'{output_dir.basepath}/{filename}',
                    'filename': filename
                }
            ]
        }


class SimpleFlowProcessor(BasePrefectProcessor):
    process_flow = simple_flow

    process_description = schemas.ProcessDescription(
        id="simple-flow",  # id MUST match key given in pygeoapi config
        version="0.0.1",
        title="Simple flow Processor",
        description=(
            "An example processor that is powered by prefect and executes a "
            "simple flow"
        ),
        jobControlOptions=[
            schemas.ProcessJobControlOption.SYNC_EXECUTE,
            schemas.ProcessJobControlOption.ASYNC_EXECUTE,
        ],
        inputs={
            "name": schemas.ProcessInput(
                title="Name",
                description="Some name you think is cool. It will be echoed back.",
                schema=schemas.ProcessIOSchema(type=schemas.ProcessIOType.STRING),
                keywords=["cool-name"],
            ),
            "message": schemas.ProcessInput(
                title="Message",
                description="An optional additional message to be echoed to the world",
                schema=schemas.ProcessIOSchema(type=schemas.ProcessIOType.STRING),
                minOccurs=0,
            ),
        },
        outputs={
            "result": schemas.ProcessOutput(
                schema=schemas.ProcessIOSchema(
                    type=schemas.ProcessIOType.STRING,
                    contentMediaType="text/plain",
                )
            )
        },
        keywords=[
            "process",
            "prefect",
            "example",
        ],
        example={"inputs": {"name": "spiderboy"}},
    )
