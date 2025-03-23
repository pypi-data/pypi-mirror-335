import typer
import os
from pathlib import Path
import logging
import toml
from dotenv import load_dotenv

from writeup.core import evaluator
from writeup.reports import json_report, pdf_report
from writeup.core.models import Feedback

from rich.table import Table
from rich.console import Console

# Load environment variables
load_dotenv()

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_client(api_key: str = None):
    import google.genai as genai
    token = api_key or os.getenv("GEMINI_API_KEY")
    if not token:
        logger.error("GEMINI_API_KEY not provided. Use --api-key option or set it in .env")
        raise typer.Exit("Missing GEMINI_API_KEY")
    return genai.Client(api_key=token)

app = typer.Typer(name="writeup", help="A CLI tool to analyze CVs in PDF format.")
console = Console()

def display_feedback(feedback: Feedback) -> None:
    table = Table(title="CV Analysis Results", show_lines=True)
    table.add_column("Parameter", style="bold cyan")
    table.add_column("Value", style="bold magenta")
    table.add_row("Score 🔢", str(feedback.score))
    table.add_row("Years of Experience ⏳", str(feedback.years_experience))
    table.add_row("Summary 📝", feedback.summary)
    table.add_row("Relevant Skills ✅", ", ".join(feedback.relevant_skills))
    table.add_row("Other Skills 🧐", ", ".join(feedback.other_skills))
    table.add_row("Pros ✅", "\n".join(f"• {p}" for p in feedback.pros))
    table.add_row("Cons 🧐", "\n".join(f"• {c}" for c in feedback.cons))
    console.print(table)

@app.command("evaluate", help="Evaluate a single CV PDF. Provide the file path, the job position, seniority level, and optionally override the API key using --api-key. Generates a report in JSON or PDF format.")
def evaluate(
    file: str = typer.Argument(..., help="Path to the CV PDF file"),
    position: str = typer.Option(..., "--position", "-p", prompt="Enter the position", help="Name of the position"),
    seniority: str = typer.Option(..., "--seniority", "-s", prompt="Enter the seniority level", help="Seniority level"),
    output: str = typer.Option(None, "--output", "-o", help="Output file name for the report"),
    report_format: str = typer.Option("json", "--format", "-f", help="Report format: 'json' or 'pdf'"),
    api_key: str = typer.Option(None, "--api-key", "-t", help="Override GEMINI_API_KEY from environment")
):
    typer.secho("Starting CV evaluation...", fg="yellow", bold=True)
    filepath = Path(file)
    if not filepath.exists():
        typer.secho(f"Error: File '{file}' not found.", fg="red")
        raise typer.Exit()

    if not output:
        default_name = "evaluation_report.pdf" if report_format.lower() == "pdf" else "evaluation_report.json"
        output = str(filepath.parent / default_name)

    typer.secho(f"Evaluating CV from file: {filepath}", fg="blue", bold=True)
    typer.secho(f"Position: {position} | Seniority: {seniority}", fg="green", bold=True)
    typer.secho("Initiating remote evaluation call...", fg="blue")
    client = get_client(api_key)
    try:
        feedback = evaluator.evaluate_cv(filepath, position, seniority, client)
    except Exception as e:
        logger.error(f"Error during evaluation: {e}")
        typer.secho("Failed to evaluate the CV. Please try again later.", fg="red")
        raise typer.Exit()

    typer.secho("Remote evaluation completed successfully.", fg="green")
    typer.secho("Displaying evaluation results:", fg="blue")
    display_feedback(feedback)

    typer.secho(f"Saving report as {report_format.upper()}...", fg="blue")
    if report_format.lower() == "json":
        json_report.save_report_as_json(feedback, position, seniority, output)
        typer.secho(f"JSON report saved to: {output}", fg="blue")
    elif report_format.lower() == "pdf":
        pdf_report.save_report_as_pdf(feedback, position, seniority, output)
        typer.secho(f"PDF report saved to: {output}", fg="blue")
    else:
        typer.secho("Invalid format specified. Please use 'json' or 'pdf'.", fg="red")

@app.command("batch_evaluate", help="Evaluate all CV PDFs in a directory. Provide the directory path, job position, and seniority level. Optionally override the API key using --api-key. Generates a batch report in JSON or PDF format.")
def batch_evaluate(
    directory: str = typer.Argument(..., help="Path to the directory containing CV PDF files"),
    position: str = typer.Option(..., "--position", "-p", prompt="Enter the position", help="Name of the position"),
    seniority: str = typer.Option(..., "--seniority", "-s", prompt="Enter the seniority level", help="Seniority level"),
    output: str = typer.Option(None, "--output", "-o", help="Output file name for the report"),
    report_format: str = typer.Option("json", "--format", "-f", help="Report format: 'json' or 'pdf'"),
    api_key: str = typer.Option(None, "--api-key", "-t", help="Override GEMINI_API_KEY from environment")
):
    typer.secho("Starting batch CV evaluation...", fg="yellow", bold=True)
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        typer.secho(f"Error: Directory '{directory}' not found or is not a valid directory.", fg="red")
        raise typer.Exit()

    if not output:
        default_name = "batch_evaluation_report.pdf" if report_format.lower() == "pdf" else "batch_evaluation_report.json"
        output = str(dir_path / default_name)

    file_list = list(dir_path.glob("*.pdf"))
    if not file_list:
        typer.secho(f"No PDF files found in directory: {directory}", fg="red")
        raise typer.Exit()
    typer.secho(f"Found {len(file_list)} PDF file(s) in directory '{directory}'.", fg="blue", bold=True)

    typer.secho("Evaluating all files... This may take a moment.", fg="blue")
    client = get_client(api_key)
    try:
        reports = evaluator.evaluate_cv_batch(dir_path, position, seniority, client)
    except Exception as e:
        logger.error(f"Error during batch evaluation: {e}")
        typer.secho("Failed to evaluate CVs in batch. Please try again later.", fg="red")
        raise typer.Exit()

    typer.secho(f"Batch evaluation completed successfully. Evaluated {len(reports)} file(s).", fg="green", bold=True)
    
    table = Table(title="Batch CV Evaluation Results", show_lines=True)
    table.add_column("File", style="bold cyan", no_wrap=True)
    table.add_column("Score 🔢", style="bold magenta", no_wrap=True)
    table.add_column("Years Exp ⏳", style="bold yellow", no_wrap=True)
    table.add_column("Summary 📝", style="bold green", max_width=60, overflow="ellipsis")
    table.add_column("Relevant Skills ✅", style="bold yellow", max_width=40, overflow="ellipsis")
    for rep in reports:
        skills = ", ".join(rep.get("relevant_skills", []))
        table.add_row(
            rep.get("file", ""),
            str(rep.get("score", "")),
            str(rep.get("years_experience", "")),
            rep.get("summary", ""),
            skills
        )
    console.print(table)

    typer.secho(f"Saving batch report to: {output} in {report_format.upper()} format...", fg="blue")
    if report_format.lower() == "json":
        json_report.save_batch_report_as_json(reports, output)
        typer.secho(f"Batch JSON report saved to: {output}", fg="blue")
    elif report_format.lower() == "pdf":
        pdf_report.save_batch_report_as_pdf(reports, position, seniority, output)
        typer.secho(f"Batch PDF report saved to: {output}", fg="blue")
    else:
        typer.secho("Invalid format specified. Please use 'json' or 'pdf'.", fg="red")

@app.command("version", help="Display the current version of writeup.")
def version():
    try:
        with open("pyproject.toml", "r") as f:
            pyproject_data = toml.load(f)
            ver = pyproject_data["tool"]["poetry"]["version"]
        typer.secho(f"writeup version: {ver}", fg="green")
    except Exception as e:
        logger.error(f"Error reading version: {e}")
        typer.secho("Could not determine version.", fg="red")

if __name__ == "__main__":
    app()
