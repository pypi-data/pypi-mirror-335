import os
import tarfile
import tempfile
from kubernetes import client
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from grdpcli import logger
import logging

# logger.setLevel(logging.DEBUG) # Disable debug logs

class CopyManager:
    def __init__(self, namespace):
        self.namespace = namespace
        self.api = client.CoreV1Api()

    def _check_pod_exists(self, pod_name):
        """Check if pod exists in namespace"""
        try:
            self.api.read_namespaced_pod(name=pod_name, namespace=self.namespace)
            return True
        except ApiException:
            logger.error(f"Pod {pod_name} not found in namespace {self.namespace}")
            return False

    def _copy_from_pod(self, pod_name, pod_file_path, local_path):
        """Copy file from pod to local system"""
        try:
            # Check if the file exists in the pod
            check_file_command = ['test', '-f', pod_file_path]
            try:
                stream(
                    self.api.connect_get_namespaced_pod_exec,
                    pod_name,
                    self.namespace,
                    command=check_file_command,
                    stderr=True,
                    stdin=False,
                    stdout=True,
                    tty=False
                )
            except:
                logger.error(f"Source file does not exist in pod: {pod_file_path}")
                return False

            # Processing the local path
            if os.path.isdir(local_path):
                # If it's an existing directory, add the file name from the pod
                local_path = os.path.join(local_path, os.path.basename(pod_file_path))
            else:
                # Checking the existence of the parent directory
                parent_dir = os.path.dirname(local_path)
                if parent_dir and not os.path.exists(parent_dir):
                    logger.error(f"Target directory does not exist: {parent_dir}")
                    return False

            # Using cat for direct file copying
            exec_command = ['cat', pod_file_path]
            resp = stream(
                self.api.connect_get_namespaced_pod_exec,
                pod_name,
                self.namespace,
                command=exec_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )

            # Writing the file contents directly
            try:
                with open(local_path, 'wb') as f:
                    f.write(resp.encode())
                
                logger.info(f"Successfully copied file to {local_path}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to write file: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Error copying from pod: {str(e)}")
            logger.debug(f"Full error: {str(e)}", exc_info=True)
            return False

    def _copy_to_pod(self, local_path, pod_name, pod_file_path):
        """Copy file from local system to pod"""
        try:
            if not os.path.exists(local_path):
                logger.error(f"Local file {local_path} does not exist")
                return False

            # Normalizing paths and removing the trailing slash
            pod_file_path = os.path.normpath(pod_file_path)
            
            # Determining the target path
            if pod_file_path.endswith('/'):
                # If the path ends with /, treat it as a directory
                target_dir = pod_file_path.rstrip('/')
                target_file = os.path.join(target_dir, os.path.basename(local_path))
            else:
                # Check if the path exists and is a directory
                check_path_command = ['ls', '-ld', pod_file_path]
                try:
                    result = stream(
                        self.api.connect_get_namespaced_pod_exec,
                        pod_name,
                        self.namespace,
                        command=check_path_command,
                        stderr=True,
                        stdin=False,
                        stdout=True,
                        tty=False
                    )
                    
                    # If the path exists and is a directory
                    if result.startswith('d'):
                        target_dir = pod_file_path
                        target_file = os.path.join(target_dir, os.path.basename(local_path))
                    else:
                        # The path exists but is not a directory - use the parent directory
                        target_dir = os.path.dirname(pod_file_path)
                        target_file = pod_file_path
                except:
                    # The path does not exist - use the parent directory
                    target_dir = os.path.dirname(pod_file_path)
                    target_file = pod_file_path

            # Check the existence of the target directory
            check_dir_command = ['test', '-d', target_dir]
            try:
                stream(
                    self.api.connect_get_namespaced_pod_exec,
                    pod_name,
                    self.namespace,
                    command=check_dir_command,
                    stderr=True,
                    stdin=False,
                    stdout=True,
                    tty=False
                )
            except:
                logger.error(f"Target directory does not exist: {target_dir}")
                return False

            logger.debug(f"Target directory: {target_dir}")
            logger.debug(f"Target file: {target_file}")

            logger.debug(f"Creating tar archive of {local_path}")
            # Create a temporary tar file
            with tempfile.NamedTemporaryFile() as tar_buffer:
                # Create a tar archive in the temporary file
                with tarfile.open(mode='w:gz', fileobj=tar_buffer) as tar:
                    # Use basename of target_file as the name in the archive
                    tar.add(local_path, arcname=os.path.basename(target_file))
                
                # Move the pointer to the beginning of the file
                tar_buffer.seek(0)
                # Read the contents of the tar archive
                tar_data = tar_buffer.read()
                
                logger.debug(f"Tar archive size: {len(tar_data)} bytes")

                # Copy the file to the pod using tar
                exec_command = ['tar', 'xzf', '-', '-C', target_dir]
                logger.debug(f"Executing tar command in pod: {' '.join(exec_command)}")
                
                try:
                    resp = stream(
                        self.api.connect_get_namespaced_pod_exec,
                        pod_name,
                        self.namespace,
                        command=exec_command,
                        stderr=True,
                        stdin=True,
                        stdout=True,
                        tty=False,
                        _preload_content=False
                    )

                    # Send tar data in one block
                    logger.debug("Sending tar data to pod")
                    resp.write_stdin(tar_data)
                    
                    # Close stdin so that tar knows that the transfer is complete
                    logger.debug("Closing stdin")
                    resp.close()

                    # Check if the file exists in the pod
                    logger.debug(f"Verifying file exists in pod: {target_file}")
                    verify_command = ['ls', '-l', target_file]
                    result = stream(
                        self.api.connect_get_namespaced_pod_exec,
                        pod_name,
                        self.namespace,
                        command=verify_command,
                        stderr=True,
                        stdin=False,
                        stdout=True,
                        tty=False
                    )
                    
                    logger.debug(f"Verification result: {result}")
                    if "No such file or directory" in str(result):
                        logger.error(f"File was not found in pod after copy: {target_file}")
                        return False
                    
                    logger.info(f"Successfully copied file to {target_file}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error during file transfer: {str(e)}")
                    return False

        except Exception as e:
            logger.error(f"Error copying to pod: {str(e)}")
            logger.debug(f"Full error: {str(e)}", exc_info=True)
            return False

    def copy(self, source, destination):
        """Copy files to/from pods"""
        try:
            # Determine the direction of the copy
            if ':' in source:
                # Copying from pod
                pod_path = source.split(':')
                pod_name = pod_path[0]
                pod_file_path = pod_path[1]
                local_path = destination
                
                if not self._check_pod_exists(pod_name):
                    return False

                logger.info(f"Copying from pod {pod_name}:{pod_file_path} to {local_path}")
                success = self._copy_from_pod(pod_name, pod_file_path, local_path)
                
            else:
                # Copying to pod
                pod_path = destination.split(':')
                pod_name = pod_path[0]
                pod_file_path = pod_path[1]
                
                # If the path in the pod ends with /, add the name of the source file
                if pod_file_path.endswith('/'):
                    pod_file_path = os.path.join(pod_file_path, os.path.basename(source))
                
                local_path = source
                
                if not self._check_pod_exists(pod_name):
                    return False

                logger.info(f"Copying from {local_path} to pod {pod_name}:{pod_file_path}")
                success = self._copy_to_pod(local_path, pod_name, pod_file_path)
                
                
            return success
                
        except Exception as e:
            logger.error(f"Error during copy operation: {str(e)}")
            return False