import argparse
from libraries.provision import ansible_runner


def push_logs_to_s3(cluster_config, bucket_name, log_dir_name):

    ans_runner = ansible_runner.AnsibleRunner(cluster_config)

    ans_runner.must_run_playbook(
        'push-logs-to-s3.yml',
        extra_vars={
            'bucket_name': bucket_name,
            'log_dir_name': log_dir_name
        }
    )


if __name__ == "__main__":

    # There is some complex argument parsing going on in order to be able to capture
    # certain arguments and process them, and pass through the rest of the arguments
    # down to sgload being invoked.
    #
    # The parse_known_args() call will essentially extract any arguments added via
    # parser.add_argument(), and the rest of the arguments will get read into
    # sgload_arg_list_main and then passed to sgload when invoked

    parser = argparse.ArgumentParser()
    parser.add_argument('--cluster-config')
    parser.add_argument('--bucket-name')
    parser.add_argument('--log-dir-name')
    args = parser.parse_args()

    # TODO: Validate args

    push_logs_to_s3(
        cluster_config=args.cluster_config,
        bucket_name=args.bucket_name,
        log_dir_name=args.log_dir_name
    )
