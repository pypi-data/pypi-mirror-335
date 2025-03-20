from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from Crypto.Cipher import AES
import argparse
import requests
import tempfile
import base64
import shutil
import boto3
import toml
import os
import subprocess

org_name = "securin"
cli_file_name = "securin-cli-win.exe"
api_host_name = "slresultapi.qa.securin.io"
config_file_name = ".aspm"

vulscan_default_config = {
    "config": {
        "scan_types": ["container","secrets","sca"],
        "severity": "",
        "app_id": "",
        "app_name": "",
        "branch_name": "default",
        "source_dir": os.getcwd(),
        "bin_version": "1.0.10",
        "hostname": ""
    },
    "secret": {
        "api_key": "API_KEY",
    },
    "output": {
        "format": "json",
        "output_file": "",
        "is_console_report": True,
        "enable_color": False,
        "is_debug": False,
        "skip_build_fail": False,
    }
}


def filter_empty(data):
    if isinstance(data, dict):
        return {k: filter_empty(v) for k, v in data.items() if v not in ("", [], None)}
    elif isinstance(data, list):
        return [filter_empty(item) for item in data if item not in ("", [], None)]
    else:
        return data

def download_file_from_s3(aws_access_key, aws_secret_key, aws_session_token, bucket_name, s3_path):
    full_s3_path = f"{s3_path}/{cli_file_name}"
    try:
        # Create a session using the provided AWS credentials
        session = boto3.Session(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token
        )
        
        # Create an S3 client
        s3 = session.client('s3')
        
        # Get the temporary directory path
        temp_dir = tempfile.gettempdir()
        if os.path.exists(os.path.join(temp_dir, org_name)):
            shutil.rmtree(os.path.join(temp_dir, org_name))
        os.makedirs(os.path.join(temp_dir, org_name), exist_ok=True)
        destination_path = os.path.join(temp_dir, org_name,cli_file_name)
        # Download the file from S3
        s3.download_file(bucket_name, full_s3_path , destination_path)
        return destination_path
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except PartialCredentialsError:
        print("Incomplete credentials provided")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def decrypt_keys(key, iv, value):
    try:
        key_bytes = bytes.fromhex(key)
        iv_bytes = bytes.fromhex(iv)
        value_bytes = base64.b64decode(value)
        
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted = cipher.decrypt(value_bytes)
        
        # Remove padding
        pad = decrypted[-1]
        decrypted = decrypted[:-pad]
        
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"An error occurred during decryption: {e}")
        return None

def get_cli_details_from_s3(api_key, version=None):
    s3_url = f"https://{api_host_name}/resultapi/cli/version/s3/details"
    
    if version:
        s3_url = f"{s3_url}?version={version}"
    
    headers = {
        "X-ASPM-Auth-Key": api_key
    }
    
    response = requests.get(s3_url, headers=headers)
    
    if response.status_code != 200 or not response.text:
        return None, None

    enc_response = response.json()
    bucket_name = enc_response.get('bucket_name', '')
    bucket_path = enc_response.get('key_path', '')
    
    return bucket_name, bucket_path

def get_latest_enc_keys(api_key):
    enc_keys_url = f"https://{api_host_name}/resultapi/enc/keys"
    headers = {
        "X-ASPM-Auth-Key": api_key
    }
    
    response = requests.get(enc_keys_url, headers=headers)
    
    if response.status_code != 200 or not response.text:
        return None, None
    
    enc_response = response.json()
    enc_key = enc_response.get('KEY', '')
    enc_iv = enc_response.get('IV', '')

    if not enc_key or not enc_iv:
        return None, None
    
    return enc_key, enc_iv

def get_aws_credentials_from_aspm(api_key):
    aws_token_url = f"https://{api_host_name}/resultapi/cli/aws/accesstoken"
    headers = {
        "X-ASPM-Auth-Key": api_key
    }
    
    response = requests.get(aws_token_url, headers=headers)
    
    if response.status_code != 200 or not response.text:
        return None, None, None
    
    enc_response = response.json()
    access_key = enc_response.get('accessKey', '')
    secret_key = enc_response.get('secretKey', '')
    session_token = enc_response.get('sessionToken', '')
    
    if not access_key or not secret_key or not session_token:
        return None, None, None
    
    return access_key, secret_key, session_token

def run_command_live(cli_args):
    process = subprocess.Popen(cli_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end="")  

    return_code = process.wait()

    stderr_output = process.stderr.read()
    
    return return_code, stderr_output


def init(args):
    print("initializing aspm config")
    if args.api_key:
        vulscan_default_config['secret']['api_key'] = args.api_key
    if args.app_id:
        vulscan_default_config['config']['app_id'] = args.app_id
    if args.app_name:
        vulscan_default_config['config']['app_name'] = args.app_name
    if args.branch_name:
        vulscan_default_config['config']['branch_name'] = args.branch_name
    if args.enable_color:
        vulscan_default_config['output']['enable_color'] = args.enable_color
    if args.format:
        vulscan_default_config['output']['format'] = args.format
    if not args.is_console_report:
        vulscan_default_config['output']['is_console_report'] = args.is_console_report
    if args.is_debug:
        vulscan_default_config['output']['is_debug'] = args.is_debug
    if args.output_file:
        vulscan_default_config['output']['output_file'] = args.output_file
    if args.scan_types:
        vulscan_default_config['config']['scan_types'] = args.scan_types.split(',')
    if args.severity:
        vulscan_default_config['config']['severity'] = args.severity
    if args.skip_build_fail:
        vulscan_default_config['output']['skip_build_fail'] = args.skip_build_fail
    if args.source_dir:
        vulscan_default_config['config']['source_dir'] = args.source_dir
    if args.bin_version:
        vulscan_default_config['config']['bin_version'] = args.bin_version
    if args.hostname:
        vulscan_default_config['config']['hostname'] = args.hostname

    filtered_config = filter_empty(vulscan_default_config)

    # Write the data to a TOML file
    with open(config_file_name, 'w') as toml_file:
        toml.dump(filtered_config, toml_file)
    print("aspm config initialized successfully")

def remove(args):
    print("Removing aspm config")
    if os.path.exists(config_file_name):
        os.remove(config_file_name)
        print("aspm config removed successfully")
    else:
        print("No aspm config found")

def scan_using_params(api_key, app_id, app_name, branch_name, enable_color, format, is_console_report, is_debug, output_file, scan_types, severity, skip_build_fail, source_dir, bin_version, hostname):
    global api_host_name

    if hostname:
        api_host_name = hostname.strip()

    bucket_name, bucket_path = get_cli_details_from_s3(api_key, bin_version)

    if not bucket_name or not bucket_path:
        print("No bucket details found")
        return

    enc_key, enc_iv = get_latest_enc_keys(api_key)

    if not enc_key or not enc_iv:
        print("No encryption details found")
        return
    
    enc_access_key, enc_secret_key, enc_session_token = get_aws_credentials_from_aspm(api_key)

    if not enc_access_key or not enc_secret_key or not enc_session_token:
        print("No AWS credentials found")
        return

    aws_access_key = decrypt_keys(enc_key, enc_iv, enc_access_key)
    aws_secret_key = decrypt_keys(enc_key, enc_iv, enc_secret_key)
    aws_session_token = decrypt_keys(enc_key, enc_iv, enc_session_token)

    if not aws_access_key or not aws_secret_key or not aws_session_token:
        print("Error decrypting AWS credentials")
        return

    executable_path = download_file_from_s3(aws_access_key, aws_secret_key, aws_session_token, bucket_name, bucket_path)

    if not executable_path:
        print("Error downloading the executable")
        return
    
    cli_args = [executable_path]
    
    if api_key:
        cli_args.extend(['--api_key', api_key])
    if app_id:
        cli_args.extend(['--app_id', app_id])
    if app_name:
        cli_args.extend(['--app_name', app_name])
    if branch_name:
        cli_args.extend(['--branch_name', branch_name])
    if enable_color:
        cli_args.extend(['--enable_color', "true"])
    if format:
        cli_args.extend(['--format', format])
    if not is_console_report:
        cli_args.extend(['--is_console_report', "false"])
    if is_debug:
        cli_args.extend(['--is_debug', "true"])
    if output_file:
        cli_args.extend(['--output_file', output_file])
    if scan_types:
        cli_args.extend(['--scanner_type', scan_types])
    if severity:
        cli_args.extend(['--severity', severity])
    if skip_build_fail:
        cli_args.extend(['--skip_build_fail', "true"])
    if source_dir:
        cli_args.extend(['--source_dir', source_dir])
    
    try:
        run_command_live(cli_args)
    except Exception as e:
        print(f"An error occurred while executing the CLI: {e}")

def scan_now(args):
    if not os.path.exists(config_file_name):
        return True
    
    config = toml.load(config_file_name)

    no_scan_param = config.get("skip_scan", False)
    if no_scan_param:
        return True

    config_data = config.get("config", {})
    secret_data = config.get("secret", {})
    output_data = config.get("output", {})

    api_key = secret_data.get("api_key", "")
    app_id = config_data.get("app_id", "")
    app_name = config_data.get("app_name", "")
    branch_name = config_data.get("branch_name", "")
    enable_color = output_data.get("enable_color", False)
    format = output_data.get("format", "")
    is_console_report = output_data.get("is_console_report", True)
    is_debug = output_data.get("is_debug", False)
    output_file = output_data.get("output_file", "")
    scan_types = config_data.get("scan_types", "")
    severity = config_data.get("severity", "")
    skip_build_fail = output_data.get("skip_build_fail", False)
    source_dir = config_data.get("source_dir", "")
    bin_version = config_data.get("bin_version", "")
    hostname = config_data.get("hostname", "")

    if isinstance(scan_types, list):
        scan_types = ",".join(scan_types)

    try:
        scan_using_params(api_key, app_id, app_name, branch_name, enable_color, format, is_console_report, is_debug, output_file, scan_types, severity, skip_build_fail, source_dir, bin_version, hostname)
    except Exception as e:
        print("Not able to run aspm", e)
        return False
    return True



def scan(args):
    global api_host_name
    
    if args.hostname:
        api_host_name = args.hostname.strip()

    bucket_name, bucket_path = get_cli_details_from_s3(args.api_key, args.bin_version)

    if not bucket_name or not bucket_path:
        print("No bucket details found")
        return

    enc_key, enc_iv = get_latest_enc_keys(args.api_key)

    if not enc_key or not enc_iv:
        print("No encryption details found")
        return

    enc_access_key, enc_secret_key, enc_session_token = get_aws_credentials_from_aspm(args.api_key)

    if not enc_access_key or not enc_secret_key or not enc_session_token:
        print("No AWS credentials found")
        return
    
    aws_access_key = decrypt_keys(enc_key, enc_iv, enc_access_key)
    aws_secret_key = decrypt_keys(enc_key, enc_iv, enc_secret_key)
    aws_session_token = decrypt_keys(enc_key, enc_iv, enc_session_token)

    if not aws_access_key or not aws_secret_key or not aws_session_token:
        print("Error decrypting AWS credentials")
        return


    executable_path = download_file_from_s3(aws_access_key, aws_secret_key, aws_session_token, bucket_name, bucket_path)

    if not executable_path:
        print("Error downloading the executable")
        return
    
    cli_args = [executable_path]
    
    if args.api_key:
        cli_args.extend(['--api_key', args.api_key])
    if args.app_id:
        cli_args.extend(['--app_id', args.app_id])
    if args.app_name:
        cli_args.extend(['--app_name', args.app_name])
    if args.branch_name:
        cli_args.extend(['--branch_name', args.branch_name])
    if args.enable_color:
        cli_args.extend(['--enable_color', "true"])
    if args.format:
        cli_args.extend(['--format', args.format])
    if not args.is_console_report:
        cli_args.extend(['--is_console_report', "false"])
    if args.is_debug:
        cli_args.extend(['--is_debug', "true"])
    if args.output_file:
        cli_args.extend(['--output_file', args.output_file])
    if args.scan_types:
        cli_args.extend(['--scanner_type', args.scan_types])
    if args.severity:
        cli_args.extend(['--severity', args.severity])
    if args.skip_build_fail:
        cli_args.extend(['--skip_build_fail', "true"])
    if args.source_dir:
        cli_args.extend(['--source_dir', args.source_dir])
    
    try:
        run_command_live(cli_args)
    except Exception as e:
        print(f"An error occurred while executing the CLI: {e}")

def main():
    parser = argparse.ArgumentParser(description="A basic Python library that takes command-line arguments.")

    subparsers = parser.add_subparsers(dest='command')

    # Subparser for 'init' command
    parser_init = subparsers.add_parser('init', help='Initialize the scan config')
    parser_init.add_argument('--api_key', type=str, required=False, help='API key')
    parser_init.add_argument('--app_id', type=str, required=False, help='Application ID')
    parser_init.add_argument('--app_name', type=str, required=False, help='Application name')
    parser_init.add_argument('--branch_name', type=str, required=False, default='default', help='Branch name')
    parser_init.add_argument('--enable_color', action='store_true', help='Enable color in report')
    parser_init.add_argument('--format', type=str, required=False, help='Output format')
    parser_init.add_argument('--is_console_report', action='store_true', default=True, help='Console report')
    parser_init.add_argument('--is_debug', action='store_true', help='Enable debug logs')
    parser_init.add_argument('--output_file', type=str, required=False, help='Output file')
    parser_init.add_argument('--scan_types', type=str, required=False, help='Types of scans to be triggered')
    parser_init.add_argument('--severity', type=str, required=False, help='Severity')
    parser_init.add_argument('--skip_build_fail', action='store_true', help='Skip build fail')
    parser_init.add_argument('--source_dir', type=str, required=False, default=os.getcwd(), help='Source directory')
    parser_init.add_argument('--bin_version', type=str,required=False, help='Which version of the CLI to use')
    parser_init.add_argument('--hostname', type=str, required=False, default="", help='Hostname of the API Endpoint')
    parser_init.set_defaults(func=init)

    parser_remove = subparsers.add_parser('remove', help='Remove the aspm config from project')
    parser_remove.set_defaults(func=remove)

    # Subparser for 'run' command
    parser_scan_run = subparsers.add_parser('run', help='Run scan in current directory')
    parser_scan_run.set_defaults(func=scan_now)

    # Subparser for 'scan' command
    parser_scan = subparsers.add_parser('scan', help='Scan something')

    parser_scan.add_argument('--api_key', type=str, required=True, help='API key')
    parser_scan.add_argument('--app_id', type=str, required=False, help='Application ID')
    parser_scan.add_argument('--app_name', type=str, required=False, help='Application name')
    parser_scan.add_argument('--branch_name', type=str, required=False, default='default', help='Branch name')
    parser_scan.add_argument('--enable_color', action='store_true', help='Enable color in report')
    parser_scan.add_argument('--format', type=str, required=False, help='Output format')
    parser_scan.add_argument('--is_console_report', action='store_true', default=True, help='Console report')
    parser_scan.add_argument('--is_debug', action='store_true', help='Enable debug logs')
    parser_scan.add_argument('--output_file', type=str, required=False, help='Output file')
    parser_scan.add_argument('--scan_types', type=str, required=False, help='Types of scans to be triggered')
    parser_scan.add_argument('--severity', type=str, required=False, help='Severity')
    parser_scan.add_argument('--skip_build_fail', action='store_true', help='Skip build fail')
    parser_scan.add_argument('--source_dir', type=str, required=False, default=os.getcwd(), help='Source directory')
    parser_scan.add_argument('--bin_version', type=str,required=False, help='Which version of the CLI to use')
    parser_scan.add_argument('--hostname', type=str, required=False, default=api_host_name, help='Hostname of the API Endpoint')
    parser_scan.set_defaults(func=scan)

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
