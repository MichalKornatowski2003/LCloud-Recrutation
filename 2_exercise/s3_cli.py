import boto3
import click
import re
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

s3 = boto3.client('s3')
bucket_name = os.getenv('BUCKET_NAME')

@click.command('list')
@click.option('--prefix', default='', help='Prefix (folder) to list files from, e.g., x-wing/')
def list_files(prefix):
    """List all files in the S3 bucket."""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                click.echo(obj['Key'])
        else:
            click.echo("No files found.")
    except Exception as e:
        click.echo(f"Error listing files: {e}")

@click.command('upload')
@click.argument('local_file_path')
@click.argument('destination_key')
@click.option('--folder', default='', help='Folder inside the bucket (e.g., x-wing/)')
def upload_file(local_file_path, destination_key, folder):
    """Upload a local file to S3."""
    try:
        key = folder + destination_key
        s3.upload_file(local_file_path, bucket_name, key)
        click.echo(f"File '{local_file_path}' uploaded to '{key}'")
    except Exception as e:
        click.echo(f"Error uploading file: {e}")

@click.command('filter')
@click.argument('regex_pattern')
@click.option('--prefix', default='', help='Prefix (folder) to filter files from, e.g., x-wing/')
def filter_files(regex_pattern, prefix):
    """List files matching a regex pattern."""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            regex = re.compile(regex_pattern)
            filtered_files = [obj['Key'] for obj in response['Contents'] if regex.search(obj['Key'])]
            if filtered_files:
                for file in filtered_files:
                    click.echo(file)
            else:
                click.echo("No files match the regex pattern.")
        else:
            click.echo("No files found.")
    except Exception as e:
        click.echo(f"Error filtering files: {e}")

@click.command('delete')
@click.argument('regex_pattern')
@click.option('--prefix', default='', help='Prefix (folder) to delete files from, e.g., x-wing/')
def delete_files(regex_pattern, prefix):
    """Delete files matching a regex pattern."""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            regex = re.compile(regex_pattern)
            files_to_delete = [obj['Key'] for obj in response['Contents'] if regex.search(obj['Key'])]

            if files_to_delete:
                for file_key in files_to_delete:
                    s3.delete_object(Bucket=bucket_name, Key=file_key)
                    click.echo(f"Deleted file: {file_key}")
            else:
                click.echo("No files match the regex pattern.")
        else:
            click.echo("No files found.")
    except Exception as e:
        click.echo(f"Error deleting files: {e}")

@click.group()
def cli():
    """AWS S3 CLI Tool"""
    pass

cli.add_command(list_files)
cli.add_command(upload_file)
cli.add_command(filter_files)
cli.add_command(delete_files)

if __name__ == '__main__':
    cli()
