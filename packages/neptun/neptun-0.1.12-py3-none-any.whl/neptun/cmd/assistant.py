import asyncio
import questionary
import typer
from pydantic_core._pydantic_core import ValidationError
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from neptun.bot.chat import Conversation
from neptun.utils.managers import ConfigManager
from neptun.utils.services import ChatService
from neptun.model.http_responses import ChatsHttpResponse, GeneralErrorResponse, ErrorResponse, CreateChatHttpResponse
from neptun.model.http_requests import CreateChatHttpRequest
from neptun.bot.tui import NeptunChatApp
from rich.markdown import Markdown
from rich.table import Table

# TODO: https://neptun-tools-docs.pages.dev/docs/web-interface/api/api-users-%7Buser_id%7D-chats-%7Bchat_id%7D-messages-last.delete

assistant_app = typer.Typer(name="Neptun Chatbot", help="Start chatting with the neptun-chatbot.")

console = Console()
bot = NeptunChatApp()
chat_service = ChatService()
conversation = Conversation()
config_manager = ConfigManager()


# will automatically start a chat based on the config-files latest id
@assistant_app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        chat()


def print_chat_table(chat):
    table = Table()
    table.add_column(f"Id",
                     justify="left",
                     no_wrap=True)
    table.add_column(f"Name",
                     justify="left",
                     no_wrap=True)
    table.add_column(f"Model",
                     justify="left",
                     no_wrap=True)
    table.add_column(f"Created At",
                     justify="left",
                     no_wrap=True)

    table.add_row(f"{chat.id}",
                  f"{chat.name}",
                  f"{chat.model}",
                  f"{chat.created_at}")

    console.print(table)


def create_new_chat_dialog():
    new_chat_name = questionary.text(
        message="Name the chat:"
    ).ask()

    if new_chat_name is None:
        raise typer.Exit()

    new_chat_model = questionary.select(message="Select a ai-base-model:",
                                        choices=[
                                                'google/gemma-2-27b-it',
                                                'qwen/Qwen2.5-72B-Instruct',
                                                'qwen/Qwen2.5-Coder-32B-Instruct',
                                                'deepseek-ai/DeepSeek-R1-Distill-Qwen-32B',
                                                'mistralai/Mistral-Nemo-Instruct-2407',
                                                'mistralai/Mistral-7B-Instruct-v0.3',
                                                'microsoft/Phi-3-mini-4k-instruct',
                                                'cloudflare/llama-3.3-70b-instruct-fp8-fast',
                                                'openrouter/gemini-2.0-pro-exp-02-05',
                                                'openrouter/deepseek-chat',
                                                'openrouter/llama-3.3-70b-instruct',
                                                'ollama/rwkv-6-world',
                                        ]).ask()
    if new_chat_model is None:
        raise typer.Exit()

    create_chat_http_request = CreateChatHttpRequest(name=new_chat_name, model=new_chat_model)

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="Creating new chat...",
                          total=None)

        result = chat_service.create_chat(create_chat_http_request=create_chat_http_request)

        progress.stop()
        if isinstance(result, CreateChatHttpResponse):

            typer.secho(f"Successfully created a new chat!",
                        fg=typer.colors.GREEN)

            print_chat_table(result.chat)

            config_manager.update_active_chat(id=result.chat.id,
                                              name=result.chat.name,
                                              model=result.chat.model)
        elif isinstance(result, ErrorResponse):
            if result.data:
                table = Table()
                table.add_column(f"Issue: {result.statusCode} - {result.statusMessage}",
                                 justify="left", style="red",
                                 no_wrap=True)
                for issue in result.data.issues:
                    table.add_row(f"{issue.message}")

                console.print(table)
            else:
                typer.secho(f"Issue: {result.statusCode} - {result.statusMessage}",
                            fg=typer.colors.RED)
        elif isinstance(result, GeneralErrorResponse):
            typer.secho(f"{result.statusMessage}",
                        fg=typer.colors.RED)


def enter_available_chats_dialog():
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="Collecting available chats...",
                          total=None)

        result = chat_service.get_available_ai_chats()

        if isinstance(result, ChatsHttpResponse):
            chat_dict = {f"{chat.id}: {chat.name}:[{chat.model}]": chat for chat in result.chats}
            chat_choices = [f"{chat.id}: {chat.name}:[{chat.model}]" for chat in result.chats[:5]]

            progress.stop()

            if result.chats is not None and len(result.chats) > 0:
                action = questionary.select(
                    message="Select an available chat:",
                    choices=chat_choices
                ).ask()

                if action is None:
                    raise typer.Exit()

                selected_chat_object = chat_dict.get(action)

                config_manager.update_active_chat(id=selected_chat_object.id,
                                                  name=selected_chat_object.name,
                                                  model=selected_chat_object.model)
                typer.secho(f"Successfully selected: {selected_chat_object.name}!",
                            fg=typer.colors.GREEN)
            else:
                typer.secho(f"No chats available!",
                            fg=typer.colors.BRIGHT_YELLOW)

        elif isinstance(result, GeneralErrorResponse):
            typer.secho(f"{result.statusMessage}",
                        fg=typer.colors.RED)


def list_available_chats():
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        progress.add_task(description="Collecting available chats...",
                          total=None)

        result = chat_service.get_available_ai_chats()

        if isinstance(result, ChatsHttpResponse):
            progress.stop()
            table = Table()
            table.add_column(f"Name",
                             justify="left",
                             no_wrap=True)
            table.add_column(f"Model",
                             justify="left",
                             no_wrap=True)
            table.add_column(f"Created At",
                             justify="left",
                             no_wrap=True)

            for iterator in result.chats:
                table.add_row(
                              f"{iterator.name}",
                              f"{iterator.model}",
                              f"{iterator.created_at}")
            console.print(table)

        elif isinstance(result, GeneralErrorResponse):
            typer.secho(f"{result.statusMessage}",
                        fg=typer.colors.RED)


def delete_selected_chat_dialog():
    questionary.text(message="")  # necessary but don't know why -> bug appears when running `neptun assistant delete` if non-existent
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        collecting_data_task = progress.add_task(description="Collecting available chats...",
                                                 total=None)

        result = chat_service.get_available_ai_chats()
        chat_dict = {f"{chat.id}: {chat.name}:[{chat.model}]": chat for chat in result.chats}
        chat_choices = [f"{chat.id}: {chat.name}:[{chat.model}]" for chat in result.chats]

        if isinstance(result, ChatsHttpResponse):
            progress.update(collecting_data_task, completed=True, visible=False)
            progress.stop()

            if result.chats is not None and len(result.chats) > 0:
                action = questionary.select(
                    message="Select an available chat:",
                    choices=chat_choices,
                ).ask()

                if action is None:
                    raise typer.Exit()

                selected_chat_object = chat_dict.get(action)

                deleting_data_task = progress.add_task(description="Deleting selected chat...",
                                                       total=None)

                deleted_chat = chat_service.delete_selected_chat(selected_chat_object.id)

                if deleted_chat is True:
                    progress.update(deleting_data_task, completed=True, visible=False)

                    progress.stop()
                    typer.secho(f"Successfully deleted chat: {selected_chat_object.name}.", fg=typer.colors.GREEN)
                else:
                    typer.secho(f"Failed to delete chat: {selected_chat_object.name}.", fg=typer.colors.RED)
            else:
                typer.secho(f"No chats available!",
                            fg=typer.colors.BRIGHT_YELLOW)


def chat():
    bot.run()


@assistant_app.command(name="options", help="Open up all options available.")
def options():
    choice = questionary.select(
        "Choose an available function:",
        choices=["Enter Chat()", "New Chat()", "List Chats()", "Delete Chat()", "Select Chat()"],
    ).ask()

    match choice:
        case "New Chat()":
            create_new_chat_dialog()
        case "Enter Chat()":
            enter_available_chats_dialog()
        case "List Chats()":
            list_available_chats()
        case "Delete Chat()":
            delete_selected_chat_dialog()
        case "Select Chat()":
            select_chat_dialog()


@assistant_app.command(name="list", help="List all available ai chat-dialogs.")
def list_chats():
    list_available_chats()


@assistant_app.command(name="enter", help="List and automatically enter a chat-dialog.")
def enter_chat():
    enter_available_chats_dialog()
    bot.run()


@assistant_app.command(name="delete", help="List and delete a chat-dialog.")
def delete_chat():
    delete_selected_chat_dialog()


@assistant_app.command(name="create", help="Create a new chat-dialog.")
def create_chat():
    create_new_chat_dialog()


@assistant_app.command(name="select", help="Select a chat-dialog.")
def select_chat_dialog(limit: int = None, select_last: bool = False):
    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
    ) as progress:
        collecting_data_task = progress.add_task(description="Collecting available chats...", total=None)

        result = chat_service.get_available_ai_chats()

        if isinstance(result, ChatsHttpResponse):
            chat_dict = {f"{chat.id}: {chat.name}:[{chat.model}]": chat for chat in result.chats}

            if select_last:
                chat_choices = [f"{chat.id}: {chat.name}:[{chat.model}]" for chat in
                                (result.chats[-limit:] if limit else result.chats[-1:])]
            else:
                chat_choices = [f"{chat.id}: {chat.name}:[{chat.model}]" for chat in
                                (result.chats[:limit] if limit else result.chats)]

            progress.update(collecting_data_task, completed=True, visible=False)
            progress.stop()

            if chat_choices:
                action = questionary.select(
                    message="Select an available chat:",
                    choices=chat_choices
                ).ask()

                if action is None:
                    raise typer.Exit()

                selected_chat_object = chat_dict.get(action)

                config_manager.update_active_chat(id=selected_chat_object.id,
                                                  name=selected_chat_object.name,
                                                  model=selected_chat_object.model)

                typer.secho(f"Successfully selected: {selected_chat_object.name}!",
                            fg=typer.colors.GREEN)
            else:
                typer.secho("No chats available!", fg=typer.colors.BRIGHT_YELLOW)

        elif isinstance(result, GeneralErrorResponse):
            typer.secho(f"{result.statusMessage}", fg=typer.colors.RED)


@assistant_app.command(name="update", help="Update an existing chat.")
def update_chat():
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        collecting_task = progress.add_task("Fetching available chats...", total=None)

        result = chat_service.get_available_ai_chats()

        if isinstance(result, GeneralErrorResponse):
            typer.secho(f"Error fetching chats: {result.statusMessage}", fg=typer.colors.RED)
            return

        try:
            chat_response = ChatsHttpResponse.model_validate(result)
            chats = chat_response.chats
        except ValidationError:
            typer.secho("Error parsing chat response!", fg=typer.colors.RED)
            return

        progress.update(collecting_task, completed=True, visible=False)

        if not chats:
            typer.secho("No chats available!", fg=typer.colors.BRIGHT_YELLOW)
            return

        chat_dict = {f"{chat.name}": chat for chat in chats}

        action = questionary.select(
            message="Select a chat to update:",
            choices=list(chat_dict.keys())
        ).ask()

        selected_chat = chat_dict.get(action)

        if not selected_chat:
            typer.secho("Invalid selection.", fg=typer.colors.RED)
            return

        # Ask if the user wants to update the name
        should_update_name = questionary.select(
            "Would you like to update the chat name?",
            choices=["Yes", "No"]
        ).ask()

        new_name = questionary.text(
            "Enter new chat name:").ask() if should_update_name == "Yes" else selected_chat.name

        # Ask if the user wants to update the model
        should_update_model = questionary.select(
            "Would you like to update the chat model?",
            choices=["Yes", "No"]
        ).ask()

        new_model = questionary.text(
            "Enter new model:").ask() if should_update_model == "Yes" else selected_chat.model

        typer.secho(f"Updating chat '{selected_chat.name}'...", fg=typer.colors.BRIGHT_BLACK)

        response = chat_service.update_chat(selected_chat.id, new_name, new_model)

        if isinstance(response, GeneralErrorResponse):
            typer.secho(f"Failed to update chat: {response.statusMessage}", fg=typer.colors.RED)
        else:
            typer.secho(
                f"Successfully updated chat to '{response.chat.name}' with model '{response.chat.model}'.",
                fg=typer.colors.GREEN
            )


@assistant_app.command(name="ask", help="Ask a question to the bot")
def ask(question: str,
        is_playground: bool = typer.Option(False, "--is-playground", help="Enable playground mode"),
        no_context: bool = typer.Option(False, "--no-context", help="Prevent Neptun form gathering previous chat messages. Ask standalone questions.")
        ):
    asyncio.run(conversation.ask(question, is_playground=is_playground, no_context=no_context))
