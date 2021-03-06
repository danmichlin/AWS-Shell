import jsonpickle
from cloudshell.api.cloudshell_api import InputNameValue
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface

from cloudshell.cp.aws.common.driver_helper import CloudshellDriverHelper
from cloudshell.cp.aws.models.deploy_aws_ec2_ami_instance_resource_model import DeployAWSEc2AMIInstanceResourceModel
from cloudshell.cp.aws.common.deploy_data_holder import DeployDataHolder


class DeployAWSEC2AMIInstance(ResourceDriverInterface):
    def __init__(self):
        # Todo remove this to a common place outside the package
        self.cs_helper = CloudshellDriverHelper()

    def cleanup(self):
        pass

    def initialize(self, context):
        pass

    def Deploy(self, context, Name=None):
        # Create cloudshell session
        session = self.cs_helper.get_session(context.connectivity.server_address,
                                             context.connectivity.admin_auth_token,
                                             context.reservation.domain)

        # create deployment resource model and serialize it to json
        aws_ami_deployment_model = self._convert_context_to_deployment_resource_model(context.resource)

        aws_ami_deployment_model.aws_key = "aws_testing_key_pair"  # we will create it on the run if needed

        ami_res_name = jsonpickle.decode(context.resource.app_context.app_request_json)['name']

        deployment_info = self._get_deployment_info(aws_ami_deployment_model, ami_res_name)

        self.vaidate_deployment_ami_model(aws_ami_deployment_model)

        # Calls command on the AWS cloud provider
        result = session.ExecuteCommand(context.reservation.reservation_id,
                                        aws_ami_deployment_model.cloud_provider_resource,
                                        "Resource",
                                        "deploy_ami",
                                        self._get_command_inputs_list(deployment_info),
                                        False)
        return result.Output

    def vaidate_deployment_ami_model(self, aws_ami_deployment_model):
        if aws_ami_deployment_model.cloud_provider_resource == '':
            raise Exception("The name of the Cloud Provider resource is empty.")

    # todo: remove this to a common place
    def _convert_context_to_deployment_resource_model(self, resource):
        deployedResource = DeployAWSEc2AMIInstanceResourceModel()
        deployedResource.aws_ami_id = resource.attributes['AWS AMI Id']
        deployedResource.cloud_provider_resource = resource.attributes['Cloud Provider Resource']
        deployedResource.storage_iops = resource.attributes['Storage IOPS']
        deployedResource.storage_size = resource.attributes['Storage Size']
        deployedResource.instance_type = resource.attributes['Instance Type']
        deployedResource.auto_power_on = resource.attributes['Auto Power On']
        deployedResource.auto_power_off = resource.attributes['Auto Power Off']
        deployedResource.wait_for_ip = resource.attributes['Wait for IP']
        deployedResource.auto_delete = resource.attributes['Auto Delete']
        deployedResource.autoload = resource.attributes['Autoload']
        deployedResource.inbound_ports = resource.attributes['Inbound Ports']
        deployedResource.outbound_ports = resource.attributes['Outbound Ports']
        deployedResource.wait_for_credentials = resource.attributes['Wait for Credentials']

        return deployedResource

    def _get_deployment_info(self, image_model, name):
        """
        :type image_model: vCenterVMFromImageResourceModel
        """
        return DeployDataHolder({'app_name': name,
                                 'ami_params': image_model
                                 })

    def _get_command_inputs_list(self, data_holder):
        return [InputNameValue('request', jsonpickle.encode(data_holder, unpicklable=False))]
