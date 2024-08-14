import boto3
import click
import re
import os
from dotenv import load_dotenv


load_dotenv()


s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

bucket_name = os.getenv('BUCKET_NAME')

@click.command('list')
def list_files():
    """List all files in the S3 bucket."""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
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
def upload_file(local_file_path, destination_key):
    """Upload a local file to S3."""
    try:
        s3.upload_file(local_file_path, bucket_name, destination_key)
        click.echo(f"File '{local_file_path}' uploaded to '{destination_key}'")
    except Exception as e:
        click.echo(f"Error uploading file: {e}")


@click.command('filter')
@click.argument('regex_pattern')
def filter_files(regex_pattern):
    """List files matching a regex pattern."""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
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
def delete_files(regex_pattern):
    """Delete files matching a regex pattern."""
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
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
