from .generator import AIFileGenerator
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from pick import pick

def create_model_options():
    """Create formatted options for the model picker"""
    options = []
    for model_name, info in AIFileGenerator.get_models().items():
        desc = info['description']
        if model_name == AIFileGenerator.DEFAULT_MODEL:
            option = f"{model_name} (Default) - {desc}"
        else:
            option = f"{model_name} - {desc}"
        options.append((model_name, option))
    return options

def main():
    console = Console()
    generator = AIFileGenerator()
    
    console.print("\n[bold blue]🤖 Iva[/bold blue]", style="bold")
    
    while True:
        command = Prompt.ask("\n[bold green]Command[/bold green] (Type 'help' for available commands)",
                           default="generate",
                           show_default=False)
        
        if command.lower() in ['exit', 'quit']:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
            
        elif command.lower() in ['help', '?']:
            console.print("\n[bold]Available commands:[/bold]")
            console.print("generate - Generate code based on your request")
            console.print("models   - List available AI models")
            console.print("model    - Change the current AI model")
            console.print("exit     - Exit the program")
            continue
            
        elif command.lower() == 'models':
            generator.list_available_models()
            continue
            
        elif command.lower() == 'model':
            options = create_model_options()
            title = 'Select an AI model (use ↑↓ arrows and Enter to select):'
            
            try:
                selected_model, _ = pick(
                    [opt[1] for opt in options],
                    title,
                    default_index=[i for i, opt in enumerate(options) if opt[0] == generator.model_name][0]
                )
                # Get the actual model name from the selected option
                model_name = next(opt[0] for opt in options if opt[1] == selected_model)
                
                generator.set_model(model_name)
                console.print(f"\n[green]✅ Model changed to: {model_name}[/green]")
            except Exception as e:
                console.print(f"\n[red]Error selecting model: {str(e)}[/red]")
            continue
            
        elif command.lower() == 'generate':
            user_request = Prompt.ask("[bold green]What would you like me to do?[/bold green]")
            output_dir = Prompt.ask("[bold cyan]Output directory[/bold cyan]",
                                  default=".",
                                  show_default=True)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Generating files...", total=None)
                structure = generator.run(user_request, output_dir)
                progress.stop()
            
            if structure:
                rprint("\n[green]✅ Files generated successfully![/green]")
                rprint(f"[dim]📁 Output directory: {output_dir}[/dim]")
        
        else:
            console.print("\n[red]Unknown command. Type 'help' for available commands.[/red]")