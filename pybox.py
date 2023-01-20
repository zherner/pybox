import argparse
import os


def parse_inputs() -> argparse.Namespace:
    """Parse command line inputs"""

    parser = argparse.ArgumentParser(
        description="Create a template python docker project, with optional AWS Lambda handler."
    )

    parser.add_argument(
        "-n",
        "--name",
        help="The name of the project to create. No spaces.",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-p",
        "--path",
        help="The path/to/dir of the project to create. No spaces.",
        required=True,
        type=str,
    )

    parser.add_argument(
        "-l",
        "--awslambda",
        action="store_true",
        help="If set, this will include the Lambda handler method",
        required=False,
    )
    return parser.parse_args()


class PYBOX:
    def __init__(self, args_in: argparse.Namespace) -> None:
        self._project_name = args_in.name
        self._project_path = args_in.path
        self._project_path_full = self._project_path + "/" + self._project_name
        self._lambda = args_in.awslambda

        self._validate_inputs()

    def _validate_inputs(self):
        check_space = [self._project_name, self._project_path]
        for i in check_space:
            if " " in i:
                raise ValueError(
                    f"The input args '{check_space}' cannot contain spaces."
                )

    def make_project(self):
        """Create the directory and the files for the project"""

        if os.path.exists(self._project_path_full):
            raise ValueError(
                f"The directory '{self._project_path_full}' already exists."
            )
        os.mkdir(self._project_path_full)

        self._mainfile_content()
        self._requirmentsfile()
        self._dockerfile()
        # self._dockercompose()
        self._makefile()

    def _mainfile_content(self):
        """Add content to the main project .py file"""

        # add content to main project file
        f = open(self._project_path_full + "/" + self._project_name + ".py", "a")
        if self._lambda:
            f.write(
                f'\ndef lambda_handler(event, context) -> None:\n  """Lambda entry method"""\n  # Lambda entry handler:\'{self._project_name}.lambda_handler\'\n  print("{self._project_name}")\n\n'
            )
            f.write(
                f'\nif __name__ == "__main__": \n  lambda_handler("", "")  # blank input for testing\n'
            )
        else:
            f.write(f'\nif __name__ == "__main__": \n  print("{self._project_name}")\n')
        f.close()

    def _requirmentsfile(self):
        """Create the project requirements.txt file"""

        # add content to main project file
        f = open(self._project_path_full + "/" + "requirements.txt", "a")
        f.write(f"# Generic requirements.txt\n")
        f.close()

    def _dockerfile(self):
        """Add Dockerfile"""

        f = open(self._project_path_full + "/" + "Dockerfile", "w")
        if self._lambda:
            f.write(
                f"""# Generic dockerfile
FROM public.ecr.aws/lambda/python:latest AS buildStage

COPY ./  ./

RUN  pip3 install --no-cache-dir -r requirements.txt

CMD [ "{self._project_name}.lambda_handler" ]
\n"""
            )
        else:
            f.write(
                f"""# Generic dockerfile
FROM public.ecr.aws/docker/library/python:latest AS buildStage

COPY ./ ./

ENTRYPOINT [ "python3", "{self._project_name}.py" ]
    \n"""
            )
        f.close()

    #     def _dockercompose(self):
    #         """Add docker-compose.yaml"""
    #
    #         f = open(self._project_path_full + "/" + "docker-compose.yaml", "a")
    #         f.write(
    #             f"""# Generic docker-compose
    # version: "3"
    # \n"""
    #         )
    #         f.close()

    def _makefile(self):
        """Add Makefile"""

        f = open(self._project_path_full + "/" + "Makefile", "a")
        f.write(
            f"""# Generic Makefile
.PHONY: clean
.DEFAULT_GOAL := help

help: ## Display this help text
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\033[36m%-30s\033[0m %s\\n", $$1, $$2}}'

build: ## Build image
	docker build --platform=linux/amd64 -t {self._project_name} ./

run: ## Run image in interactive mode
	docker run -it {self._project_name}

clean: ## Remove image
	docker rmi -f {self._project_name}
\n"""
        )
        f.close()


if __name__ == "__main__":
    args = parse_inputs()

    p = PYBOX(args)
    p.make_project()
