import os

from gradient_labs import (
    Client,
    Tool,
    ToolParameter,
    ParameterType,
    ParameterOption,
    HTTPDefinition,
)


def main():
    client = Client(api_key=os.environ["GLABS_MGTMT_KEY"])

    tool = client.create_tool(
        tool=Tool(
            name="Launch the rocket",
            description="Send the rocket into the stratosphere",
            parameters=[
                ToolParameter(
                    name="speed",
                    description="How fast the rocket will be launched",
                    type=ParameterType.STRING,
                    required=True,
                    options=[
                        ParameterOption(value="slow", text="Slow"),
                        ParameterOption(value="medium", text="Medium"),
                        ParameterOption(value="warp-speed", text="Warp Speed"),
                    ],
                )
            ],
            http=HTTPDefinition(
                method="POST",
                url_template="https://api.rocket.com/launch",
                header_templates={"Content-Type": "application/json"},
            ),
        )
    )
    print(f"Created: {tool.id}")


if __name__ == "__main__":
    main()
