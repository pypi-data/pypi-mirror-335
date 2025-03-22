from .generator import AIFileGenerator
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

def main():
    console = Console()
    generator = AIFileGenerator()
    
    console.print("\n[bold blue]🤖 Iva[/bold blue]", style="bold")
    
    while True:
        user_request = Prompt.ask("\n[bold green]What would you like me to do?[/bold green] (Type 'exit' to quit)", 
                                default="exit",
                                show_default=False)
        
        if user_request.lower() in ['exit', 'quit']:
            console.print("\n[yellow]👋 Goodbye![/yellow]")
            break
            
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
        
        rprint("\n[green]✅ Files generated successfully![/green]")
        rprint(f"[dim]📁 Output directory: {output_dir}[/dim]")