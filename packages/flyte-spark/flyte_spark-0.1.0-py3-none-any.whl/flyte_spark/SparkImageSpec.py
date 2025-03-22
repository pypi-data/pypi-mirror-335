from flytekit.image_spec import ImageSpec
from importlib.resources import files
from pathlib import Path
import atexit
import os


class SparkImageSpec(ImageSpec):
    """
    ImageSpec for Spark tasks with ipv6 support.

    Example:
        SparkImageSpec(
            registry="211125663991.dkr.ecr.us-west-2.amazonaws.com",
            packages=["pyarrow"],
            platform="linux/arm64",
        )
    """

    def __post_init__(self):
        """
        Post-initialization for the SparkImageSpec.

        This method is fixing the ipv6 issue with older spark images used by flyte.
        """
        super().__post_init__()

        # Avoid doing anything at runtime if we are in a Flyte execution context
        if os.getenv("FLYTE_INTERNAL_EXECUTION_ID", "false") == "true":
            return

        # Ensure spark plugin is included once
        if "flytekitplugins-spark" not in (self.packages or []):
            self.packages = ["flytekitplugins-spark"] + (self.packages or [])

        # Get the entrypoint script from package resources
        resource_path = files("flyte_spark.resources").joinpath("entrypoint.sh")
        local_script = Path("entrypoint.sh")
        local_script_str = str(local_script)

        # Copy the script to current directory
        with open(local_script, "w") as f:
            f.write(resource_path.read_text())
        local_script.chmod(0o755)  # Make executable

        # Register cleanup
        atexit.register(lambda: local_script.unlink(missing_ok=True))

        # Add build commands
        if local_script_str not in (self.copy or []):
            self.copy = [local_script_str, *(self.copy or [])]

        copy_cmd = f"(cp /opt/entrypoint.sh /opt/entrypoint_old.sh && cp {local_script_str} /opt/entrypoint.sh) || true"
        if copy_cmd not in (self.commands or []):
            self.commands = [copy_cmd, *(self.commands or [])]
